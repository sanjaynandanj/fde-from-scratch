# Drill: Turn a Rambling Stakeholder Email Into a Scoped Sprint

**Phase 7 · Lesson 12 · ~1.5h**

## PROBLEM

11:47pm on a Sunday. The champion's email lands. Subject line: "some thoughts before Monday." Body: 800 words of stream-of-consciousness — the VP wants a dashboard, the merch team hates the current filter logic, someone from finance saw the demo and wants to overlay margin data, the champion is worried about the accuracy on new SKUs, oh and by the way IT mentioned a networking change coming Wednesday, and the exec committee meets Friday and it would be great to show progress. There's no ask. There's no priority. There's no clear question. The FDE opens the email Monday morning and freezes — where does he even start? The junior instinct is to reply "thanks, will look into all of this." The correct instinct is to reply with a *plan* — a scoped sprint distilled from the noise, mirrored back so the champion can nod or correct — before touching a line of code.

This drill is the customer-craft capstone. Everything in Phase 7 shows up in it.

## INTUITION

A rambling email is not a problem to answer; it's a raw input to a process. Your job is to run the process out loud, in writing, back to them:

1. **Enumerate every ask.** Number them. Even the ones that look like context. Sometimes the fifth item is the real request.
2. **Cluster and archetype each ask.** Which are outcome-level ("make it smarter"), which are behavior-change, which are already backlog-item shaped? (See Lesson 03.)
3. **Route each ask.** Some are for you (backlog). Some are for the champion (decision). Some are for IT/security/legal (external). Some are just venting.
4. **Sort by (value × confidence) / effort.** Not by order-in-email. The email order reflects what was on the champion's mind at 11:47pm, not what matters.
5. **Cut ruthlessly.** A one-week sprint fits 3-5 items done well. Everything else gets deferred, delegated, or declined — explicitly, in writing, using the flavors from Lesson 07.
6. **Confirm and demo.** Reply with the plan. Land it as the pre-read for Wednesday's weekly. Ship the demo of the top item by Friday.

The tempo: read Monday 9am, reply with a plan by 11am, work Monday afternoon on item one, demo Wednesday, ship Friday. Never let a Sunday-night email steal Monday morning.

## BUILD IT

The **Rambling-to-Sprint Reply Template** — the exact structure you send back within two hours of receiving one of these emails.

```
Subject: Re: some thoughts before Monday — proposed sprint

Hi [champion],

Big email — thanks for dumping it out. Let me mirror back what I heard so we're aligned before I start swinging.

I counted 7 distinct asks in your note. Grouped:

DO THIS WEEK (in the pilot sprint):
  1. [ask] — [one-line why] — I can have a demo by Wednesday
  2. [ask] — [why] — validating with [named user] by Thursday
  3. [ask] — [why] — targeting Friday deploy

DEFER TO NEXT SPRINT (documented, but not this week):
  4. [ask] — noted; would like your call on whether it displaces one of the above
  5. [ask] — noted; will scope in Friday's readout

ROUTE ELSEWHERE (not our scope):
  6. [ask about IT change] — I'll ping [IT contact] directly, will loop you when I hear back
  7. [ask from finance about margins] — this feels like a Q4 conversation, not pilot scope; want me to send a polite "not now"?

RISKS I NOTICED IN YOUR EMAIL:
- [You mentioned accuracy on new SKUs] — this is the real thing worth solving; I'm putting it as item 1.
- [Exec committee Friday] — I'll send you a one-slide (Lesson 09 format) by Thursday EOD you can drop straight in.

WHAT I NEED FROM YOU:
- Confirm the top-3 above by 11am today, or tell me what I got wrong.
- [Named user] intro so I can validate item 2.
- 15 min Wednesday after the weekly to review the exec one-slide.

Talk soon,
[FDE]
```

Rules:

- Reply within two hours during business time. Speed signals control.
- Number every ask. The champion needs to see you extracted all seven, or she'll assume you missed the one that mattered.
- Show which flavor of no you're using per deferred item. Naming the flavor tames scope creep before it starts.
- Land the "risks I noticed" section — it turns the email from noise into signal and shows you can read between the lines. This is where the merch-team complaint (buried in paragraph three) surfaces as item 1.
- Ask for a *specific* confirmation ("by 11am today") not "let me know what you think." Deadlines get replies.
- Copy no one on the first reply. Champion-to-you conversations stay bilateral until the plan is agreed. Then loop in the room via the weekly.

## FIELD NOTES

- The Sunday-night email is almost always a proxy for the champion feeling political pressure from above. Address the source, not just the surface: "sounds like the exec committee is on your mind — let me help you go in Friday with an artifact you can lead with."
- Never reply "I'll get back to you." That's just deferred stress for both of you. Reply with structure, even if the structure is "here's what I heard, here's what I don't yet have opinions on, meeting me tomorrow at 10?"
- The 7-item count is diagnostic. If you extract fewer than 5 from an 800-word email, you're missing subtext. If you extract more than 10, you're padding.
- Save these emails and your replies. Over an engagement they become a diary of scope evolution — enormously useful in the renewal conversation.
- If the champion pushes back on your top-3, that's *good* — it means the plan surfaced a hidden priority. Iterate the plan; don't defend the first version.
- Not every rambling email needs a full reply template. A three-item email might just need a three-line acknowledgment. Match effort to input.

## INTERVIEW ANGLE

This exercise — a rambling input turned into a scoped plan — is the essence of the FDE role, and interview loops know it. Expect it as a take-home, a case exercise, or a behavioral probe.

Sample questions:

1. *"I'm going to read you an email a customer sent me. Walk me through your response."* — Live case. They'll read something rambling. Strong candidates enumerate items out loud, cluster them, and propose a plan with a named ask back. Weak candidates start describing solutions.
2. *"How do you handle a customer who keeps adding scope?"* — Tests whether you have a written process (this drill's template) versus a personality trait ("I push back"). Best answers describe the artifact you send.
3. *"Tell me about a time a stakeholder message made you realize you'd been prioritizing wrong."* — STAR. Best stories show reading between the lines of an email/message and reprioritizing based on the *implicit* signal.

## DRILL

Below is a synthesized rambling email. Reply to it using the Rambling-to-Sprint Reply Template in full — numbered enumeration, three tiers of routing, risks-noticed, named asks with deadlines. Time-box to 45 minutes.

> Subject: quick thoughts before Monday
>
> Hey — hope your weekend is good. Wanted to get some things down while they're fresh. So the demo Wednesday went great, the VP loved it, though she said after that the numbers on the new product lines still look weird and she's worried about presenting to the board on the 22nd if we can't explain them. Also Priya from ops mentioned the export button times out on their bigger reports, would be great if that could get fixed, small thing I think. Oh and I heard through the grapevine that IT is doing some network maintenance next Thursday that might affect the sandbox — you might want to check with Raj. Also finance is asking whether we can layer in the margin data for the top 50 SKUs, I told them maybe but wanted to check with you. And the merch team wants training, they've been asking for two weeks, can we set something up? I know we said week 8 but they're getting antsy. Last thing — the security team sent me a questionnaire I don't understand, I'll forward it separately, need it back by end of month apparently. Sorry for the brain dump, talk Monday.

After you write your reply, self-grade against the template: did you extract at least 6 items? Did you name the flavor of no on the deferred ones? Did you surface the board-on-the-22nd risk as item 1 (that's the real emergency)? Did you route the security questionnaire, the IT ticket, and the finance ask separately? Did you end with a *specific* confirmation deadline? Iterate until yes.
