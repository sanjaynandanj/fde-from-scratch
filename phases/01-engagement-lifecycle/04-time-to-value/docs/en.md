# Time-to-Value as the Only KPI That Matters

**Phase 1 · Lesson 04 · ~1h**

## PROBLEM

Two FDE teams work at similar-sized manufacturing customers on similar problems (predictive maintenance for factory equipment). Team A sets up a "proper" infrastructure — a data lake, a feature store, a training pipeline, MLOps tooling. In week 6 they have a beautiful architecture and no user has seen a prediction. Team B, at the sister customer, dumps three months of sensor CSVs into SQLite in week 1, writes a hand-tuned heuristic in week 2, shows the plant manager a ranked list of at-risk machines on Friday of week 2, and by week 6 has iterated the heuristic four times based on the plant manager's feedback. The customer of Team A cancels in month three. The customer of Team B renews and expands the contract. Team A wrote better code. Team B moved the number six weeks earlier.

Every hour that passes before the customer sees value is an hour the political case for your engagement is quietly weakening.

## INTUITION

Time-to-value (TTV) is the elapsed calendar time between engagement start and the moment a customer-side human, in their own words, says "this is doing something useful for me." Not "this is impressive." Not "this is technically interesting." *Useful for me.* Every other KPI in an engagement — code quality, architecture, cost, latency — is subordinate to TTV until that moment happens. After that moment, priorities can shift. Before it, they cannot.

Why TTV is *the* KPI:

- **Political capital decays.** The exec who sponsored you had a reason on day one. That reason has to be validated before the reason gets stale (org changes, budget cycles, new priorities). 30 days is usually the half-life.
- **The champion is fighting for you internally.** Every week without a visible win, they lose credibility. Every week with a visible win, they gain it. You are the arms dealer in a political fight your champion is waging on your behalf.
- **Real value creates real feedback.** Until the user *uses* the thing, all requirements are hypothetical. Speculation compounds. Actual use collapses the requirement tree.
- **Renewal math is anchored to first value.** The customer will remember "we saw a result in week 2" and forget that the result was scrappy. They will remember "we saw a result in month 4" and forget that the result was elegant.

The trade-off is real. Optimizing for TTV means writing throwaway code, cutting scope, faking non-critical pieces, and shipping ugly. All of these feel wrong to a good engineer. They are correct in the pilot phase. The elegance debt gets paid in the production phase, when you know what's worth being elegant *about*.

## BUILD IT — the TTV budget decision tree

Every scoping and build decision in a pilot passes through this tree. Print it. Apply it before agreeing to anything.

```
NEW REQUEST OR IDEA
    |
    v
Does it accelerate the moment the user sees value?
    |         |
    YES       NO
    |         |
    v         v
Fits in the  Is it required for
current      day-30 readout?
week?           |         |
    |           YES       NO
    YES         |         |
    |           v         v
    v         Fits in     DEFER to
   DO IT     remaining    production
             pilot        phase.
             build days?  Write it in
                |         the out-of-scope
                YES  NO   log.
                |    |
                v    v
              DO IT  CUT
                    something
                    else or
                    DEFER
```

Simple heuristics that fall out of this tree:

- **Fake the boring parts.** If the customer wants exports to their CRM but the CRM integration takes 5 days, show a CSV download this week and the CRM integration next month. The user experiences the workflow now.
- **Seed the demo with real-but-hand-curated data.** In week 1 you don't have the full pipeline. You have 200 rows you picked by hand. That's fine. The user learns whether the workflow is useful; you learn what the pipeline needs to do.
- **Cache aggressively, iterate ugly.** A materialized view refreshed nightly is a fine pilot answer to a "real-time" ask. Nobody's making trading decisions off your dashboard yet.
- **Never wait on infra.** If prod-grade auth would take two weeks, use HTTP basic auth in the sandbox and put "prod auth" in the production-phase backlog. The customer will not renew based on your auth story; they'll renew based on the metric.

## FIELD NOTES

- Engineers coming from platform / infra backgrounds struggle with TTV thinking. They were rewarded for building things that scale. In an FDE pilot, scaling is a category error — you're building a thing that has to matter *before* it has to scale.
- Executives smell "not real yet" from a mile away. Do not demo *architecture*. Demo the user pushing a button and getting a result. The architecture slide is for later, if ever.
- TTV includes access time. If access takes 4 weeks, your effective build window shrinks. Chasing credentials on day one is TTV work — it just doesn't feel like it because you're not coding.
- The clock resets when a stakeholder changes. If your champion leaves, you have a new TTV clock with the new champion. Plan a fresh visible win in their first month.
- Some pilots are structurally slow — highly regulated data, on-prem constraints, air-gap. In those cases, TTV isn't "user sees production result in 30 days," it's "user sees a synthetic-data walkthrough in 30 days" with a written path to real data by day 90. Adjust the promise; keep the discipline.

## INTERVIEW ANGLE

TTV shows up in almost every FDE behavioral round because it's the clearest way to distinguish an FDE mindset from a SWE mindset.

1. "Tell me about a time you shipped something you knew was not architecturally right, because getting it to the user mattered more." (They want: explicit trade-off, real time pressure, a customer-facing benefit that justified the debt.)
2. "You have two weeks and two workstreams: build the ETL pipeline properly, or hand-curate data for a Friday demo. Which and why?" (They want: hand-curate; explain that the demo unlocks feedback that will change the ETL requirements.)
3. "How do you know when to stop optimizing for TTV and start hardening?" (They want: exit criteria of pilot phase, the moment the customer commits to production, the specific artifacts — like a written pilot exit memo — that mark the shift.)

## DRILL

Take your pilot scoping doc from Lesson 03. For each in-scope item, answer: what would the fake / cached / hand-curated version look like this week? Now write the "TTV budget" — a bulleted list of what you'll fake, what you'll defer, and what you'll build for real. Send yourself an email dated day 7 of the imaginary pilot describing the first thing the user saw. If that email is boring — nothing to demo, all setup — restructure the plan.
