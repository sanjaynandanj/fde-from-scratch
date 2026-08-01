# Company Loops — What Each FDE Interview Actually Emphasizes

How the major FDE employers structure their loops, what each stage is really
measuring, and how to prepare for each.

**Honesty note, read first.** This file describes *publicly known loop shapes* —
assembled from company career pages, job descriptions, published interview guides,
and widely reported candidate experiences — plus clearly flagged generalizations
from how these companies describe the roles. It deliberately contains no named
interviewers, no purported insider questions, and no claims of secret rubrics.
Loops change frequently, vary by team and region, and recruiters will tell you your
specific loop if you ask — **always ask**; "can you walk me through the stages and
what each evaluates?" is a normal, expected question that costs you nothing.
Where this file says "typically" or "commonly," it means exactly that: a reasonable
generalization, not a guarantee.

---

## Palantir — Forward Deployed Software Engineer (Delta) / Deployment Strategist (Echo)

**The role split, per Palantir's own public descriptions**: Delta is the forward
deployed *engineer* — embeds with customers, integrates data, builds on top of
Foundry/Gotham/AIP, ships operational software in the field. Echo (Deployment
Strategist) is the less-code-heavy counterpart — problem decomposition, customer
strategy, metric design, driving outcomes — though Echoes are expected to be
technical enough to work with data directly. Many candidates are pipeline-eligible
for both, and the loops overlap heavily in the decomp round.

**Typical loop shape** (commonly reported; varies):

1. **Recruiter screen** — background, motivation, logistics.
2. **Technical phone screen** (Delta) — practical coding: data manipulation,
   parsing, algorithms applied to realistic data rather than pure puzzle leetcode.
   For Echo, this is often replaced or supplemented by an analytical/decomp screen.
3. **Decomposition interview** — the signature round (see below).
4. **Onsite / final loop** — typically some combination of: a deeper decomp or
   case, a systems/"how would you build it" discussion, a values/behavioral
   conversation, and for Delta a further hands-on technical round. Palantir has
   also been known to use short take-home or presentation elements for some
   pipelines.

