# Enterprise Topology: Where Your Code Is Allowed to Run

**Phase 4 · Lesson 01 · ~1h**

## PROBLEM

Your team wins a pilot with a mid-tier US bank. The champion is excited, the data is interesting, and you have a working demo running on your laptop against an anonymized sample. You send over the standard architecture diagram — your SaaS in AWS us-east-1, TLS everywhere, SOC 2 Type II attached. The bank's cloud governance lead responds with a two-line email: "We do not permit customer data to leave our tenancy. Please share your VPC-deployable and BYOC options." Nobody on your side has a clean answer. The pilot slips three weeks while your infra team retrofits a Terraform module and your legal team argues about who owns the KMS keys. Meanwhile the champion's calendar fills up with other priorities.

The trap wasn't technical — the trap was assuming there was one place your code could run. Enterprises have a *topology*: a fixed set of environments where third-party software is allowed to execute, each with different rules. If you don't know which zone the customer is offering you before you scope the pilot, you will always end up re-architecting on their clock.

## INTUITION

Every enterprise you deploy into sorts third-party software into roughly five zones. From most permissive (fastest to ship) to most restrictive (longest lead time):

1. **Vendor SaaS.** Their users hit your `app.yourco.com`. Their data crosses your boundary. You own the whole stack. This is what your marketing site sells. Regulated enterprises frequently disallow it for anything above internal-use data.
2. **Vendor SaaS with private link.** Same as above but the customer's traffic never touches the public internet — they connect via AWS PrivateLink, Azure Private Endpoint, or a dedicated tunnel. Common concession from customers who dislike SaaS but tolerate it with network isolation.
3. **Single-tenant in vendor cloud.** You deploy a dedicated stack (own VPC, own DB, own KMS key) but you still operate it. The pitch: "your data never mixes with any other customer's."
4. **BYOC / customer-tenant deployment.** Your software runs in the *customer's* cloud account — their AWS org, their subscription, their GCP project. You may have limited operator access via cross-account IAM. This is Palantir Foundry BYOC, Snowflake native apps, Databricks on the customer's VPC. Common for regulated verticals.
5. **On-prem / air-gapped.** Their data center, or a classified enclave with no internet. You ship a tarball or an OVA. You do not have live access. Every operation is scripted or done by their staff via runbook.

Each zone shifts three things: **who operates it** (you → them), **how you update it** (push → shipped release), and **what data can flow** (everything → nothing outbound). Zone 1 lets you deploy in an afternoon; zone 5 lets you deploy in six to twelve months.

The FDE's job at the start of an engagement is not to argue the customer up to zone 1. It is to figure out which zone their security and cloud governance teams will *actually* approve for this data class, and then design the pilot for that zone from day one. Retrofitting a SaaS app into BYOC in month three is the classic engagement-killer.

## MAP IT

No code — build the topology map on paper before scoping the pilot.

1. Draw the five zones as concentric rings, most permissive outside, air-gapped in the center. Label each ring with: who operates, where data lives, how you push updates, typical lead time.
2. For each zone write one **hard blocker** — the thing that makes this zone unavailable. Examples: "SaaS blocked because our data is PCI regulated", "BYOC unavailable because they have no cloud team, only data centers".
3. Prepare six questions for the customer's cloud/security team. Aim for a 30-minute call in week one. Sample: *"Do you allow SaaS for this data class?"*, *"Do you have a BYOC pattern already published for other vendors?"*, *"Which cloud region must this run in?"*, *"Who owns the KMS keys — you or us?"*, *"Do you have an existing PrivateLink/Transit Gateway posture?"*, *"What's the fastest zone you've approved a vendor into in the last 12 months?"* That last one is the honest question — their history predicts your timeline.
4. Write the pilot's target zone at the top of the scope doc. Every architectural decision downstream inherits from it.

## FIELD NOTES

- Regulated customers (banks, health, defense, utilities) usually offer only zones 3–5. Ask which one before the second meeting. If they can only host you in zone 5 and your product has never shipped air-gapped, that is a scoping conversation with your own team, not a heroic engineering push.
- "We're a cloud-first company" from the customer does not mean zone 1. It usually means "we have a mature BYOC pattern that other vendors use — please follow it." The pattern is often documented; ask for it.
- The zone the customer offers is not always the zone their business wants. IT/security guards the moat; the champion may push you to escalate. Do not go around IT — they will remember, and they sign the renewal.
- Zone drift is real: pilots start in zone 1 sandboxes with fake data, then production requires zone 3. Plan for the drift; do not rewrite from scratch. Twelve-factor discipline, config over code, and stateless services buy you portability across zones.
- The customer's answer to "which region" tells you about data residency. If they say Frankfurt, GDPR is now a first-class constraint on your pilot — Phase 6 territory.

## INTERVIEW ANGLE

Enterprise topology comes up in system-design and behavioral rounds. Interviewers want to see that you understand the operational cost of each zone and can price a deployment in weeks, not vibes.

Sample questions:

1. "A bank wants our platform but says data can't leave their AWS org. What are your options and what changes in your architecture?" (BYOC path; single-tenant stack in their account; cross-account IAM for operator access; likely their KMS keys; likely their VPC and egress policy.)
2. "The customer offers you two deployment paths — single-tenant in your cloud, or BYOC. Which do you recommend for a 30-day pilot?" (Single-tenant is faster to stand up if their data class allows it; BYOC almost never fits inside 30 days for a first engagement; make the pilot scope match the fast path.)
3. "How do you find out which topology a new customer will actually approve?" (Ask their cloud/security team directly in week one; ask for their published vendor patterns; ask for the fastest recent vendor onboarding as a proxy for reality.)

## DRILL

Take a real product you know (yours or a public one). Write a one-page "deployment topology brief" that lists which of the five zones it currently supports, which it does not, and what the engineering work would be to add the next zone up in restrictiveness. Estimate that work in weeks. Then write one paragraph on which customer segments unlock at each zone — this is exactly the artifact your engineering leadership needs when a new deal shows up.
