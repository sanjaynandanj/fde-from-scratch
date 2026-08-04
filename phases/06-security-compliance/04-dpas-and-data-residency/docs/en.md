# DPAs and Data Residency: Reading the Contract You're Bound By

**Phase 6 · Lesson 04 · ~1h**

## PROBLEM

Week six of a European engagement. Your team's RAG demo is landing. The CTO wants to move to production and asks the obvious next question: "can we use OpenAI for the reasoning layer?" You say yes — it's the good model, the pilot uses it, latency is fine. Two days later the customer's DPO circulates a redlined Data Processing Agreement and highlights three lines: "personal data shall not be transferred outside the EEA except under approved SCCs"; "sub-processors require 30-day prior written notice"; "the model provider is not on the current sub-processor list." Your "yes" was a promise you didn't have authority to make. The pilot pauses while your legal and their legal argue about Schrems II for four weeks. You lose the quarter.

The DPA is the shortest, most-ignored, most-load-bearing document in every enterprise engagement. FDEs who can read one — actually read one, not skim — ship faster because they stop making promises the contract has already broken.

## INTUITION

Four concepts do most of the work.

**Controller vs Processor.** The customer is (almost always) the **Controller** — they decide why and how the data is used. You are the **Processor** — you act on their instructions. Your subprocessors (cloud, LLM, monitoring) are **Sub-processors**. This chain matters legally: the Controller is on the hook to regulators; you are on the hook to the Controller; sub-processors are on the hook to you. Under GDPR, the Controller must approve your sub-processors, usually with a notice-and-objection clause.

**The DPA itself.** A Data Processing Agreement is the contract that lets a controller share regulated data with a processor. Required under GDPR Article 28. It defines: purpose and duration of processing, categories of data and data subjects, controller instructions, confidentiality, security measures, sub-processor terms, subject-rights assistance, breach notification timelines (usually 24–72h), audit rights, deletion/return at end of contract. Every enterprise vendor has a template DPA; every enterprise customer redlines it. Learn to read the redlines.

**Data residency.** Where the bytes physically sit and where they may transit. EU customers often require data to stay in the EEA. India, Russia, China, and increasingly the Gulf require in-country residency for certain data classes. Residency and *sovereignty* are not the same — sovereignty adds "and no non-local entity may compel access" (which is why US CLOUD Act keeps European DPOs awake). If the customer requires sovereignty, hosted US LLMs are simply off the table until an EU-sovereign inference option is contracted.

**Transfer mechanisms.** GDPR forbids sending personal data outside the EEA unless a valid transfer mechanism applies: **adequacy decisions** (the destination country is deemed adequate — UK, Switzerland, Japan, and post-DPF the US with conditions), **Standard Contractual Clauses (SCCs)** (contractual guarantees, updated in 2021), or **Binding Corporate Rules** (intra-group only). Post-Schrems II (2020) SCCs alone are not enough for US transfers — you also need a Transfer Impact Assessment and often supplementary technical measures (encryption with customer-held keys, pseudonymization). The 2023 EU-US Data Privacy Framework restores adequacy for DPF-certified US processors, but not everyone is certified and the framework itself is being challenged.

## BUILD IT

Build the **DPA Read-Through Checklist** — the twelve-clause pass every FDE runs on every DPA in the first week of an engagement. Print it, staple it to the DPA, mark it up in blue pen.

```
1.  Roles.               Who is Controller / Processor / Sub-processor?
2.  Purpose.             What are we allowed to do with the data — precisely?
3.  Data categories.     What classes of data does the DPA cover?
                         (PII / PHI / financial / children's data?)
4.  Data subjects.       Whose data — employees, customers, patients, minors?
5.  Residency.           Where may the data be stored, processed, transited?
6.  Sub-processors.      Approved list; notice period; objection rights.
7.  Transfer basis.      SCCs / adequacy / DPF / BCRs — which?
8.  Security measures.   Annex II — encryption, access, logging, testing.
9.  Breach clock.        Hours from discovery to notification to Controller.
10. Subject rights.      How you assist DSARs (access, erasure, portability).
11. Audit rights.        Frequency, notice, cost, scope.
12. Termination.         Delete-vs-return, verification, retention overrides.
```

Then the FDE overlay — three questions the checklist doesn't ask but you must:

- **Which clauses does my current architecture already violate?** Sub-processor lists are the top offender. If your monitoring stack sends logs to a US SaaS and the DPA is EU-only, you've violated Clause 6 before you shipped a line of code.
- **Which clauses does my roadmap violate?** Adding a hosted LLM in month two requires an amendment. Adding a new region for redundancy requires an amendment. Plan the amendment cadence.
- **Where's the sub-processor list stored, and is it a real document I can update?** If sub-processors are named inline in the DPA, every change is a legal negotiation. If they live in an appendix updated by notice, you can move. The FDE move is to negotiate the *appendix* structure early.

Sign it with your champion — actual signature, actual date, actual "I've read the twelve clauses and here's what breaks my current plan." That memo is the artifact you fall back on when someone six weeks later asks "why can't we just use the hosted LLM?"

## FIELD NOTES

- The DPA lives in a folder your CSM or legal team owns. Ask for it in week one. If they can't produce it in an hour, that's a finding — someone is going to sign something they haven't read.
- Redlines are signal. If the customer heavily redlined the sub-processor clause, they've been burned before. If they heavily redlined the audit clause, they expect to audit. Read the redlines as a psychological profile of the security org.
- Residency requirements are often *policy*, not law. "Our data must stay in the EEA" is sometimes a hard GDPR posture and sometimes a preference the CISO negotiated with the board. The distinction changes what's negotiable — ask.
- The breach clock starts on *discovery*, not confirmation. Discovering an anomaly at 5pm Friday doesn't buy you the weekend. Lesson 09 builds the runbook that respects that clock.
- Sub-processor lists are the fastest thing to break with an LLM stack. Adding a new model provider mid-engagement is the modern equivalent of adding a new cloud region — it triggers notice, objection windows, and sometimes contract amendments. Assume every model swap is a legal event.

## INTERVIEW ANGLE

DPA questions show up in the deployment round and the customer round. Interviewers are testing whether you can slow down at the right moment.

1. "The customer wants a feature that requires calling an external API. Walk me through what you check before saying yes." (DPA sub-processor clause, transfer basis, security annex, breach clock — plus the mitigation ladder: in-tenant deployment, self-hosted alternative, amendment negotiation.)
2. "Your EU customer says 'no US cloud.' What are their real options?" (EU-region hosting on hyperscaler with SCCs plus supplementary measures; EU-sovereign cloud provider; on-prem. Explain the trade-offs of each in one sentence apiece.)
3. "What does 'processor' mean and when might you accidentally become a joint controller?" (Joint controllership triggers when you influence *why* the data is processed, not just *how*. It matters because joint controllers share regulator liability. Common trap: training a shared model on customer data.)

## DRILL

Find a public DPA — most large SaaS vendors post them (Notion, Stripe, Vercel, OpenAI). Pick one. Run the twelve-clause checklist against it and mark up the document. Then answer three questions in writing: (1) if you were an FDE deploying this vendor's tool into a Frankfurt-based bank, which clauses would you need to escalate before signing? (2) what's the sub-processor list — where does it live, how is it updated? (3) what would a Schrems II-era Transfer Impact Assessment on this vendor conclude? Save the marked-up DPA as your reference — the next customer's DPA will feel familiar.
