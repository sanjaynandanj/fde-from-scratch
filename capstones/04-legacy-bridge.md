# Capstone 04 — Legacy Bridge

**A 1990s lab system's nightly fixed-width SFTP drop becomes a clean, modern JSON API — with incremental sync, quarantine, and reconciliation.** · Estimated: 8–10 hours · Extends Capstone 01's Meridian engagement.

---

## Overview

The dashboard pilot worked (Capstone 01). Now Dana wants lab results on it — "half our discharge delays are 'waiting on labs', prove it." The lab system is **LabTrak 4.2**, installed in 1996, vendor acquired twice since, effectively unsupported. It cannot be replaced during your engagement and it cannot be queried live. What it *can* do — because someone configured it during the Clinton administration — is export a fixed-width file every night and push it over SFTP.

This is the most common integration in the enterprise field: not a REST API, not a webhook — a nightly file from a system older than you, with an encoding nobody remembers choosing and a layout documented in a Word file last saved in 2004. Your job is to build the bridge: a robust ingestion pipeline and a clean JSON API on top, so every downstream consumer (your dashboard, future Meridian systems) sees a modern interface and never has to know LabTrak exists.

There is no real SFTP server and no real LabTrak. You simulate both: a local drop directory stands in for the SFTP landing zone (the protocol is not the lesson; the file and its failure modes are), and a generator plays LabTrak — badly, on purpose.

## Scenario

From your working session with the lab systems manager, Ed Brennan (23 years at Meridian, the only person who understands LabTrak, retiring in 14 months — remember that for Capstone 06):

> **ED:** The export runs at 2:10am. Usually. If the batch queue is backed up it can be 5am, and twice a year it just doesn't run and nobody notices till a nurse calls. The file's supposed to be one row per result. Layout's in a Word doc I'll email you — it's mostly right. Couple things it won't tell you: corrected results come through as a *new* row with the same accession number and a `C` in column 214, and you'd better take the corrected one. And the units field — potassium's been reported in two different units since the 2009 analyzer swap, depends which machine ran it.
>
> **RICH:** Constraint from me: you read the file, you never write to that share, and if your pipeline dies it dies quietly on our side — no retry storms against that SFTP box, it's fragile.

Everything Ed said is a requirement. Late files, missing files, the correction convention, the dual-unit trap, and the two-decade layout doc that is "mostly right."

## Prerequisites

