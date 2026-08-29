# AI-Specific Governance: Model Cards, Usage Policies, the EU AI Act

**Phase 6 · Lesson 07 · ~1.5h**

## PROBLEM

Your pilot at a European insurer works. The claims-triage LLM is routing correctly, saving twelve minutes per adjuster per case, and the CFO wants it live for renewal. Then their newly-hired AI Governance Officer joins the readout with a two-page memo: *"For any AI system involved in insurance underwriting or claims processing, we require an EU AI Act Article 9 risk management file, a model card per Article 13, human-oversight documentation per Article 14, and a fundamental-rights impact assessment before deployment."* You Google half of those terms during the meeting. Your team's answer — "we use GPT-4 and prompt it well" — lands badly. Legal pauses the go-live. A competitor with less product but a full governance dossier eats the renewal.

AI-specific governance is a new muscle for FDEs. The compliance frameworks in Lesson 01 barely mention it; the DPA in Lesson 04 has clauses that predate LLMs. What's emerging — the EU AI Act, NIST AI RMF, ISO/IEC 42001, and customer-side AI policies — will decide whether your pilot ships in 2026 and beyond. Learn to speak it before the AI Governance Officer joins the call.

## INTUITION

Four things to internalize.

**The EU AI Act is a product-safety regime.** It classifies AI systems into **Prohibited** (social scoring, real-time biometric ID in public with exceptions), **High-Risk** (Annex III list: credit scoring, employment decisions, essential services eligibility, insurance risk assessment, law enforcement, migration, education), **Limited-Risk** (chatbots, deepfakes — transparency obligations), and **Minimal-Risk** (everything else). Plus a parallel regime for **General-Purpose AI (GPAI)** models with additional obligations for **systemic-risk** models above certain compute thresholds. Most FDE pilots at regulated customers land in Annex III without realizing it — insurance, credit, HR, education, healthcare are all in scope.

High-risk obligations include: risk management system (Article 9), data governance (Article 10), technical documentation (Article 11), record-keeping/logging (Article 12), transparency to users (Article 13), human oversight (Article 14), accuracy/robustness/cybersecurity (Article 15), post-market monitoring, and a fundamental-rights impact assessment for deployers of certain systems. Prohibitions applied from February 2025; GPAI rules from August 2025; high-risk rules phase in through 2026–2027.

**Model cards are the deployer's artifact.** Google's 2018 "Model Cards for Model Reporting" paper defined the format that has become industry-standard and is now referenced (with different naming) in the AI Act, NIST AI RMF, and Anthropic/OpenAI system cards. Fields: intended use, out-of-scope uses, training data (or "not disclosed by provider" plus what you know), evaluation data and metrics, known limitations, ethical considerations, quantitative bias/fairness slices, contact for feedback. As an FDE using someone else's foundation model, you produce a *deployment card* — the system-level document that composes the provider's model card with your prompts, retrieval sources, evals, and controls.

**NIST AI RMF and ISO/IEC 42001 are the voluntary frameworks.** NIST AI RMF 1.0 (2023) organizes AI risk into four functions — **Govern, Map, Measure, Manage** — with practical categories under each. It's US-origin, voluntary, but referenced by federal contracts. ISO/IEC 42001 (2023) is the AI Management System standard — the ISO 27001 equivalent for AI, certifiable. US customers accept NIST; global customers increasingly want 42001. Both give you a defensible structure for saying "we govern AI."

**Usage policies are the last mile.** Providers publish acceptable-use policies (Anthropic, OpenAI, Google, Meta). Customers publish their own. When a bank's policy says "no LLM-generated content in customer-facing communications without human review," your architecture must enforce that, not just document it. Map the policies you're bound by early — provider-side, customer-side, and any regulator-side — and check for conflicts.

## BUILD IT

Build the **AI System Card** — the one-document dossier every FDE-shipped LLM system should carry from day one. Twelve sections, most fittable on one page each. Fill it while building; do not retrofit.

