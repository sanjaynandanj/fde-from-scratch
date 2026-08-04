# Running the Weekly: Status, Wins, Risks, Asks

**Phase 7 · Lesson 05 · ~1h**

## PROBLEM

An engagement at a mid-size bank. The FDE runs the Wednesday sync — a 60-minute meeting with the champion, two directors, and whoever from the customer's side wanders in. He spends the hour giving a heartfelt update: what the team did this week, what they learned, some architecture context, and a live tour of the new dashboard. Two months in, the champion pulls him aside: "these meetings are draining. My directors have stopped attending. Can we make them shorter?" What she means is: your meeting has no shape. There is no artifact. Nobody knows what got decided. She is losing political air-cover because her leadership feels she is spending an hour a week on something without visible progress. The engagement isn't in trouble because the work is bad — it's in trouble because the *rhythm* is bad.

The weekly is not a status meeting. It is the recurring artifact that keeps your project real inside your customer's political system.

## INTUITION

A great weekly does four jobs, in this order, in under 45 minutes:

1. **Prove momentum** with what shipped since last week.
2. **Surface risk** early enough that someone in the room can help.
3. **Make asks** so the customer sees exactly what unblocks the next week.
4. **Reserve time for their questions**, on their terms.

Ordering matters. If you lead with risks, you sound like you're in trouble. If you lead with asks, you sound like a burden. If you lead with wins, you buy the political capital to talk honestly about the rest.

The second insight: the meeting is not the artifact — the pre-read is. Ship a one-page written status 24 hours before the meeting. Half your audience will read it and skip the meeting; the other half will show up warmed up. Both outcomes are good.

## BUILD IT

The **WWRA One-Pager** — Wins, Watches, Risks, Asks. One page. Ships Tuesday for a Wednesday meeting.

```
PROJECT: [Codename] · Week [N] of [Total] · [Date]
PILOT GOAL: [one sentence — the metric that gets renewal signed]
STATUS: 🟢 On track  |  🟡 Watch  |  🔴 At risk  (pick one, be honest)

WINS THIS WEEK
- [Ship-verb] [artifact]: [one-line impact, with number if possible]
- [Ship-verb] [artifact]: [one-line impact]
- [Ship-verb] [artifact]: [one-line impact]
(3-5 items, each starting with a verb: shipped, deployed, integrated, validated)

WATCHES (things trending in the wrong direction, not yet risks)
- [What we're watching]: [why it matters, what would tip it into a risk]
- [What we're watching]: [why]

RISKS (things that will hurt the timeline if we don't act)
- [Risk]: [likelihood: L/M/H] · [impact: L/M/H] · [proposed mitigation] · [decision needed by]
- [Risk]: [L/M/H] · [L/M/H] · [mitigation] · [decision by]

ASKS (specific, named, dated)
- [Name]: [what you need] by [date] — so that [downstream effect]
- [Name]: [what] by [date] — so that [why]

NEXT WEEK
- [3-5 shipping items]

METRICS
- [pilot-KPI]: [current value] (target: [X], last week: [Y])
- [health metric]: [value]
```

Rules:

- Every Ask has a *name* — a specific human, not "the security team." Ambiguous asks don't get done.
- Every Risk has a *decision date*. Risks without dates are complaints.
- Wins must be concrete — "shipped forecast v2 with cold-start handling" beats "made progress on forecasting."
- Never move a Watch to Risk to hide the fact you missed it last week. If it should have been a Risk two weeks ago, say so.
- The status color is honest. A pattern of three green weeks in a row followed by "surprise, we're red" destroys credibility. If nothing is at risk, nothing is ambitious.

The meeting itself: 5 minutes reviewing the one-pager (assume half didn't read it), 10 minutes on Wins with a live demo if possible, 10 minutes on Risks + Asks, 10 minutes for their questions, 5 minutes to confirm decisions and owners in writing. Send a one-line follow-up email within an hour: "confirming [Name] owns [Ask] by [date]; [Risk] mitigation approved."

## FIELD NOTES

- Send the pre-read at the same time every week. Tuesday 4pm for a Wednesday 10am. Rhythm matters more than perfection.
- If nobody has questions, you probably went too long. Cut ten minutes off next week's agenda.
- The single most valuable thing in the meeting is the *pause* after "any risks I'm missing?" Wait ten seconds. Someone always speaks.
- Rotate who runs the demo. If the same FDE always drives, the customer never learns the tool. Have a user drive by week six.
- Cancel the weekly during dead weeks (holidays, freezes). Meetings that consistently have nothing to report train people to skip them.
- Save every WWRA one-pager. At the end of the engagement, stitched together they are the renewal deck.

## INTERVIEW ANGLE

Behavioral rounds and take-home debriefs both probe communication cadence. Interviewers want to see that you understand the weekly as a political artifact, not a status ritual.

Sample questions:

1. *"How would you structure a weekly customer sync?"* — Strong answers name a specific format (WWRA or similar), specify a pre-read, and put Asks *after* Wins. Weak answers describe a feature demo.
2. *"You have a Wednesday meeting and nothing shipped this week. What do you do?"* — Correct instincts: don't skip, but change the shape — bring a decision to unstick, or bring a data point that reframes the problem. Never fake a win.
3. *"A stakeholder stops attending your weekly. What does that tell you and what do you do?"* — Tests political awareness. They want to hear you diagnose (bored? unhappy? reorged?) and reach out one-on-one before assuming.

## DRILL

Take an engagement — real or from Phase 1 — and write a full WWRA one-pager for a hypothetical week four. Include: status color with justification, 4 concrete wins, 2 watches, 2 risks with named decision owners and dates, 3 asks each with a named human, next-week shipping list, and 2 tracked metrics with current and target values. Time-box to 30 minutes. Then rewrite it as if the status is 🔴 instead of 🟢 — the same project, same work, different reality. Notice how the shape stays the same; only the content changes. That constancy is the rhythm your customer buys.
