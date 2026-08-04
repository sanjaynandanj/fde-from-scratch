# Discovery: Finding the Metric That Gets Renewal Signed

**Phase 1 · Lesson 02 · ~1h**

## PROBLEM

A junior FDE spends three weeks at a mid-market retailer doing "discovery." He interviews 14 people. He builds a beautiful process map with 47 boxes and swim-lanes for merchandising, planning, allocation, replenishment, and store ops. He can tell you how a SKU flows from the buyer's Excel file to the POS. His deck is called *Current State Assessment* and it is 38 slides. On week four, the customer's VP of Merchandising walks into the review, flips to slide 12, and says: "Okay but what number are you going to move?" The FDE freezes. He has understood the business but he has not found the metric. Two weeks later the engagement is on a "strategic pause" and by month three it's dead.

Discovery is not understanding the business. Discovery is finding the number.

## INTUITION

Every enterprise deal that renews renews because someone with a budget can point at a number that moved and say "that was them." Your entire discovery mission is to find that number *before* you write a line of code, and to find the human who will point at it.

The number has four properties:

1. **Owned.** A specific customer-side person's quarterly review depends on it. Not "the company's." A person's.
2. **Measured today.** They already track it, in a dashboard or a monthly deck. If they don't measure it, moving it will feel imaginary.
3. **Movable in 30 days.** Not "cultural transformation." Something a working piece of software could plausibly nudge in a pilot window.
4. **Worth more than the contract.** The math of moving it 5% has to exceed your ARR by a factor of at least 3–5x. If it doesn't, the champion won't fight for renewal.

Everything else — the systems map, the personas, the workshops — is scaffolding to find those four properties on one specific metric.

The trap is that customers rarely tell you the metric on day one. They tell you the *symptom* ("our forecasts are bad"), or the *aspiration* ("we want to be AI-first"), or the *project name* ("Project Beacon"). Your job is to translate those into a number with an owner.

## BUILD IT — the discovery interview cheat sheet

Print this. Take it into every discovery conversation. Fill it in during, not after.

```
INTERVIEW: <name>, <title>, <date>
Their quarterly review depends on: __________________
The number in their monthly deck they wish were higher/lower: __________________
Current value: ______   Target value: ______   Owner of that target: ______
Where the number lives today (system / dashboard / spreadsheet): ______
Last time the number moved materially — what caused it: ______
What they would do differently if the number moved 10%: ______
Who else looks at this number: ______
Do THEY believe it can be moved by software? (Y / N / hedged): ______

RED FLAGS:
[ ] They named an aspiration, not a metric
[ ] They named a metric they don't own
[ ] The number isn't measured today
[ ] They can't math the value of a 10% move
```

Run this against every stakeholder in weeks 0–2. You are looking for the *intersection* of what multiple people bring up. When three different people independently name the same number — that's the metric. When each person names a different number, you don't have a metric yet, you have a portfolio of hopes.

The output of discovery is a single sentence, written down, in a doc the exec sponsor has seen:

> "Success means moving <metric> from <baseline> to <target> by <date>, measured in <system>, owned by <name>."

If you cannot write that sentence, discovery is not done. It does not matter how many interviews you've done.

## FIELD NOTES

- The first metric the champion names is usually wrong. It's the metric that *they* care about; the renewal will be decided by their boss. Ask "and what does your VP measure you on?" Follow that number up the org until you hit someone with budget authority.
- Data quality kills more metrics than ambition. A great metric that lives in a broken system is not a great metric. Always ask to *see* the number in its native system before you commit to moving it. If the number is manually compiled by an analyst on the 5th of every month, your pilot has a new dependency you didn't know about.
- Vanity metrics are seductive. "Time saved," "hours automated," "documents processed" — customers love these because they're easy to compute. They also don't drive renewal. Push for revenue, cost, risk, or cycle time. Something a CFO would print.
- Some customers refuse to name a metric because they know they can't be held to it. That refusal is itself a signal — the engagement is being run without executive backing, and you should route around this stakeholder to find someone who *will* commit to a number.

## INTERVIEW ANGLE

Discovery is a favorite topic in FDE loops because it separates SWEs who think the customer will hand them a spec from FDEs who know they'll have to extract it.

1. "You've been dropped into a Fortune 500 with the mandate 'help supply chain use AI.' How do you find the metric to target?" (They want: structured stakeholder mapping, follow the number up the org, land on something owned, measured, and financially material.)
2. "Your champion says 'we want to save time.' What's your next question?" (They want: convert to owned, quantified metric — whose time, doing what, worth how much, measured where.)
3. "What's the difference between discovery and requirements gathering?" (Trick — discovery is finding the *why*; requirements gathering is scoping the *how*. The former makes the latter useful.)

## DRILL

Pick a company you know well (current employer, past employer, or a public company you can research). Imagine you're an FDE landing there next Monday. Write down three candidate metrics you'd probe for. For each, name a plausible owner (title, not person), the system where it lives today, and a rough estimate of what a 10% move would be worth annually. Now rank them by pilot-feasibility: which one could plausibly be moved in 30 days by working software? That's your target metric. Keep this — the format shows up in Phase 8 (decomp) and again in the Capstone 1 discovery transcript exercise.
