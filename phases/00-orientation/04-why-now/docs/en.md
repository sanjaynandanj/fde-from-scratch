# Why Now: Model Commoditization and the Deployment Gap

Phase 0 · Lesson 04 · ~1h

## PROBLEM

A Fortune 500 insurer runs a GenAI hackathon in 2023. Forty demos, three standing ovations, an executive mandate, a seven-figure budget. Eighteen months later: zero of the forty demos are in production. Not because the models weren't good enough — because nobody could get the claims data out of the mainframe, past the compliance committee, through the security review, and into a system the adjusters would actually use. The models kept getting better the whole time. The gap wasn't intelligence. The gap was deployment. Multiply that story across every large enterprise on earth and you have the market that created the modern FDE role.

## INTUITION

Two curves explain the moment:

**Curve 1: model capability is commoditizing.** Frontier models from multiple labs cluster near each other on most enterprise tasks; open-weight models trail by months, not years; the cost per token of a given capability level has fallen relentlessly. When several vendors can supply roughly the capability you need, the model itself stops being the differentiator. Nobody wins an enterprise deal on benchmark deltas anymore.

**Curve 2: enterprise deployment difficulty is not falling.** The blockers are not in the model:

- **Data**: the knowledge is in seventeen systems, three of them from the 1990s, none with clean exports. Schema archaeology and entity resolution don't get easier because the model got smarter.
- **Trust and compliance**: SOC 2, HIPAA, data residency, security review, the 300-row questionnaire. These processes move at institutional speed.
- **Integration**: SSO, VPCs, air-gapped environments, the firewall change ticket.
- **Workflow**: software only creates value when a claims adjuster or supply planner changes how they work. That is a human problem, solved on-site.
- **Evaluation**: "it seems good" doesn't survive procurement. Someone must build the golden set and prove accuracy on the customer's own data.

The value of closing the gap is enormous and the supply of people who can close it is tiny — because the skill braid (Lesson 01) is taught nowhere and mostly learned by accident. Hence: labs and platform companies hiring FDEs aggressively, forward-deployed teams becoming revenue-critical, and premium compensation for a role that didn't exist as a category fifteen years ago.

Palantir proved the economics first: sell the outcome, embed engineers to deliver it, harden the repeated work into platform. The AI wave re-ran the same discovery at industry scale — every lab that tried to sell APIs into enterprises found they had to send engineers with them. The pattern generalizes: **whenever a technology's capability outruns organizations' ability to absorb it, forward deployment is the arbitrage.**

The honest caveat: parts of the gap *will* close. Better tooling, agentic coding, standardized connectors, and maturing enterprise AI teams will erode the routine work. What persists is the judgment layer — discovery, trust, decomposition, evaluation, workflow change — which is precisely what this curriculum weights.

## MAP IT

1. List the last three "AI pilot failed" stories you've seen (news, your own company, friends). For each, classify the primary cause: data, compliance, integration, workflow, or evaluation. Model capability will almost never be the answer — notice that.
2. Draw the two curves (capability rising and commoditizing; deployment difficulty flat) on one chart. Shade the widening area between them. Label it "the FDE market." Annotate where you think each curve is in 3 years.
3. Write three sentences: which parts of the gap do you believe close within 5 years, which persist, and therefore which skills in this repo's catalog are durable vs. depreciating. Keep it; re-answer after Phase 6 and compare.

## FIELD NOTES

- Inside a customer, the deployment gap has a face: the mainframe team of two people near retirement, the CISO who has burned before, the middle manager whose job your pilot threatens. The gap is sociotechnical; treating it as purely technical is the classic new-FDE error.
- Budget dynamics matter: enterprises now have AI budget that *must* be spent and board pressure to show results. That urgency is why pilots get funded fast — and why a pilot that shows value in 30 days beats a perfect system in 12 months.
- "Commoditization" doesn't mean models don't matter. It means model choice becomes an engineering decision (cost, latency, hosting constraints — Phase 5) instead of the deal-winner.

## INTERVIEW ANGLE

The "why now / why this role" question is a soft opener in nearly every FDE loop, and a strong answer signals market understanding, not just enthusiasm.

Sample questions:

1. "Why do you think companies like ours hire FDEs instead of just selling API access?" (Answer with the deployment gap: data, trust, integration, workflow, evals.)
2. "Models keep improving — doesn't that make this role obsolete?" (The mature answer: routine deployment work erodes; judgment, trust, and decomposition persist; the role climbs the value stack.)
3. "What's the hardest part of getting AI into production at a large enterprise?" (Pick one gap component and tell it concretely — data access or eval credibility land best.)

## DRILL

Take one enterprise you know well (a past employer works). Write the one-page "deployment gap memo" for bringing an LLM assistant to its core workflow: the five gap components as headers, two concrete blockers under each, and a guess at which single blocker kills the project if unmanaged. This memo format returns in Phase 1 discovery and Phase 8 cases.
