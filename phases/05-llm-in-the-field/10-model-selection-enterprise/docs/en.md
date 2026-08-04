# Model Selection in the Enterprise: Hosted, VPC, On-Prem Weights

**Phase 5 · Lesson 10 · ~1h**

## PROBLEM

The customer's CISO reads the DPA on Tuesday and calls a meeting Wednesday morning. "We can't send this data to a public LLM API. It's regulated." You had assumed hosted-Claude or hosted-GPT was the default because the pilot never explicitly discussed model deployment topology. The champion is uncomfortable; the CISO is firm; the VP is watching. You could argue about SOC 2 and enterprise privacy commitments (which do exist and are often sufficient), or you could hear what the CISO actually said: "regulated data cannot leave our environment." The pilot needs a model in their environment, not their DPA amended. You have four architectures to choose from. Picking the right one in the meeting — with the cost and quality trade-offs on the tip of your tongue — is the difference between a paused pilot and a signed procurement.

## INTUITION

Enterprise model deployment lives on a spectrum from convenient-but-external to controlled-but-heavy:

**Hosted API (public).** The provider runs the model in their cloud. You call an API. Fastest to ship, best models, subject to the provider's data policy. Fine for 70% of enterprise deployments once the SOC 2 and enterprise-privacy-terms conversation happens. Blocked by regulated data (HIPAA in some jurisdictions, defense, some financial workloads) and by customer risk appetite.

**Hosted API with private link (VPC-peered).** The provider offers a private connection so traffic doesn't traverse the public internet. Same model, better network story, same data policy. Often unblocks CISO objections about network exposure without unblocking their objections about data residency.

**VPC / dedicated deployment.** The provider (Azure OpenAI, AWS Bedrock, Anthropic on Bedrock, GCP Vertex) runs the model inside the customer's cloud region or in a dedicated tenancy. Data doesn't leave the region. The model weights are still the provider's; the customer just has stronger isolation guarantees. This is the sweet spot for regulated enterprise deployments — near-hosted convenience, strong data-residency and data-processing story.

**On-prem / air-gapped (open-weight models).** The customer runs open-weight models on their own hardware (Llama, Mistral, Qwen, etc.). Full control, full responsibility, worse models (the gap has narrowed but not closed), GPU hardware cost, ops burden. The right choice when the customer cannot allow *any* external data flow — defense, some intelligence, some healthcare. Also the right choice when the customer's request volume is so high that per-token pricing dwarfs the fixed infrastructure cost.

The decision axes: data-residency requirements, quality bar, latency budget, cost curve, operational tolerance, procurement timeline. Rarely is one architecture right for everything the customer wants to do — it is common to run a hosted model for internal-only tools and a VPC-deployed model for customer-facing ones.

## BUILD IT

A decision matrix you can bring to the CISO meeting:

```
                    Hosted API   Private Link   VPC/Dedicated   On-Prem/OSS
Time to ship          days         weeks          weeks-months    months
Model quality         top          top            top             mid-top
Data residency        provider     provider       customer region customer DC
Data policy           provider     provider       provider*       customer
Fixed cost            $0           low            low-mid         high (GPU)
Marginal cost         per-token    per-token      per-token       near-zero
Ops burden            none         low            low-mid         high
Regulated ok          sometimes    often          usually         always
```

*VPC deployments have provider-hardened data-processing terms; the model weights are still provider IP.

**A concrete decision tree you can walk through in the meeting:**

```
Can the customer send data to a public API under existing terms?
  Yes -> Hosted API. Ship.
  No  -> Can they use a private link to the same provider?
           Yes -> Private link. Ship in weeks.
           No  -> Do they have an approved cloud (AWS/Azure/GCP)?
                    Yes -> VPC deployment on Bedrock/Azure OpenAI/Vertex.
                    No  -> Do they have GPU hardware or budget?
                             Yes -> Open-weight on-prem.
                             No  -> This engagement needs an architecture
                                    conversation before a model conversation.
```

**Quality delta framing.** When you propose the OSS/on-prem path, tell the truth about the quality gap: on many enterprise tasks (extraction, classification, straightforward RAG) the gap is 5-15% and closing. On complex reasoning or long-context tasks, the gap is larger. Show them the eval-harness output for both models on their own golden set (Lesson 06); do not let the model choice be a religious argument.

## FIELD NOTES

- The CISO's real question is often not "which model" but "who do I sue when this goes wrong." Providers with enterprise-grade indemnification (Anthropic, OpenAI enterprise, Azure OpenAI) close deals that "the best open model" cannot. Bring the indemnification story to the meeting.
- "Air-gapped" means different things at different customers. Sometimes it means no internet; sometimes it means "no public internet but we have an approved gateway." Ask specifically what egress paths exist and whether an approved LLM provider gateway can be added — a lot of "air-gapped" customers have exceptions for approved vendors.
- Fine-tuning on-prem is the fantasy customers reach for. In practice, prompt engineering + RAG + light adapter tuning covers 90% of use cases with none of the on-prem-training ops burden. Do not accept a pilot scope that requires from-scratch training unless you have training-infrastructure engineers on the team.
- Procurement takes weeks for hosted, months for VPC, quarters for on-prem. Match the pilot design to the timeline. If the customer says "on-prem by Q4," start the VPC pilot in parallel — the customer's data policy will usually accept VPC for the pilot with a clear roadmap to on-prem for production.
- Multi-model is the honest end state. A hosted flagship for the hardest 10% of queries; a VPC mid-tier for the common 80%; a rules-based or small-model classifier for the trivial 10%. The router that decides is a customer artifact — make it configurable and audit-logged.

## INTERVIEW ANGLE

Model-selection questions probe whether you understand enterprise procurement and regulated-data constraints, not just model benchmarks. Interviewers listen for the four-architecture spectrum and the CISO conversation.

Sample questions:

1. "A regulated customer says they can't use the public API. Walk me through the options." (Private link, VPC on the major clouds, on-prem open-weight. Walk through the trade-offs and the decision tree; end with a recommendation that depends on the specific regulation.)
2. "When would you recommend on-prem open-weight models over a hosted service?" (Air-gapped or truly private-data environments, very high volume where per-token dwarfs infrastructure, customers who require full control of weights. Acknowledge the quality gap and ops burden explicitly.)
3. "The customer's CISO objects to model X's data policy. What do you do?" (Read the specific objection, offer VPC or private-link path with the appropriate provider, or an alternative provider with better terms. Never argue the policy; propose an architecture that removes the objection.)

## DRILL

Pick a hypothetical customer: mid-size healthcare payer, US-based, HIPAA-covered. Walk through the four-architecture decision tree for a member-services RAG deployment. Draft the two-page memo you would send the CISO: recommended architecture, alternatives considered, data-flow diagram, indemnification story, cost estimate at 10k requests/day, and the procurement timeline. Save it — you will adapt the same memo for every regulated customer you meet.
