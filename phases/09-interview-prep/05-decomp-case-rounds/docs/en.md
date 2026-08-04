# Decomp & Case Rounds: Applying Phase 8 Under Pressure

**Phase 9 · Lesson 05 · ~1h**

## PROBLEM

A candidate has drilled the decomp rounds. She's done all of Phase 8. She's read every case in [`case-interviews.md`](../../../interview-bank/case-interviews.md). She could recite the five-move pattern in her sleep: clarify, decompose, metric, 80/20, estimate. Then she walks into a Palantir decomp round on a Thursday morning: "a large e-commerce retailer is losing money on returns processing — where do you start?" She freezes for eight seconds. She starts, restarts. She feels the interviewer's silence and starts overcompensating with hedging language ("that's a great question, so let me think about this from first principles…"). By minute six she's talking about returns fraud, warehouse ergonomics, and third-party logistics vendors simultaneously. The interviewer pushes on one thread; she abandons it and goes to another. She leaves the round drained and gets a rejection with the note "structure broke down under pressure — knew the moves but couldn't execute them live."

She had the theory. She didn't have the reps. Decomp under pressure is not the same skill as decomp on paper, and this lesson exists because the gap between them decides Palantir loops.

## INTUITION

The decomp round is 30–45 minutes of thinking-out-loud against an ambiguous operational problem, with a smart interviewer who is deliberately going to push on things you say. What's actually being measured is not intelligence — every candidate in the loop is intelligent — but *structure under stress*.

Three sub-signals interviewers score:

- **Do you have a repeatable structure**, or does each problem get a bespoke response that gets worse when tired? The five-move pattern isn't a script — it's scaffolding you fall back on when your working memory hits its limit.
- **Do you update or defend when challenged**? Interviewers *deliberately disagree with you* — sometimes on things you're right about. Blind capitulation reads as brittle; brittle defensiveness reads as ego. The correct move is to engage the specific critique, update where they've named something real, and hold ground where you have a reason, with the reason stated.
- **Do you narrate trade-offs, or make silent choices**? "I could go after fraud or after operational cost — I'll start with operational cost because it's usually larger in returns and easier to observe in the data" is a decomp interviewer's happy sound.

The pressure-specific failure modes to name and drill against:

- **Rambling**: you keep talking to avoid silence. Fix: pauses are legal. "Let me structure this for a moment" earns you three seconds of unpunished silence.
- **Depth without breadth**: you go 40 minutes into fraud subcategories and never talk about anything else. Fix: sketch the full tree before diving.
- **Estimation panic**: they ask "how big is that?" and you blank. Fix: any answer with stated assumptions beats no answer; "call it 5 million shipments a year, so if 10% are returned that's 500k…" is graded well even when the numbers are approximate.
- **Anchoring**: you commit to the first metric that comes to mind and defend it past the point where you should have updated. Fix: propose two metrics, then pick.

## BUILD IT

The pressure-adapted decomp protocol. Rehearse this until it fires when your working memory is empty:

**Move 1 — Clarify (60–90 seconds).** Ask three or four questions that would actually change your approach. Not "tell me more" — specific. For the returns problem: "What kind of retailer — grocery, apparel, electronics? What's their scale — millions of orders? What does 'losing money' mean concretely — margin per return, gross returns cost, an audit finding? Is the problem 'we return too many things' or 'each return costs too much'?" The answers reshape the whole tree. Refusing to guess before asking is a strong move.

**Move 2 — Decompose out loud (2–3 minutes).** Draw the tree in words. For returns: *cost of return = (cost per return) × (number of returns)*. Cost per return has sub-branches (labor, shipping, restocking, refunds on non-restockable items, fraud losses). Number of returns has sub-branches (customer-driven — did the wrong item ship, did it arrive damaged, did it not match expectations; policy-driven — is the free-returns window too generous). *Name the branches, then pick one to explore first, saying why.*

**Move 3 — Pick the biggest branch (30 seconds).** Order-of-magnitude reasoning: "Cost-per-return is probably $10–30; number of returns is probably 10–20% of orders. For a large retailer that's tens of millions of returns a year. The number of returns branch dominates the total unless cost-per-return has one huge subcomponent — so I'll start with return volume." State the reasoning; the interviewer often wants exactly this move.

