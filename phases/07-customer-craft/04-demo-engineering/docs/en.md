# Demo Engineering: Narrative Arc, Seeded Data, Recovery Moves

**Phase 7 · Lesson 04 · ~1.5h**

## PROBLEM

The Wednesday demo, week four, at a national health system. Five stakeholders in the room, three on video, and — surprise — the CMO has dropped in. The FDE opens the app, clicks "run pipeline," and gets a spinner. Twenty seconds pass. The champion starts nervous-joking. At second forty, the FDE alt-tabs to a terminal, finds a stack trace, mumbles "one moment," and starts debugging live. By minute three the CMO has left the call. The demo did not fail because the software was bad. It failed because there was no narrative, no fallback, and no rehearsal. The next week's demo — same software, same room — goes flawlessly because the FDE has learned what demo engineering actually is.

A demo is a piece of software. Treat it with the same rigor as production and it becomes your single most powerful engagement tool.

## INTUITION

A good demo has a *story*, and every second of the runtime serves it. Three principles:

1. **Narrative arc, not feature tour.** Nobody wants to see your fifteen buttons. They want to see the day-in-the-life of the person whose life this changes. Structure: setup (here's the world today), inciting incident (a real case where it breaks), rising action (walk through the tool), resolution (the outcome number). Twelve minutes, tops.
2. **Seeded data over live data.** Live data means live surprises — nulls, spinners, empty states, embarrassing records. Seed a dataset that showcases the range of behavior you want to prove, and ship it as the "demo mode" of your app. Real data is a milestone for week 8, not the safety net for week 4.
3. **Recovery moves rehearsed.** Something will break. Have three canned moves ready: (a) the fallback ("here's a screenshot from yesterday's run showing this working"), (b) the pivot ("let me show you the other flow while this reruns"), (c) the honesty ("that's a real bug, thank you — I'll debug after the call, but the concept holds"). Never debug live in front of executives.

The best FDEs treat the demo as a scripted product, versioned in git, rehearsed twice before every showing.

## BUILD IT

The **Demo Script Structure** — a text file that lives in the repo alongside the code. Fields:

```
DEMO_ID: pilot-week4-demand-forecast
DURATION: 12 minutes
AUDIENCE: VP Merch, Director Ops, CMO, 2 users
GOAL: sign off on cold-start heuristic; unlock production data access

SETUP (2 min)
- Open with: "Last week you asked for new-SKU handling. Here's what we built."
- Show slide: the problem in one sentence + last month's failure case
- Set expectations: "12 minutes, then questions"

INCITING INCIDENT (2 min)
- Open the app in demo mode (seed set: 200 new SKUs from March launch)
- Show current-state forecast: zeros across the board
- Verbatim line: "This is what merch was seeing on April 1."

RISING ACTION (5 min)
- Flip feature flag `cold_start_v1`
- Show new forecast: category-mean fallbacks with confidence bands
- Click one SKU: show the "why" panel (which category, N similar SKUs, sample size)
- Filter to the 20 SKUs the champion picked for validation
- Show the accuracy chart against actuals-to-date

RESOLUTION (2 min)
- Land the outcome number: "on the 20 SKUs merch validated, MAPE dropped from N/A to 18%"
- Show the deploy checklist for production, one item highlighted red (data access)
- Ask: "what would make you comfortable turning this on for real inventory next month?"

Q&A (open)

RECOVERY MOVES
- If app fails to load → screenshot deck at /demo/backup/screens/*.png
- If forecast API errors → prerecorded 60s screen recording at /demo/backup/happy_path.mp4
- If a stakeholder asks about SKUs outside the seed → "great edge case — noting it for next week"
- If CMO asks about ROI → pull up the one-slide from Lesson 09, don't improvise
```

Rules: rehearse it aloud twice, timed. Anything that can't be shown in 12 minutes is cut or deferred. Every "click X" step must have a fallback screenshot. Never demo unversioned code — tag the demo commit before the meeting.

## FIELD NOTES

- The best demos end with a question, not a summary. "What would make you comfortable turning this on?" is worth more than "any questions?"
- Bring a printout of the script for yourself. Screens fail; paper doesn't.
- Executives arrive late and leave early. Front-load the outcome number in the first two minutes, then let the storytelling unfold. Do not save the punchline for the end.
- Seeded data must look real. Use plausible SKU IDs, plausible names, plausible dates. A demo with `test1, test2, test3` will destroy trust even if the software is perfect.
- Never let a customer drive the demo. If they ask "can I click around?", promise a sandbox next week and keep control today.
- Record every demo (with permission). Watch it back. You will be humbled and you will improve fast.
- Wednesday demos become a rhythm. Missing one is worse than a mediocre one. Ship *something* every week.

## INTERVIEW ANGLE

The "demo round" is standard at Palantir FDE loops, and behavioral rounds at every enterprise-AI shop will probe your demo instincts. Interviewers want to see storytelling instinct plus operational discipline.

Sample questions:

1. *"Walk me through how you'd prepare for a Wednesday demo to a skeptical VP."* — Strong answers cover: narrative arc, rehearsal, seeded data, three recovery moves, a closing ask. Weak answers are "I'd make sure the code works."
2. *"Your demo breaks live in front of an executive. What's your next 30 seconds?"* — Correct instinct: acknowledge, pivot to fallback, do not debug in front of them. Bonus points for having the fallback ready.
3. *"Tell me about a demo that changed the trajectory of a project."* — Behavioral. They want a story where a demo either saved a stalled engagement or accelerated a stuck decision. Best answers include what you'd have changed about the script in hindsight.

## DRILL

Take a project you have shipped. Write the Demo Script Structure for a 12-minute demo of it to a hypothetical VP. Include: verbatim opening line, seeded dataset description (specific IDs, plausible names, at least 20 rows), five click-by-click steps, an outcome number, a closing question, and three recovery moves for likely failures. Then rehearse it aloud, timed. If it runs over 12 minutes, cut features until it doesn't. If a friend can watch it and tell you the outcome number without prompting, you have a working demo.