- **Phase 3**, especially lessons 08 (incremental sync, watermarks, idempotent upserts), 09 (connectors, SFTP-with-a-nightly-CSV), 10 (quarantine), 11 (reconciliation), 12 (retries)
- **Phase 10** drills 05 (the SFTP feed that sometimes doesn't arrive) and 06 (fixed-width mainframe export)
- **Capstone 01** — patient MRNs in the lab feed resolve against your Meridian patient store

## Milestone 1 — Play LabTrak: the generator and the layout spec (~2h)

**Deliverables**

- `LAYOUT.md` — the record layout you "received from Ed": ~20 fixed-width fields (accession number, MRN, test code, result value, units, reference range, collected/resulted timestamps, ordering physician ID, correction flag at a documented column, status). Write it like the 2004 Word doc it imitates — then include your own annotated version marking the two places where the doc is *wrong* relative to what the generator actually emits (a field one column off; an undocumented status code). Discovering doc-vs-reality drift is the exercise; the generator plants it, your parser must survive it.
- `generators/gen_labtrak.py` — emits one nightly file per simulated day into `dropzone/incoming/`, deterministic under seed, in **cp1252 encoding** (not UTF-8 — there is a `µ` in the units field waiting for the naive reader). Damage profile: ~1.5% short/garbled lines, correction rows per Ed's convention, the potassium dual-unit split by analyzer ID, occasional duplicate rows within one file, and per-day event injection: a late file, a missing file, an empty file, and one file that is a partial re-send of the previous day.
- Fenced answer key: the true current result set per day.

**Acceptance criteria**

- Byte-identical output under a fixed seed; every pathology is parameterized and self-asserted.
- The layout drift (doc says X, file does Y) is real: parsing strictly by `LAYOUT.md`'s original section demonstrably mis-reads a field.

## Milestone 2 — The watcher and the fixed-width parser (~2h)

**Deliverables**

- `bridge/watch.py` — polls the drop zone on an interval, detects new files by name + size-stable check (file may still be uploading — simulate a slow write and handle it), moves each into `processing/` then `archive/` or `failed/`. If the expected nightly file has not arrived by a configurable deadline, emits a MISSING-FILE alert record (a log line and a row in an alerts table — Capstone 06 will consume this). Per Rich: no aggressive retries; poll intervals are gentle and configured.
- Fixed-width parser: column-slicing driven by a layout *config* (not hardcoded offsets), explicit `cp1252` decode, strict field validation (numerics parse, timestamps parse, status codes in the known set), and per-row outcomes: clean, quarantined (with reason code), or flagged (parses but suspicious — e.g., result value outside physiological range).
- The layout-drift fix, documented: your annotated layout config, plus a note in the README on how you detected the drift (the story is part of the deliverable — it is the story you tell in the interview).

**Acceptance criteria**

- Encoding test: the `µ` survives round-trip into SQLite and out of the API as proper UTF-8 `µg/L`.
- Quarantine rate matches the generator's injected garble rate within 0.5 points; every quarantined row retains the raw line verbatim.
- Missing-file day produces the alert record; late-file day processes normally on arrival; the still-uploading file is not read early (test with a deliberately slow writer).

## Milestone 3 — Incremental sync, corrections, idempotency (~2h)

**Deliverables**

- Canonical `lab_results` store in SQLite keyed by accession number, with **upsert semantics**: a correction row (`C` flag, same accession) supersedes the original; the superseded version is retained in a history table with supersession timestamp — labs are exactly the domain where "what did we believe on Tuesday" is a compliance question.
- Watermark/ledger of processed files (name, hash, row counts, processing timestamp). Re-processing an already-seen file (the partial re-send day) is detected by hash/overlap and does not duplicate or regress data.
- Unit normalization: the potassium dual-unit problem handled by an explicit conversion table keyed on analyzer ID, with the original value + unit preserved alongside the normalized one. Never destroy the source value.
- In-file duplicate rows collapsed deterministically, counted, and reported.

**Acceptance criteria**

- Idempotency test: process the full simulated month twice; final DB state identical (assert row counts and a content checksum).
- Correction test: original visible in history, corrected value is what the API serves, both linked by accession.
- Out-of-order test: process day N+1 before day N; final state still converges to the answer key.
- Every potassium result carries both original and normalized values; a planted cross-analyzer pair normalizes to equal values.

## Milestone 4 — The modern JSON API (~1.5h)

**Deliverables**

- Stdlib `http.server` JSON API: `GET /results?mrn=&since=&test_code=` (paginated), `GET /results/{accession}` (current + history), `GET /patients/{mrn}/latest` (latest result per test code — the endpoint your Capstone 01 dashboard actually wants), and `GET /health` reporting last-file-processed time, quarantine counts, and sync lag (Capstone 06 will monitor this).
- Clean contract: camelCase-free, ISO-8601 timestamps with zone, normalized units, corrected-flag surfaced honestly (`"corrected": true, "supersededAt": ...` — consumers must be able to know). A one-page `API.md` a Meridian developer could integrate from without ever seeing a fixed-width file.
- MRN join: results for patients unknown to the Capstone 01 patient store are served but flagged `"patientResolved": false` — never silently dropped, never silently guessed.

**Acceptance criteria**

- `since=` incremental polling by a consumer returns exactly the new/changed results across a multi-day simulation (test drives a fake consumer through 5 days and reconciles against the answer key).
- `/health` degrades correctly on the missing-file day (status reflects staleness).
- Full API test suite runs against a live server instance started and stopped by the test itself.

## Milestone 5 — Reconciliation reports (~1.5h)

Rich's warning from Capstone 01 applies double here: the meeting dies when numbers don't reconcile.

**Deliverables**

- Nightly reconciliation report (script + markdown output per day): rows in file vs rows loaded vs quarantined vs duplicates collapsed vs corrections applied — the arithmetic must balance to zero, and the report says so explicitly ("312 in = 301 loaded + 5 quarantined + 4 dup + 2 corrections superseding").
- Cross-system count check: results-per-patient-per-day from the bridge vs an independent tally computed straight from the raw archived files, with any delta itemized to the row level.
- Month-end summary for Dana: totals, quarantine trend, missing/late file incidents with timestamps, and mean sync lag — one page, chartless, readable by a VP.

**Acceptance criteria**

- The balance equation is asserted for every simulated day, including the pathological ones.
- A deliberately-introduced bug (comment out the dup-collapse step in a test) makes reconciliation *fail loudly* — proving the report can catch a real defect, which is the entire point of reconciliation.
- Month-end summary is script-generated.

---

## Grading rubric

| Dimension | Novice | Competent | Strong hire |
|---|---|---|---|
| **Legacy realism** | Parses a clean fixed-width file | Encoding, garble, corrections handled | Layout-drift discovered and documented; Ed's every remark traceable to a handled case |
| **File handling** | Assumes the file arrives | Late/missing/partial handled | Size-stable read, gentle polling per Rich, alertable missing-file deadline, archived originals |
| **Sync correctness** | Reload everything nightly | Watermarks + upserts | Provably idempotent, order-independent, correction history preserved for compliance |
| **API design** | Fixed-width columns with JSON syntax | Clean contract, pagination, `since=` | The consumer never smells LabTrak; honesty flags (`corrected`, `patientResolved`) surfaced; `/health` built for the ops team that comes after you |
| **Reconciliation** | Row counts logged somewhere | Daily balanced report | Balance asserted to zero daily; harness proven able to catch a planted defect; VP-readable month-end |

## Stretch goals

- Backfill mode: Meridian finds 3 years of archived nightly files; ingest 1,000 files with a progress ledger, resumable after a mid-backfill kill (`kill -9` test).
- Layout version 2: LabTrak gets "patched" and two fields widen mid-month; support dual layouts selected by file date, zero downtime.
- Push notifications without infrastructure: an `outbox` table + a consumer-poll pattern, and a short doc on why you did not build webhooks for a pilot.

## Estimated hours

| Milestone | Hours |
|---|---|
| 1 — LabTrak generator + layout | 2 |
| 2 — Watcher + parser | 2 |
| 3 — Incremental sync | 2 |
| 4 — JSON API | 1.5 |
| 5 — Reconciliation | 1.5 |
| **Total** | **8–10** |