**What the decomp round emphasizes**: an ambiguous operational problem ("a shipping
company keeps losing containers"; "a government agency's benefits backlog is
growing") with nothing given. Graded on: clarifying questions that actually change
your plan, structuring (users → data → entities → metric → first solution),
back-of-envelope quantification, 80/20 instinct, and trade-off narration under
follow-up pressure — the interviewer will push on whatever you assert. This is
Phase 8 of this curriculum and [case-interviews.md](case-interviews.md), run live.

**What the company screens for culturally** (from their public materials and role
descriptions): outcome obsession over process, comfort being dropped into unfamiliar
domains, low ego under challenge — decomp interviewers deliberately disagree with
candidates to see whether they update, defend, or fold; both blind capitulation and
brittle defensiveness read badly. Mission questions ("why Palantir," including its
government work) should be expected and answered honestly — they publicly select
for people who have actually thought about it.

**How to prepare**:
- Drill timed decomps aloud until the five-move pattern (clarify / decompose /
  metric / 80-20 / estimate-with-ranges) is reflexive. All five cases in this
  repo's case file, plus Phase 8's drills.
- For Delta: practice data-wrangling coding — parse a messy file, join datasets,
  dedup — fluently in your language of choice, under time pressure, talking while
  typing.
- Prepare estimation muscle: Fermi arithmetic with stated assumptions is graded
  in nearly every round.
- Have a real answer to "why this company," including the uncomfortable parts.

---

## OpenAI — Forward Deployed Engineer / Solutions Architect / Solutions Engineering

**The role, per public job postings**: embed with strategic customers to build
production LLM applications on OpenAI's models — RAG systems, agents, evals,
integration with enterprise stacks — often described explicitly as a
customer-embedded, ship-fast engineering role, sometimes with significant travel.
Related-but-distinct tracks (solutions architect, partner engineering) share much
of the loop shape with more emphasis on advisory breadth versus building depth.

**Typical loop shape** (commonly reported; varies by team):

1. **Recruiter + hiring-manager conversations** — heavy emphasis on customer
   experience: have you actually shipped with/for external stakeholders?
2. **Technical screen** — practical coding, frequently API-integration flavored:
   call a model, process data, handle failures — closer to real work than to
   algorithm puzzles.
3. **Take-home or live build** — commonly an LLM-application exercise: build
   something against their API (or a described corpus), often the RAG-over-documents
   archetype ([take-home-patterns.md](take-home-patterns.md), Archetype 3), with a
   presentation/walkthrough afterward.
4. **Onsite rounds** — typically: LLM system design (design a production RAG/agent
   system for an enterprise scenario — evals, cost, latency, safety, and failure
   handling expected unprompted), customer-scenario/behavioral rounds (difficult
   stakeholder, ambiguous scope, production incident), and cross-functional
   conversations.

**What it emphasizes**: applied LLM engineering *judgment* — chunking, retrieval
quality, evals and golden sets, hallucination containment, cost/latency budgets —
plus the customer craft to deploy it: candidates who can build but not explain
trade-offs to a stakeholder, or who hand-wave evaluation, generalize poorly here.
Section 3 of [theory-questions.md](theory-questions.md) is essentially this loop's
theory surface.

**How to prepare**:
- Build a real RAG system end-to-end with an eval harness before interviewing —
  the difference between having done it and having read about it is audible within
  two minutes.
- Practice LLM system design aloud: "design document Q&A for a bank" — and force
  yourself to cover evals, guardrails, cost, and the failure story every time.
- Have production war stories about model behavior: a hallucination you contained,
  a retrieval failure you diagnosed, a cost you cut. If you lack them, generate
  them: this curriculum's Phase 5 flagships and drills exist to produce exactly
  these stories legitimately.
- Know their product surface (API capabilities, structured outputs, tool use)
  at practitioner depth — it's the toolbox the role sells.

---

## Anthropic — Applied AI / Forward Deployed Engineering

**The role, per public postings**: help enterprise customers deploy Claude
successfully — solution architecture, prompt and retrieval engineering, evals,
production integration — with the company's safety orientation explicitly present
in how the role is described: deployments should be reliable, honest about
limitations, and well-governed.

**Typical loop shape** (commonly reported; varies):

1. **Recruiter and hiring-manager screens** — motivation and customer background;
   expect a genuine "why Anthropic" conversation — the company publicly
   self-selects for people who take its mission seriously, and a purely
   opportunistic answer lands poorly.
2. **Technical screen** — practical coding; Anthropic has publicly noted that its
   engineering interviews favor realistic tasks (and has distinctive policies about
   AI-assistant use in interviews — check current guidance with your recruiter
   rather than assuming).
3. **Work-sample / take-home** — commonly an applied exercise around building with
   Claude: an extraction or RAG task, prompt engineering with evaluation, or a
   customer-scenario design doc.
4. **Onsite rounds** — applied LLM system design, customer-facing behavioral
   scenarios, and values/collaboration conversations.

**What it emphasizes** (from public role descriptions, generalized): the same
applied-LLM core as other frontier-lab loops — retrieval, evals, structured
extraction, production reliability — with comparatively more explicit weight on
*honest capability communication*: knowing what the model can't do, designing
refusal and human-oversight paths, and being straight with customers about
accuracy. The integrity-around-data competency ([behavioral.md](behavioral.md),
competency 6) and questions like Q100/Q117 in the theory bank are directly in
this loop's lane.

**How to prepare**:
- Everything in the OpenAI preparation list applies; build with Claude
  specifically — long-context patterns, tool use, structured outputs.
- Prepare at least one story where you *limited* an AI system's scope or shipped
  an honest accuracy story under pressure — and one where you designed
  human-in-the-loop review.
- Read their published enterprise-deployment material and usage policies well
  enough to discuss governance questions fluently.
- Expect and welcome eval-depth follow-ups: "how would you know it's working?"
  is never a throwaway question in this loop.

---

## Scale AI — Forward Deployed Engineer / GenAI Solutions

**The role, per public postings**: build custom GenAI applications for enterprise
and government customers on Scale's platform and services — historically strong in
data-engine work (labeling, evaluation, fine-tuning data) with the forward-deployed
motion focused on making models work against customer data and workflows. Government
and defense engagements are a significant, publicly stated part of the business —
some roles require clearance eligibility; check postings.

**Typical loop shape** (commonly reported; varies):

1. **Recruiter screen.**
2. **Technical screen(s)** — practical coding with a data-heavy flavor: munging,
   pipelines, API integration.
3. **Project/take-home or live build** — frequently an applied ML/LLM exercise
   against a dataset: extraction, classification with evaluation, or a small
   RAG build.
4. **Final rounds** — system design (data pipelines + LLM applications),
   customer-scenario behavioral, and team conversations.

**What it emphasizes**: the data end of the FDE braid more than most — expect
fine-tuning versus RAG trade-offs, training-data quality, evaluation design, and
"how would you get labeled data for this?" to come up naturally, given the
company's data-engine heritage. Speed and scrappiness are recurring themes in how
the company publicly describes itself; long-cycle process answers land worse than
ship-and-iterate answers.

**How to prepare**:
- Be strong on the eval-and-data-quality theory (Sections 1 and 3 of the theory
  bank), especially golden sets, label bias, and fine-tune-vs-RAG decisions
  (Q92–Q93).
- Practice the messy-data take-home archetypes 1 and 4 — data-heavy exercises
  are common here.
- If pursuing government-facing roles: understand deployment constraints
  (air-gaps, ATO-style approval processes — Q47, Q66) and clearance logistics.
- Have a crisp story about a time you improved a system by improving its *data*
  rather than its model or code.

---

## Sierra — Agent Engineer / Forward Deployed

**The role, per public descriptions**: Sierra builds customer-facing AI agents
(conversational agents for support and commerce) for enterprises, and its
forward-deployed engineers embed with customers to design, build, and tune those
agents against real business processes — a role the company's founders have
publicly described as central to how the product ships. The engagement surface is
narrower and deeper than a general FDE role: production conversational agents,
their guardrails, and their integration into customer systems (order management,
CRM, support stacks).

**Typical loop shape** (generalized from public descriptions and reported
experiences — Sierra is younger and less documented than the others; verify with
the recruiter):

1. **Recruiter / hiring-manager screens** — strong emphasis on customer-facing
   experience and product sense.
2. **Technical screen** — practical coding and integration work.
3. **Project round** — commonly an agent-flavored applied exercise: design or
   build a conversational flow with tool calls, handle the failure cases,
   define quality measurement.
4. **Final rounds** — system design for agent deployments, behavioral rounds on
   customer scenarios, and founder/leadership conversations (a small-company
   norm).

**What it emphasizes**: agent-specific judgment — conversation design, tool-call
safety against production systems (Q96 in the theory bank is squarely this),
escalation-to-human design, and measuring agent quality (containment/resolution
rates and their honest definition — note that "resolution rate" has all the
gameability problems of any metric, and saying so is a strong move). Because the
agents face the customer's *customers*, brand-safety and guardrail thinking gets
unusual weight.

**How to prepare**:
- Build a small tool-using agent with explicit guardrails and an escalation path;
  be ready to defend every safety decision.
- Think through metric design for conversational quality (Phase 8's metric lesson
  applied to conversations: leading vs lagging, gameable vs honest).
- Prepare customer-empathy stories involving *end-user* experience, not just
  stakeholder management.
- Know their public case studies and be ready to reason about one: "how would you
  have built that deployment?"

---

## The generic AI-startup FDE loop

Dozens of AI-application companies (Glean and many younger ones) now hire FDEs,
solutions engineers, and "deployed engineers" with loops that converge on a common
shape. If you're interviewing somewhere not listed above, expect a subset of:

1. **Recruiter/founder screen** — at small companies, often the founder directly;
   motivation and customer experience.
2. **Practical technical screen** — data munging or API integration, rarely
   hard leetcode.
3. **Take-home** — almost always one of the five archetypes in
   [take-home-patterns.md](take-home-patterns.md), most commonly RAG-over-documents
   or open-ended-dataset. At startups the take-home is disproportionately decisive,
   because the team is too small to ignore a strong artifact.
4. **Take-home walkthrough + extension** — present it, then extend it live
   ("add auth; add a second data source") — re-read your own submission the night
   before.
5. **Customer-scenario round** — a role-play or deep behavioral: scope a vague
   request, handle a hostile stakeholder, explain a failure.
6. **Founder/values conversation.**

**What generic loops emphasize** — three things, everywhere:

- **Autonomy evidence**: startups need FDEs who operate without infrastructure or
  supervision; every stage is scanning for "has this person shipped something real,
  alone, end-to-end?" Portfolio artifacts (a deployed project, this curriculum's
  capstones, a public repo with a real README) carry unusual weight.
