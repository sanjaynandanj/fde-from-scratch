# Metric Design: Leading vs Lagging, Gameable vs Honest

**Phase 8 · Lesson 04 · ~1.5h**

## PROBLEM

Month four of a support-ticket triage pilot at a mid-sized SaaS company. The FDE's dashboard proudly reports the primary metric: **average time-to-first-response** dropped from 4.2 hours to 1.1 hours. The champion is thrilled. Renewal looks locked. Then the CSAT team publishes their quarterly report: customer satisfaction is *down*. The VP of Support pulls the FDE into a room and asks the question that ends careers: "Why does your dashboard say we got faster and your customers say we got worse?" Twenty minutes of investigation reveals it: agents are auto-sending a "thanks for reaching out, we're looking into this" bot-response within 60 seconds of every ticket. The first-response timer stops. The customer waits the same four hours as before, but now they've been notified that they're waiting. The metric moved. Nothing improved. The pilot metric was gameable, the agents figured it out in week two, and the FDE spent three months celebrating a scoreboard that had been quietly rigged.

The junior version of the lesson is "pick better metrics." The senior version is that *every metric is gameable*, and the FDE's job is to design a metric *system* — a primary plus a guard plus a diagnostic — such that gaming any one of them shows up in another. The candidate who understands this walks into a customer meeting and says, "I want three metrics and I'll tell you which one to trust when they disagree." That candidate gets hired.

## INTUITION

Four properties matter for any pilot metric. They compound.

**Leading vs lagging.** Lagging metrics measure outcomes — CSAT, revenue, retention, LWBS rate. They're the truth, and they move too slowly to steer by. A quarterly CSAT drop tells you the pilot failed three months after you could have fixed it. Leading metrics — first-response time, alert queue depth, model draft edit-distance — move in days or hours and are the steering wheel. Every pilot needs both: a leading metric to iterate against weekly, a lagging metric to prove renewal-worthy value. The rookie mistake is picking only one, in either direction. Only-leading builds a fast car with no destination; only-lagging builds a destination with no wheel.

**Gameable vs honest.** A gameable metric is one an operator can move without moving the underlying reality. First-response-time is gameable by autoresponders. Alerts-closed is gameable by rubber-stamping. Recovery-time is gameable by pre-cancelling everything. If the operator's incentive comp is tied to a gameable metric and the pilot ships that metric solo, expect gaming within one quarter — this is not cynicism, it's arithmetic on human behavior. Every gameable primary needs a *guard metric* whose degradation would show the gaming: pair first-response with CSAT or with time-to-resolution; pair alerts-closed with QA-agreement rate; pair recovery-time with total passenger disruption.

**Definable vs vibey.** "Improve the customer experience" is not a metric. "P90 door-to-provider time, by hospital, by acuity band, by hour-of-week" is a metric — because every noun in it is defined in the customer's actual data. The test: could two engineers, given the definition, compute the same number from the same data without asking each other questions? If no, the metric isn't defined; the pilot will spend three weeks arguing about what it means. Precision-in-definition is the boring skill that separates FDEs who ship from FDEs who negotiate.

**Owned vs orphaned.** Every metric has to have a human at the customer whose job depends on it moving. Orphan metrics — ones nobody's compensation or reputation is tied to — don't move even when your pilot succeeds, because nobody acts on them. Before locking a metric, ask: "Who at your company has this on their scorecard?" If nobody, you've picked a topic, not a metric.

## BUILD IT

A **metric-design table** — the artifact you bring to the discovery meeting and refuse to leave without filling in:

