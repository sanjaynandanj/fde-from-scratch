# Scoping: The Pilot That Proves Value in 30 Days

**Phase 1 · Lesson 03 · ~1.5h**

## PROBLEM

A global bank signs a six-figure pilot with an FDE team. The customer's sponsor wants "an AI copilot for our credit analysts." The FDE lead, eager to please, agrees to a scope that includes: document ingestion across six deal-room systems, entity resolution for counterparties, a chatbot UI, integration with the risk data warehouse, and a fine-tuned model. Timeline: 30 days. On day 21, nothing works end-to-end. On day 30, they demo a mock with hand-picked data. On day 45, the sponsor's boss cancels the project because "it doesn't do anything real." The FDE team wrote clean code. They just scoped a six-month project into a 30-day window and everyone politely watched it fail.

30-day pilots don't fail because engineers are slow. They fail because the scope was set by someone who didn't have to build it.

## INTUITION

A 30-day pilot is a promise: on day 30, a specific customer-side human will look at working software running on their real data and be able to answer the question *did the metric move?* — yes or no. Every scoping decision serves that promise.

The math of scoping is unforgiving. You have roughly 20 working days. Subtract 3 for access battles that will happen. Subtract 2 for the security review that will land unexpectedly. Subtract 3 for demos and status calls. Subtract 2 for the one thing that always breaks (encoding, a schema change, a person going on leave). You have ~10 real build days. Everything you scope must fit in 10 days *of construction against a moving target*.

The right shape of a 30-day pilot is:

- **One user, one workflow, one metric.** Not a platform. Not a copilot. A single workflow, end-to-end, for one persona, moving one number.
- **Real data, narrow slice.** One quarter of one region's data is better than "all data." You want data that is real enough to be defensible and small enough to be tractable.
- **Boring stack.** SQLite, a Python script, one HTML dashboard. Anything that requires infrastructure approval is not in scope. If it needs a Kubernetes cluster, it's a production project pretending to be a pilot.
- **Weekly demoable.** Every Friday of the pilot, something works that didn't work last Friday. If your build plan has "week 3: integration," week 3 has no demo, and you're one bad week from invisible.

The wrong shape looks ambitious and rigorous. It has architecture diagrams, phases within phases, and words like "foundation." Foundations are month-6 problems. Move the metric first.

## BUILD IT — the 30-day pilot scoping template

```
PILOT SCOPING DOC — <customer> — <pilot name>
DATES: <start> to <end>   DEMO SCHEDULE: every Friday, 30 min

THE PROMISE (one sentence, exec-readable):
  On <end date>, <persona> will use <artifact> against <data slice>
  and we will measure <metric> moving from <baseline> toward <target>.

IN SCOPE (exhaustive — if it's not here, it's not happening):
  1. <workflow step>          — build days: <n>
  2. <workflow step>          — build days: <n>
  3. <dashboard / artifact>   — build days: <n>
  Total build days budgeted:  <sum, must be <= 10>

EXPLICITLY OUT OF SCOPE (write these down; you will be asked):
  - <thing customer wants but not in this pilot>
  - <integration deferred to production phase>
  - <persona not being served in this pilot>

DATA SLICE:
  Source system: <name>       Extract format: <CSV / SQL / API>
  Volume: <rows / MB>         Time window: <e.g., Q1 2026, US only>
  Access owner: <name>        Access confirmed date: <blank until confirmed>

WEEKLY MILESTONES (each is demoable):
  W1 Fri: <thin end-to-end skeleton against sample data>
  W2 Fri: <real data flowing, baseline number visible>
  W3 Fri: <first real workflow lever exposed to user>
  W4 Fri: <metric measured, exec-facing readout>

EXIT CRITERIA (customer signs at pilot end):
  [ ] <persona> ran <workflow> at least <n> times
  [ ] <metric> was measured pre and post
  [ ] Written go/no-go decision from <exec sponsor>
```

Fill this out for a plausible pilot. Notice the forcing functions: 10 total build days, out-of-scope list you commit to in writing, weekly demoable milestones, exit criteria signed by a specific human. When customers push scope, you point at the doc — not to fight, but to help them make a real trade-off.

## FIELD NOTES

- The scoping conversation is a *negotiation*, not a transcription. Customers ask for what they want. Your job is to translate that into what will fit and still be worth the pilot fee. "We can do A or B in 30 days, not both. Which one is the readout your CFO wants to see?"
- Never quote scope in features. Quote scope in *what the user can do on day 30*. "Analyst can pull a counterparty exposure summary in under 60 seconds against last quarter's book" beats "counterparty exposure summary feature."
- The exec sponsor should sign the scoping doc — literally, an email reply saying "yes, this is what we want." Without that sign-off, week 3 will bring a surprise stakeholder who "just wants one more thing."
- Change requests during the pilot are answered with a menu: "yes, and we drop X" or "yes, and it lands after pilot exit." Never "yes, and we'll try to fit it in." Trying is how zombie pilots start.
- If the customer refuses to narrow scope, that's diagnostic. Either their exec doesn't back the pilot or the pilot is politically a check-the-box exercise. Both are bad news; both are better to know in scoping than in week 3.

## INTERVIEW ANGLE

Scoping is one of the highest-signal questions in FDE loops. Interviewers want to see you cut, prioritize, and negotiate in real time.

1. "The customer wants a full document Q&A platform. You have 30 days. Walk me through how you scope it." (They want: pick one persona, one document type, one query pattern; boring stack; weekly demoable; explicit out-of-scope list.)
2. "The champion asks you to add three features mid-pilot. What do you do?" (They want: menu of trade-offs, written scope change, exec-visible; not silent absorption.)
3. "How do you decide what to cut when the pilot slips?" (They want: cut breadth before depth — one workflow that fully works beats three half-workflows; preserve the metric readout above all.)

## DRILL

Take the discovery output from Lesson 02's drill. Turn it into a 30-day pilot scoping doc using the template above. Force yourself to fit the build into 10 days. What did you cut? What went into "explicitly out of scope"? What are the four weekly milestones? Now imagine the champion asks in week 2 to add a fourth workflow — write the two-line email response that offers a menu instead of a yes. This artifact and email pattern reappears verbatim in Lesson 10 and Capstone 1.
