# The Demo-Quality Bar: What to Fake, What Must Be Real

**Phase 2 · Lesson 02 · ~1h**

## PROBLEM

Tuesday of week two. The engagement lead has booked a demo for Thursday with the customer's COO — the economic buyer, the one who signs the renewal. The FDE has 48 hours. Her instinct, honed by three years of shipping production software, is to wire the auth flow, plumb the audit log, and generalize the parser to handle the four export formats she's seen. Thursday morning she has half a working auth flow, a parser that handles two formats, and no dashboard. The demo goes badly. The COO leaves after eight minutes. Two weeks later she watches a colleague do the same demo — one hardcoded user, one export format, a dashboard that opens straight to a preloaded scenario — and the COO stays for forty minutes and asks about pricing.

The difference wasn't skill. It was knowing what the demo needed to *actually* prove and what it could pretend.

## INTUITION

A demo has two audiences: the person watching and the person's imagination. The person watching needs the narrative to survive. Their imagination fills in everything you don't touch. Your job is to figure out which parts they will touch — and make those parts real — while leaving the rest as convincing scenery.

The dimensions of the trade-off:

- **Real data vs seeded data.** The workflow they care about must run on *their* data, or data indistinguishable from it. The rest can be seeded.
- **Real logic vs scripted output.** The one number that shows up on their dashboard — the recovered revenue, the flagged transactions — must come from your actual pipeline. The three other charts around it can be static.
- **Real integration vs mocked boundary.** Their SSO doesn't need to work in the demo. Their data source *sometimes* does — depends on whether the discussion will hinge on freshness.
- **Real errors vs happy path.** Never demo an error path unless you can control it. Never demo something that touches a network you don't own.

The heuristic: **fake anything the customer won't touch this quarter; make real anything that generates the number in the deck.**

## BUILD IT

Use this two-column checklist before every demo. Fill it out on paper. If a row lands in the wrong column, you have work to do or a story to tell.

```
DEMO SURFACE            | MUST BE REAL             | CAN BE FAKED
------------------------|--------------------------|----------------------------
The headline number     | Yes — from real logic    | Never
The customer's own data | Yes — at least one slice | Everything else seeded
Auth / SSO              | No                       | Hardcoded user is fine
Audit log               | No                       | Show a screenshot in slides
Data refresh cadence    | No                       | "Nightly" is what you say
Second data source      | No — narrate it          | "Assume this feed lands"
Error handling          | No                       | Happy path only
Performance             | No                       | 2s hardcoded loader is OK
Export to Excel         | Yes if they'll ask       | Otherwise seed one file
Permissions model       | No                       | One role, one view
```

Rule of thumb: for a 30-minute demo, expect at most three surfaces to get clicked. Instrument those three; paint the rest.

The counter-rule: **write down every fake.** A single file, `FAKES.md`, listed by surface. When the champion asks "does auth actually work?" three weeks later, you want to answer honestly in ten seconds. Losing track of what's real is how pilots die at production handoff.

## FIELD NOTES

- The customer *will* ask "is this the real data?" during the demo. The correct answer is a specific slice — "this is your Q3 export from the sandbox we got Tuesday" — not a marketing yes. Vague yeses are how you lose the room mid-demo.
- Never demo something you built that morning without a rehearsal. The failure mode isn't a bug; it's you looking surprised. Surprise is worse than a bug.
- If security is in the room, they will fixate on the fake boundary. Get ahead of it: "we've hardcoded a user for demo purposes; the SSO flow is on the sequence we sent your IAM team last week." Named, dated, defused.
- The demo bar creeps up every meeting. What you faked in week 2 you must build for real by week 6, or the same fake will bite you when a new stakeholder joins the call. Keep the FAKES.md and burn it down.

## INTERVIEW ANGLE

FDE interviewers probe judgment about scope, not craftsmanship. They want to see you pick the right surfaces to make real.

Sample questions:

1. "You have 48 hours to demo an anomaly-detection pipeline to a customer's CFO. What do you build for real, what do you fake?" (Testing: the CFO cares about the number and the workflow that reads it. Real: detection logic on their data, dashboard showing anomalies. Fake: auth, refresh cadence, secondary sources, alerting.)
2. "A stakeholder asks mid-demo whether the SSO flow works. Walk me through how you answer." (Testing: honesty + composure. Named, dated, defused. Not a marketing yes.)
3. "What's the risk of a demo that's too polished?" (Testing: understanding that a too-polished demo raises expectations you can't meet at handoff — the pilot dies at production because the fakes have to become real all at once.)

## DRILL

Take a demo you have given or seen. Reconstruct it as the two-column checklist above. For every row that landed in "faked," write one sentence: what would have to become real for production, and how long that takes. If any row would take longer than one week, that's your first production risk — flag it in a `FAKES.md` you can hand to the next engineer. Keep the file. You will start every pilot with a blank one from now on.
