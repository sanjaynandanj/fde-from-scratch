# Working the Org: IT, Security, Legal, and the Intern Who Knows Everything

**Phase 7 · Lesson 08 · ~1h**

## PROBLEM

Week two at a global manufacturer. The FDE has met the business champion, the users, and the two directors above them. Everything is going great — until Friday afternoon, when he learns that the IT ticket for warehouse read access was closed as "insufficient business justification" on Tuesday and no one told him. The FDE emails IT. No response. He escalates to the champion, who emails IT. No response. He asks the champion who runs IT. She says "I'm not sure, we usually just… submit tickets." Meanwhile the security team, whom nobody has met, has flagged the project in a weekly risk review. Legal is drafting language for the DPA that would prohibit the exact workflow the pilot is built around. And an intern in the data team — who has been on the project's shared Slack channel silently for three weeks — knows exactly who to call at IT because his uncle works there. Nobody thought to ask him.

The org is a system. You will not win by pretending it's just your champion.

## INTUITION

Every enterprise has three horizontal functions that will touch your engagement whether you invite them or not — IT, security, and legal — plus a class of high-context low-title people who know how the org actually works. Getting to them early is not politics; it's engineering.

The mental model: each function has a *stated concern*, an *actual incentive*, and a *fast path* through it. Learn all three per function:

- **IT** — Stated: uptime, standards. Actual: not getting yelled at when something breaks; being brought in early rather than late. Fast path: one named human, briefed weekly, treated as a partner.
- **Security** — Stated: policy compliance. Actual: not signing off on something that later becomes a headline. Fast path: give them the security package before they ask; propose scoped-down defaults.
- **Legal** — Stated: contract enforceability. Actual: minimizing novel language they have to defend to their boss. Fast path: use their template if any exists; give them a redlined starting point rather than a blank slate.
- **The high-context low-title people** — analysts, executive assistants, veteran developers, interns from data. They know who is on vacation, whose ticket to skip, which VP is about to leave. Cultivate them like collaborators; they will save your engagement.

## BUILD IT

The **Org-Working Playbook** — a per-engagement doc with four blocks. Fill it out in week one.

```
IT
  Primary contact: [Name, title, email, backup contact]
  How I met them: [meeting / intro / cold email / champion introduction]
  What they need from us: [security package? architecture doc? change tickets?]
  Cadence: [monthly 15-min check-in]
  Open tickets: [list with numbers and dates]
  Watch-outs: [known standards, e.g., "no direct DB access, must go through gateway"]

SECURITY
  Primary contact: [Name, backup]
  Formal review stage: [none / in progress / passed / conditional]
  What they've asked for: [checklist]
  Our security one-pager: [link, version, last-updated]
  Standing agreement: [any pre-approved patterns, e.g., "read-only access to warehouse OK"]
  Watch-outs: [regulated data classes, restricted regions]

LEGAL
  Primary contact: [Name, backup]
  Active documents: [DPA, MSA, SOW, order form — status of each]
  Redline history: [where we conceded and where they conceded]
  Watch-outs: [specific clauses they always push, novel language they always block]

HIGH-CONTEXT LOW-TITLE PEOPLE
  [Name, role, why they matter, what they know]
  [Name, role, why they matter, what they know]
  [Name, role, why they matter, what they know]
  (Aim for 3-5 by week two. Coffee, not calendars.)

DECISION AUDIT
  Every function-level decision that could affect the pilot, dated:
  - [date] [function] [decision] [source] [implication]
```

Rules:

- One named human per function. "The security team" is not a contact.
- No ticket is submitted without a named human copied on the summary. Tickets die in queues; humans respond.
- Every function meeting has a written followup, sent within 24h, that becomes the record of agreement.
- The "high-context low-title" section is where you note names your champion never mentioned. If it's empty in week three, you don't know the org well enough.

## FIELD NOTES

- Ask your champion: "who at IT / security / legal do you already have a good relationship with? Can you introduce me?" A warm intro is worth ten cold tickets.
- Bring coffee. Physically. On-site, in-person, in the break room. This sounds absurd until you see how much easier your next ticket moves.
- Never surprise IT or security with an ask. Warn them in a low-stakes conversation two weeks before you need something. Ambush requests get "no" by reflex.
- The intern who knows everything is often the child or friend of a mid-level manager. They see the org sideways. Take them seriously — they will end up running a team in three years.
- Legal will move slowly for reasons that have nothing to do with you. Do not personalize the delay. Reduce it by giving them clean, familiar drafts.
- Every function has an *ally* — someone inside who quietly agrees with you and can nudge things along. Find them.
- Security teams that say "no" broadly often say "yes" specifically. "Can we deploy in your VPC with read-only access to a redacted table?" gets a different answer than "can we deploy AI?"

## INTERVIEW ANGLE

FDE loops at every serious enterprise-AI shop probe your instinct for cross-functional politics. Interviewers want to see that you know the org exists and treat it as engineering surface area, not annoyance.

Sample questions:

1. *"Your champion is great but security has stalled your project for four weeks. What do you do?"* — Strong answers: identify who at security is actually reviewing, ask for a direct meeting, offer to redesign the ask, bring the champion in as air-cover rather than an intermediary.
2. *"Who's the first person you'd get coffee with at a new customer site, outside your champion's org?"* — Tests org intuition. Great answers name a specific archetype (an executive assistant, an analyst, a veteran IT person) and the reason.
3. *"Tell me about a time a low-level employee changed the trajectory of a project."* — STAR probe. They want stories where you paid attention to someone with tacit knowledge and it saved you weeks.

## DRILL

Take an engagement (real or from Phase 1). Fill out the Org-Working Playbook in full. In the "high-context low-title" section, list at least three real names — if you can't, that's your first assignment: draft the emails or Slack messages you'd send this week to meet them. Then, for one of the three functions (IT, security, or legal), draft the *first message* you'd send to introduce yourself — cold, warm, or via intro — under 120 words. Read it aloud. Is it a request, or is it a relationship-opener? Rewrite until it's the second one.
