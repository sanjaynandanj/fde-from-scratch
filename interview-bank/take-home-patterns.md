# Take-Home Patterns — The 5 Recurring FDE Archetypes and How to Win Them

FDE take-homes are not leetcode. They are simulations of the job: here is something
messy and underspecified, you have a few hours, show us what you'd actually ship.
Across companies, virtually every FDE take-home is one of five archetypes — and each
one is secretly grading the same three things:

1. **Judgment under a time budget** — what you chose to do, and what you chose not to.
2. **Contact with reality** — did you find the trap in the data, or process it blindly?
3. **Communication** — can a stranger run your work and understand your decisions in
   five minutes? The README is not documentation; it is the deliverable.

A universal rule before the archetypes: **respect the stated time limit and say so.**
If they say 4 hours, deliver an honest 4 hours plus a "what I'd do with more time"
section. Reviewers can tell when a "4-hour" submission took 20 — and it doesn't read
as impressive; it reads as someone who will blow every pilot timeline. Scope control
*is* the test.

---

## Archetype 1 — The Messy-CSV Analysis

**The prompt shape**: "Here's a CSV (or three) of [orders / sensor readings / claims /
support tickets]. Tell us something interesting," or "answer these four questions
about the data." The files are deliberately damaged: mixed date formats, duplicate
rows, Excel-mangled IDs, encoding glitches, a column that changes meaning halfway
through, impossible values.

### What's really being tested

- Whether you **profile before you analyze**. The damage is planted; finding it is
  the exam. A candidate who computes averages over a column containing `-999`
  sentinels has failed regardless of chart quality.
- Whether you handle mess **explicitly** — documented decisions, quarantined bad
  rows — or silently drop/coerce and hope.
- Whether your "something interesting" is *actually interesting* — an insight a
  business owner would act on, not "the mean order value is $47.20."
- Basic craft: can you write clean, runnable data code without a notebook full of
  dead cells.

### The winning approach — 4-hour budget

| Time | Activity |
|---|---|
| 0:00–0:40 | **Profile everything.** Row counts, types, null rates, cardinality, top values per column, duplicate check, date-range sanity. Write down every anomaly found — this list is gold. |
| 0:40–1:20 | **Clean deliberately.** Fix what's fixable (dates, encodings, dedup with a stated rule), quarantine what isn't, and log counts for every action: "removed 212 exact duplicates; quarantined 47 rows with unparseable dates (0.3%)." |
| 1:20–2:40 | **Answer the questions / find the insight.** Aim for 2–3 findings with a "so what" attached, at least one of which is only visible *because* you cleaned correctly (this proves the cleaning mattered). One good chart per finding, labeled axes, no chart junk. |
| 2:40–3:20 | **Harden.** Make it run end-to-end from raw files with one command. Add 3–5 assertions on the invariants your analysis depends on. |
| 3:20–4:00 | **Write the README** (template below). This is not the leftover slot — protect it. |

**The differentiating move**: a short "Data quality findings" section listing every
trap you found, what you did about it, and how it would have distorted the analysis
if unhandled. Reviewers planted those traps; showing them the full list, with impact,
is the strongest possible signal — it's the take-home equivalent of the customer
data-profile readout from week one of a real engagement.

### The README that wins

```markdown
# [Task name] — [Your name]

## How to run
    python analysis.py data/          # produces output/report.md and output/*.png
    (Python 3.10+, stdlib + pandas/matplotlib only)

## Answers / Key findings
1. <Finding, one sentence, with the number.>  <One sentence of "so what.">
2. ...
(Details and charts: output/report.md)

## Data quality findings (what I found and what I did)
| Issue | Extent | Handling | Impact if ignored |
|---|---|---|---|
| Dates in 3 formats incl. DD/MM ambiguity | 100% of `order_date` | Column-level format election; 14 ambiguous rows quarantined | Q3 revenue shifts by 8% |
| ... | | | |

## Decisions & assumptions
- Dedup rule: exact match on (id, timestamp); kept latest by `updated_at`. Why: ...
- Treated `-999` in `temperature` as sentinel null (212 rows). Why: ...

## What I'd do with more time
- <2–4 items, specific, prioritized — not a wish list.>

## Time spent: ~4h (0.7 profiling / 0.7 cleaning / 1.3 analysis / 0.6 hardening / 0.7 writeup)
```

