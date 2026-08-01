# Capstone 02 — Entity-Resolution Engine

**Production-grade dedup across three CRM extracts.** · Estimated: 8–10 hours · Extends the resolution patterns from Capstone 01.

---

## Overview

In Capstone 01 you built entity resolution good enough for a pilot. This capstone builds it good enough to bet a company's revenue reporting on. The difference is not the matching algorithm — it is everything around it: blocking that scales, scoring you can defend in a meeting, survivorship rules a business owner signed off on, an audit trail that answers "why did these two merge?" six months later, and precision/recall you *measured* instead of vibed.

This is the single most common FDE take-home archetype (see `interview-bank/take-home-patterns.md`). Do this capstone well and you have a portfolio piece that answers the interview question before it is asked.

## Scenario: Northgate Industrial Supply

Northgate Industrial Supply is a fictional B2B distributor (MRO parts, ~40k customer accounts). Over 18 months they acquired two smaller competitors: **Vulcan Fastener Co.** and **TriState Maintenance Products**. Three sales teams, three CRMs, one very unhappy CFO who just discovered that "Acme Manufacturing" appears to be 11 different customers with 4 different credit limits, and one of them is on credit hold while another just got net-60 terms.

The extracts you receive:

1. **Northgate CRM** (Salesforce-ish CSV) — ~40k accounts. Best hygiene of the three but a decade of drift: "Acme Mfg", "ACME MANUFACTURING INC", branch offices entered as separate accounts, phone numbers in 4 formats.
2. **Vulcan CRM** (Dynamics-ish CSV) — ~12k accounts. Different field names, addresses split across 3 columns, a `parent_account` field that is populated 30% of the time and wrong some of that time.
3. **TriState** (export from a homegrown Access database) — ~8k accounts. The nightmare file: no stable IDs (row numbers), company names with embedded contact names ("Acme Mfg - ask for Doug"), addresses in one free-text column, an `active` flag that means different things depending on which decade the row was created in.

Overlap is real and unknown to the customer: many accounts bought from two or all three companies. Your engine must produce one golden customer record per real-world business, with full traceability.

The business stakes drive the rules: merged records determine **credit limit, payment terms, and assigned sales rep** — which is why survivorship cannot be "pick the longest string" and why a false merge (two different companies fused) is far more expensive than a false split.

## Prerequisites

- **Phase 3**, especially lessons 05 (blocking/exact match), 06 (fuzzy, scoring, survivorship), 10 (quarantine), 13 (lineage)
- **Phase 10** drill 03 (deduplicate the CRM) — this capstone is that drill at 10x rigor
- **Capstone 01** milestone 4 — reuse your match-decision-log and needs-review-queue patterns

## Milestone 1 — Generators and the labeled sample (~2h)

As in Capstone 01: you write the world, then the three broken views of it.

**Deliverables**

- `truth.py`: ~15k real-world businesses; each assigned to 1–3 of the source systems with realistic overlap (~20% of businesses in 2+ systems).
- Three generators producing the extracts described above, each with its own damage profile, deterministic under a seed.
- A fenced answer key mapping every source row to its true business ID.
- **The labeled sample**: a separate file of 500 record *pairs* (mix of true matches, true non-matches, and deliberately hard cases — same name different city, same address different company) with labels. This simulates the "the customer's ops team hand-labeled 500 pairs for you" step, which in the field you must always request. Only tests and the evaluation script may read labels.

**Acceptance criteria**

- Deterministic under seed; damage rates parameterized and self-asserted.
- The hard-case pairs exist by construction (generator plants them), not by accident.

## Milestone 2 — Normalization and blocking (~2h)

40k × 60k comparisons is 2.4 billion pairs. Blocking is what makes this an engine instead of a science fair.

**Deliverables**

- Canonical normalization module: legal-suffix stripping (Inc/LLC/Co/Corp variants), whitespace/punctuation, phone → digits, address tokenization (from the free-text TriState column too), embedded-contact-name stripping.
- At least three blocking strategies run in union: e.g., normalized-name prefix, phone, zip + street number. Documented reasoning for each: what class of true match does it catch, what does it miss.
- Blocking metrics printed: candidate pairs generated, reduction ratio vs full cross-product, and — measured against the answer key in tests — **pair completeness** (what fraction of true matching pairs survive blocking).

**Acceptance criteria**

- Pair completeness ≥ 0.98 (a true match that never becomes a candidate pair is unrecoverable — blocking recall is the ceiling on system recall).
- Candidate set < 1% of the full cross-product.
- Full blocking pass on all ~60k records completes in under 60 seconds, stdlib only (dict-based inverted indexes are enough).

## Milestone 3 — Scoring and match decisions (~2h)

**Deliverables**