```
METRIC DESIGN TABLE

┌──────────────┬──────────────────────┬──────────────────────┬─────────────────────┐
│              │ PRIMARY              │ GUARD                │ DIAGNOSTIC          │
├──────────────┼──────────────────────┼──────────────────────┼─────────────────────┤
│ What         │ What we're moving    │ What must NOT move   │ Leading indicator   │
│              │                      │ (or must move with)  │ we watch weekly     │
├──────────────┼──────────────────────┼──────────────────────┼─────────────────────┤
│ Definition   │ Precise, computable  │ Precise, computable  │ Precise, computable │
│              │ from existing data   │ from existing data   │ from existing data  │
├──────────────┼──────────────────────┼──────────────────────┼─────────────────────┤
│ Cadence      │ Weekly               │ Monthly (lagging OK) │ Daily               │
├──────────────┼──────────────────────┼──────────────────────┼─────────────────────┤
│ Owner        │ Named human at       │ Named human at       │ Named human at     │
│              │ customer             │ customer             │ customer            │
├──────────────┼──────────────────────┼──────────────────────┼─────────────────────┤
│ Slicing      │ By segment / time /  │ By segment           │ By segment / stage  │
│              │ severity band        │                      │                     │
├──────────────┼──────────────────────┼──────────────────────┼─────────────────────┤
│ Gaming vector│ How could someone    │ (guard exists to     │ (usually not gamed  │
│              │ move this without    │ catch the primary's  │ — it's diagnostic)  │
│              │ moving reality?      │ gaming)              │                     │
└──────────────┴──────────────────────┴──────────────────────┴─────────────────────┘

Worked example — support triage pilot:

  Primary:    P90 time-to-resolution, by ticket severity, weekly
  Guard:      CSAT at close, by severity, monthly
  Diagnostic: reopen rate within 7 days, daily

  Rejected metrics (say out loud why):
    - "First-response time" — gameable by autoresponders
    - "Tickets closed per day" — gameable by rubber-stamping
    - "Customer satisfaction" alone — too lagging to steer by
```

Two moves that harden the system.

**Reject metrics aloud.** Explicitly enumerate the metrics you *considered and rejected*, and why. This does two things: it demonstrates to the interviewer or customer that you know the space, and it inoculates against later "why didn't we use X?" second-guessing. A rejected metric with a stated reason is a decision; a metric that just didn't come up is an oversight.

**Instrument the guard from day one.** The guard metric is worthless if it's only computed at renewal time — by then the gaming is baked in. Ship the guard on the same dashboard as the primary, even if it's noisy for the first month. When the two diverge, you find out in week two, not month four.

## FIELD NOTES

- The most political conversation in an engagement is the metric conversation. Customers arrive with an implicit metric ("customers are unhappy") and a preferred metric ("CSAT") and the actual right metric is usually neither. Landing the metric definition is a two-week negotiation that most FDEs try to compress into one meeting and lose.
- Guard metrics get cut for "simplicity" more than any other artifact. When the champion says "let's just focus on the one number," they're proposing to remove the safety line. Push back. The one-number pilot is the one that gets gamed.
- Reference: the anti-gaming lesson from the ER wait-time case walkthrough (Lesson 08) — pairing door-to-provider with LWBS as guard and boarding-hours as diagnostic is the canonical three-metric FDE move. Study it. That triad structure transfers to almost every operational pilot.
- Real customers often already have a corrupted metric on a dashboard somewhere — "we track NPS." Killing an existing bad metric is politically harder than adding a good one, so the pragmatic play is often to *add* the honest metric next to the incumbent, let them diverge for a quarter, then propose the swap when the evidence is undeniable.

## INTERVIEW ANGLE

Sample questions:

1. **"Design the metric for a fraud-detection pilot at a bank."** (They want the triad, not a number. Primary: precision-at-K flagged alerts, weekly. Guard: false-positive impact on legitimate customers (blocked transactions per million, monthly). Diagnostic: analyst investigation yield per hour. Rejected: "fraud caught %" because ground truth requires audit and is thus circular. Anti-gaming: the primary is gameable by flagging only obvious cases — the guard on customer impact catches that, but a stronger guard is *coverage* (share of true fraud caught, estimated from the random-sample lane), which requires the random-sample lane to exist.)

2. **"Your primary metric is moving. What would tell you it's real vs gamed?"** (Answer shape: the guard metric moves in the *right* direction alongside, or at minimum doesn't degrade. The diagnostic shows the *mechanism* — you can point at which stage got faster or which pattern got flagged. If the primary moves and both guard and diagnostic are flat, assume gaming until proven otherwise.)

3. **"A metric that would embarrass the customer — do you ship it?"** (Yes, with framing. Boarding hours in the ER case indict inpatient units, not the ER. The FDE move is to brief the executive privately before the cross-department readout, so the finding lands as insight, not accusation. Metrics with political weight need political staging.)

## DRILL

Take a pilot you've shipped or seen. Fill in the metric-design table for it in full — including the "rejected metrics" row. Then ask: what's the fastest way someone could game the primary without moving reality? If the guard metric wouldn't catch that gaming vector, redesign the guard. Do this until you can produce a defensible triad for any operational pilot type in under 10 minutes.
