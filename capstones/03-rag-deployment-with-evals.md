# Capstone 03 — RAG Deployment with Evals

**Grounded Q&A over Meridian Health's policy documents, with the eval harness built the way you'd build it with a real customer.** · Estimated: 9–11 hours · Extends Capstone 01's Meridian engagement.

---

## Overview

Every RAG demo works. Almost no RAG deployment survives contact with the customer's actual questions. The gap is closed by exactly one thing: an evaluation harness built *with* the customer, against *their* documents, before anyone argues about accuracy in a meeting.

In this capstone you return to Meridian Health (Capstone 01). The pilot dashboard earned trust; Dana's next ask is grounded Q&A over Meridian's policy and procedure library — "our nurses page through 40 PDFs to answer questions the documents already answer." You will build the corpus, the retrieval pipeline, the answer layer, the refusal and PII guardrails, and — the actual deliverable — a golden-set eval and an accuracy report honest enough to show Rich.

Per repo convention, all LLM behavior uses **MockLLM**: a deterministic, scriptable stand-in (see Phase 0 lesson 06 and Phase 5). No API keys, no network. The engineering — chunking, retrieval, grounding, citation checking, refusal logic, evals — is real; only the generation is scripted. That trade is deliberate: the parts that fail in the field are the parts you are building.

## Scenario

Maria's team fields the same questions daily: "What's the lift-assist policy on 4 West?", "Who can witness a controlled-substance waste?", "What's the visitor policy in the ICU after 8pm?" The answers live in ~30 policy documents of wildly varying quality. Two constraints from the discovery follow-up call:

> **RICH:** If this thing invents a policy that doesn't exist and a nurse acts on it, that's not a bug, that's a patient-safety incident. I'd rather it refuse ten real questions than invent one answer.
>
> **DANA:** And the compliance team's condition: questions sometimes contain patient details — "can Mr. Kowalski in 4W12 have visitors" — nothing patient-identifying goes into logs or answers. Policy in, policy out.

Those two quotes are your non-functional requirements. Refusal is a feature. PII handling is a gate, not a nice-to-have.

## Prerequisites

- **Phase 5**, especially lessons 01 (RAG from scratch), 02 (chunking), 03 (retrieval quality), 06 (eval harness), 07 (hallucination control, refusal), 11 (guardrails)
- **Phase 6** lesson 03 (PII detection and redaction)
- **Capstone 01** — the Meridian context, personas, and repo patterns

## Milestone 1 — Corpus generation (~2h)

**Deliverables**

- A generator producing ~30 Meridian policy documents as plain text/markdown, deterministic under seed. Realistic variety by construction: clean numbered policies; a scanned-and-OCR'd-looking one (broken line wraps, `O`/`0` swaps); two policies that **contradict each other** (the 2019 visitor policy and the 2023 revision — only one is current, indicated by an effective-date header); a policy that exists only as a converted table (pipe-text); and at least three topics deliberately *absent* from the corpus (e.g., anything about physician credentialing) so refusal can be tested against real gaps.
- A corpus manifest: doc ID, title, effective date, owner department, supersedes.

**Acceptance criteria**

- Deterministic under seed; contradiction pair and known-gap topics planted by construction and listed in the manifest for test use.
- At least 4 distinct formatting pathologies present (assert via generator self-test).

## Milestone 2 — Ingestion, chunking, retrieval (~2.5h)

**Deliverables**

- Chunker that respects document structure (headers/sections), attaches metadata to every chunk: doc ID, section, effective date. Handles the OCR-damaged doc without producing garbage chunks (a quality filter that quarantines unreadable chunks — same quarantine philosophy as Capstone 01).
- TF-IDF retrieval from scratch (per Phase 5 lesson 01): tokenizer, IDF weighting, cosine scoring. Stdlib only.
- Recency rule: when retrieved chunks come from documents where one supersedes another, the superseded chunk is demoted or dropped — the 2019/2023 contradiction must be resolved by metadata, not by luck.
- A retrieval debug CLI: given a query, show top-k chunks with scores — the tool you will live in during milestone 4.

**Acceptance criteria**

- Planted test: a query about visitor hours retrieves the 2023 policy, not the 2019 one.
- OCR-damaged doc contributes usable chunks or quarantines them — no mojibake in any top-5 result for the test query set.
- Retrieval latency < 200ms per query over the full corpus.

## Milestone 3 — Grounded answers, citations, refusal (~2.5h)

**Deliverables**

