# Saying No: Scope Control Without Losing the Room

**Phase 7 · Lesson 07 · ~1h**

## PROBLEM

Week five of a pilot at a specialty retailer. The champion loves the tool. So does her boss. So, now, does her boss's peer VP, who happened to see a demo. On Monday the champion emails: "hey, quick one — can we add a supplier scorecard tab? Should be small since you already have the data." The FDE, wanting to be helpful and to keep goodwill flowing, says yes. On Wednesday the peer VP emails: "loved the demo — can we get a mobile view for the field team?" Yes. On Friday: "one more — can it handle our EU subsidiaries too, they use different SKUs?" Yes, of course. Three weeks later the pilot's original goal — cold-start forecasting — has slipped a month, none of the new asks are done well, the champion is frustrated, and the FDE is quietly resentful. Nobody said no. So everyone lost.

Saying no is a customer craft, not a personality trait. Done well, it *increases* trust because it makes your yeses meaningful.

## INTUITION

There are five flavors of no, and picking the right one matters more than the courage to use it:

1. **"Not now."** The ask is legitimate, but it competes with the pilot goal. Park it in a written backlog with a date to revisit. Cheapest no.
2. **"Not by us."** The ask is legitimate and important, but it's not what you were brought in for. Route it to the right team — internal or external. Makes you look like a good citizen.
3. **"Not without X."** Conditional yes: sure, if you can get us data access / a second engineer / an extra two weeks. Turns a scope negotiation into a resource negotiation.
4. **"Not the way you framed it."** The ask hides a different real need. Reframe: "before we build a scorecard tab, can I ask why — is it a specific supplier conversation coming up? Would a one-time report be enough?"
5. **"Not at all."** The ask is a bad idea and building it would hurt the pilot. The hardest no; use rarely, with evidence.

The universal grammar: acknowledge → name the tradeoff → propose an alternative → confirm alignment in writing. Nobody remembers a soft no; they remember whether they felt heard.

## BUILD IT

The **Scope Tradeoff Card** — a one-artifact pattern you use in the moment.

```
ASK: [verbatim, one sentence]
STATED VALUE: [why they want it, in their words]
IMPLIED SIZE: [your honest estimate, in days]
IMPACT ON PILOT GOAL: [what would slip; be specific]
NO-FLAVOR: [not now / not by us / not without X / not that way / not at all]
ALTERNATIVE: [the smaller/simpler/deferred thing you'll do instead]
CONFIRMATION: [the sentence you'll send in writing within 4 hours]
```

Filled example:

- ASK: "Can we add a supplier scorecard tab? Should be small since we have the data."
- STATED VALUE: giving merch a way to compare suppliers during quarterly reviews.
- IMPLIED SIZE: 4-6 days done well (schema, aggregation, UI, validation), plus ongoing maintenance.
- IMPACT ON PILOT GOAL: cold-start forecasting rollout slips one week; production data-access conversation delayed.
- NO-FLAVOR: not now.
- ALTERNATIVE: "Can I export a one-time supplier scorecard as a CSV this week, so you have it for the review? We can look at making it a tab after the forecast lands."
- CONFIRMATION email: "confirming: I'll get you a supplier scorecard CSV by Thursday for the review. We're keeping the tab out of pilot scope for now so we can hit the forecast go-live on the 20th. Sound right?"

Rules:

- Write the confirmation in writing, always. Verbal yeses and nos both drift. The email is the artifact.
- Say the tradeoff in *their* terms: "we'd slip the forecast go-live" beats "it's out of scope."
- Never blame process ("that's not in the SOW"). Own the choice: "I'd rather ship the forecast well than start a scorecard poorly."
- Propose the alternative in the same breath as the no. A no without an alternative is a wall.
- Escalate ambiguous scope decisions to the champion in writing before they become resentment. Weekly reviewing the WWRA one-pager (Lesson 05) is where these live.

## FIELD NOTES

- The riskiest scope creep comes from *peers of the champion* — VPs who saw the demo and want a piece. They have no ownership of the pilot goal, so they optimize for their own agenda. Route these back to the champion: "let me loop in [champion] since she owns the roadmap."
- The safest scope creep comes from *users* asking for small usability fixes. Say yes to more of these — they build daily adoption and cost hours, not weeks.
- "Just a small thing" is almost never small. Whenever you hear it, force a size estimate before agreeing.
- If you find yourself resenting a customer's asks, you already said yes to too many. Reset with a written scope conversation, not silent overwork.
- The champion often doesn't want the extra scope either but doesn't have the political room to say no themselves. Your no gives them cover. This is one of the most valuable services you provide.
- Track scope changes formally. A running "In / Out / Deferred" list in the shared doc means you never have to relitigate old conversations.

## INTERVIEW ANGLE

Scope control is a top-three FDE behavioral probe. Interviewers know that new FDEs default to "yes, and…" and want to see you've internalized that saying no *well* protects the engagement.

Sample questions:

1. *"A customer VP asks for a new feature during a demo. What do you say in the moment?"* — Correct instincts: acknowledge, don't commit in the room, offer to follow up, capture the ask. Weak answers commit on the spot.
2. *"Tell me about a time you said no to a customer and it strengthened the relationship."* — STAR. Best stories show that the no was framed as tradeoff protection, and that the customer thanked you later.
3. *"Your champion asks for something that would blow the pilot timeline. How do you handle it?"* — Tests whether you can push back on the person who is your biggest political asset. They want to hear that you'd frame the tradeoff in terms of the pilot goal, not refuse the ask.

## DRILL

Take three real asks you've received recently — from a customer, a manager, or a peer — and fill out a Scope Tradeoff Card for each: verbatim ask, stated value, honest size estimate, impact, no-flavor, alternative, and confirmation sentence. Then rewrite each confirmation email in three tones: warmer than natural, plainer than natural, and cooler than natural. Notice which one you'd actually want to receive. Send the plainest one.