- **Speed with judgment**: the take-home time-box discipline and the 80/20
  instinct — startups are burned most often by engineers who gold-plate.
- **Customer signal**: any genuine evidence of having sat with users and changed
  course because of it. Internal-customer stories count fully.

**How to prepare**: everything in this repo, honestly — the generic loop is the
curriculum's target surface. Specifically: have one polished, demoable project you
can present in ten minutes and extend live; drill archetypes 3 and 5 of the
take-home patterns; and prepare questions to ask *them* that show field literacy
("who runs deployments today?", "what does your longest-running customer
engagement look like?", "what's the handoff model?") — at startups the questions
you ask are graded nearly as heavily as the answers you give.

---

## Cross-company preparation matrix

| Preparation asset | Palantir | OpenAI | Anthropic | Scale | Sierra | Startup |
|---|---|---|---|---|---|---|
| Timed decomp drills (Phase 8, case file) | ●●● | ●● | ●● | ●● | ●● | ●● |
| Messy-data coding fluency | ●●● | ●● | ●● | ●●● | ●● | ●●● |
| RAG build + eval harness (Phase 5) | ● | ●●● | ●●● | ●●● | ●● | ●●● |
| Agent/tool-safety design | ● | ●●● | ●●● | ●● | ●●● | ●● |
| Behavioral bank (6 competencies) | ●●● | ●●● | ●●● | ●● | ●●● | ●●● |
| Take-home archetype practice | ●● | ●●● | ●●● | ●●● | ●●● | ●●● |
| Estimation / Fermi with ranges | ●●● | ●● | ●● | ●● | ●● | ●● |
| "Why this company," honestly prepared | ●●● | ●● | ●●● | ●● | ●● | ●●● |
| Demoable portfolio project | ●● | ●● | ●● | ●● | ●●● | ●●● |

●●● = loop-deciding · ●● = graded · ● = background

Final reminder: every claim in this file is a snapshot of a moving target. The
two questions that keep you current cost one email each: ask the recruiter for the
loop structure, and ask each interviewer at the start what their round evaluates.
Both are considered professional, not presumptuous — and asking them is itself
FDE behavior: clarify the metric before you start solving.
