# Handoff: Runbooks, Training, and Making Yourself Unnecessary

**Phase 1 · Lesson 08 · ~1h**

## PROBLEM

Two years into a Palantir-style engagement at a global bank, the FDE lead is famous internally. Every incident routes to her Slack DM. She knows which cron job runs at 3am, which analyst's spreadsheet feeds the pipeline, which VP is sensitive about which dashboard tile. The customer loves her. On paper, the engagement is a triumph. In practice, it's a hostage crisis. When the FDE lead tries to rotate off the account, the customer's engineering team can't operate the platform. Two P1 incidents happen in her first week away. The customer demands she come back. She comes back. Renewal happens — but at flat pricing, because the customer is bitter about the dependency they didn't ask for. Her engagement is not a win; it's a trap she built by being too helpful.

If the customer needs you personally to keep the lights on, you have not finished the engagement. You have created technical debt that lives in your head.

## INTUITION

The final phase of every engagement is transferring operational and cognitive ownership to the customer. This is uncomfortable because for months you were rewarded for being indispensable, and now you're being asked to be dispensable. Good FDEs treat handoff as a first-class deliverable with its own artifacts, timeline, and success criteria.

Three assets carry the handoff:

**1. The runbook.** Written for a tired human at 2am with no context. Every alert has a page in the runbook. Every page has: what it means, how to check, how to fix, when to escalate. Not "the codebase is self-documenting." A literal doc with copy-pasteable commands.

**2. The training.** Live sessions with the customer's operational team, hands-on, using the runbook. Not a slide deck. Not a recorded video (though those help). The customer's on-call engineer *runs* an incident drill while you watch and coach. Then they run one without you. Then they run one and you leave the room.

**3. The rotation.** A calendar-committed plan for reducing your presence: weekly → biweekly → monthly → quarterly → off. Each stage has explicit exit criteria (e.g., "customer resolved 3 consecutive incidents without pinging us"). No stage is skipped based on vibes; each is signed off.

The goal is *provable* independence, not asserted independence. The customer's team has to demonstrate operational competence in front of you before you leave. If they haven't, you haven't handed off, no matter how thick the runbook.

## BUILD IT — the handoff pack

Ship this as a package at the start of the handoff phase. It's the last artifact you'll produce for the engagement.

```
HANDOFF PACK — <customer> — <system>

1. RUNBOOK (one page per alert / one page per common task)
   Template for each page:
     ALERT / TASK: <name>
     WHAT IT MEANS: <plain English>
     WHERE TO LOOK: <dashboard URL, log query, command>
     HOW TO FIX: <numbered steps, copy-pasteable>
     WHEN TO ESCALATE: <threshold, to whom, how>
     LAST TIME THIS FIRED: <date, brief history>

2. ARCHITECTURE MAP (one page):
   - Data flow diagram (boxes and arrows)
   - What runs where (host, container, schedule)
   - Auth boundary
   - Backup / recovery mechanism

3. OPERATIONS CALENDAR:
   - Daily: <health check, review overnight alerts>
   - Weekly: <backup verify, cost review>
   - Monthly: <access review, dependency updates>
   - Quarterly: <DR drill, capacity review>

4. CONTACT SHEET:
   - Customer-side owners (primary, backup, exec)
   - Our side (support tier, escalation, account owner)
   - Third parties (SSO vendor, cloud, DB vendor)

5. KNOWN QUIRKS (the things only you know):
   - <"the nightly job takes 3x as long on the 1st of the month">
   - <"user X's dashboard is customized differently, don't touch">
   - <"if the ingestion lags > 2h, restart the connector before paging">

6. TRAINING PLAN:
   Session 1 (60 min): architecture walkthrough
   Session 2 (60 min): runbook walkthrough with role-play
   Session 3 (90 min): supervised incident drill — synthetic alert
   Session 4 (90 min): unsupervised incident drill — you watch, don't help
   Sign-off: customer's ops lead signs a memo that team is ready

7. ROTATION PLAN:
   Weeks 1-2 (post-handoff): daily 15-min sync, you on-call primary
   Weeks 3-4: biweekly sync, customer on-call primary, you backup
   Month 2:   monthly sync, customer full ownership, you consult on request
   Month 3+:  quarterly business review only
   Exit criteria at each stage: <named, measured>
```

The known quirks section is the hidden lever. Every engagement accumulates lore — the specific things only the FDE remembers. Writing them down is often the single most valuable page in the handoff pack, and it's the one FDEs are most tempted to skip because it feels beneath a good engineer.

## FIELD NOTES

- Handoff resistance comes from both sides. You resist because being needed feels good and safe. The customer's ops team resists because they know they're being asked to take on a system they didn't design. Both are normal; both must be pushed through.
- The customer's ops team is not your pilot champion's team. They're a different group with different incentives — often measured on uptime and ticket queue. Build the relationship in the *production* phase, before handoff, or they'll show up cold and hostile.
- Runbooks decay. Ship a "runbook owner" role on the customer side. Someone is responsible for updating it. Otherwise in 6 months it's stale and useless.
- The training is where you find out what's really unclear. If the ops team gets stuck on step 4 of a runbook page, it's not their fault — the runbook is wrong. Iterate.
- Leaving too early is worse than leaving too late. Two false-start handoffs (you leave, get pulled back, leave again) destroys the customer's confidence. Better to overstay by two weeks than to leave and be dragged back.

## INTERVIEW ANGLE

Handoff is a favorite behavioral topic because it tests maturity, not skill. Interviewers want to see that you understand your value is not in being irreplaceable.

1. "Tell me about a time you handed off a system you built to another team. What did you do to make sure it stuck?" (They want: written runbooks, live training, phased rotation, provable independence.)
2. "How do you know when a handoff is complete?" (They want: the customer's team has demonstrated operational competence — not just received documentation. A named milestone: unsupervised incident resolved, or n weeks without escalation.)
3. "You've become the customer's dependency. What do you do?" (They want: acknowledge it as a problem, not a compliment. Concrete plan: identify the dependency surface, docs and drills to transfer it, phased reduction of presence, explicit escalation path for after you leave.)

## DRILL

Take a system you've operated (personal project, work project, this repo's build system — anything real). Write one runbook page for a plausible alert or task. Force yourself to write copy-pasteable commands and to name the "when to escalate" threshold. Then draft the "known quirks" section — the three things only you know that would trip up a stranger. If you can't articulate the quirks, you don't know your system as well as you think. This page format appears in Capstone 6 (Production handoff pack).