### Classic mistakes

- **Analyzing without profiling** — missing the planted traps; instant fail.
- **Silent cleaning** — dropping rows with no count, no rule, no mention. Reviewers
  diff your numbers against the raw data; unexplained deltas read as carelessness.
- **The 40-cell notebook** with dead ends, no narrative, and out-of-order execution.
  If you use a notebook, it must run top-to-bottom clean — better: a script plus a
  short report.
- **Insight theater** — ten shallow charts instead of two findings with consequences.
- **Over-engineering** — a configurable ETL framework for a one-shot analysis. Wrong
  judgment, and it ate the README time.
- **Ignoring the ambiguous-date landmine** — if day/month order is ambiguous,
  *saying so and stating your resolution rule* is worth more than any chart.

---

## Archetype 2 — Build-a-Small-API

**The prompt shape**: "Build a small service that ingests this data and exposes
endpoints for [search / lookup / aggregate]. Include tests. Don't spend more than
N hours." Sometimes with a spec, often deliberately underspecified.

### What's really being tested

- **Sensible design at small scale** — clean layering (ingest / store / serve), not
  a framework showcase. FDE APIs are pilot APIs: clarity beats cleverness.
- **Edge-and-error behavior** — what happens on a bad ID, malformed input, empty
  result? This is where "would ship at a customer site" separates from "demo-ware."
- **Testing judgment** — a few tests that hit the load-bearing logic and the error
  paths, not 100% coverage of getters.
- **Underspecification handling** — did you make reasonable choices and *document
  them*, or freeze / gold-plate?

### The winning approach — 4-hour budget

| Time | Activity |
|---|---|
| 0:00–0:30 | Read the data first (yes, profile again — API take-homes hide data traps too). Sketch the endpoints and the storage shape. Choose boring: SQLite or in-memory + the language's standard/minimal web stack. |
| 0:30–1:00 | **Walking skeleton**: one endpoint returning real data end-to-end. |
| 1:00–2:30 | Fill out endpoints. Validation on every input; correct status codes (400 vs 404 vs 500); pagination if lists can be large; consistent JSON error shape. |
| 2:30–3:15 | **Tests**: happy path per endpoint + the error paths + one data-edge test (the weird record from profiling). Runnable with one command. |
| 3:15–4:00 | README, example curl calls that actually work, and a "design decisions / not done" section. |

**The differentiating moves**: a consistent error envelope (`{"error": {"code":
..., "message": ...}}`) discussed in the README; input validation that shows you've
been burned before (limits on page size, rejection of malformed dates *with a helpful
message*); and one sentence about what you'd change for production (auth, real DB,
migrations) — showing you know the difference between pilot-grade and prod-grade
without having built the wrong one.

### The README that wins

```markdown
# [Service name]

## Run it
    python app.py           # serves on :8000, ingests data/ on startup (~2s)
    python -m pytest        # 14 tests, ~1s

## Try it
    curl 'localhost:8000/customers?q=smith&page=1'
    curl 'localhost:8000/customers/C-1042'
    curl 'localhost:8000/customers/NOPE'     # -> 404, error envelope

## API
| Method | Path | Notes |
|---|---|---|
| GET | /customers | `q` search, paginated (default 20, max 100) |
| ... | | |

## Design decisions
- SQLite over Postgres: single-file deploy, adequate for N=50k; swap path noted in code.
- Search is normalized-prefix match, not fuzzy: right cost/benefit at this size. 
- Ingest quarantines malformed rows (logged count) rather than failing startup.

## Not done (deliberately, for the time box)
- Auth (would add token middleware first), rate limiting, OpenAPI spec.

## Time spent: ~4h
```

