# Hypothesis Trees: Structuring an Ambiguous Problem in 5 Minutes

**Phase 8 · Lesson 03 · ~1h**

## PROBLEM

Ninety seconds into a decomp round, the interviewer says: "The retailer's inventory is off by 4% and nobody knows why." The candidate — a strong data engineer — starts listing possibilities out loud, in the order they occur to him. "It could be theft. Or maybe the receiving process. Or the POS system has a bug. Or seasonal demand. Or the vendors are short-shipping. Or..." Four minutes later he has produced a bulleted list of eleven mostly-overlapping causes, no structure connecting them, and no way to say which one to look at first. The interviewer, patient: "Which of these matters most?" The candidate: "Well, they all might..." He's not wrong. He's also not employable as an FDE, because in the field the same list will produce the same paralysis while the customer's meter runs.

The candidate who gets the offer takes 45 seconds of silence, then says: "Shrinkage is book minus count. So either the book is wrong, the count is wrong, or the delta between them — actual physical loss — is real. Book-wrong splits into intake errors and system errors. Count-wrong is measurement noise. Real-loss splits into external theft, internal theft, and vendor issues. Let me estimate each branch and prune." Same brain, same domain knowledge — but a *tree* instead of a *list*, and pruning instead of enumeration. Everything downstream flows from that reframe.

## INTUITION

A hypothesis tree is a MECE (mutually exclusive, collectively exhaustive) decomposition of "why is X happening" into branches you can estimate and eliminate. It's a search structure, not a taxonomy. The point is not to be comprehensive — it's to *make the pruning move visible*, so 30 minutes of investigation becomes tractable instead of open-ended.

Three properties separate a real tree from a bulleted list.

**The root is an equation, not a topic.** "Shrinkage" is a topic. "Book inventory minus counted inventory equals shrinkage" is an equation, and every branch is a term or component of that equation. Root as equation forces MECE by construction — if branches don't sum to the root, you have a bug in the tree, not in the world. Same trick for "ER wait times are up" → "P90 door-to-provider = triage interval + waiting-room interval + room-to-provider interval," three branches, each individually measurable. Same for "recovery from a storm is slow" → "recovery time = aircraft repositioning time + crew legality resolution time + decision-cycle time." The equation is the tree.

**Branches carry weight estimates.** Every branch gets a rough share — "I think receiving is 30% of shrink, POS fraud 20%, external theft 25%, count noise 25%." The estimates are wrong, and that's fine; their job is to *rank the branches for investigation order*. The 30% branch gets the first hour. This converts "we have no idea" into "our first cut says receiving; here's the data to check that." Interviewers grade this heavily — it's the difference between a possibility list and a work plan.

**Leaves are testable in a day.** A branch is fully decomposed when its leaves are things you could get evidence on by tomorrow — "look at receiving deltas per vendor," "sample 100 cycle counts and measure noise," "check void/refund patterns by cashier." Leaves that aren't day-testable mean you haven't decomposed enough. This is what makes hypothesis trees different from analysis frameworks — they end in *actions*, not categories.

The five-minute constraint is real. In an interview you have to build the tree fast enough that the rest of the decomp has room. In the field you build it in the first customer meeting, on their whiteboard, while they watch — which means it has to be robust to wrong branch weights and easily editable when the champion says "actually, we already know it's not that."

## BUILD IT

A **hypothesis-tree skeleton** for the three problem archetypes an FDE meets:

