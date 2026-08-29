# Requirements Decomposition: From "Make It Smarter" to a Backlog

**Phase 7 · Lesson 03 · ~1.5h**

## PROBLEM

Monday morning, week three of a pilot at a specialty retailer. The champion forwards an email from her VP: "the demand forecast needs to be smarter — right now it's making bad calls on new SKUs and the merch team is losing trust." That is the entire brief. The FDE, feeling productive, spends a day tuning the model, adding two features, and improving a MAPE metric by 4%. He shows it Wednesday. The VP watches for two minutes and says: "no, I meant we launched 200 new SKUs last month and the forecast just showed zero for all of them because they had no history — that's what needs fixing." The FDE lost a week. The stated problem ("smarter") had nothing to do with the actual problem (cold-start handling for new SKUs). One question on Monday would have surfaced it.

Requirements decomposition is the discipline that turns vague executive prose into a backlog of things you can actually build, sized in hours, ordered by leverage.

## INTUITION

There are three levels a request can live at, and you must move down all three before you write code:

1. **Outcome.** "Make it smarter." "Reduce fraud losses." "Speed up onboarding." Not buildable. Every outcome hides at least three different mechanisms.
2. **Behavior change.** "The forecast should return a sensible number for a SKU with zero historical data." "The fraud model should catch card-not-present anomalies within four hours." Buildable, but still fuzzy about *how*.
3. **Backlog item.** "Implement a cold-start heuristic that falls back to category-mean when SKU history < 4 weeks; expose it as `forecast(sku, use_cold_start=True)`; ship behind a feature flag; acceptance: forecast returns a non-zero number for 100% of the 200 new SKUs from last month, and merch team signs off on 20 sampled values." Buildable, sized, testable.

The move from level 1 to level 3 is the whole skill. Doing it in the room with the customer — not alone at your desk — is how you avoid the wasted-week failure above.

## BUILD IT

The **Decomp Template** — a one-page artifact you fill in for every stated request. Sections:

**1. Verbatim ask.** Copy-paste the sentence, don't paraphrase. Paraphrasing is where the truth gets lost.

**2. Outcome (level 1).** Rewrite as a single sentence starting with "so that…" — "so that merchandising trusts the forecast when planning new-SKU inventory." If you cannot write this sentence, you don't understand the ask yet.

**3. Concrete example.** From discovery: one real case where the current system failed. SKU number, date, expected behavior, actual behavior. If you cannot produce one, you're not ready to build — go get one.

**4. Behavior changes (level 2).** Bullet list. Each starts with a system name and a verb: "The forecast API returns…", "The dashboard shows…", "The pipeline logs…". Aim for 3-7 bullets per outcome.

**5. Backlog items (level 3).** For each behavior change, one or more tickets. Each ticket has: title, one-sentence description, acceptance criteria (measurable), estimate in hours, dependencies, owner. Estimates in hours, not story points — customers understand hours.

**6. Explicit non-goals.** What this ask does *not* include. This is where you preempt scope creep: "we are not changing the model for products with sufficient history; we are not touching the reorder logic."

**7. Open questions.** Numbered. Each with an owner and a due date. Never leave discovery loose ends undocumented — they migrate into surprise scope.

**8. Order-of-attack.** The backlog items sorted by (customer value × confidence) / effort. Top three are next week's sprint. Everything below the line is written down so the customer sees you heard it but is explicitly not in scope for the pilot.

Do this on a shared doc, in the meeting, with the champion in the room. The act of watching you write the decomp is what earns their signoff.

## FIELD NOTES

- Customers cannot tell you what they want in level-3 language. Never punish them for it — translation is your job, not theirs.
- The "so that…" sentence in section 2 is worth more than the entire rest of the doc. If the champion pushes back on your version of it, you found a misalignment before wasting a sprint.
- Non-goals are the most political section. Write them softly ("not in the pilot scope") not harshly ("won't do"). The room still needs to feel heard.
- Beware of asks that decompose into more than 15 tickets — that's a program, not a request. Either negotiate scope, or push back that this needs its own planning cycle.
- Estimates in hours means *your* hours, not a team's. If you double for team velocity, mark it clearly.
- Revisit the decomp doc every Friday. Move tickets between "shipped / in progress / not started / cut" and share the diff. This is a status doc and a scope doc rolled into one.

## INTERVIEW ANGLE

Decomp shows up in case rounds (Phase 8) as a formal exercise, and in behavioral rounds as a probe on ambiguity handling. Both flavors test the same skill: taking a fuzzy statement and producing a shippable plan under time pressure.

Sample questions:

1. *"A customer says 'we want the AI to handle exceptions.' Walk me through how you get from that sentence to next week's sprint."* — Tests the three-level move. They want to hear you ask for a concrete example first, before decomposing.
2. *"You have five backlog items and one week. How do you pick the two you ship?"* — Tests prioritization. Correct instinct: customer value × confidence / effort, plus a bias toward whatever unblocks the next demo.
3. *"Tell me about a time a customer request turned out to mean something completely different than you thought."* — Behavioral. They want the moment of realization and the process change afterward. Best answers include a decomp artifact adopted going forward.

## DRILL

Take this exact one-liner from a hypothetical customer email: *"the ticket triage isn't good enough — support is drowning and CSAT is slipping."* Fill out the Decomp Template in full: verbatim ask, "so that…" outcome, one concrete example you'd ask for, 5 behavior changes, 8-12 backlog items with hour estimates and acceptance criteria, 5 non-goals, 5 open questions with owners, and the ordered attack plan for next week. Time-box to 45 minutes. Then read your own doc as if you were the VP of Support — does it show you understood the problem? Iterate until yes.