- MockLLM harness: the mock is scripted per-test with expected outputs, including deliberately *bad* outputs (uncited claims, fabricated policy numbers) so your defenses can be tested. Your defenses cannot be tested against a mock that only behaves.
- Answer pipeline: query → retrieve → assemble grounded prompt (chunks + citation instructions + Meridian glossary) → MockLLM → **post-hoc grounding check**: every sentence in the answer must be attributable to a retrieved chunk (n-gram/token-overlap check is sufficient); uncited or unsupported sentences trigger rewrite-or-refuse.
- Refusal design, three distinct classes with distinct user-facing messages: (a) nothing relevant retrieved → "not in the policy library, here's who owns this area" (use the manifest's owner field); (b) retrieval confidence below threshold → refuse rather than stretch; (c) question is out of scope for a policy assistant (medical advice, patient-specific decisions) → refuse with redirection. Rich's rule is the spec: refusing well beats answering badly.
- Every answer carries citations: doc ID + section, rendered for a human.

**Acceptance criteria**

- Test: MockLLM scripted to fabricate a policy number → grounding check catches it → user sees a refusal or corrected answer, never the fabrication.
- Test: each of the three refusal classes triggers on its planted query and produces its distinct message.
- Test: known-gap topic (planted in milestone 1) yields refusal class (a) with the correct owning department.

## Milestone 4 — The golden set, built "with the customer" (~2h)

This is the milestone that separates FDE work from demo work. You simulate the customer workshop where the golden set gets built — and you play both chairs.

**Deliverables**

- `GOLDEN-SET-WORKSHOP.md`: a short doc describing the session you would run with Maria's team — who is in the room, how questions are sourced (real questions from the floor, not questions the vendor invents), how "correct" is adjudicated when two charge nurses disagree, who owns the set afterward. Then the simulated output:
- A golden set of ≥ 60 QA items in JSONL, each with: question (phrased the way a nurse would, including sloppy phrasing and abbreviations), expected answer key points, required citation (doc ID), category, and — critically — item type: `answerable`, `gap` (should refuse, class a), `low-confidence` (should refuse, class b), `out-of-scope` (class c), `stale-trap` (the 2019/2023 contradiction), and `pii-laden` (contains a patient name/room that must not surface in logs or answers).
- Distribution requirement: ≥ 15% of items are refusal-type. An eval set where every question is answerable teaches the system to never refuse.

**Acceptance criteria**

- Schema-validated JSONL; every `answerable` item's citation exists in the manifest.
- The workshop doc addresses adjudication and ownership — the two things that kill golden sets in real deployments.
- Question phrasing is field-realistic (abbreviations, misspellings, "4W" not "the fourth-floor west medical-surgical unit").

## Milestone 5 — Eval harness, PII guardrails, accuracy report (~2h)

**Deliverables**

- Eval runner: executes the full golden set through the real pipeline (MockLLM scripted from the golden set's expected behaviors, including some scripted failures to prove the harness catches them), scoring per item: retrieval hit (did the right doc reach top-k), citation correctness, answer key-point coverage, and refusal correctness (refused when it should, didn't when it shouldn't).
- PII guardrail: input filter using Phase 6 lesson 03 patterns — patient-name/room/MRN detection on incoming questions; detected PII is redacted before logging and before the prompt; the answer path never echoes it. Audit log stores the redacted form only.
- `ACCURACY-REPORT.md`, written for Dana and Rich, produced entirely by script: overall and per-category scores; retrieval hit rate vs answer quality separated (so you can say *where* it fails); refusal precision/recall as its own headline table (Rich's metric); the failure gallery — every failed item with a one-line diagnosis; and a recommendation section that an honest engineer would write ("ready for supervised pilot on units X; not ready for Y because Z").

**Acceptance criteria**

- Harness detects planted failures: a scripted-bad MockLLM run measurably drops the score (test asserts this) — proving the eval can fail.
- PII test: a `pii-laden` golden item runs end-to-end and the raw patient name appears nowhere in logs, prompt record, or answer (grep-style assertion over all artifacts).
- Refusal recall on refusal-type items ≥ 0.9; false-refusal rate on answerable items ≤ 0.15 — and the report states both numbers plainly.
- Report numbers are script-generated, never hand-typed.

---

## Grading rubric

| Dimension | Novice | Competent | Strong hire |
|---|---|---|---|
| **Retrieval engineering** | Bag-of-words over raw files | Structured chunks, metadata, recency handling | Stale-trap resolved by design; quarantine for garbage chunks; debug tooling used and shown |
| **Grounding & refusal** | Trusts the model output | Citation rendering + basic refusal | Post-hoc grounding check catches scripted fabrications; three refusal classes, each tested, each with a useful message |
| **Golden set** | Vendor-invented easy questions | Realistic phrasing, categories | Refusal-type and trap items ≥ 15%; workshop doc handles adjudication and ownership like someone who has watched a golden set die |
| **Evals** | "It seemed accurate" | Scripted scoring, real metrics | Harness proven able to fail; retrieval vs generation failures separated; refusal metrics headlined |
| **PII & honesty** | PII in logs, report is a sales doc | Redaction works, report is accurate | End-to-end PII assertion across all artifacts; report makes a defensible not-ready call somewhere |

## Stretch goals

- Query-log mining loop: generate 200 synthetic "production" queries, cluster the refusals, and produce the "next 5 documents to add to the corpus" memo — the renewal conversation in document form.
- Confidence calibration: bucket answers by retrieval score and show measured accuracy per bucket; expose the bucket in the UI as "high/medium confidence."
- Human-in-the-loop mode (Phase 5 lesson 13): below-threshold answers route to a review queue file instead of the user, with a reviewer CLI.

## Estimated hours

| Milestone | Hours |
|---|---|
| 1 — Corpus generation | 2 |
| 2 — Ingestion + retrieval | 2.5 |
| 3 — Grounding + refusal | 2.5 |
| 4 — Golden set workshop | 2 |
| 5 — Evals + PII + report | 2 |
| **Total** | **9–11** |
