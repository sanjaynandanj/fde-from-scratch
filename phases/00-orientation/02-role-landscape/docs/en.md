# The Role Landscape: Palantir, OpenAI, Anthropic, Scale, Sierra

Phase 0 · Lesson 02 · ~1h

## PROBLEM

A candidate preps for "an FDE interview" as if the title means one thing. She grinds Palantir-style decomposition cases for three weeks, walks into a loop at an AI lab, and gets asked to live-code a retrieval pipeline against a messy document dump and then defend an eval methodology. Different company, same title, materially different job — and she prepared for the wrong one. The title "Forward Deployed Engineer" is a family of roles, not a single spec. If you don't know which flavor you're interviewing for, you're guessing.

## INTUITION

**Palantir invented the role** and still defines its center of gravity. Publicly, Palantir has described a split that the industry mostly knows by its internal shorthand:

- **Forward Deployed Engineers** (historically "Deltas," from the Delta force analogy) embed with customers, integrate data, and build product-on-top-of-platform to solve the customer's actual problem. Heavy travel historically, heavy ownership, judged on customer outcomes.
- **Product/platform engineers** (historically "Echoes," as in "engineering") build Foundry/Gotham itself, informed by what Deltas hit in the field. The boomerang between the two tracks — field learnings hardening into product — is the core of Palantir's model.

The famous interview signature: decomposition. Take an ambiguous operational problem ("reduce food waste for a grocery chain") and structure it — data model, metric, MVP — in real time.

**OpenAI** hires Forward Deployed Engineers explicitly by that name. Public job descriptions emphasize embedding with strategic customers, building production LLM applications on the API, and shipping quickly with customer engineering judgment. Expect practical coding, LLM system design (RAG, evals, agents), and customer-scenario questions.

**Anthropic** hires under names like Applied AI / Solutions Architect / Forward Deployed flavors. Public postings emphasize helping enterprises deploy Claude safely and effectively: prompting, evals, integration patterns, and a distinctive weight on safety and honest capability communication.

**Scale AI** has a long-running Forward Deployed / Deployment Engineer motion around getting its data engine and GenAI platform working inside enterprise and government customers — heavier on data pipelines and government/compliance contexts than the labs.

**Sierra** (agent platform for customer service) hires "Agent Engineers" — effectively FDEs whose whole job is designing, building, and tuning customer-facing AI agents for each client, with heavy emphasis on conversation quality, guardrails, and measurable containment/resolution rates.

Generalizing honestly — details shift, postings change, and internal titles move around, so treat this as a map, not gospel:

| Axis | Palantir | AI labs (OpenAI/Anthropic) | Scale | Sierra |
|---|---|---|---|---|
| Core artifact | Data-integrated ontology + apps | LLM app on the API | Data pipeline / platform deploy | Production agent |
| Signature skill | Decomposition + data modeling | LLM engineering + evals | Data ops at scale | Conversation design + guardrails |
| Interview signature | Decomp case | Practical coding + LLM design | Practical + customer scenarios | Agent/quality scenarios |

The braid is the same everywhere: full-stack speed, data wrangling, enterprise deployment, customer craft. The weighting differs.

## MAP IT

1. Pull up three real, current FDE-family job postings (any of the companies above). For each, highlight phrases in four colors: prototyping speed, data integration, enterprise/deployment, customer-facing. Compute the rough ratio.
2. Write a one-line "center of gravity" for each posting (e.g., "LLM app builder who can sit with a customer").
3. Map yourself: score your own experience 1–5 on each of the four strands. The lowest score is your study priority for the rest of this curriculum.

## FIELD NOTES

- Titles are unstable. The same job ships as FDE, Deployment Engineer, Applied AI Engineer, Solutions Architect, Agent Engineer, or Member of Technical Staff (Deployed). Read the *description*, not the title.
- Compensation and travel expectations vary more across FDE roles than across SWE roles. Ask directly in the loop; it's a normal question.
- Almost every company with this role describes the same boomerang: field pain becomes product roadmap. Your leverage as a candidate is showing you can operate on both sides of that loop.

## INTERVIEW ANGLE

Knowing the landscape is itself interview signal — "why this company's version of the role" is a near-universal question.

Sample questions:

1. "Why an FDE role here rather than a product engineering role?" (They're testing whether you understand the trade: ambiguity and customer exposure for leverage and ownership.)
2. "What do you think is different about deploying AI at an enterprise versus building AI products?" (The deployment-gap thesis — see Lesson 04.)
3. "Where do you see this role in three years?" (Maps to the career arc in Lesson 05; companies want people who see the field→product boomerang, not people escaping SWE.)

## DRILL

Pick the two companies from this lesson whose flavors differ most in your view. Write a half-page memo: how would you prepare differently for each loop? Which three lessons in this repo's catalog would you prioritize for each? Check your answer against Phase 9 Lesson 01 when you get there.
