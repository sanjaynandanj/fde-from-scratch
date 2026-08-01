# Capstone 06 — Production Handoff Pack

**Monitoring, runbook, training, admin guide, and the make-yourself-unnecessary checklist — ending in a simulated handoff review.** · Estimated: 6–8 hours · The closing move of the Meridian engagement (Capstones 01–05).

---

## Overview

The pilot converted (Capstone 05 worked). Now comes the part that decides whether Meridian renews next year or quietly resents you: the handoff. An FDE's finished state is *absence* — the system runs, Meridian's own people operate it, extend it, and trust it, and your phone does not ring. Most engineers never practice this. It is a skill with concrete deliverables, and every one of them can be built and tested at your desk.

In this capstone you produce the complete handoff pack for the Meridian system (dashboard + ingestion + entity resolution + lab bridge, whichever capstones you built — Capstone 01 alone is sufficient): monitoring and alerting minimums implemented in code, an operational runbook you have verified by breaking things, a training deck outline per audience, an admin guide, and the make-yourself-unnecessary checklist. It ends with a **simulated handoff review** — a structured self-audit played from the customer's chair, graded like the real meeting it imitates.

The clock that makes this urgent: Rich has assigned two Meridian IT staff to own the system — Priya Nair (5 years, capable, has never seen your codebase) and Tom Osei (18 months, junior). Ed Brennan, the only person who understands LabTrak, retires in 14 months. If Priya and Tom cannot run this without you by day 30 of the handoff, the production contract has a problem.

## Prerequisites

- **Phase 1** lesson 08 (handoff: runbooks, training, making yourself unnecessary)
- **Phase 4** lessons 08 (observability minimum), 10 (release management)
- **Phase 6** lessons 05 (least privilege), 06 (audit logging), 09 (incident response)
- **Capstone 01** (required); 03/04 monitoring hooks (`/health`, alert records) if built

## Milestone 1 — Monitoring and alerting minimums (~2h)

Not a Grafana cosplay — the stdlib minimum that actually catches the failures this system actually has. Define the minimums, implement them, and prove each one fires.

**Deliverables**

- `MONITORING.md` — the philosophy page first: what "healthy" means for this system stated as invariants (nightly file arrived by deadline; quarantine rate within band; reconciliation delta within tolerance; dashboard responding; disk within budget; sync lag bounded), and for each invariant: the check, the threshold *and why that number*, the alert severity, and who acts on it (Priya/Tom/escalate-to-vendor).
- `monitor/check.py` — a single scheduled-style checker (runnable via cron/Task Scheduler; document both) that evaluates every invariant against the live system and writes structured results to an `alerts` log/table. Alert delivery is a pluggable notifier with two stdlib implementations: append-to-file and SMTP-shaped stub (a class with the real interface writing to an outbox directory — no external service, per repo rules).
- Alert hygiene by design: deduplication (a condition alerting since Tuesday is one open alert with an updated count, not 400 emails), state transitions (OPEN → RESOLVED with timestamps), and a weekly digest generator (open alerts, flapping checks, trend of quarantine rate) — the artifact Priya reads Monday morning.
- Fault-injection tests: for **every** invariant, a test that induces the failure (delete the nightly file, spike quarantine, break reconciliation, stop the server, fill the disk via a mocked `disk_usage`) and asserts the right alert fires at the right severity — and that recovery transitions it to RESOLVED.

**Acceptance criteria**

- Every invariant in `MONITORING.md` has a corresponding implemented check and a fault-injection test; a table in the doc cross-references them (doc-to-code drift is the disease; the table is the vaccine).
- Dedup test: the same failure across 5 consecutive runs yields one OPEN alert, count=5.
- Thresholds are justified in writing from pilot data (e.g., "quarantine band 1.5–3.5% because 90-day pilot mean was 2.4%, σ=0.4"), not invented.

## Milestone 2 — The operational runbook, broken-and-verified (~1.5h)

Extend the Capstone 01 runbook from "what I'd tell someone" to "what Priya executes at 6:45am without calling anyone."

