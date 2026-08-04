# The Compliance Alphabet: SOC 2, ISO 27001, HIPAA, GDPR, FedRAMP

**Phase 6 · Lesson 01 · ~1.5h**

## PROBLEM

Second call with a mid-market health insurer. The champion is warm, the use case is clean, the demo landed. Ten minutes in, their CISO joins the bridge and asks four questions in a row: "Are you SOC 2 Type II? HITRUST? Where do you store PHI? Do you have a BAA?" You have answers to none of them — your CEO handles compliance conversations, and she's on a plane. You freeze, promise a follow-up doc by Friday, and the deal slides two months while your team scrambles to produce evidence that already existed but wasn't in your head. The champion goes cold. Your competitor — half your product, twice your compliance answers — closes the account.

Compliance illiteracy is the single most common way FDEs lose deals they should have won. The frameworks aren't hard; they're just an alphabet nobody teaches you. Learn the alphabet, learn what each letter *actually protects*, and you stop being the reason security says no.

## INTUITION

Five frameworks cover 90% of what you'll be asked. Learn them as a small map, not a memorization drill:

**SOC 2** is an American attestation, produced by an auditor, that says your organization operates against the AICPA Trust Services Criteria — Security (always), plus optionally Availability, Confidentiality, Processing Integrity, Privacy. **Type I** is "you have the controls on paper on date X." **Type II** is "you operated them for 6–12 months and here's the evidence." Type II is what enterprise buyers actually want. SOC 2 is *your* posture — it says nothing about the customer's data class.

**ISO 27001** is the international equivalent — a certification (not an attestation) that you run an Information Security Management System with documented risk treatment. Europe and Asia weight it heavier than SOC 2; global buyers want both.

**HIPAA** is US healthcare data law. Two roles: Covered Entity (the hospital) and Business Associate (you, if you touch Protected Health Information). The controlling document is a **Business Associate Agreement (BAA)** — no BAA, no PHI, no exceptions. HITRUST is a certifiable framework that maps HIPAA + others into auditable controls; some payers demand it.

**GDPR** is EU personal-data law, effective 2018, extraterritorial (applies if you process EU residents' data regardless of where you're incorporated). Two roles: **Controller** (decides why and how) and **Processor** (acts on the controller's instructions). Vendors are almost always processors. Governs consent, purpose limitation, data minimization, subject rights (access, deletion, portability), breach notification within 72 hours, and cross-border transfer via Standard Contractual Clauses or adequacy decisions. CCPA/CPRA is the California cousin; Brazil's LGPD is the Latin cousin.

**FedRAMP** is the US federal government's cloud authorization program. Levels: Low, Moderate, High (plus DoD IL2/IL4/IL5). Moderate is the practical floor for civilian agencies. Getting FedRAMP-authorized takes 12–24 months and seven figures; **operating on a FedRAMP-authorized platform** (AWS GovCloud, Azure Government) is what your engagement will actually require. StateRAMP is the state-government analog.

The FDE mental model: **framework, jurisdiction, data class, evidence artifact**. When a CISO asks "are you SOC 2?" she means: *give me the report so my third-party-risk team can check the box*. The right answer is never "yes/no" — it's "Type II covering Security and Confidentiality, report available under NDA, latest audit period ended March, one qualification around access review cadence which we remediated in Q2." That sentence closes deals.

## BUILD IT

Build the **Compliance Map** — a single-page reference you carry into every discovery call. Format: a 5-row table with these columns, filled from memory:

| Framework | Jurisdiction | Who cares | Data class | Artifact you must produce | Time-to-obtain |
|---|---|---|---|---|---|
| SOC 2 Type II | US-origin, global-accepted | Every enterprise buyer | Any customer data | Auditor report (under NDA) | 12+ months of evidence |
| ISO 27001 | Global | EU, APAC, global buyers | Any customer data | Certificate + Statement of Applicability | 6–12 months |
| HIPAA + BAA | US healthcare | Payers, providers, pharma | PHI | Signed BAA + policies + risk assessment | Days (BAA); ongoing (posture) |
| GDPR (Processor) | EU personal data | Any EU-resident data | Personal data | DPA + SCCs + Records of Processing | Days (contracts); ongoing (posture) |
| FedRAMP Moderate | US federal | Civilian agencies | CUI, agency data | ATO letter + SSP + POA&M | 12–24 months |

Now add the FDE column that CEOs skip: **what you can offer in week one if you don't have it yet.** Compensating controls: run in the customer's tenant so their compliance covers you; sign an NDA-only-mode DPA; pseudonymize before egress (Lesson 03); offer a security questionnaire response (Lesson 08). Every "no" has an inheritable-controls answer.

Tape the map inside your notebook. When a stakeholder says a letter, you know four things about it in under three seconds: what it protects, who signs it, what document proves it, and what you offer if you don't have it.

## FIELD NOTES

- Frameworks overlap heavily — SOC 2, ISO 27001, and HIPAA share ~70% of underlying controls. If you're SOC 2 Type II, the HIPAA gap is usually policies, BAA, and one or two specific safeguards, not a rebuild.
- The report is not the posture. A SOC 2 with material exceptions is worse than no SOC 2 — enterprise reviewers read the "Section 5: Other Information" the auditee thought nobody would read. Know your own qualifications before the CISO does.
- "We're SOC 2 in progress" is a real answer if you can name the auditor, the scope, and the target date. It stops being a real answer the second month you say it.
- FedRAMP-authorized *infrastructure* (running on GovCloud) is not the same as being FedRAMP-*authorized* yourself. Say the exact sentence; do not let the customer conflate them.
- GDPR fines are 4% of global revenue for the top tier — but the field pain is usually the 72-hour breach clock, not the fine. If your incident-response runbook (Lesson 09) doesn't start the clock on hour zero, you will miss it.

## INTERVIEW ANGLE

FDE loops probe compliance literacy in the customer round and sometimes the system-design round. They are not testing whether you can recite the alphabet — they are testing whether you can hold a real conversation with a CISO without your CEO on the line.

1. "A healthcare customer asks if you're HIPAA-compliant. What do you say?" (They want the ladder: "HIPAA doesn't certify vendors — the right question is whether we can sign a BAA, what safeguards we operate, and what our subprocessors look like. Yes to all three, and here's the artifact." Bad answer: "yes.")
2. "Walk me through the difference between SOC 2 Type I and Type II, and which one your buyer will accept." (Point-in-time vs operating-effectiveness over 6–12 months; enterprise buyers want Type II, period.)
3. "The customer is in Germany and asks about data transfers. What's the FDE-level answer?" (SCCs post-Schrems II, plus the practical: offer EU-region hosting or run in their tenant.)

## DRILL

Pick three real companies you'd want to work at as an FDE (e.g., Anthropic, Palantir, Sierra). For each, spend 15 minutes finding their public compliance posture — trust center, security page, sub-processor list. Fill in the Compliance Map for each: which frameworks, which regions, which subprocessors. Then write the 30-second CISO answer for each ("we operate under SOC 2 Type II covering… available under NDA at…"). Practice saying it out loud until it sounds boring. Boring is the goal — boring compliance answers close deals.
