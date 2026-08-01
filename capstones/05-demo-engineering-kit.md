# Capstone 05 — Demo Engineering Kit

**A seeded dataset, a demo app, a beat-by-beat narrated script, and a failure-recovery plan — the demo treated as an engineered artifact, not a performance.** · Estimated: 6–8 hours · Extends Capstones 01–04.

---

## Overview

A demo is a system with an SLA of one: it must work once, at a specific time, in front of specific people, on hostile wifi. FDEs who treat demos as "I'll just show the app" lose deals to FDEs who treat demos as engineering: seeded data chosen scene by scene, a narrative arc with named beats, rehearsed recovery moves for every failure mode, and a version of the truth that is impressive without being a lie.

In this capstone you build the complete demo kit for the Meridian engagement's biggest moment: the **pilot-to-production decision meeting**. In the room: Dana (champion), Rich (skeptic), Maria (user), the CFO (economic buyer), and — announced that morning — the CEO is "dropping in for ten minutes." Your Capstone 01 dashboard and (if built) the 03 Q&A and 04 lab bridge are the product. This capstone is everything around them.

Everything here is buildable and testable at your desk: the seeder is code, the demo app is code, the script and recovery plan are documents you *drill against* the running system.

## Scenario

The stakes memo from Dana, two days before the meeting:

> The CFO has approved exactly one of the last four pilot-to-production requests. The three that died all died the same way: the demo broke, or the vendor couldn't answer "is this our real data?", or someone went twenty minutes over and the decision got deferred to a meeting that never happened. You have 25 minutes plus questions. He will interrupt. The CEO, if she shows, will ask one question and it will not be on your agenda.

Constraints that make this engineering rather than theater:

- The demo runs on **your laptop, fully local** (Rich's rule from Capstone 01 still stands — and it conveniently makes you immune to wifi). Hostile network is still in scope: assume the conference-room display, screen-share fallback, and any live-anything can fail.
- The data shown must be **derived from the real pilot data shapes but demo-safe**: no real-looking patient identifiers that could be mistaken for actual PHI (Phase 6 lesson 10 and drill 09). "Is this our real data?" must have a one-sentence honest answer you scripted in advance.

## Prerequisites

- **Phase 2** lessons 02 (demo-quality bar), 06 (seeded demo data), 07 (feature flags per stakeholder)
- **Phase 7** lessons 04 (demo engineering), 06 (objection handling), 09 (executive communication)
- **Phase 6** drill 09 (redact the dataset, keep it useful)
- **Capstone 01** (required); Capstones 03/04 optional but enrich the demo surface

## Milestone 1 — The seeded dataset: every scene has a star (~2h)

A demo dataset is not a sample of production. It is a *cast*. Every moment in the script needs a specific record that makes the point vividly, and nothing in the dataset may undermine you.

**Deliverables**

- `demo/seed.py` — deterministic seeder that builds the full demo database, constructing named scene-support records on top of realistic background volume: **the Tuesday spike** (a unit where census jumps and the staffing gap goes red on screen — the Maria beat), **the reconciliation match** (month totals landing within the stated tolerance of billing — the CFO beat), **the caught duplicate** (a patient with two billing accounts, resolved, with the audit trail one click away — the Rich beat), and **the delay story** (one anonymized patient journey where a discharge sat 6 hours "waiting on labs" — the narrative spine).
- Safety pass: names drawn from an obviously-fictional-but-professional generator (no real-roster collisions with common real formats — document your approach); MRNs in a reserved test range; a `SAFETY.md` stating exactly what the data is, how it was derived, and the scripted one-sentence answer to "is this our real data?" ("Real structure, real volumes, real anomalies from your files — identities synthesized, and I can show you the derivation.")
- Negative sweep: an automated check that no metric visible on any demo screen is accidentally embarrassing or absurd (no negative census, no 400% ratio, no $0 month, no unit with zero staff unless it is the planted story).

**Acceptance criteria**

- One command, deterministic, < 30 seconds to a fully seeded demo state.
- Each named scene record is asserted by a test (the Tuesday spike is actually red under your thresholds; the reconciliation delta is actually within tolerance).
- The negative sweep runs as a test and fails when you plant an absurd value.

## Milestone 2 — The demo app: flags, presets, and the panic button (~1.5h)

**Deliverables**

- Demo-mode layer on the Capstone 01 dashboard: a `?scene=` deep-link for every beat in the script (scene 1 → CFO reconciliation view, scene 2 → Maria's unit grid on the spike day, etc.) so navigation during the demo is one keystroke, never five clicks while people watch you click.
- Stakeholder feature flags (lesson 2.07): CFO view leads with dollars, Maria view leads with ratios, a `--exec` flag that hides anything half-built. Document which flags are on for this meeting and why.
- The panic button: `demo/reset.py` restores the exact opening state in < 10 seconds without visible drama, safe to run mid-meeting.
- Static fallback deck: a script that snapshots every scene into standalone HTML files (self-contained, no server) — if the app dies irrecoverably, you present from snapshots and nobody sees a stack trace.

**Acceptance criteria**

- Every scripted beat is reachable by direct URL; a test walks all scene links against the seeded DB and asserts 200 + expected key numbers present in the response.
- Reset verified mid-session: mutate state, reset, assert opening state restored.
- Snapshots regenerate from the live app in one command and render standalone (open from file://, no server running).

## Milestone 3 — The narrated script: a beat-by-beat arc (~1.5h)

**Deliverables**

- `demo/DEMO-SCRIPT.md`, structured as numbered beats totaling 20 minutes of a 25-minute slot (interruptions are certain; the buffer is designed, not hoped for). Each beat specifies: elapsed-time target, what is on screen (the scene link), the spoken line that lands the point (written out — not "talk about reconciliation" but the sentence), the persona it serves, and the transition. Required arc:
  1. **Cold open on the trusted number** — reconciliation vs billing, first 90 seconds, before any feature. Disarm the meeting-killer from Capstone 01's transcript.
  2. **The problem made visible** — the delay story, one patient journey, told in Maria's vocabulary.
  3. **The 6am decision** — Maria's screen on the spike day; the agency-call she would not have made.
  4. **Trust, proactively** — the caught duplicate and its audit trail, addressed *to Rich by name* before he asks.
  5. **The money** — CFO view: agency-spend framing, honest about what is measured vs projected.
  6. **The ask** — the production decision, stated plainly, with the one-slide summary (lesson 7.09) as the closing screen.
- Objection appendix: the 6 most likely questions (including "is this our real data?", "what happens when you leave?" — your Capstone 06 teaser — and "why not just do this in Epic/our EHR?") each with a 2–3 sentence scripted answer and, where applicable, the scene link that shows rather than tells.
- The CEO contingency: a 3-minute compressed cut (which beats survive, which die) selectable mid-meeting, written into the script as "if the CEO arrives, jump to track B."

**Acceptance criteria**

- Beats sum to ≤ 20 minutes with per-beat targets; every on-screen claim in the script matches a number the seeded data actually shows (test: extract claimed figures from the script's fenced metadata and assert against the API — the script cannot drift from the data).
- Someone else could deliver it: no beat depends on unstated context.
- Track B exists and stands alone.

## Milestone 4 — The failure-recovery plan, drilled (~1.5h)

Hope is not a recovery strategy. Write the plan, then rehearse it against real induced failures.

**Deliverables**

- `demo/RECOVERY.md` — a two-column playbook (symptom → move) covering at minimum: **wifi/display dies** (you were local; what still breaks — screen sharing, the projector — and the fallback order: HDMI → snapshots → printed one-slide); **the app crashes mid-beat** (the panic line you say while reset runs — write the actual sentence, silence is the killer); **the data looks wrong on screen** (the honesty move: never bluff a number — the scripted "let me note that and show you the audit trail for how we'd trace it" pivot, and when to take it offline); **the exec asks an off-script question** (the triage: answer-from-a-scene / honest-parking-lot / decomp-it-live — with one worked example of each); **you're 10 minutes over before beat 4** (the pre-decided cut order of beats — decided now, calm, not live, flustered).
- Drill log: run the demo end-to-end at least three times against induced failures — kill the server mid-beat-3, corrupt a displayed value, force track B — and log each drill: what failed, recovery time, what you changed in the script or tooling afterward. At least one drill must produce a real change (if all three go perfectly, your induced failures are too soft).
- Pre-flight checklist: the 10-minute T-minus routine (seed, walk all scenes, snapshots regenerated, reset tested, battery, display adapter, script printed).

**Acceptance criteria**

- Every recovery move is executable: the crash move references the tested reset; the display move references snapshots that actually open standalone.
- Drill log shows three runs with timings and at least one resulting change, cross-referenced to a diff.
- Recovery from the induced crash to back-on-script measured under 60 seconds.

---

## Grading rubric

| Dimension | Novice | Competent | Strong hire |
|---|---|---|---|
| **Seeded data** | A random sample, hoping it looks good | Deterministic, realistic, safe | Every beat has a planted star record with a test; negative sweep proves nothing on screen can ambush the presenter |
| **Demo app** | The regular app, driven live by clicking | Scene links + reset | One keystroke per beat, per-persona flags, standalone snapshot fallback — three layers of defense, all tested |
| **Script** | Feature tour in app-menu order | Timed beats, personas addressed | Opens on the trusted number, disarms the skeptic by name, honest about measured vs projected; script claims asserted against live data |
| **Recovery** | "I'll improvise" | Written playbook | Drilled against induced failures with timings and a resulting change; the off-script-exec triage shows judgment, not just preparation |
| **Honesty** | Fakes what should be real | Clear about what is seeded | The "is this real data?" answer is scripted, one sentence, and true |

## Stretch goals

- Record the demo: deliver it solo against a timer, note every stumble against the script, iterate once, and keep both recordings' drill notes.
- Build the leave-behind: a self-contained HTML page (snapshots + the one-slide + the ask) you could email Dana within an hour of the meeting.
- Hostile-hardware drill: deliver the entire demo from the static snapshots alone, no server, and note which beats lose the most — then fix the two worst snapshots.

## Estimated hours

| Milestone | Hours |
|---|---|
| 1 — Seeded dataset | 2 |
| 2 — Demo app + fallbacks | 1.5 |
| 3 — Narrated script | 1.5 |
| 4 — Recovery plan + drills | 1.5 |
| **Total** | **6–8** |