**Deliverables**

- `RUNBOOK.md` covering: routine ops (daily 10-minute check, weekly digest review, monthly reconciliation sign-off); an incident section per alert type with symptom → diagnosis commands (exact commands, expected output shown) → fix → verification → what-to-record; the restore path (backup script + restore script + how you know restore worked); and escalation criteria with the bright line between "Priya fixes" and "call the vendor," including what to capture *before* calling so the call is short.
- Every diagnostic and fix procedure is a runnable script or an exact command — no step says "investigate the logs" without saying which log, which pattern, and what good looks like.
- Verification log: for each incident type, you (playing Priya, using *only* the runbook — no memory allowed) induced the failure and walked the written steps. Record where the runbook was wrong or assumed unstated knowledge, and the fix you made to the doc. As with Capstone 05's drills: a verification pass with zero corrections means the test was too soft.

**Acceptance criteria**

- Backup → destroy → restore round-trip test passes and is referenced from the runbook.
- Verification log shows every incident type walked, with at least two documented runbook corrections arising from the walks.
- A cold reader could execute the daily check in under 10 minutes (time yourself; record it).

## Milestone 3 — Training deck outline and admin guide (~1.5h)

**Deliverables**

- `TRAINING.md` — outlines for three audiences, because one deck for everyone trains no one: **operators** (Priya/Tom — 2 sessions: architecture-as-data-flow, then hands-on incident drills using your fault-injection tools as the lab exercises); **users** (Maria's team — one 30-minute session: reading the dashboard, what the numbers mean, what to report and to whom); **stakeholders** (Dana/CFO — 15 minutes: what is measured, what the monthly report means, what to ask for next). Each outline: learning objectives phrased as capabilities ("can requeue a quarantined batch"), slide-by-slide beats, and the hands-on exercise per session — training without a lab is a lecture, and lectures don't transfer systems.
- Session-zero artifact: the operator training's first lab is fully written out (the "missing nightly file" drill: induce it with the milestone-1 tooling, diagnose with the runbook, fix, verify, close the alert).
- `ADMIN-GUIDE.md` — the reference doc, distinct from the runbook (runbook = what to do when; admin guide = how it is put together): configuration reference (every knob, default, and consequence of changing it), user/access model (who can see the dashboard, how audit logging works, least-privilege notes per Phase 6), data retention and the quarantine/history growth story, release procedure (how Meridian applies your v1.1 without breaking demos — versioning per lesson 4.10), and the dependency map (what breaks if the file share moves, the answer to "can we rename that folder?").

**Acceptance criteria**

- Every operator learning objective maps to a runbook section or admin-guide section (traceability table) — training teaches the docs, so the docs survive the training.
- The written lab was executed end-to-end against the real system once, with timing.
- Admin guide's configuration reference is generated or verified against the actual config the code reads (a test enumerates config keys and asserts each appears in the doc).

## Milestone 4 — The make-yourself-unnecessary checklist (~1h)

The discipline: enumerate everything that currently requires *you*, then eliminate, delegate, or document each one.

**Deliverables**

- `UNNECESSARY.md` — built by walking your own engagement honestly: every task you performed in the last simulated month, classified: **eliminated** (automated away — link the commit), **delegated** (Priya or Tom now owns it — link the runbook/training section that transfers it, and the drill where they "did it without you"), **documented** (rare enough to leave as a written procedure), or **retained** (still vendor work — and each retained item priced honestly: is this a support contract line or a gap you should close before handoff?).
- The knowledge-concentration audit: the "what if I disappear tomorrow" walk — every piece of tribal knowledge in your head, written down or explicitly logged as a retained risk. Include the Ed Brennan mirror: you flagged Meridian's bus-factor-of-one on LabTrak in Capstone 04; apply the same standard to yourself and say so in the doc.
- Exit criteria: the measurable definition of done for the handoff — e.g., "operators have closed 5 real or induced incidents unassisted; zero vendor contacts for routine ops in 2 consecutive weeks; monthly reconciliation signed by Meridian, not by us" — the criteria Dana would sign.

**Acceptance criteria**

- No task is unclassified; retained items have a stated reason and a cost/risk note.
- Exit criteria are observable and countable, not "customer feels confident."
- At least three items moved from "requires me" to eliminated/delegated *during* this capstone, with evidence links.

## Milestone 5 — The simulated handoff review (~1.5h)

The closing meeting, run as a structured self-audit. You play both sides — and the customer side plays to win.

**Deliverables**

- `HANDOFF-REVIEW.md` — the transcript-style record of the review meeting: attendees (Rich chairing, Priya, Tom, Dana for the last ten minutes), agenda (walkthrough of exit criteria → live incident drill → open-items negotiation → sign-off decision).
- The live drill, executed for real: pick one fault-injection scenario *at random* (script the random pick; no choosing your best one), induce it, and resolve it using only the runbook while "narrating as Priya." Record: time to detect (did monitoring fire?), time to diagnose, time to resolve, and every point where the docs fell short.
- The hard-question gauntlet — written answers, in-character, honest: Rich's five ("What happens the first time this pages at 2am and you're gone?", "Which parts of this would you rebuild before I put my name on it?", "What's the single most likely failure in the next 90 days?", "What did you document only because I made you?", "If we call you in 6 months, what will it be about?"). Weasel answers fail the capstone; the strong-hire answer to "what would you rebuild" names something real.
- The sign-off page: open items with owners and dates, retained-vendor-work list (from milestone 4), the support boundary, and the signature block — plus your one-paragraph engagement retrospective: what you would do differently at Meridian from day one, knowing what you know now.

**Acceptance criteria**

- The drill was actually executed (timings and alert IDs recorded, cross-referenced to the alerts log) — not narrated fiction.
- Every doc gap the drill exposed became either a doc fix (linked) or an open item with an owner (listed). Zero gaps found means re-run with a different random scenario.
- The hard-question answers reference real artifacts (specific runbook sections, specific retained items, specific commits) rather than generalities.

---

## Grading rubric

| Dimension | Novice | Competent | Strong hire |
|---|---|---|---|
| **Monitoring** | Logs exist; someone could look at them | Checks implemented, alerts fire, tested | Invariants argued from pilot data; every check fault-injected; dedup and digest show respect for the on-call human |
| **Runbook** | Written from memory, never executed | Exact commands, verified once | Broken-and-verified per incident type with documented corrections; a cold reader survives 6:45am alone |
| **Training & admin** | One deck, all audiences | Per-audience outlines + reference guide | Objectives are capabilities with labs; docs and training cross-traced; config reference verified against code |
| **Unnecessary-ness** | "They can email me" | Tasks classified, exit criteria defined | Measurable exit criteria a customer would sign; own bus-factor named with the same rigor applied to Ed; visible movement during the capstone |
| **Handoff review** | A summary of features delivered | Structured review, drill executed | Random-scenario drill with real timings; hard questions answered against real artifacts; the "what I'd rebuild" answer proves self-awareness |

## Stretch goals

- The 90-day letter: write the email you send Meridian at handoff+90 — what to check, what will have drifted, what the renewal conversation should be about — and the monitoring evidence Priya would attach to it.
- Chaos week: script a 7-day simulation that fires 2 random faults on random days; run the whole week operating only via runbook and digest, and report MTTR trend day 1 vs day 7.
- The successor test: hand the entire pack to another person (or run it cold after a two-week gap), have them execute the daily check and one drill with zero verbal context, and fold every stumble back into the docs.

## Estimated hours

| Milestone | Hours |
|---|---|
| 1 — Monitoring + alerting | 2 |
| 2 — Runbook, broken-and-verified | 1.5 |
| 3 — Training + admin guide | 1.5 |
| 4 — Unnecessary checklist | 1 |
| 5 — Simulated handoff review | 1.5 |
| **Total** | **6–8** |

When the sign-off page is signed and your phone stays quiet, the engagement is finished — which is the only definition of finished that counts in this job.
