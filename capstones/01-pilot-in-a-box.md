# Capstone 01 — Pilot-in-a-Box

**A full simulated engagement, end to end.** · Estimated: 25–30 hours · This is the spine — capstones 02–06 extend the codebase and artifacts you build here.

---

## Overview

Every other lesson in this repo teaches one muscle. This capstone makes you run the whole race: you are the FDE dropped into a 400-bed hospital network with a skeptical IT director, a champion VP who needs a win by end of quarter, and three data sources that have never agreed with each other in their lives.

You will take a discovery-call transcript (below) and turn it into: a 30-day pilot plan, working ingestion for three messy feeds, an entity-resolution layer for patients and staff, an operations dashboard the VP can open every morning, a weekly demo script, and a handoff runbook. All in Python stdlib. All self-testing.

There is no real customer, so you play both sides. That is deliberate — the discipline of writing the customer's data *badly* (realistic generators) and then fixing it is the closest thing to field experience you can get at a desk.

## Scenario: Meridian Health

Meridian Health is a fictional regional network: one 400-bed flagship hospital (Meridian General), two satellite clinics, ~2,800 staff. Their pain: **discharge delays and agency-nurse overspend**. Patients medically ready for discharge sit for hours waiting on process; meanwhile staffing decisions are made from a spreadsheet updated at 6am against a census that changed by 9am. Leadership suspects the two problems are connected but cannot see them on one screen.

Their systems:

