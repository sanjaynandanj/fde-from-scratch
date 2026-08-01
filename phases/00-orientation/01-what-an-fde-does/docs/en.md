# What an FDE Actually Does: A Week in the Field

Phase 0 · Lesson 01 · ~1h

## PROBLEM

A new hire — strong SWE background, three years at a good infra company — lands at his first customer site on a Monday. He expects a backlog, a sprint board, a codebase. Instead he gets a conference room with a whiteboard nobody will let him erase, a VP who wants "the AI thing" live by end of quarter, a database he has no credentials for, and a CSV export named `FINAL_data_v3_ACTUAL (2).csv`. By Wednesday he's written zero product code and is starting to panic. By Friday, the *senior* FDE on the engagement has shipped a demo dashboard, gotten read access to the warehouse, and booked the next exec meeting — and wrote maybe 400 lines of code all week.

The gap between those two weeks is the job. Nobody panicked because the senior FDE knew what the week was supposed to look like.

## INTUITION

The FDE role is engineering where the constraint is never the code. The constraints are access, trust, ambiguity, and time-to-value. A representative week:

**Monday.** 9am: stand-up with your own team (usually 1–3 FDEs per engagement). 10am: meeting with the customer's data team — you need warehouse credentials, and the ticket has been "in review" for six days. You spend the meeting finding the human who can approve it, not arguing about the ticket. Afternoon: read their data. Not their docs — their *data*. Row counts, null rates, the columns that are lies.

**Tuesday.** Build. Head-down day if you've protected it. You're writing a parser for their export format, a thin API over it, a one-page dashboard. Everything stdlib-or-close, everything disposable, everything demoable.

**Wednesday.** The weekly customer sync. You demo what exists — even if it's two days old and half-fake — because a visible artifact every week is what keeps the engagement alive. You collect three new requirements, decline one of them out loud, and write down who asked for what.

**Thursday.** The messy middle: entity resolution isn't converging because their customer IDs got mangled by Excel; security wants a document about where the LLM prompts go; your champion pings you that the VP wants a number — "how much money does this save?" — by Friday.

**Friday.** You produce the number, with error bars and a written list of assumptions. You ship the week's build to their sandbox. You write a five-line status email: shipped, learned, blocked, next, ask. Then you update your own team on what the pilot actually needs next week versus what was planned.

Notice the ratio: maybe 40% coding, 30% data archaeology, 30% humans. The coding is real engineering — but it is *shaped* by the other 60%.

## MAP IT

No code in this lesson. Instead, build the mental model on paper:

1. Draw a 5-day calendar grid. Place these 12 activities on it where you think they belong: warehouse-access chase, head-down build, weekly demo, status email, security questionnaire, data profiling, stakeholder coffee, requirement triage, estimate with error bars, sandbox deploy, internal stand-up, champion check-in.
2. For each activity, tag it **C** (code), **D** (data), or **H** (human). Count the tags. If you got more than 50% C, re-read the week above.
3. Write down the three artifacts the week produced that a customer can *see*: the demo, the number-with-assumptions, the status email. Everything else was in service of those.

## FIELD NOTES

- The week above is a *good* week. Bad weeks are dominated by one blocked credential or one stakeholder who went quiet. Detecting those early is a skill this curriculum drills.
- Travel varies wildly by company and customer. Some engagements are fully remote; some are three days a week on-site in an industry town you've never heard of. On-site time is disproportionately valuable in week 1–3 and drops after.
- You will often be the only technical person the customer's executives ever meet from your company. You are the product, the docs, and the support line.

## INTERVIEW ANGLE

Every FDE loop probes whether you understand that the role is not pure SWE. Interviewers listen for candidates who talk about time-to-value, access battles, and demos — not sprint velocity.

Sample questions:

1. "Walk me through what you'd do in your first week at a customer site where the goal is 'deploy our platform for their supply-chain team.'" (They want: meet stakeholders, get data access moving on day one, profile real data, ship something visible by Friday.)
2. "Tell me about a time you delivered value before you had everything you needed." (Behavioral probe on ambiguity tolerance.)
3. "How much of this role do you think is coding?" (Trick question — the right answer is a ratio plus *why* the non-coding parts exist.)

## DRILL

Take a project you have actually shipped. Rewrite its first week as an FDE engagement: who was the champion, what was the access battle, what would the Wednesday demo have been, what number-with-error-bars would the VP have wanted on Friday? Write the Friday status email (five lines: shipped, learned, blocked, next, ask). Keep it — you will reuse the format in Phase 1 and in behavioral interviews.