### Classic mistakes

- **Framework maximalism** — a service mesh's worth of structure for four endpoints;
  time dies, judgment questioned.
- **No error handling** — a stack trace on bad input is the single most common fail;
  FDE reviewers poke the API with garbage *first*.
- **Ingesting the data with no validation** — the provided data contains at least one
  malformed record; crashing on startup because of it is a planted-trap fail.
- **Tests that test the framework** ("assert 200 on /") while the aggregation logic —
  the actual point — is untested.
- **A README without working curl examples.** Reviewers copy-paste; if the first
  command errors, the review is over before it starts.

---

## Archetype 3 — RAG-over-Documents

**The prompt shape**: "Here's a folder of documents (policies / manuals / contracts /
wiki dump). Build a system that answers questions about them. Here are five sample
questions." Increasingly the flagship take-home at AI-company FDE loops. Sometimes
API keys are provided; sometimes the constraint is "no external calls" (which is a
gift — see below).

### What's really being tested

- **Retrieval engineering, not model prompting.** Everyone can call a chat API; the
  signal is chunking choices, retrieval quality, and grounding discipline.
- **Whether you evaluate.** The five sample questions are a hint: they want to see
  an eval, however small. Candidates who build a golden set (the 5 given + ~10 of
  their own, with expected answers) and report scores are in a different tier.
- **Hallucination handling** — do answers cite sources? Does the system refuse when
  the corpus doesn't contain the answer? (At least one sample question is usually
  unanswerable from the corpus — a planted trap.)
- **Corpus contact** — did you notice the documents' actual structure and mess
  (duplicate versions, a scanned PDF, tables), or feed them blindly to a splitter?

### The winning approach — 6-hour budget (this archetype usually gets 4–8)

| Time | Activity |
|---|---|
| 0:00–0:45 | **Read the corpus like an FDE.** Inventory: how many docs, formats, structures; find the traps (near-duplicate versions? one unparseable file? tables?). Note them for the README. |
| 0:45–1:45 | Ingestion: parse, structure-aware chunking (respect headings/sections; keep table headers attached), metadata per chunk (doc, section, date/version if present). |
| 1:45–2:45 | Retrieval: hybrid if cheap (BM25/TF-IDF + embeddings; or TF-IDF alone if no external calls — a from-scratch TF-IDF retriever in stdlib is very achievable and reviewers love it), top-k with scores. |
| 2:45–3:45 | Generation: grounded prompt (answer only from context, cite chunk IDs, refuse if not found). If no API allowed: extractive answers (return the best passages with highlights) — a *retrieval-first* system with honest extractive output beats a hallucinating generative one, and saying that in the README is a flex. |
| 3:45–4:45 | **The eval.** Golden set: given questions + your own, including 2 unanswerable ones. Report retrieval hit-rate and answer correctness in a small table. This hour is the best-spent hour of the entire take-home. |
| 4:45–6:00 | Polish the refusal behavior, add the CLI/minimal UI, write the README with the eval table front and center. |