```
ARCHETYPE 1 — "Number X is bad"  (shrinkage, wait times, churn)

Root: X = A + B + C   (or A * B * C for multiplicative)
      │
      ├── Branch A [weight: 30%]
      │       ├── Leaf: check <specific data> for <specific pattern>
      │       └── Leaf: peer-compare against <benchmark>
      ├── Branch B [weight: 45%]  ← INVESTIGATE FIRST
      │       ├── Leaf: ...
      │       └── Leaf: ...
      └── Branch C [weight: 25%]
              └── Leaf: ...

Pruning rule: kill branches whose upper-bound weight
doesn't reach a decision threshold. If branch C could
only ever explain 5% of the gap and the gap is 40%,
stop looking there.


ARCHETYPE 2 — "Process P is slow"  (case triage, IROPS recovery)

Root: total_time = sum of stage intervals
      │
      ├── Stage 1 [avg time, tail time]
      ├── Stage 2 [avg time, tail time]  ← the tail matters
      └── Stage 3 [avg time, tail time]

Rule: decompose the P90, not the mean. The interesting
story lives in whichever stage owns the tail.


ARCHETYPE 3 — "Signal S is noisy"  (fraud, alerts, anomalies)

Root: observed_signal = true_signal + measurement_noise + adversarial_action
      │
      ├── True signal [what's the base rate?]
      ├── Measurement noise [what's the sensor lying about?]
      └── Adversarial [who's gaming the metric?]

Rule: if you can't split observed from measured, your metric
is not a metric — it's a report of your own instrument.
```

Two moves that make trees survive interview pressure.

**Weight before decomposing further.** As soon as a branch appears, assign a rough weight. Delaying weights until the tree is "complete" is how you end up with 15 leaves and no rank. Weight-then-decompose keeps the tree pruned as it grows.

**Say the pruning move out loud.** "I'm going to ignore external theft for now — even if it's 100% of the residual after other branches, the top-100 stores concentration says process fixes will hit first, and cameras take six months to procure." This sentence is worth more than the tree itself. It converts a diagram into a decision.

## FIELD NOTES

- In the field, customers *already have* a hypothesis tree — it's the informal one their team argues about at the ops meeting. Your job is often to draw their implicit tree explicitly on their whiteboard and put weights on the branches. That act alone is worth the pilot fee; it's the first time anyone at their company has seen the full space in one picture.
- Wrong weights are fine; missing branches are fatal. The politically dangerous branch — "maybe our own process is causing this" — is the one most likely to be missing from the customer's implicit tree, and adding it is a delicate art. Frame it as a hypothesis to *rule out*, not as a finger point.
- Trees get *smaller* over the engagement, not bigger. As branches get pruned, the pilot narrows to the winning subtree. A team still holding all 11 branches at week four is a team that hasn't decided anything.
- The best interviewers will grab your marker and *add a branch* to your tree. This isn't a trap — they're testing whether you can integrate new information without abandoning the structure. Absorb the branch, re-weight, keep moving.

## INTERVIEW ANGLE

Sample questions:

1. **"A SaaS company's churn just jumped from 3% to 5% quarterly. Build the tree."** (Answer: churn = involuntary (payment failure) + voluntary (cancellation) + product-death (dormant → dropped). Voluntary splits into value ("didn't get ROI"), fit ("wrong customer"), competitive ("switched"), champion ("our buyer left"). Weight the branches with rough thirds. Note: the P90 signal — accounts that expanded then churned — is a different tail worth breaking out.)

2. **"You built the tree. How do you decide which branch to investigate first?"** (Two criteria multiplied: (a) probability the branch explains a large share of the gap, weighted by (b) speed of getting evidence. A branch that could explain 40% but needs a 6-week data pull loses to a branch that could explain 20% and can be checked with today's export. State the criterion explicitly.)

3. **"Your top branch turns out to be small. What now?"** (You re-weight and move to the next branch. Interviewers *want* to see the branch fail — it tests whether your process survives being wrong. The wrong answer is defending the dead branch; the right answer is "good, that saved us six weeks, moving to branch B.")

## DRILL

Pick three headlines this week describing operational failures. For each, build the hypothesis tree in five minutes flat, with weights and day-testable leaves. Then, without looking at your work, redraw the tree from memory 24 hours later. If you can reconstruct the equation-root and the pruned branches, the shape has stuck. If you can only reconstruct the topic bullet list, it hasn't — do three more.