```
1.  System name & version              (semantic version + prompt hash)
2.  Intended use                       (specific tasks; the sentence that closes deals)
3.  Out-of-scope use                   (explicitly forbidden; anti-scope creep)
4.  Users & affected persons           (adjusters use it; claimants affected by it)
5.  Model composition                  (base model, provider, version, prompt template,
                                        retrieval sources, tools, fine-tunes)
6.  Data                               (training data disclosure from provider; RAG
                                        sources; evaluation datasets)
7.  Performance                        (eval-harness results — Phase 5 Lesson 06 —
                                        overall and by slice)
8.  Known limitations                  (hallucination rate, refusal rate, out-of-domain
                                        behavior, latency/cost budgets)
9.  Human oversight                    (where in the flow, what the human sees, what
                                        override authority they have, SLA)
10. Risk classification                (EU AI Act tier + rationale; NIST RMF categories)
11. Monitoring & incident response     (drift metrics, red flags, escalation — Lesson 09)
12. Governance metadata                (owner, reviewer, next review date, DPA references,
                                        provider AUP link, customer AI policy link)
```

The three FDE-specific moves that separate a real system card from a compliance PDF:

- **Version the prompt.** Prompts are code; they belong in the version field. When the model drifts because someone tweaked a prompt, the card and the audit log (Lesson 06) let you point at the change.
- **Wire the card to the eval harness.** Section 7 must be reproducible — a scripted run against the golden set, not a screenshot from Q1. When the customer asks "how do you know this is still 94% accurate?", you rerun and hand them the artifact.
- **Publish the out-of-scope list.** More AI deployments die from *scope creep into unintended uses* than from base failures. A one-line rejection ("this system does not decide claim denials — it triages") in the UI and in the card protects everyone.

## FIELD NOTES

- Most customers are still figuring out AI governance themselves. If they hand you a policy that predates ChatGPT, offer the collaborative version: "here's the system card format we use; would this satisfy your review?" You become the reference implementation for them.
- Foundation-model provider disclosures are patchy. You will not get training-data lineage from OpenAI. Say so plainly in Section 6; regulators expect the honest gap more than the fabricated answer.
- Human oversight is a design decision, not a checkbox. "A human reviews before send" only counts if the human actually has time, context, and authority to override. Auditors probe whether oversight is real or theatrical; design the loop that survives that probe.
- The AI Act's extraterritorial reach mirrors GDPR — providers and deployers outside the EU are in scope if the output is used in the EU. Do not assume geography saves you.
- "It's just a chatbot" is not a defense in Annex III domains. A chatbot that routes claims is claim-processing. Classify by function, not vibe.

## INTERVIEW ANGLE

AI-governance questions are the newest addition to FDE loops and — because they are new — a high-leverage differentiator. Interviewers listen for whether you can navigate a real conversation with a governance officer.

1. "How would you classify our claims-triage LLM under the EU AI Act, and what does that trigger?" (Annex III insurance-risk assessment → high-risk → Article 9 risk management, Article 14 human oversight, Article 13 transparency, Article 12 logging. Then explain how the system card wires each obligation to an artifact.)
2. "What goes in a model card for a system you built on GPT-5?" (System-level card composing provider disclosures with your prompt, RAG sources, evals, oversight, and monitoring — with the honest gaps around foundation-model training data called out explicitly.)
3. "The customer's AI policy conflicts with the provider's AUP — for example, they want the model to refuse certain topics the provider allows, or vice versa. What do you do?" (Map both, escalate the conflict to legal on both sides, and either implement the stricter requirement in your layer — system prompt, output filters, refusals — or negotiate a written waiver. Never ignore.)

## DRILL

Pick an LLM system you've built or would like to build. Draft the twelve-section System Card in a single markdown file. Do the honest version: fill in what you know, mark "unknown — provider does not disclose" where accurate, and note the specific artifacts that would populate each section in a real deployment (eval runs, prompts, retrieval indices). Then classify it under the EU AI Act — is it Annex III? Which article obligations apply? Write the one-paragraph rationale. Save the card as a template; you will produce five versions of it before the year is out.