**The differentiating moves**: the eval table (even 15 questions); citations in every
answer; correct refusal on the unanswerable question (call out that you noticed it
was planted); and a "retrieval failure analysis" — one paragraph on which question
your system handles worst and why. That paragraph *is* Lesson 5-03 (why the demo
works and production doesn't) performed live, and it's exactly what a hiring FDE
wants to see.

### The README that wins

```markdown
# Doc-QA over [corpus]

## Run
    python ingest.py docs/        # parses, chunks (~1,200 chunks), builds index
    python ask.py "What is the refund window for enterprise plans?"
    python eval.py                # runs the 15-question golden set

## Eval results (the headline)
| Metric | Score |
|---|---|
| Retrieval hit@5 (13 answerable Qs) | 12/13 |
| Correct answers (graded by hand) | 11/13 |
| Correct refusals (2 unanswerable Qs) | 2/2 |

Worst case: Q7 (cross-document comparison) — retrieval returns both docs but
generation merges their terms; fix would be per-doc extraction then compare.

## Design
- Chunking: section-aware (headers preserved), ~300 tokens, tables kept whole.
- Retrieval: TF-IDF + BM25-style scoring, top-5. Hybrid embeddings noted as upgrade.
- Grounding: answers cite [doc:section]; refusal when top score < threshold
  (tuned on golden set).

## Corpus findings
- `policy_v2.pdf` and `policy_final.pdf` are near-duplicates (v2 newer) — indexed
  v2 only, noted as a versioning decision.
- `scan_003.pdf` has no text layer — excluded and flagged (would OCR in production).

## What I'd do with more time
Reranking; per-section parent-expansion; larger golden set with a second grader.

## Time: ~6h
```

### Classic mistakes

- **No eval.** The single biggest separator. A beautiful pipeline with zero
  measurement reads as "will ship vibes to a customer."
- **Fixed-size chunking through tables and headers** — then wondering why the
  policy-table question fails.
- **No refusal path** — the system confidently answers the planted unanswerable
  question; in an FDE review this is close to disqualifying, because it's the
  exact failure that torches customer trust in the field.
- **Ignoring the corpus traps** — duplicate versions both indexed (contradictory
  retrievals), the scanned PDF silently contributing nothing.
- **Prompt-maximalism** — a 2-page prompt and no retrieval work; or spending the
  whole budget on a chat UI while retrieval is `text.split("\n\n")`.
- **Burning hours on vector DB setup** for 40 documents — in-memory arrays or
  TF-IDF was fine; infra maximalism is judgment failure at take-home scale.

---

## Archetype 4 — Data Reconciliation

**The prompt shape**: "System A (ERP extract) and System B (bank statement / vendor
report / new platform) should agree. They don't. Explain the differences and produce
a reconciliation." Two-to-three files, engineered so that several *classes* of
discrepancy are present simultaneously.

### What's really being tested

