# Hallucination Control: Grounding, Citations, Refusal Design

**Phase 5 · Lesson 07 · ~1.5h**

## PROBLEM

At a healthcare payer, the assistant confidently told a member-services agent that a specific procedure was covered under Plan Silver at 80%. It was not — the plan document said 60%, the model interpolated. The agent quoted the wrong number to the member on the phone. The customer's Chief Compliance Officer, unhappy, wanted to know how this could happen with a "grounded" system. You explain: the model was shown the correct chunk. It also invented a citation pointing to a chunk that didn't say what it claimed. Nothing in the pipeline caught it, because "check that the cited chunk ID exists" is not the same as "check that the cited chunk actually supports the claim." The pilot survived. The lesson didn't have to be learned on that call. Hallucination control is the layer between "the model produces fluent text" and "the enterprise can put its name on the text."

## INTUITION

Hallucination has three distinct shapes. Each needs a different control:

**Fabrication.** The model invents facts not in the sources. Cause: the model wasn't instructed to stay grounded, or was, but the sources didn't contain the answer and it filled in. Control: strict prompt scoping ("answer ONLY from sources"), a confidence gate before generation (Lesson 01), and a refusal path when retrieval is weak.

**Misgrounding.** The model produces something that resembles the sources but subtly changes a number, entity, or scope. This is the compliance-officer nightmare — the answer *looks* grounded, cites real chunks, and is wrong. Control: extractive verification. After generation, take each claim in the answer and check that it appears — verbatim or as a supported paraphrase — in the cited chunk. In its cheapest form: check that key entities (numbers, dates, IDs) in the answer appear in the cited chunk. Fail closed on mismatch.

**Overgeneralization.** The model answers a narrow question with a broad claim. Sources say "Plan Silver covers procedure X at 80% in-network"; the model drops the "in-network" qualifier. Control: prompt for scoped answers ("include all qualifiers present in the sources") and evaluate on qualifier-preservation as a metric distinct from correctness.

The philosophy: assume the model will hallucinate, and design the surrounding system so that hallucinations are detected, refused, or surfaced to a human. Never bet on the model being disciplined; bet on your checks.

## BUILD IT

Three layered controls, each independent:

**Layer 1: Refusal gate (pre-generation).** If retrieval top-1 score is below threshold, return the refusal template. No model call. This alone kills the "answer for questions not in the corpus" class of hallucinations.

**Layer 2: Citation validity (post-generation, cheap).** Parse citations from the answer. Assert every cited ID was in the retrieved set. Reject and retry (or refuse) on hallucinated citations.

```python
def check_citations(answer: str, retrieved_ids: set) -> bool:
    cited = set(re.findall(r"\[([\w#-]+)\]", answer))
    if not cited:
        return False  # ungrounded answer, refuse
    return cited.issubset(retrieved_ids)
```

**Layer 3: Extractive grounding check (post-generation, thorough).** For each numeric or named-entity claim in the answer, verify it appears in the cited chunk. Simplest version: extract numbers and named entities from the answer, extract from the cited chunks, assert containment.

```python
def entities(text: str) -> set:
    # Numbers, percentages, dates, proper nouns (capitalized runs).
    return set(re.findall(r"\d[\d.,%]*|\b[A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)*", text))

def check_grounding(answer: str, chunks: list) -> list:
    ans_ents = entities(answer)
    source_text = " ".join(c["text"] for c in chunks)
    src_ents = entities(source_text)
    return [e for e in ans_ents if e not in src_ents]  # ungrounded entities
```

If the list is non-empty, the answer contains an entity not present in the sources — flag, log, escalate. In a strict-mode deployment, refuse. In a review-mode deployment, surface to the human reviewer.

**The refusal template.** Blunt is trustworthy. "I don't have that information in the provided sources." No apologies, no suggestions, no invented alternatives. Add a link to escalation ("For questions not covered here, contact `benefits@acme.com`") — refusal without a next step feels like a bug to users; refusal with a next step feels like a feature.

## FIELD NOTES

- Extractive grounding is imperfect. It over-flags (paraphrases with different word forms) and under-flags (semantic errors with identical entities). It is still worth shipping — it catches the exact class of misgrounding that compliance officers care about, and its false positives are recoverable (retry or human review).
- The customer will ask "what's the hallucination rate?" There is no single number. Report three: refusal rate (should the system have answered?), fabrication rate on cases it did answer, misgrounding rate on cases with citations. Each has a different fix. A single number invites the wrong conversation.
- Sycophancy is a hallucination cousin. When a user says "the policy says 30 days, right?" and the actual policy says 15, weak prompts will let the model agree. Test this explicitly with leading questions in your eval set. The prompt must say: "If the user asserts a fact that contradicts the sources, correct them politely, citing the source."
- Refusal is the feature. Customers whose systems refuse cleanly build user trust faster than customers whose systems answer everything. The champion often doesn't believe this until you show it in production. Set the refusal rate expectation in discovery — "we expect to refuse 10-25% of real queries" — so it lands as design, not failure.
- In regulated deployments, log everything: the query, the retrieved chunk IDs and scores, the model output, the citation check result, the grounding check result. When the CCO calls, "here is the exact evidence chain" is the only acceptable answer.

## INTERVIEW ANGLE

Hallucination questions in FDE loops are increasingly common because the labs' enterprise customers are increasingly regulated. Interviewers listen for layered controls, honest acknowledgment of limits, and refusal-as-feature framing.

Sample questions:

1. "How do you stop an LLM from hallucinating in a customer deployment?" (Layered controls: pre-generation refusal gate, prompt grounding, citation verification, extractive entity check, human review for high-stakes. Bonus: acknowledge that no single control is sufficient.)
2. "The model cites a real document but says something the document doesn't say. How do you catch it?" (Extractive grounding — verify claims/entities in the answer appear in the cited source. Discuss false-positive tolerance and the trade-off with refusal rate.)
3. "The customer wants zero hallucinations. What do you say?" (Reframe: no ML system has zero errors; the design is about detection, refusal, and escalation. Show them the eval breakdown by failure mode. Set an acceptable-refusal-rate SLA in exchange for a maximum-fabrication-rate SLA.)

## DRILL

Take the RAG system from Lesson 01. Add Layer 3 — the extractive grounding check. Write a MockLLM script that produces (a) a correct grounded answer, (b) an answer with a hallucinated citation ID, (c) an answer that cites a real chunk but changes a number. Assert your checks catch (b) and (c) and let (a) through. Now add a query that should refuse and verify the refusal happens before the model call. Save the test suite — you will run it on every prompt change for the rest of the engagement.