1. **ADT feed** — the admission/discharge/transfer event stream from their EHR. You get it as a nightly pipe-delimited dump that is HL7-flavored but not HL7-compliant: event type, timestamps in two formats, patient MRN, unit, bed, attending physician ID. Roughly 1 in 40 rows is damaged (truncated, doubled delimiter, timestamp in local time with no zone).
2. **Staffing spreadsheet** — nursing operations maintains `StaffingMaster_FINAL_v3 (2).xlsx`, exported for you as CSV. Merged-cell damage, unit names that don't match ADT unit codes ("4 West" vs "4W" vs "MED-SURG 4"), staff names formatted three ways, agency nurses entered with the agency's name in the employee-ID column.
3. **Billing export** — patient-level charge summaries from a separate billing system that uses its own account number, not the MRN. Patient names are UPPERCASE LAST,FIRST; dates of birth exist here (they don't in the staffing file); ~2% of rows are duplicate accounts for the same human.

### Discovery-call transcript (excerpt)

Work from this. It is your only requirements document until you write a better one.

> **Attendees:** Dana Okafor (VP Operations, Meridian — your champion), Rich Paulsen (Director of IT), Maria Vance (Nursing Ops Manager), you (FDE).
>
> **DANA:** Look, I'll be blunt about why you're here. Our average discharge-order-to-departure time is somewhere between four and seven hours depending on who you ask, and we spent $11 million on agency nursing last year. My CFO thinks those are two separate problems. I think they're the same problem: we can't see census and staffing on the same screen, so we staff for yesterday.
>
> **YOU:** When you say "depending on who you ask" — who are the askers?
>
> **DANA:** Billing says one number because they work off discharge-complete timestamps. The units say another because they track when the order was written on a whiteboard. Nobody trusts either.
>
> **MARIA:** The whiteboard is real, by the way. 4 West still runs on a whiteboard. My staffing sheet is the closest thing we have to truth and I update it at six in the morning from the overnight report. By nine it's fiction.
>
> **RICH:** Before we go further — you are not touching the EHR directly. Not the database, not the API, nothing live. Last vendor who asked for a live interface, that project took eleven months and died in security review.
>
> **YOU:** Understood. What CAN I get without a security review?
>
> **RICH:** The nightly ADT extract already lands on a file share — it exists because the state reporting team needed it in 2016. I can give you that, the billing team's monthly export, and whatever Maria emails you. Read-only, flat files, de-identified is preferred but we have a BAA process if you need identifiers.
>
> **YOU:** Maria, when you're making the 6am staffing call, what question are you actually trying to answer?
>
> **MARIA:** How many nurses do I need on each unit for the next twelve hours, and whether I have them or have to call the agency. Agency is a four-hour lead time and costs double. If I could see, by unit, expected census against scheduled staff — even just this morning's truth instead of last night's — I'd cut agency calls I make out of fear.
>
> **DANA:** That's the pilot right there. One screen. Census versus staffing by unit, and where the discharge delays are stacking up. If you can show my CFO that screen with real Meridian data in thirty days, I can get budget for the real project.
>
> **YOU:** What does "real Meridian data" need to mean for the CFO to believe it?
>
> **DANA:** It has to match numbers he already trusts. He trusts the billing export. If your patient counts disagree with billing by more than a couple percent, the meeting's over.
>
> **RICH:** And I'll say the quiet part: I've watched three of these pilots die. They die when the vendor's numbers don't reconcile and everyone spends the meeting arguing about the data instead of the problem. Don't be that meeting.

Read that transcript again. Everything you need is in it: the metric that gets renewal signed, the data-access constraints, the political landscape, the reconciliation bar, the demo audience, and the 30-day clock.

## Prerequisites

- **Phase 1** (Engagement Lifecycle) — pilot design, the drill on writing plans from transcripts
- **Phase 2** (Rapid Prototyping) — stdlib API + one-file dashboard patterns
- **Phase 3** (Data Integration & Entity Resolution) — you will use almost every lesson
- **Phase 7** (Customer-Facing Craft) — demo engineering, running the weekly
- Helpful: Phase 10 drills 01, 02, 03, 06, 12

## Repository layout you will produce

```
capstone-01/
├── PLAN.md                 # 30-day pilot plan
├── generators/             # synthetic messy-data generators (one per source)
├── ingest/                 # parsers + quarantine
├── resolve/                # entity resolution for patients and staff
├── dashboard/              # stdlib http.server app + one HTML file
├── demo/DEMO-SCRIPT.md     # weekly demo script
├── handoff/RUNBOOK.md      # handoff runbook
└── tests/                  # every milestone asserts its own correctness
```

---

## Milestone 1 — Discovery to 30-day pilot plan (~3h)

Turn the transcript into `PLAN.md`. This is a writing deliverable, and it is graded as hard as the code.

**Deliverables**

- One-page problem statement: the metric (agency spend avoided / discharge-delay visibility), the champion, the blocker, and the success condition Dana stated ("one screen the CFO believes in 30 days").
- Week-by-week plan (weeks 1–4) with a named demo at the end of each week. Week 1's demo must be achievable with only the ADT file.
- Explicit scope fence: three things you are *not* doing in the pilot (e.g., live EHR integration, predictive staffing, historical backfill beyond 90 days) and one sentence each on why.
- Data-access request list: exactly which files, from whom, at what cadence, with the fallback if one is late (per lesson 1.05, assume one will be).
- Risk register: at least 5 risks with a mitigation each. "Numbers don't reconcile with billing" must be one of them.

**Acceptance criteria**

- The plan fits on ~2 pages. A VP could read it in five minutes.
- Every week ends in something demoable, not "infrastructure complete."
- The reconciliation bar (within ~2% of billing counts) appears as an explicit checkpoint, not an afterthought.
- Rich's constraints (flat files, read-only, no live EHR) are honored everywhere.

## Milestone 2 — Generators: write the customer's data, badly (~5h)

Before you can ingest Meridian's data, you must create it. Build three generators, seeded and deterministic, that produce realistically damaged files.

**Deliverables**

- `generators/gen_adt.py` — 90 days of ADT events for ~3,000 unique patients: A01 admit, A02 transfer, A03 discharge, A08 update. Pipe-delimited. Inject damage at known rates: ~2.5% malformed rows (truncation, doubled delimiters), two timestamp formats, occasional out-of-order events, a handful of discharges with no matching admit.
- `generators/gen_staffing.py` — daily staffing CSV per unit: scheduled nurses, shift, unit name drawn from a *different* vocabulary than ADT unit codes, names in mixed formats ("Vance, Maria RN", "MARIA VANCE", "M. Vance"), agency staff with junk IDs.
- `generators/gen_billing.py` — monthly patient charge summaries keyed by account number, with DOB, UPPERCASE names, ~2% duplicate accounts per patient, and a known ground-truth mapping (account → MRN) written to a separate answer-key file that your pipeline is forbidden to read.
- A shared `truth.py` module holding the underlying clean world (patients, staff, events) so all three exports are *views of the same reality* — that is what makes reconciliation meaningful later.

**Acceptance criteria**

- Same seed → byte-identical output files. Run twice, `diff` clean.
- Damage rates are parameterized and asserted by a self-test (e.g., generator's own test counts malformed rows and checks the rate is within tolerance).
- The answer key is written but clearly fenced (`answer_key/` directory with a README saying the pipeline may not import it; only tests may).
- No external libraries. `csv`, `random`, `datetime`, `json` carry you.

## Milestone 3 — Ingestion with quarantine (~5h)

Parse all three sources into a canonical SQLite database. Bad rows go to quarantine, never to `/dev/null`.

**Deliverables**

- One parser per source in `ingest/`, each producing canonical records (define your canonical schema first — lesson 3.04) into SQLite.
- Quarantine table: every rejected row stored verbatim with source, line number, reason code, and timestamp. Reason codes are an enum, not free text.
- A single `ingest/run.py` that ingests all three sources idempotently — running it twice does not duplicate data (watermark or content-hash approach, lesson 3.08).
- Ingestion report printed at the end: rows read / loaded / quarantined per source, top 3 quarantine reasons.

**Acceptance criteria**

- Quarantine rate matches the generators' injected damage rate within 0.5 percentage points — proving you reject exactly what is broken, nothing more.
- Re-running ingestion is a no-op (assert row counts unchanged).
- A malformed row you invent by hand (add a test) lands in quarantine with the correct reason code.
- All timestamps normalized to one format in the canonical store; the two ADT formats both parse.

## Milestone 4 — Entity resolution: patients and staff (~6h)

The billing export doesn't know MRNs. The staffing sheet doesn't know employee IDs half the time. Resolve both.

**Deliverables**

- Patient resolution: link billing accounts to ADT patients using name + DOB (blocking on DOB or name initial, then scored fuzzy match — lessons 3.05/3.06). Collapse duplicate billing accounts to one patient.
- Staff resolution: normalize the three name formats and the unit-name vocabularies into canonical staff and unit entities. Ship an explicit unit-mapping table ("4 West" / "4W" / "MED-SURG 4" → `4W`) with a documented process for unmapped values (they quarantine, they don't guess).
- Match-decision log: every link recorded with score, rule fired, and match tier (exact / high-confidence fuzzy / needs-review).
- Precision/recall measurement: tests compare your patient links against the fenced answer key and print both numbers.

**Acceptance criteria**

- Patient linkage: precision ≥ 0.98, recall ≥ 0.95 against the answer key. (Precision matters more — Rich's warning — a wrong merge in a hospital is worse than a miss.)
- Zero unit-name values silently dropped: every distinct raw unit string is either mapped or in the needs-review list.
- The needs-review queue is small enough to be human-workable (< 2% of records) and is exported as a CSV a customer could actually triage.

## Milestone 5 — The one screen: ops dashboard (~5h)

Build the screen Dana described: census vs staffing by unit, plus discharge-delay visibility.

**Deliverables**

- `dashboard/server.py` — stdlib `http.server` serving JSON endpoints off SQLite: current census by unit, scheduled staff by unit/shift, census-to-staff ratio, and discharge-delay board (patients with a discharge event pending > N hours, reconstructed from ADT event sequences).
- One HTML file, no build step (lesson 2.03): the unit grid with ratios, color thresholds (define them and document why), and the delay board.
- Reconciliation panel: your patient count for the month vs the billing export's count, with the delta percentage displayed *on the dashboard*. You show the CFO the reconciliation before he asks. That is the whole trick.
- Usage telemetry (lesson 2.11): log every dashboard request with timestamp and endpoint, and a tiny report script that summarizes "views per day" — the number that proves adoption at week 4.

**Acceptance criteria**

- `python dashboard/server.py` then open a browser: works with zero dependencies and zero configuration.
- Reconciliation delta vs billing is ≤ 2% and displayed with the calculation explained on hover or a footnote.
- Delay board correctly handles the generator's out-of-order and orphaned events (test with known cases).
- Endpoints respond in < 500ms on the full 90-day dataset (assert in a test with `time.monotonic`).

## Milestone 6 — Weekly demo script and handoff runbook (~4h)

The pilot ends with two documents that most engineers never write and every FDE writes constantly.

**Deliverables**

- `demo/DEMO-SCRIPT.md` — the week-4 demo to Dana, Rich, Maria, and the CFO. Beat-by-beat: opening (the number the CFO trusts, reconciled, first), the Maria moment (6am decision on the screen), the Rich moment (quarantine + audit trail shown proactively), the ask (what you need for production). Include the exact seeded data state the demo runs against and 3 pre-planned answers to likely objections.
- `handoff/RUNBOOK.md` — how Meridian's own IT runs this without you: daily operation (run ingestion, check quarantine), the 5 most likely failures with symptoms and fixes (file didn't arrive, quarantine spike, reconciliation drift, dashboard down, disk growth), and escalation criteria.
- A `make_demo.py` script that resets the database to the exact demo state deterministically.

**Acceptance criteria**

- A stranger could deliver your demo from the script alone — it names what is on screen at each beat.
- The runbook was tested: intentionally break each of the 5 failure modes and confirm the runbook's diagnosis steps actually surface the problem.
- Demo reset is one command and idempotent.

---

## Grading rubric

| Dimension | Novice | Competent | Strong hire |
|---|---|---|---|
| **Pilot plan** | A feature list with dates | Weekly demos, scope fence, honest risks | Reads like it was written for Dana specifically; the reconciliation checkpoint and Rich's constraints are load-bearing, not decorative |
| **Data handling** | Parses the happy path; bad rows crash or vanish | Quarantine with reasons; idempotent ingestion | Quarantine rates asserted against generator ground truth; every anomaly is either handled or visibly queued |
| **Entity resolution** | Exact-match joins, silent misses | Blocking + scoring, measured precision/recall | Hits the precision bar, ships a triage-able review queue, and can explain every survivorship choice |
| **Dashboard** | Data on a page | The one screen Dana asked for, fast, zero-dep | Reconciliation displayed proactively; telemetry proves someone would actually use it |
| **Customer craft** | Docs written for other engineers | Demo script and runbook a stranger could execute | Demo is engineered around the three personas' fears; runbook was broken-and-verified |
| **Engineering hygiene** | Runs on the author's machine, sometimes | Self-testing, deterministic, stdlib-only | Tests encode the *contract* (rates, precision, latency, idempotency), not just "it ran" |

## Stretch goals

- Add an A08 (patient update) merge path: updates change patient attributes and your resolution layer handles the churn without breaking existing links.
- Simulate week-3 disaster: the ADT file arrives 6 hours late and truncated. Write the incident timeline and the email to Dana.
- Build a second dashboard view feature-flagged per stakeholder (lesson 2.07): CFO sees dollars, Maria sees ratios.
- Backfill: ingest 90 days in random order and prove the final state is identical to in-order ingestion.

## Estimated hours

| Milestone | Hours |
|---|---|
| 1 — Pilot plan | 3 |
| 2 — Generators | 5 |
| 3 — Ingestion + quarantine | 5 |
| 4 — Entity resolution | 6 |
| 5 — Dashboard | 5 |
| 6 — Demo script + runbook | 4 |
| **Total** | **25–30** (with debugging reality tax) |

When you finish, keep everything. Capstone 02 hardens your resolution layer, 03 adds grounded Q&A over Meridian's policies, 04 bolts on their lab system, 05 professionalizes your demo, and 06 turns your runbook into a full handoff pack.
