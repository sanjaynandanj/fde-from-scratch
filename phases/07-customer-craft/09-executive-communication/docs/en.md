# Executive Communication: The One-Slide Update

**Phase 7 · Lesson 09 · ~1h**

## PROBLEM

Thursday afternoon, week eight of a pilot at a hospital system. The champion Slacks: "CFO is asking about the AI thing in tomorrow's exec meeting — can you send me a summary I can use?" The FDE, wanting to be thorough, spends four hours writing a three-page brief covering architecture, integration status, model accuracy, adoption metrics, and next steps. He sends it Friday morning. The champion responds three hours later: "thanks — but I only have 90 seconds in the meeting, do you have something shorter?" There is no time to redo it. The champion pastes two random sentences from the brief into the meeting. The CFO leaves unclear on whether the project is on track. Two weeks later, budget is quietly reallocated to a different initiative. The FDE didn't lose the pilot on the technology. He lost it on the format of the summary.

Executives read differently than the people you talk to daily. Learn their format or lose their attention.

## INTUITION

Executives make decisions in seconds, not minutes. Three cognitive constraints govern their attention:

1. **Answer first, evidence after.** They want the punchline in the first sentence. Everything else is optional. A brief that builds to a conclusion has already lost them.
2. **One number, not five.** The one number that would change the decision. Multiple metrics feel rigorous to you and dilute the point to them.
3. **A specific ask, or no ask.** A brief without a decision-request is noise. A brief with three decision-requests overloads. Pick one.

The one-slide (or one-paragraph) update is the format executives trained themselves on for twenty years. Learn to produce it and your champion will forward it verbatim to their VP, who will forward it to the CFO, who will remember your project's name when budget conversations happen.

## BUILD IT

The **One-Slide Format** — 5 sections, no more, no less. Fits on a single slide or a single Slack message.

```
[PROJECT NAME] — [DATE] — STATUS: 🟢/🟡/🔴

HEADLINE  (one sentence, past tense, ends with a number)
[e.g., "Cold-start forecasting shipped to pilot; MAPE dropped from N/A to 18% on 200 new SKUs."]

WHY IT MATTERS  (one sentence, connects to a business outcome the exec cares about)
[e.g., "Merch team can now plan inventory for new-SKU launches without manual overrides — the workflow that caused $2.1M in overstock last quarter."]

WHAT'S NEXT  (2-3 bullets, each starting with a verb, each with a date)
- Roll out to production data — Aug 20
- Onboard second merch team — Aug 27
- Present renewal proposal — Sep 5

RISK  (one sentence, honest, with a mitigation)
[e.g., "Production data access still pending IT approval; escalating via [name] this week if not resolved by Wednesday."]

ASK  (one sentence, one decision, named)
[e.g., "Need [CFO name]'s sponsorship on the IT ticket to unlock production access this week."]
```

Rules:

- Total word count: under 120. If yours is longer, cut.
- The headline must contain a number. If it doesn't, you haven't found the outcome.
- No jargon. "Cold-start heuristic" becomes "handling for products with no sales history." If a non-technical VP can't read it, rewrite.
- Never more than one Ask per slide. Multi-ask slides get zero decisions.
- The status color is honest. If you've been green for eight weeks with nothing hard happening, you weren't being ambitious.
- Ship it as a PNG *and* as pasteable text. Champions will paste it into their own materials.

Optional companion: the **90-second script.** Given the slide, what does the champion *say* out loud in the meeting? Draft it for them:

> "The AI forecasting pilot shipped its new-SKU capability last week — MAPE dropped from N/A to 18% on the 200 new SKUs we launched in March. That's the exact workflow that cost us $2M in overstock last quarter. We're rolling to production data on the 20th and onboarding a second team on the 27th. The one thing that would help this week: your sponsorship on the IT access ticket."

You have just done the champion's job for them. That is the highest-leverage 90 seconds of your week.

## FIELD NOTES

- Executives skim. Bold the number. Bold the ask. Nothing else.
- Never send a one-slide with more than one color of status. Consistency is credibility.
- The first draft always has three asks. Kill two. If they're all critical, prioritize and ship the others next week.
- If your champion has to edit your one-slide before forwarding, you missed. Iterate the template until they forward verbatim.
- Numbers without denominators are useless: "18% MAPE" is fine only if the audience knows what's normal; "18% MAPE, down from ~40% baseline" is better.
- Save every one-slide. Sequenced, they become the renewal deck — literally.
- Distinguish the one-slide from the WWRA one-pager (Lesson 05): WWRA is for the working team, one-slide is for the exec above your champion. Different audiences, different formats.

## INTERVIEW ANGLE

Executive communication comes up in behavioral rounds and in take-home debriefs where you present findings. Interviewers listen for whether you can compress a complex project into a decision-usable summary.

Sample questions:

1. *"You have 90 seconds with a CFO. What do you say about your project?"* — Strong answers follow headline / why-it-matters / next / risk / ask, land a number, and end with a specific decision request. Weak answers describe the technology.
2. *"Show me a status update you've sent to an executive."* — Bring a real one-slide (redacted). They'll evaluate structure, headline sharpness, ask specificity.
3. *"Tell me about a time a communication failure hurt a project."* — STAR. Best stories show a specific format change ("we moved from three-page briefs to one-slide") and the result.

## DRILL

Take a project you have shipped (real work, side project, or a Phase 1 pilot from earlier lessons). Write the One-Slide Format in full: headline with a number, why-it-matters tied to a business outcome, three dated next-steps, one honest risk, and one named ask. Total word count under 120. Then write the 90-second script your champion would say aloud, using the slide. Rehearse it out loud, timed. If it runs over 90 seconds, cut. Send both to a non-technical friend and ask them to summarize what your project is and what you're asking for. If they can't in one sentence each, iterate.