- **Systematic method** — do you classify discrepancies by cause, or eyeball rows?
  The planted classes usually include: timing differences (transaction in A today,
  in B tomorrow), duplicates on one side, format-driven mismatches (IDs mangled,
  amounts as strings/negatives-in-parentheses, currency or sign conventions),
  genuinely missing records, and one definitional difference (A nets refunds,
  B doesn't — the subtle one that separates candidates).
- **Match-rate honesty** — what fraction did you explain, and how confident are you
  in each class? A 100% "explained" claim is a red flag; the strong submission has
  an explicit residual.
- **Accounting-adjacent care**: exact decimal arithmetic (no float drift in money),
  sign conventions, one-to-many matches (one payment covering three invoices).

### The winning approach — 4-hour budget

| Time | Activity |
|---|---|
| 0:00–0:30 | Profile both sides: counts, totals, date ranges, key uniqueness, amount distributions. Compute the headline gap first — "A sums to 1,204,332.10; B to 1,197,884.55; gap 6,447.55" — everything that follows explains that number. |
| 0:30–1:00 | Normalize: keys (trim/case/Excel-damage repair), amounts (decimal, signs, parentheses), dates (formats, and note timezone/posting-date semantics). |
| 1:00–2:15 | **Tiered matching**: exact on (key, amount, date) → exact key with date window (catches timing) → amount+date without key (catches key mangling) → one-to-many candidates (sum matching within key/date). Every record ends in exactly one bucket: matched-tier-N, or unmatched-A / unmatched-B. |
| 2:15–3:00 | **Classify the unmatched** into cause classes with evidence; hunt the definitional difference by segmenting the residual (if the gap concentrates in refund rows — there it is). |
| 3:00–4:00 | Produce the reconciliation report (the deliverable): waterfall from A's total to B's total through each explanation class, plus the honest residual. README. |

**The differentiating move**: the **reconciliation waterfall** — a table walking from
one system's total to the other's through each named cause with counts and amounts,
ending in a stated unexplained residual ("14 records, $312.40, 0.03% — candidates
for manual review, likely X"). That table is exactly what you'd hand a customer's
controller, and reviewers from Palantir-style backgrounds recognize it instantly.

### The README that wins

```markdown
# Reconciliation: ERP vs bank statement

## Run
    python reconcile.py data/erp.csv data/bank.csv   # -> output/reconciliation.xlsx + report.md

## Headline
ERP total: $1,204,332.10 (8,412 records) · Bank total: $1,197,884.55 (8,391 records)
Gap: $6,447.55 — **99.7% explained**, residual $312.40 (14 records) for review.

## Reconciliation waterfall
| Step | Records | Amount | Running gap |
|---|---|---|---|
| Starting gap | | 6,447.55 | 6,447.55 |
| Timing (posted next business day, matched ±3d) | 96 | 0.00 | 6,447.55 |
| Duplicates in ERP (double-keyed exports) | 11 | 4,891.15 | 1,556.40 |
| Definitional: ERP gross vs bank net-of-fees | 8,391 | 1,244.00 | 312.40 |
| **Unexplained residual** | 14 | **312.40** | — |

## Method
Tiered matching (exact → date-window → keyless amount+date → one-to-many sum);
all money as Decimal; match tiers and rules in reconcile.py, each with counts.

## Notable findings
- Bank deducts a per-transaction fee ERP records separately — the "definitional"
  class. Recommend: reconcile gross + fee account jointly.
- ERP export double-writes records updated during export window (11 found).

## Time: ~4h
```

### Classic mistakes

- **Row-by-row eyeballing** with no tiers and no classes — doesn't scale, misses
  systematics, reads as junior.
- **Float money.** `0.1 + 0.2` arithmetic producing phantom cents in a
  reconciliation take-home is an instant credibility hole. Use decimals.
- **Claiming 100%** — either the residual was forced into a class it doesn't belong
  to, or the definitional plant was mis-assigned. The honest residual is a feature.
- **Missing the one-to-many** — declaring three invoices "unmatched" when one bank
  payment covers them; the planted case that separates tiers of candidates.
- **No waterfall** — findings scattered in prose instead of one table from total to
  total. The controller-grade artifact is the deliverable; its absence means the
  candidate doesn't know what the customer needs.

---

## Archetype 5 — Open-Ended "Impress Us With This Dataset"

**The prompt shape**: "Here's a dataset (or a public dataset link). Spend up to N
hours. Build something you find interesting; be prepared to present it." No
questions, no spec. The scariest and most gameable archetype.

### What's really being tested

- **Product sense** — can you find a *user and a problem* in raw data, or do you
  produce an aimless EDA? The differentiator is framing: "I built X for user Y
  because the data shows problem Z" versus "here are some distributions."
- **Scoping** — an ambitious idea cut to an honest N hours beats a modest idea
  fully polished *and* beats an ambitious idea half-broken. They are watching the
  cut itself.
- **End-to-end bias** — FDE reviewers strongly prefer a small working *thing*
  (queryable, clickable, demoable) over a static analysis of the same quality.
- **The presentation** — this archetype almost always feeds a live walkthrough
  round; build with the 10-minute demo in mind.

### The winning approach — 6-hour budget

| Time | Activity |
|---|---|
| 0:00–0:45 | Profile the data (always). List 3 candidate directions; for each: who's the user, what's the pain, what's demoable in the budget. **Pick the one with the clearest user + a data-supported surprise.** Write the choice and the two rejects into the README now — showing the decision is part of the deliverable. |
| 0:45–1:15 | Define the walking skeleton for the pick and the demo narrative: "open on the map, click the anomaly, show the detail." Working backward from the demo moment keeps the build honest. |
| 1:15–4:15 | Build end-to-end thin: ingest → derived insight → minimal interface (a one-file web page over an API, or a crisp CLI — whatever demos the insight). Include one moment of genuine surprise from the data — the thing that makes the reviewer say "huh." |
| 4:15–5:00 | Self-test, seed a clean demo path, handle the embarrassing edge (empty result, missing data region). |
| 5:00–6:00 | README + a 10-line demo script for yourself. If presenting: rehearse once, timed. |

**The differentiating moves**: naming the user in the first sentence; the two
rejected directions with reasons (scope judgment made visible); one genuine
data-derived surprise rather than generic charts; and a working demo path that a
reviewer can reproduce in two commands. If the dataset is one of the war-horse
public sets, assume the reviewer has seen thirty NYC-taxi heat maps — the bar for
"interesting" rises with the dataset's fame, which is an argument for finding the
odd corner of the data rather than the obvious center.

### The README that wins

```markdown
# [Thing] — [one-line: what it is and for whom]

Ex: "Refill-risk radar — a triage view for pharmacy ops showing which patients'
refill gaps predict churn, built from the prescriptions dataset."

## Demo (2 commands)
    python build.py data/
    python serve.py            # -> localhost:8000, open on the pre-seeded view

## The finding
<One paragraph: the data-supported surprise, with the number, and why user Y cares.>

## What I chose and what I rejected
- **Chose**: X — clear user, demoable in budget, data supports it.
- Rejected: A (needed data we don't have), B (interesting but no actionable user).

## How it works
<5 lines: pipeline → derived metric → interface. Link to code map.>

## Honest limitations
<3 bullets. Ex: "correlation not causation on the churn signal; would validate
with holdout period"; "assumes refill dates are entry-accurate — they're not,
see data notes.">

## With more time
<Prioritized, 3 items.>

## Time: ~6h
```

### Classic mistakes

- **The aimless EDA** — 25 charts, no user, no problem, no verb. The most common
  submission and the most forgettable.
- **The overreach** — half of an ambitious ML product, ending in a broken demo and
  an apologetic README. Scope failure is *the* failure this archetype exists to
  detect.
- **No stated choice** — reviewers can't see judgment unless you show the options
  you rejected.
- **Ignoring data limitations** — presenting a churn "prediction" without noting
  the leakage or entry-date caveats; FDE reviewers probe exactly there in the
  follow-up round, and discovering the caveat *for* you is bad; watching you hide
  it is worse.
- **Building for yourself** — a technically cute artifact (a query language! a
  compression scheme!) with no plausible user; clever, and precisely not the job.
- **Unrehearsed presentation** — this archetype's live round is won by narrative
  (problem → user → finding → demo → limits), not by feature count.

---

## Cross-cutting: the meta-rubric reviewers actually hold

| Dimension | Weak | Strong |
|---|---|---|
| Time honesty | Obvious 3× overrun, or gold-plating | Honest budget, visible allocation, "with more time" list |
| Data contact | Processed blindly | Found the planted traps, documented handling + impact |
| Scope judgment | Everything half-done, or trivial scope fully done | Deliberate 80/20 with the cut explained |
| Reproducibility | "Works on my machine," missing deps | One or two commands, pinned/minimal deps, runs first try |
| Communication | Code dump + thin README | README answers run/what/why/limits in 5 minutes |
| Honesty | Overclaims, hidden failures | Stated limitations, honest residuals, refusals that work |
| Tests/checks | None, or coverage theater | Few assertions on load-bearing logic + error paths |

And one final field note: the follow-up interview about your take-home is usually
worth as much as the artifact. Re-read your own submission the night before, know
every decision's *why*, and be ready to extend it live ("how would you add
incremental updates? auth? a second data source?"). The take-home buys you the
conversation; the conversation is where the offer happens.