**Move 4 — Metric (2–3 minutes).** Design one leading and one lagging metric for the branch. Leading: "returns initiated per hundred orders shipped, by SKU category." Lagging: "gross return cost as % of revenue, monthly." Explicitly name what's gameable and what's honest. Then anchor the pilot on one, defended.

**Move 5 — 80/20 solution (4–5 minutes).** What ships in week one, given constraints? "Ingest the returns log and the order log, entity-resolve orders to returns, produce a per-SKU return-rate dashboard, and identify the top 20 SKUs by absolute return count — that's usually where 60% of the pain is." Then name what you'd add if the pilot grew: fraud detection, size-recommendation model, packaging redesign hypotheses.

**Move 6 — Estimation with ranges (1–2 minutes).** When they push "how big could the win be?", walk numbers with visible assumptions. "If the top 20 SKUs account for 20% of returns, and returns cost $15 each on average, and we can cut those SKU returns by even 20% via better size guides and clearer photos, that's a low-single-digit-percent improvement on a nine-figure returns bill, or single-digit millions annually — with a range of 2–8x depending on what we actually find in the data."

When they push back — which they will:

- If they're right, say so plainly. "Fair — I was underweighting the fraud branch; let me re-order." Updating is not weakness; failure to update is.
- If they're testing you and you have a reason, hold it with the reason. "I hear that; the reason I started here is that operational cost usually dominates fraud in absolute dollars, though fraud rate matters if it's growing. Do you have a sense of which they're seeing?"
- Never say "great question." Never say "let me think about that." Just think, or say "give me a moment to structure this."

Rehearsal method that actually builds pressure tolerance:

- Record yourself running a case out loud, cold. Play it back at 1.5x. The moments you can't follow yourself are where structure is missing.
- Have a friend disagree with you on purpose during a mock. The reflex to argue or to fold is exactly what the round is testing.
- Time-box moves. If you're still in Move 1 at minute five, you're stalling. Move 2 doesn't require certainty; it requires structure.

## FIELD NOTES

- On the job, decomp under pressure happens in customer meetings. The exec asks "how would you approach this?" and you have 90 seconds to sound structured. The interview round rehearses this exact muscle — which is why it's weighted the way it is.
- The best FDEs decomp on paper reflexively. Whenever a customer's problem lands in your inbox, the first artifact you produce is a tree of branches, ranked. Interview drills build this reflex.
- Decomp rounds do not want the *right* answer. They want to see you *derive* an answer. Interviewers will happily grade a candidate high whose final recommendation is wrong, if the reasoning was structured and updated.
- Watch your energy in month-long loops. Decomp is high-cognitive-load; a candidate who does three decomp rounds in one onsite fades on the third. Prep for stamina, not just structure.

## INTERVIEW ANGLE

Meta-questions about decomp interviews:

1. "What's your process when you get stuck?" — the model answer is a protocol: pause deliberately, re-list what you know, name what's missing, ask a clarifying question if there's one that would unblock, and pick a direction with stated reasoning.
2. "How do you know when you've decomposed enough?" — "when the leaves are things I could either estimate a number for or ship a first version of. Everything above that is still abstract."
3. "Have you ever changed your mind mid-decomp?" — the strong answer is a specific example with what the signal was: "yes — I had assumed the ingestion volume was the constraint, then the interviewer told me the source system was slower than I'd estimated, and the constraint moved to source-side throttling; I re-ranked the tree."

## DRILL

Set a 30-minute timer. Pick a case from [`case-interviews.md`](../../../interview-bank/case-interviews.md) you haven't done, or invent one ("a large hospital system's ER wait times are increasing"). Read the prompt, start the timer, and run the six moves out loud, recording yourself. When the timer rings, stop mid-sentence if you have to. Play back the recording. Grade yourself: did you clarify before deciding? Did you name the tree before diving? Did you state at least one estimation with visible assumptions? Did you name a leading and a lagging metric? Did you propose a shippable week-one artifact? Any move you skipped is where next week's practice goes. Do this three times a week for four weeks — the reps compound, and by the end the moves fire under real pressure.
