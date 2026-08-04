# Anatomy of an Engagement: Discovery to Handoff

**Phase 1 · Lesson 01 · ~1.5h**

## PROBLEM

An FDE lead we'll call Priya inherits a stalled engagement at a regional insurance carrier. The kickoff was five months ago. There is a slack channel, a github repo with 11k lines of Python, and a customer champion who won't return calls. When Priya asks the outgoing FDE what phase the engagement is in, he says "we're kind of in production but also still doing discovery, and the pilot never really ended." That sentence is the diagnosis. The engagement had no anatomy — no crisp transitions between phases, no artifact that marked the end of one phase and the start of the next — so every meeting relitigated scope, every new requirement got absorbed into "the pilot," and the customer's exec sponsor stopped believing anything was ever going to ship. Priya's first job isn't to write code; it's to name what phase they're in, out loud, in front of the customer, and force the transition.

The engagements that die don't die from bad code. They die from phase confusion.

## INTUITION

An engagement has four phases, and each phase has one job. If you can't name the job of the current phase in one sentence, you are in phase drift.

**Discovery (weeks 0–2).** Job: find the single metric that, if moved, gets the contract renewed. Not "understand the business." Not "map the systems." Find the number. Everything else in discovery is in service of finding that number and the human who owns it.

**Pilot (weeks 2–8).** Job: move that number, on the customer's real data, in a way the customer's exec can see. Pilots that skip real data are demos, not pilots. Pilots that skip exec visibility are science projects. Pilots that skip a deadline are zombies.

**Production (weeks 8–20).** Job: harden the pilot into something the customer can run without you present in every meeting. This is the phase most FDEs underestimate — the code you wrote for the pilot is 30% of what production needs. The other 70% is auth, monitoring, retries, backfills, DR, docs, and the security review you dodged in month one.

**Handoff (weeks 16–24).** Job: make yourself unnecessary. If leaving would break the customer, you have not finished the engagement — you have created a hostage situation, and the renewal conversation next year will be brutal because the customer will resent needing you.

The phases overlap in calendar but not in intent. On any given Tuesday you might be doing production hardening on feature A, pilot iteration on feature B, and fresh discovery on feature C. That's fine — as long as you can name which phase each thread is in.

## BUILD IT — the engagement one-pager

Every engagement you run gets a one-page living doc with this exact shape. Copy this template into your notes now.

```
ENGAGEMENT: <customer> — <product line>
PHASE: [ ] discovery  [ ] pilot  [ ] production  [ ] handoff
PHASE START DATE: <date>       PHASE EXIT CRITERIA: <one sentence>

THE METRIC:
  <the single number that gets renewal signed>
  Baseline: <value>   Target: <value>   Owner (customer-side): <name>

THIS WEEK'S ARTIFACT:
  <what the customer will see this Friday>

STAKEHOLDERS:
  Champion: <name, title, why they care>
  Economic buyer: <name, title, budget authority>
  Blocker: <name, title, what they can block>
  End user: <name, title, day-to-day pain>

BLOCKERS:
  [ ] <what is blocking, who owns unblocking, promised date>

NEXT PHASE TRIGGER:
  <the specific event that moves us to the next phase>
```

Fill this out for a real or hypothetical engagement now. If any field is blank, that blank is your next action. The most common blank in stalled engagements is *phase exit criteria* — no one wrote down what "done with pilot" means, so pilot never ends.

## FIELD NOTES

- Phase transitions need a ceremony. A written email, a signed doc, a slide the exec approves. Without ceremony the customer's team will keep treating the pilot like it's still open for scope. "Pilot exit memo" — three paragraphs, sent to the exec sponsor, cc'ing the champion — is the cheapest ceremony that works.
- The champion changes jobs. Assume it. When your champion gets promoted, poached, or moved to a different BU, your engagement stalls for 4–8 weeks unless you have a second relationship pre-built. Every phase, name a backup champion.
- Consultants show up in production phase. Deloitte / Accenture / whoever will be brought in "to help with change management." They are not your enemy but they will slow you down. Treat them as a stakeholder; give them a role; do not let them own the runbook.
- Legal wakes up at the phase boundaries. DPA revisions, MSA amendments, and the security addendum will land the week you're trying to demo the pilot exit. Schedule legal review to *start* two weeks before the phase transition, not on the day of.

## INTERVIEW ANGLE

Interviewers use this topic to test whether you think structurally about customer work or whether you just do whatever's in front of you.

1. "Walk me through the phases of a customer engagement and the job of each." (They want: crisp one-sentence job per phase, exit criteria, not textbook consulting language.)
2. "You inherit an engagement that's been running for six months with no clear success criteria. What do you do in your first week?" (They want: name the phase confusion, force an artifact, get the metric written down and agreed to.)
3. "How do you know when a pilot is over?" (They want: exit criteria defined at pilot start, not judged at pilot end — and a ceremony that marks the transition.)

## DRILL

Take a project you've been part of — internal or external. Reconstruct its engagement anatomy. When did discovery end? What was the pilot exit criteria (was there one)? Did the production phase actually happen or did you skip to hoping? Was there a handoff, or are you still the only person who can operate the thing? Write a one-paragraph postmortem naming the phase where the engagement was weakest, and one artifact that would have fixed it. Save this — you'll reuse the format in the Phase 11 capstone.
