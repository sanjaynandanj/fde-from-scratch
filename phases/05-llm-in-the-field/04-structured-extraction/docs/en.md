# Structured Extraction: Schemas, Validation, Retry-on-Garbage

Phase 5 · Lesson 04 · ~2h

## PROBLEM

The pilot that gets funded at half the enterprises you'll visit is some variant of: "we have 40,000 PDFs — invoices, contracts, intake forms — and four people who retype them into the ERP." The model demo takes an hour: paste an invoice, ask for JSON, get JSON. The champion is thrilled. Then you run the same prompt over the first real batch and discover what "get JSON" actually means at scale: the model wraps output in markdown fences with a cheerful "Sure! Here is the JSON:", returns `total` as the string `"1,499.00"`, lowercases the currency code your ERP validates against an enum, invents a `confidence` field nobody asked for, and — on one memorable document — returns a haiku about invoices. Each failure is rare. At 40,000 documents, *every* rare failure happens hundreds of times, and every one that reaches the ERP is a data-corruption incident with the customer's name on it.

The demo was the model. The product is the *harness*: a schema that defines "correct," a validator that rejects everything else, and a bounded retry loop that feeds errors back to the model. That harness is maybe 60 lines. It's also the difference between a demo and a system a controller will sign off on.

## INTUITION

Three design decisions define the harness:

**Where does "correct" live?** In a schema — explicit, machine-checkable, and *outside* the prompt. You'll also describe the schema in the prompt, but the prompt is a request; the validator is the law. The schema needs types, required-vs-optional, and enums (`currency` must be one of the codes the ERP accepts — "eur" is not "EUR" to an ERP). One deliberate strictness: **reject unknown fields.** A model that adds `confidence: 0.9` is hallucinating structure; today it's harmless, tomorrow it's a field your downstream code accidentally starts trusting.

**How lenient is parsing?** Two-layered. Be *tolerant of packaging* — strip markdown fences before parsing, because refusing an answer over decoration is throwing away money. Be *strict about content* — with one principled exception: coerce int to float where the schema wants float, because JSON's `250` for a total is unambiguous and rejecting it would be pedantry. Everything else — string-where-float, enum-case mismatches — gets rejected. The line to hold: coerce only where meaning is unambiguous; never "repair" ambiguity (parsing `"1,499.00"` yourself means guessing whether `,` is a thousands separator — European invoices will punish you).

**What happens on failure?** The insight that makes extraction shippable: **the error message is the next prompt.** Models are good at fixing *specifically named* mistakes. "Not valid JSON: expecting ',' at line 3" or "field 'total' must be float, got str" produces a corrected retry far more reliably than re-sending the original prompt and hoping. But the loop must be *bounded* — a model that never converges must raise after N attempts, not burn tokens forever — and the attempt count must be *recorded*, because attempts-per-document is the cost-and-health metric of a production extraction pipeline. Rising attempt rates are how you notice a model version change degraded you before the customer does.

The economics, for the CFO conversation: a retry doubles the cost of the ~10% of documents that need it (~1.1x total cost) and eliminates the failure mode where a human audits every row (~2x labor). This is the cheapest reliability you will ever buy.

## BUILD IT

Run it: `python code/lesson.py`. The whole harness, plus a MockLLM scripted with the classic three-act failure.

**The schema is data, not code.** Five fields, each with a rule:

```python
SCHEMA = {
    "invoice_id": {"type": str, "required": True},
    "vendor": {"type": str, "required": True},
    "total": {"type": float, "required": True},
    "currency": {"type": str, "required": True, "enum": ["USD", "EUR", "INR"]},
    "line_items": {"type": list, "required": False},
}
```

Schema-as-data means the customer's fields change (they will, in week two) without touching validator logic.

**Fence-stripping is tolerance of packaging.** `strip_fences` regex-extracts the interior of ` ```json ... ``` ` blocks if present, else returns the raw text. Note in the test that attempt 1 fails *anyway* — the fenced content itself is truncated, invalid JSON. Stripping fences isn't about trusting the model; it's about failing on the real problem.

**`validate` returns a list of errors, not a boolean.** This is the design decision the retry loop depends on — a boolean says "bad"; a list says *what to fix*:

```python
if rule["type"] is float and isinstance(value, int):
    value = data[field] = float(value)
if not isinstance(value, rule["type"]):
    errors.append(f"field '{field}' must be {rule['type'].__name__}, "
                  f"got {type(value).__name__}")
elif "enum" in rule and value not in rule["enum"]:
    errors.append(f"field '{field}' must be one of {rule['enum']}, got '{value}'")
```

The int→float coercion is the one permitted repair, applied *before* the type check so `250` passes as `250.0`. Missing required fields, wrong types, bad enum values, and unknown fields all accumulate into one list — the model gets told *everything* wrong at once, converging in one retry instead of playing twenty questions.

