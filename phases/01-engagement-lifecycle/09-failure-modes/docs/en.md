# Failure Modes: Zombie Pilots, Champion Churn, Scope Death Spiral

**Phase 1 · Lesson 09 · ~1h**

## PROBLEM

An engagement manager reviews her portfolio at end of quarter. Twelve engagements. Three are humming. Nine are in some state of stall. She digs into the nine. One has been "wrapping up the pilot" for four months. Another's champion left the company six weeks ago and nobody caught it. A third had a clean scope in month one but is now committed to seven adjacent features nobody planned. A fourth ships every Friday but the customer's users haven't logged in for three weeks. The stalls don't look like failures — nobody's angry, nobody's escalating — they look like drift. That's what makes them dangerous. Engagements rarely die in a single meeting. They die in patterns that were visible weeks or months earlier if anyone was watching for them.

Recognizing failure modes early is a survival skill, not a diagnostic one. By the time an engagement obviously fails, you missed the window to save it.

## INTUITION

Most engagement failures cluster into a small number of recognizable patterns. Each has an early signature, a mid-stage manifestation, and a terminal outcome. Learning the signatures is the entire game — because the fixes are cheap when caught early and impossible when caught late.

**Zombie pilot.** The pilot never ends. Week 8, 10, 12, 16 — still "wrapping up." Symptom: no signed pilot exit memo, no committed production budget, users still calling it "the pilot." Cause: no exit criteria defined at pilot start. Terminal outcome: pilot funding runs out; nothing productionizes; renewal doesn't happen because there's no case to make. **Fix:** force a written exit memo with a date. If the customer won't sign it, you have a much bigger problem you now know about.

**Champion churn.** Your champion changes jobs, moves BUs, or gets a new boss. Symptom: they stop responding to Slacks, cancel weekly demos, invite you to fewer meetings. Cause: single-thread relationship with one person. Terminal outcome: engagement quietly loses air; no one internally advocates for renewal. **Fix:** pre-build a second champion in the production phase; monthly touchpoint with the exec sponsor even when it feels unnecessary.

**Scope death spiral.** Every week, requests accumulate. You say yes to keep the customer happy. The backlog outgrows the team. Deadlines slip. The customer starts to feel like *you* are the reason things are slow. Symptom: no written out-of-scope list; every meeting produces new requirements; no one says "no." Cause: FDE afraid to disappoint. Terminal outcome: burnout, missed dates, angry exec. **Fix:** menu-based scope negotiation ("yes and we drop X"); written out-of-scope log; monthly review of what got cut.

**Silent non-adoption.** You ship features weekly. The dashboard says usage is trending down. Nobody complains — nobody's *using* it enough to complain. Symptom: activity metrics quiet or declining; feature requests dry up; champion's demos start feeling forced. Cause: pilot solves a problem the users don't actually have, or the workflow isn't in their daily habit. Terminal outcome: renewal conversation reveals "we didn't really use it." **Fix:** instrument from day one; walk the floor; sit with a user and watch them work.

**Political capture.** The engagement gets absorbed by a big internal initiative — a "transformation program," a consulting engagement, an ERP replacement. Symptom: new stakeholders appear in weekly meetings without context; slide templates change; your work gets rebranded. Cause: your champion lost internal turf or is trying to survive by aligning with a bigger project. Terminal outcome: pilot becomes one bullet on someone else's slide; renewal is out of your control. **Fix:** hard maintain your own metric readout; keep the exec relationship warm; escalate quickly to your own leadership.

**Security late arrival.** Security team wasn't looped in early. They show up in month three with a 300-row questionnaire and an aversion to your architecture. Symptom: new required review, new required control, new required tool. Cause: skipped security in the access battle plan. Terminal outcome: 4–8 week delay, sometimes fatal. **Fix:** engage security in week 1 even if they say they'll get to it later.

## BUILD IT — the weekly failure-mode checklist

Every Monday, before the customer sync, run this checklist for each active engagement. Any yes is a signal to act.

```
FAILURE-MODE CHECKLIST — <engagement> — <week n>

Zombie pilot risk:
  [ ] Pilot is past its committed end date, no signed exit memo
  [ ] Meetings still discuss pilot scope changes
  [ ] No named production owner

Champion churn risk:
  [ ] Champion missed 2+ demos or syncs in last 4 weeks
  [ ] Champion's calendar shows new manager / new role indicators
  [ ] No second champion identified

Scope death spiral risk:
  [ ] Out-of-scope log has no entries in last month (you're saying yes to everything)
  [ ] Weekly backlog additions > completed items for 3+ weeks
  [ ] Team saying "we'll try to fit it in" more than "we'll swap X for Y"

Silent non-adoption risk:
  [ ] Weekly active users trending down or flat
  [ ] No user-initiated feature requests in last month
  [ ] Champion demos feel scripted, not usage-driven

Political capture risk:
  [ ] New non-technical stakeholders in weekly meeting
  [ ] Your work being rebranded under a program name
  [ ] Champion's language shifts to "the initiative"

Security late arrival risk:
  [ ] Security has not signed off on current phase
  [ ] Any new integration touched in last month without a review

Any yes -> add to this week's status email under RISKS.
Two+ yeses on same axis for 3 weeks -> escalate to sponsor.
```

The value is in *doing this weekly*. Failure modes are cheap to fix in week 8, expensive in week 12, and impossible in week 20.

## FIELD NOTES

- Silent non-adoption is the deadliest failure mode because it doesn't feel like failure. Everyone's polite. The champion still demos. But the pilot is dying. The only defense is instrumentation from day one and honest weekly readouts.
- Champion churn detection lives in details. New job title on LinkedIn, a re-org email cc'd to you, a champion who suddenly cancels for "another meeting" more often. Read the small signals.
- Scope death spiral often looks like *goodness* — everyone is happy, the customer is excited, you're building lots. Then week 10 hits and you're 40% behind on the metric readout because you were building sideways.
- Escalation is a scalpel, not a hammer. When you escalate, do it with data and a specific ask. "We've missed 3 weeks of demos with the champion; can you (sponsor) confirm his continued sponsorship or nominate a replacement?" — that's an escalation. "The champion is unresponsive" — that's a complaint.
- Some engagements should be killed. If two failure modes are terminal, propose a graceful wind-down rather than lingering. Preserving future business at the customer often means acknowledging *this* engagement is dead and repositioning.

## INTERVIEW ANGLE

Failure modes come up in behavioral rounds and in "tell me about a time" prompts. The signal is whether you *recognize* failure early and act, versus discovering it in retrospect.

1. "Tell me about an engagement that didn't go well. What was the first sign?" (They want: a specific early signal you saw, whether you acted on it, what you learned. Not "the customer changed their mind" — that's a non-answer.)
2. "How do you tell the difference between a healthy pilot and a zombie pilot?" (They want: exit criteria written at pilot start, weekly demo cadence, executive readouts, and — most importantly — the pilot has a *date* on which someone decides go/no-go.)
3. "You suspect your champion is losing internal air cover. What do you do?" (They want: pre-existing second champion, exec-sponsor relationship you can activate, escalation with data and a specific ask, willingness to have the awkward conversation.)

## DRILL

Take a project you were on — internal or external — that stalled or failed. Map it to one of the six failure modes above. Reconstruct the earliest signal you had. Was it visible in week 4? Week 8? What did you do (or not do) with it? Now write the two-sentence Slack you *would have* sent to your engagement lead at that moment. Save it — this is the pattern-recognition muscle that pays off in Phase 7 (customer-facing craft) and in every behavioral interview you will ever do.
