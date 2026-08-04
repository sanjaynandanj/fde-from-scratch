# Objection Handling: "Our Data Is Different", "Security Won't Allow It"

**Phase 7 · Lesson 06 · ~1h**

## PROBLEM

A discovery call with an insurance carrier. Twenty minutes in, after the FDE describes what a working pilot could look like, a senior VP leans back and says: "look, no offense, but our data is different. Everything I've ever seen from vendors doesn't work here. You've never seen a book of business like ours." The FDE, wanting to be respectful, agrees, says "of course, we'd need to look at your specifics," and moves on. Two weeks later he learns the VP walked out of that call telling his peers "another vendor who doesn't understand insurance." The engagement never recovers. The objection wasn't a fact; it was a test. And the FDE failed it by treating it as one.

Objection handling is not persuasion. It is the specific move of taking a defensive statement, extracting the real concern behind it, and answering *that* concern with evidence — without making the objector feel stupid.

## INTUITION

Every recurring enterprise objection is a mask over a real concern. Three that you will hear every engagement:

- **"Our data is different."** The mask. The real concern: "I don't want to look foolish sponsoring something that fails, and I've seen vendors underestimate our messiness." The right move is not to disagree — it's to *validate* the messiness and demonstrate you've handled it before.
- **"Security won't allow it."** The mask. Real concern: usually one of (a) "I don't want to fight my own security team," (b) "I don't understand what you're proposing well enough to defend it," or (c) actual security constraints that are entirely legitimate. Each requires a different response.
- **"We tried this before, it didn't work."** The mask. Real concern: "I don't want to be the person who greenlit the same failure twice." The right move is to name what was different last time and *invite them to gatekeep the pivot*.

The general pattern: acknowledge → reframe as a shared problem → provide a specific piece of evidence → offer a small, verifiable next step. Never argue. Never dismiss. Never let the objection sit unaddressed.

## BUILD IT

The **Objection Playbook** — one page per recurring objection. Standard format:

```
OBJECTION: [verbatim phrase you'll hear]
REAL CONCERN (usually): [what they actually worry about]
DO NOT: [the tempting wrong move]
INSTEAD:
  1. Acknowledge — one sentence, no "but"
  2. Reframe — turn it into a shared question
  3. Evidence — a specific artifact or story
  4. Small next step — a verifiable thing you can do this week
FOLLOWUP: [one-line email you send within 24h]
```

Filled examples:

**"Our data is different."**
- Real concern: I don't want to be embarrassed by a vendor who underestimates our mess.
- Do not: agree glibly and move on; over-promise; describe how flexible your system is.
- Instead:
  1. "Absolutely — every book we've seen has its own quirks, and I'd rather find yours in week one than week ten."
  2. "Can we look at one messy example together right now? I'd rather see it than guess."
  3. Show a screenshot of the worst schema you've handled — dates in 14 formats, mixed encodings — with the code that resolved it.
  4. "Give me read access to a sample table by Friday. I'll return a profile of it Monday, no commitments."
- Followup email: "great chat — attaching the schema-profile output from the last engagement I mentioned; ready to run this on your data whenever access is provisioned."

**"Security won't allow it."**
- Real concern: I don't want to fight my own security team on your behalf.
- Do not: promise it will be fine; badmouth security teams; propose exceptions.
- Instead:
  1. "That's the right instinct — I'd rather work with your security team from day one than around them."
  2. "Would it help if I sent you our security package now, so you can circulate before we ask for anything?"
  3. Have a ready-made security one-pager (data flow, credentials, logging, redaction, compliance certs) and offer it in the meeting.
  4. "Can you introduce me to the security lead this week? Even a 20-minute intro call gets us moving."
- Followup email: "as promised, our security one-pager attached; happy to be introduced to [name] whenever works."

**"We tried this before, it didn't work."**
- Real concern: I don't want to sponsor the same failure twice.
- Do not: dismiss the previous vendor; claim you're better; ask for the postmortem in the meeting.
- Instead:
  1. "That's really valuable context — most engagements fail for one of two or three specific reasons, and I'd want to know which one hit you."
  2. "What broke — the data, the adoption, the accuracy, the deployment?"
  3. Whatever they say, show a specific mechanism you have for that failure mode (e.g., "we deploy behind a feature flag with a rollback command that a non-engineer can run").
  4. "Can I see the postmortem or talk to the person who ran the previous effort?"
- Followup email: names, next steps, and one paragraph on what would be different this time.

Build a page for every objection you hear more than twice. This is your career-long asset.

## FIELD NOTES

- The objection is rarely from the person you're in the room with. It's usually a quote from someone up their chain, being tested on you. Answer it in language the up-chain person will believe.
- Never say "no, that's wrong." Say "here's what we've seen." Data over debate.
- Silence after an objection is powerful. Wait. Often they'll un-object themselves ("well, I guess we could try a limited scope…").
- The best objection handling happens *before* the objection. Preempt "our data is different" in your intro by saying "every book of business we've seen has quirks — what should I know about yours upfront?"
- Some objections are actually correct. When "security won't allow it" is true, respect it and change your architecture. Fighting a legitimate constraint is how you lose a security team forever.

## INTERVIEW ANGLE

Behavioral rounds probe this heavily — it's a proxy for whether you can survive a hostile stakeholder without losing the room.

Sample questions:

1. *"A customer VP tells you 'our data is different, this won't work.' What do you say?"* — Strong answers acknowledge the real concern (embarrassment), don't argue, and propose a small verifiable step. Weak answers describe the flexibility of the tech.
2. *"Tell me about a time you got a hard 'no' from a stakeholder and turned it around."* — STAR probe. Best stories show that you didn't argue, you diagnosed the real concern and returned with a small demonstration.
3. *"When is an objection actually correct and you should listen?"* — Tests judgment. They want to hear you distinguish reflexive skepticism from real constraints (legitimate security, regulated data, prior failures with a diagnosed root cause).

## DRILL

Write Objection Playbook pages for three objections you have heard (in customer, sales, or interview settings): the verbatim phrase, the real concern, the wrong move, the right four-step response, and the 24-hour followup. Then role-play them with a friend: they read the objection in a hostile tone, you respond. Repeat until the response feels natural without notes. The muscle memory is the point.