**The retry loop feeds errors back, bounded.** `extract` is the harness's heartbeat:

```python
for attempt in range(1, max_attempts + 1):
    raw = llm.complete(prompt)
    try:
        data = json.loads(strip_fences(raw))
    except json.JSONDecodeError as e:
        prompt = f"Your output was not valid JSON ({e}). Return ONLY JSON.\nDOC: {document}"
        continue
    errors = validate(data)
    if not errors:
        data["_attempts"] = attempt
        return data
    prompt = f"Fix these errors and return the full JSON again: {errors}\nDOC: {document}"
raise ValueError(f"extraction failed after {max_attempts} attempts")
```

Two failure classes, two different corrective prompts — parse errors get the JSON-only instruction with the *parser's own message*; validation errors get the full error list. The document rides along in every retry (the model needs the source, not just the scolding). Success stamps `_attempts` into the result — the observability hook. Exhaustion raises loudly; in production that `ValueError` routes the document to a human-review queue rather than crashing the batch.

**The test scripts the three-act failure and checks the *prompts*.** Act one: fenced, truncated prose. Act two: string total, lowercase currency. Act three: correct. The assertions go beyond the output:

```python
assert "not valid JSON" in llm.prompts[1], "attempt 2 must carry the parse error"
assert "must be float" in llm.prompts[2] and "must be one of" in llm.prompts[2]
```

The harness's *feedback quality* is under test, not just its final answer — if the retry prompt ever stops carrying the errors, the suite fails even though extraction still succeeds. The remaining cases pin the edges: a clean first-try response with int coercion (`_attempts == 1`, `total == 250.0`), a never-converging model raising after exactly 4 attempts, and the unknown-field hallucination (`confidence: 0.9`) caught by name.

## FIELD NOTES

- Real accuracy problems are usually *semantic*, not structural: valid JSON, right types, wrong values — the model read the shipping total instead of the invoice total. Schema validation can't catch that; the eval harness (Lesson 06) with a labeled golden set can. Ship both, and add cheap semantic checks where they exist (line items should sum to `total`, dates should be plausible).
- Negotiate the schema with the *consuming system's* owner, not the champion. The ERP's import spec is the real contract; "close enough" fields are re-keyed by the same four people you were meant to free.
- Batch economics: log `_attempts` per document from day one and graph it on the pilot dashboard. It's simultaneously your cost model, your model-regression alarm, and — trending down after a prompt fix — the chart that demos beautifully in the weekly.
- Set `max_attempts` low (3–4). If a document doesn't converge in three specific-feedback rounds, it won't in ten — it's a bad scan, a weird template, or genuinely ambiguous, and a human should see it. The review-queue rate (typically 2–5%) goes *in* the proposal, not under the rug: "97% straight-through, 3% human-reviewed" is a claim a controller can sign.

## INTERVIEW ANGLE

Structured extraction is a favorite practical exercise in lab FDE loops — often literally "here's a document and a target schema; make model output reliable." Interviewers look for schema-outside-the-prompt, error feedback, and bounded retries; candidates who say "I'd just prompt it to return JSON" fail on the spot.

Sample questions:

1. "The model returns JSON 95% of the time. Your batch is 40k documents. What do you build?" (Validator + bounded feedback-retry loop + human-review queue for exhaustion; 95% → ~99.5%+ straight-through with attempts as the health metric.)
2. "When should your harness coerce a value versus reject it?" (Coerce only unambiguous representation gaps like int→float; reject anything requiring interpretation — locale-formatted numbers, enum case — and feed the error back.)
3. "How do you detect that a model upgrade silently degraded your extraction?" (Attempts-per-document trend, exhaustion rate, plus a golden-set eval gate — bridging to Lesson 06.)

## DRILL

1. **Extend:** add a `date` field with rule `{"type": str, "required": True, "format": "YYYY-MM-DD"}` and teach `validate` to check the format with a regex. Script a MockLLM that returns `"15/03/2026"` first, then the ISO form on retry — assert the retry prompt names the format.
2. **Break:** make the schema require a field the document genuinely doesn't contain (e.g., `po_number` on this invoice). Watch the loop burn all four attempts on an unwinnable task. What should the harness distinguish here? (Model failure vs. document deficiency.) Sketch the fix: allow the model to return an explicit `null` with a reason, validated as a distinct "not present" outcome.
3. **Fix:** `validate` mutates its input (`data[field] = float(value)`) — the caller's dict changes as a side effect of *checking* it. Refactor to return `(errors, coerced_copy)` without mutation, fix `extract` accordingly, and add an assertion that the original parsed dict is untouched. Then write one sentence on why mutation-during-validation is the kind of bug that only surfaces after someone adds a "dry-run" mode.