- Pairwise scorer combining field similarities (name token overlap or trigram similarity, address, phone, city/zip — all implementable in stdlib; `difflib.SequenceMatcher` is allowed) into a weighted score with per-field null handling that you document (missing phone is not evidence against a match).
- Three-band decision policy: auto-match ≥ upper threshold, auto-non-match ≤ lower threshold, needs-review in between. Thresholds chosen *using the labeled sample* — show the threshold-sweep table (precision/recall at each cutoff) that justified your choice.
- Transitive clustering of matched pairs into entities, with a guard: if a cluster exceeds a size cap or contains an internal contradiction (two different verified phone numbers, conflicting states), flag the whole cluster for review instead of merging.

**Acceptance criteria**

- On the labeled sample: **precision ≥ 0.99 on auto-matches** and recall ≥ 0.90 overall (the review queue may capture the rest). The asymmetry is the point — restate in your README why false merges cost more here.
- Needs-review queue ≤ 5% of candidate pairs.
- The chain-merge guard has a test: a planted A~B, B~C, A≁C triangle does not silently produce a 3-cluster.

## Milestone 4 — Survivorship and the golden record (~1.5h)

**Deliverables**

- Written survivorship policy (`SURVIVORSHIP.md`), framed as the memo you would send the Northgate CFO for sign-off. Per field, the rule and the business rationale: e.g., credit limit → most conservative value pending manual review, never auto-max; payment terms → Northgate's system wins (acquirer's terms govern); address → most recently verified source; sales rep → explicit tie-break rule because two reps will both claim the account (this is a political decision — say so, and route it to the customer).
- The engine that applies the policy and emits golden records with per-field source attribution.
- Conflict report: every golden record where sources disagreed on a business-critical field (credit limit, terms, hold status), exported as a CSV for customer review.

**Acceptance criteria**

- Every golden-record field traceable to a source row and rule (spot-check tests).
- Zero credit limits or hold-statuses resolved by "highest wins" — the tests assert conservatism.
- The policy doc distinguishes decisions you made from decisions you escalated to the customer.

## Milestone 5 — Audit trail and evaluation report (~1.5h)

**Deliverables**

- Append-only audit log (SQLite or JSONL): every merge decision with inputs, per-field scores, rule/threshold fired, timestamp, and engine version. Plus a `why.py` tool: give it two source record IDs, it prints the full explanation of why they did or did not merge.
- Un-merge support: a command that splits a golden record back into its sources and logs the reversal — because the customer *will* find one wrong merge, and "we can fix it in seconds, here's the log" is the difference between a hiccup and a lost account.
- `EVALUATION.md`: final precision/recall on the labeled sample, blocking metrics, cluster-size distribution, review-queue size, threshold-sweep table, and honest known weaknesses (e.g., "franchise locations sharing a phone number will over-merge; mitigated by the cluster guard, not solved").

**Acceptance criteria**

- `why.py` produces a correct, human-readable explanation for a planted true match, a planted non-match, and a review-band pair.
- Un-merge round-trip test: merge → un-merge → source records intact, audit log shows both events.
- Every number in `EVALUATION.md` is produced by a script, not typed in.

---

## Grading rubric

| Dimension | Novice | Competent | Strong hire |
|---|---|---|---|
| **Blocking** | Full cross-product or one lucky key | Multiple strategies, measured reduction | Pair completeness measured and treated as the recall ceiling; each strategy justified by the miss-class it covers |
| **Matching** | Single threshold, unmeasured | Three bands, precision/recall on the labeled sample | Threshold sweep shown; precision asymmetry argued from business cost; chain-merge guard tested |
| **Survivorship** | Longest-string / most-recent everywhere | Per-field rules, documented | Rules framed as customer sign-off decisions; political fields (sales rep) explicitly escalated; conservatism on money fields tested |
| **Auditability** | Merges happen, evidence vanishes | Decision log exists | `why.py` + un-merge + versioned log: a wrong merge is a 5-minute fix with a paper trail |
| **Honesty** | Reports only the wins | Reports P/R accurately | Names its own failure modes and quantifies the review burden it creates for the customer |

## Stretch goals

- Incremental mode: a fourth "weekly delta" file arrives; new records resolve against existing golden records without re-running the world, and the audit log shows stable entity IDs surviving the update.
- Hierarchy resolution: use Vulcan's unreliable `parent_account` plus address evidence to propose branch → headquarters rollups as a *suggested* layer, never auto-applied.
- Review UI: one-file stdlib web page that serves the needs-review queue as side-by-side cards with match/no-match buttons writing back to the audit log.

## Estimated hours

| Milestone | Hours |
|---|---|
| 1 — Generators + labeled sample | 2 |
| 2 — Normalization + blocking | 2 |
| 3 — Scoring + decisions | 2 |
| 4 — Survivorship | 1.5 |
| 5 — Audit trail + evaluation | 1.5 |
| **Total** | **8–10** |
