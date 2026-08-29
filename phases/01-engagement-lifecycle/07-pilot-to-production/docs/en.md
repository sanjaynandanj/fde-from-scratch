# From Pilot to Production: The Re-Architecture Conversation

**Phase 1 · Lesson 07 · ~1h**

## PROBLEM

A pilot succeeds. The metric moved. The exec sponsor loved the demo. The champion is celebrating. The FDE team, exhausted, rolls straight from pilot into production, extending the pilot codebase — SQLite, one Python file, hardcoded creds, no tests. Six weeks later production is on fire. The nightly job silently drops rows. The auth "works" but doesn't map to the customer's SSO. The one senior FDE who wrote the pilot leaves for another engagement and no one can debug the pipeline. The customer files a support ticket that reads "the product is broken." Renewal is now on the line, over a system whose *pilot* they loved. The FDE team paid for skipping the re-architecture conversation.

The pilot codebase is not the production codebase. Not because the pilot was bad, but because it was optimized for a different objective. Rewriting the boundary between them is a conversation you have with the customer, not a decision you make in silence.

## INTUITION

A pilot is optimized for time-to-value against a narrow slice. Production is optimized for reliability, scale, security, and operability. These objectives don't just imply different code — they imply different *ownership models*, different *cadences*, and different *SLAs*. The transition needs to be explicit, both internally and with the customer.

Three questions structure the re-architecture conversation:

**1. What do we keep, what do we rewrite, what do we retire?** The pilot has three kinds of code: things that worked and should be preserved (usually: the core algorithm, the data model, the user-facing workflow); things that were shortcuts that must be rewritten (usually: auth, storage, ingestion, error handling); things that were built for one-off demos and must be retired (seeded data, mock integrations, ad-hoc scripts).

**2. Who runs it?** In pilot, the FDE runs everything. In production, someone else has to be able to. Is it the customer's platform team? A managed offering from your side? A hybrid? Each answer implies different requirements: docs, runbooks, monitoring surface, on-call structure.

**3. What is the SLA and who pays for it?** Pilots have no SLA. Production has one, whether or not you sign it. "Business hours, 99.5%, recovery under 4 hours" costs different money than "24x7, 99.9%, 15-minute RTO." The customer needs to pick, and pay accordingly.

The conversation typically lands 2–3 weeks after pilot exit, once the customer's champion has internally sold "we want to keep this." You come in with a menu, not a plan. The customer picks from the menu; you write the plan.

## BUILD IT — the pilot-to-production memo

Draft this doc at pilot exit. Send it to the exec sponsor. Walk through it in a 60-minute meeting with the champion, IT lead, and (if identified) the production owner.

```
PILOT-TO-PRODUCTION MEMO — <pilot name>

WHAT THE PILOT PROVED:
  Metric: moved from <baseline> to <achieved> — target was <target>
  Users: <n> people ran the workflow <m> times over <weeks>
  Confidence in the result: <high/med/low, and why>

WHAT THE PILOT DID NOT PROVE (candidly):
  - <e.g., "scale beyond one region">
  - <e.g., "integration with production SSO">
  - <e.g., "behavior under real error conditions">

RE-ARCHITECTURE PROPOSAL:

  KEEP (works, is production-shape):
    - <algorithm / data model / API contract>

  REWRITE (shortcut in pilot, real in production):
    - Auth: <SSO integration path>
    - Storage: <SQLite -> managed Postgres / warehouse>
    - Ingestion: <ad-hoc -> scheduled, idempotent, watermarked>
    - Observability: <print statements -> structured logs + metrics>
    - Deploy: <local -> container in your VPC / our tenant>

  RETIRE (was for the pilot only):
    - Seeded demo data
    - Mock connectors
    - Hand-tuned per-user configs

OPERATIONAL MODEL — pick one:
  [ ] Fully managed by us (SaaS-style)
  [ ] Deployed in your VPC, we operate
  [ ] Deployed in your VPC, you operate, we support
  [ ] On-prem, you operate, we support

SLA MENU — pick one:
  [ ] Bronze: business hours, best effort, monthly report
  [ ] Silver: 12x5, 99.5%, weekly report, 8h RTO
  [ ] Gold:  24x7,  99.9%, real-time alerts, 1h RTO

TIMELINE:
  Week 1-2: SSO + storage rewrite
  Week 3-4: ingestion + observability
  Week 5-6: security review + IT approvals
  Week 7-8: parallel run against pilot
  Week 9:   cutover
  Week 10-12: hypercare (elevated FDE presence)

WHAT WE NEED FROM YOU:
  - Production data access (see access battle plan v2)
  - Named production owner
  - SSO integration slot with your IAM team
  - Security review kickoff
  - Signed SLA and updated MSA
```

The memo is doing three jobs at once: (a) declaring pilot success in writing so the win is banked, (b) being honest about what the pilot didn't prove so surprises later aren't political, and (c) forcing the customer to *make choices* about op model and SLA rather than defaulting to "just make it work like the pilot."

## FIELD NOTES

- The re-architecture conversation is easier with a customer who understands they need to invest. Some don't — they think "the pilot works, just make it production." When you hit this, the memo above becomes essential. It reframes production as their decision, not your gold-plating.
- Parallel run is worth the cost. Two to four weeks of running the new architecture alongside the pilot, with reconciliation of outputs, catches 80% of surprises before they hit users. Budget for it.
- Hypercare is a real line item. The first 2-4 weeks after cutover need elevated FDE presence — daily standups, faster response, someone on call. Bill for it or you'll burn out.
- The champion may not survive the transition. Their political win was the pilot, not the production system. Identify the production owner early — often a different person in IT or ops — and start building that relationship before cutover.
- Retire the pilot artifacts explicitly. Delete the SQLite file. Kill the demo URL. Announce the retirement. Zombie pilot infrastructure that "still works" becomes tech debt and confusion for the customer's team.

## INTERVIEW ANGLE

The pilot-to-production transition is a favorite system design question in FDE loops, especially at Palantir and Anthropic. Interviewers want to see structured thinking about *change*, not just about steady-state architecture.

1. "You ran a successful 30-day pilot on SQLite with one file. The customer wants to go to production for 500 users across three regions. Walk me through the plan." (They want: keep/rewrite/retire framing, explicit op model choice, SLA menu, parallel run, hypercare.)
2. "How do you have the conversation when the customer thinks production is 'just deploy the pilot'?" (They want: written memo, honest about what the pilot didn't prove, force choices via a menu, quantify the cost of each SLA tier.)
3. "What's the biggest risk in the pilot-to-production transition?" (They want: pick one — often "the customer changes ownership without change management," or "SLA committed without ops capacity" — and defend it.)

## DRILL

Take your pilot from earlier lessons. Write the pilot-to-production memo. Force yourself to make the "what the pilot did not prove" section honest. Draft the operational-model menu and pick the option you'd recommend. Write the two-paragraph message you'd send to the exec sponsor to request the 60-minute re-architecture meeting. Save this — it maps directly to Capstone 6 (Production handoff pack).
