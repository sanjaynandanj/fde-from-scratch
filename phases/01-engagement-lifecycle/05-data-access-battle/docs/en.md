# The Data Access Battle: Getting Credentials Before Week 3

**Phase 1 · Lesson 05 · ~1h**

## PROBLEM

An FDE at a healthcare payer starts an engagement Monday. Kickoff goes well. The exec sponsor says "our team will get you access to the claims warehouse this week." On Wednesday she asks the customer's engineering lead for the credential. He says he'll open a ticket. Friday she checks — the ticket is with security. The following Wednesday, security says they need a data classification review. The Friday after that, classification says they need an executed BAA amendment. The BAA amendment is with legal. Legal is out for two weeks. It is now day 24 of a 30-day pilot and she has never seen a claim record. She spent the entire pilot writing beautiful code against synthetic data that turns out to have none of the messiness of the real data. On day 30 she demos synthetic. The customer's reaction is polite and terminal.

The pilot didn't fail because of the code. It failed on day one, when access wasn't treated as the critical path.

## INTUITION

At every enterprise, real data access is gated by a chain of humans who each have veto power and no incentive to move fast. The chain typically looks like: data owner → IT → security → compliance → legal → procurement. You need "yes" from every link. Any one of them saying "let me get back to you" adds 3–10 business days.

Access is not an IT problem. It is the primary risk on your engagement. Treat it accordingly.

Three principles:

**1. Start the access chain on day zero.** Before the kickoff deck is finished, before the scope is signed, you are asking who owns access, what the chain is, and what artifacts (DPA, classification, BAA, SIG questionnaire) they will need from you. The single highest-leverage day in the engagement is the day *before* it starts.

**2. Human, not ticket.** Tickets sit. Humans move when other humans stand next to them. Every link in the chain has a specific human whose fingertip on a keyboard unblocks you. Find them, get on their calendar, and *stay* on their calendar until they've done the thing.

**3. Have a working plan B for every day of blockage.** Synthetic data that mimics real messiness. Read-only exports. Screen-shared browsing of the real system with a customer-side employee driving. Anything that keeps you in contact with data-shaped problems while the credential chain runs.

The failure mode is quiet. You send a Slack, they say "working on it," you build against synthetic, and nobody escalates until it's too late. Access debt compounds silently and reveals itself only when the demo can't handle real inputs.

## BUILD IT — the access battle plan

Fill this out on day 0. Update it weekly. Escalate any row stuck in the same state for 5 business days.

```
ACCESS BATTLE PLAN — <customer> — <pilot>

SYSTEMS NEEDED (be specific — table names or endpoints):
  1. <system> — read-only for <tables/endpoints>  — WHY: <what pilot step needs it>
  2. <system> — <access type>                     — WHY: <...>
  3. <system> — <access type>                     — WHY: <...>

FOR EACH SYSTEM:

  System: <name>
  Data owner (customer-side): <name, title, contact>
  Approval chain: <owner> -> <IT> -> <security> -> <compliance> -> <legal>
  Artifacts they'll require from us:
    [ ] Data classification form
    [ ] DPA / BAA / addendum
    [ ] Security questionnaire (SIG / CAIQ)
    [ ] Named users on our side
    [ ] VPN / bastion / IP allowlist config
  Current state (updated weekly): <name of human currently blocking>
  Days blocked: <n>
  Escalation trigger: <n days> -> escalate to <sponsor>
  Fallback if not unblocked: <synthetic, extract, screen-share, sample dump>

DAY-30 ACCESS FLOOR (minimum needed to demo on real data):
  - <the smallest access subset that lets the pilot show real value>

STANDING WEEKLY ACCESS SYNC:
  Attendees: <FDE lead, customer IT lead, champion>
  Purpose: 15 min, walk each row, name the human who unblocks each
```

Notice the "Day-30 access floor" row. Not everything has to unblock — you just need the minimum viable access subset to hit the pilot's promise. Ranking access matters more than requesting it.

## FIELD NOTES

- The customer's data team is not being obstructionist. They've been burned by vendors before, or their manager is measuring them on breach risk, or they simply have 30 other things on their queue. Treat them as a partner, learn their pressures, offer to write the classification form yourself for them to review.
- The BAA / DPA / addendum trap is real. The template your sales team signed at contract time often doesn't cover the specific data you're about to touch. Get the *right* legal artifact identified in week 1, not the week you need the data.
- Sample dumps are your friend. Ask early for a "10k-row anonymized export to a shared drive" — this is often approvable in days when live access takes weeks, and it gives you real messiness to code against.
- Watch for surprise systems. The champion says "just the claims warehouse" — but the workflow requires enrichment from the member database, the provider directory, and last quarter's DRG codes. Discovery of surprise systems in week 3 is common. Ask "what other systems does this workflow touch?" in every discovery interview.
- Never accept a shared credential. If IT hands you "here, use jsmith's login," refuse. It's a compliance landmine and a legal problem waiting. Named service accounts scoped read-only or bust.

## INTERVIEW ANGLE

Access battles come up in behavioral rounds and in scenario questions. Interviewers want to see that you take access seriously and have concrete tactics.

1. "You're on day 10 of a 30-day pilot and you still don't have data access. What do you do?" (They want: named escalation path, plan B on synthetic or export, weekly access sync, and a written note to the exec sponsor naming the risk.)
2. "How do you convince a nervous IT team to give you access?" (They want: understand their risk, offer scoped read-only, come with the paperwork pre-filled, propose a named service account, not a plea for trust.)
3. "What's the earliest an FDE should start worrying about access?" (They want: before the engagement starts — in the sales/scoping phase — because the chain takes weeks and can't be parallelized.)

## DRILL

Pick a system you've worked with (a warehouse, a SaaS API, a legacy ERP). Reconstruct the plausible access chain to get read-only production access as a vendor. Who's the data owner? What's the IT gate? What compliance artifact would legal want? Fill out the access battle plan for a hypothetical 30-day pilot against this system. Now identify the "Day-30 access floor" — the smallest subset of tables/endpoints that would still let a pilot prove value. This is the ranking exercise you'll do live on real engagements.
