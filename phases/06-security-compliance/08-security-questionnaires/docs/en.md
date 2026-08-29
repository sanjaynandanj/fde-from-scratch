# Security Questionnaires: Answering the 300-Row Spreadsheet

**Phase 6 · Lesson 08 · ~1h**

## PROBLEM

Friday, 4pm. Champion pings: "our procurement team needs their vendor security questionnaire back by Monday close. It's attached." You open it — 312 rows across nine tabs, CAIQ v4 with the customer's twenty extra questions bolted onto the front, some marked "attach evidence." A quarter of the questions are ambiguous ("Describe your cryptographic module management program"). A quarter don't apply ("Does your SCADA network segment from IT?"). A quarter overlap ("Do you have MFA?" appears eight times worded differently). The last quarter are genuinely useful. Your CEO is out. Your account manager forwards it to you with a smiley face. If you answer it badly Monday, the deal slips a month. If you fake it, your future SOC 2 auditor will find the discrepancy. If you refuse to answer it, the deal dies.

Every FDE at a serious enterprise-AI company eventually does this. The senior move is not "answer faster" — it's *build a library so you never answer the same question twice*, and negotiate scope on the questions that don't apply.

## INTUITION

Four things to understand about questionnaires as a genre.

**They come in flavors.** **CAIQ** (Consensus Assessment Initiative Questionnaire) from the Cloud Security Alliance is the closest to a standard — ~260 questions mapped to CSA CCM controls. **SIG** (Standardized Information Gathering) from Shared Assessments is the financial-services heavyweight — SIG Core (~1,300 questions) and SIG Lite (~150). **VSAQ** (Vendor Security Assessment Questionnaire, Google-origin) is short and open-source. Then every large customer has a *custom* questionnaire — usually SIG or CAIQ with 20–100 bolted-on questions specific to their concerns. Learn to recognize the flavor in the first minute.

**Questions map to evidence.** Every well-formed question can be answered from one of a small set of underlying facts: SOC 2 report, ISO 27001 certificate, pen-test report, security policy document, DPA, architecture diagram, sub-processor list, backup/DR runbook, business continuity plan, incident-response plan. If your organization has these ten artifacts current and accessible, ~90% of a 300-row questionnaire is copy-paste plus context. The other ~10% requires the FDE brain — the questions that ask about the *specific engagement* you're running.

**Answers have three shapes.** *Yes with evidence* (attach or cite the artifact). *No with compensating control* (be honest about the gap and describe what you do instead). *N/A with rationale* (explain why the question doesn't apply — you're SaaS, they asked about datacenter physical security, here's how your infrastructure provider covers it). Auditors and reviewers respect all three; they punish only handwaving.

**The library compounds.** The first questionnaire takes 30 hours. The tenth takes 3 — because 90% of your answers are stored, indexed, and versioned. Building this library is arguably the highest-ROI unglamorous work in an enterprise-AI company.

## BUILD IT

Build the **Answer Library** — a canonical set of ~120 responses keyed to the questions you'll see over and over. Store as YAML or Markdown, one file per topic. Version it. Every engagement teaches you 5–10 new answers; every questionnaire completed reuses 80% of existing ones.

Structure per entry:

```yaml
- id: MFA-001
  topics: [access-control, authentication]
  aliases:
    - "Do you enforce multi-factor authentication for all users?"
    - "Is MFA required for administrative access?"
    - "Describe your authentication mechanisms."
  answer_short: >
    Yes. MFA is enforced via SSO (Okta) for all workforce accounts, including
    administrative access. Backup codes and hardware keys (YubiKey) are supported.
  answer_long: >
    All workforce accounts authenticate through Okta with mandatory MFA. Second
    factor is TOTP or FIDO2 (YubiKey preferred for administrative roles).
    Customer-facing product authentication is documented separately (see AUTH-002).
    Break-glass accounts require hardware-key MFA and are audit-logged.
  evidence:
    - artifact: soc2-typeii-2026-Q1.pdf
      section: "CC6.1, CC6.6"
    - artifact: security-policy-v3.2.pdf
      section: "3.2 Access Control"
  last_verified: 2026-07-15
  owner: security-team
```

Then the FDE overlay — three habits that separate a real library from a graveyard of stale docs.

1. **The intake pass, first.** Before answering any question, spend 30 minutes categorizing the whole spreadsheet: reusable (library hit), engagement-specific (needs your input), N/A (explain and skip), escalate (legal, security officer, or product decision needed). This triage keeps you from answering the first question for four hours and running out of Sunday.
2. **The "N/A" template.** ~15–20% of any questionnaire is genuinely N/A because the questioner used a template that assumes on-prem, or datacenter, or hardware. Have a canned N/A response per common category, always ending with what you *do* provide. "N/A — we operate as SaaS on AWS us-east-1; physical security is inherited from AWS SOC 2 (see AWS-INHERIT-001)." That answer works for a dozen questions.
3. **Versioned, dated, owned.** Every entry has a `last_verified` date and an owner. Anything older than 12 months is stale until re-verified. This is what prevents you from confidently answering "yes we rotate keys quarterly" for a control that quietly stopped two years ago.

Bonus: build a tiny script (or spreadsheet formula) that matches questionnaire rows against `aliases` fuzzy-string and pre-fills the answer + evidence columns. A 300-row questionnaire becomes 60 rows of real work.

## FIELD NOTES

- Never fabricate. Every fabricated answer is a landmine that detonates in an audit or an incident review. If the honest answer is "we don't do that yet, and here's the timeline," give it — enterprise reviewers respect honest gaps more than false yeses.
- Escalation paths matter. Some questions require a legal call ("Do you indemnify against IP infringement of AI-generated output?"), a product call ("Does your model retain customer data for training?"), a security-officer call ("What's your key-rotation cadence?"). Know who to ping and how fast they answer.
- The customer's reviewer is often a third-party firm (BitSight, SecurityScorecard, an outsourced GRC vendor) who doesn't know your product. Write for that reader — clear language, no jargon, one link per assertion. If they can't verify quickly, they mark it as risk.
- "Attach evidence" questions are opportunities. A pre-assembled evidence pack (SOC 2 + ISO cert + pen test summary + DPA + architecture one-pager) as PDF attachments is worth 30 answered questions — because reviewers browse the pack and mark related questions "verified via evidence."
- Timing is negotiable. If the deadline is Monday and the questionnaire is 300 rows, ask for Wednesday and get it 90% of the time. Rushing produces the fabrications that kill you six months later.

## INTERVIEW ANGLE

Questionnaire questions show up in the customer round and sometimes as a take-home. Interviewers are testing whether you'd fold under process pressure or navigate it.

1. "The customer sends a 300-row security questionnaire on a Friday afternoon with a Monday deadline. Walk me through your approach." (Triage first, evidence pack ready, library-driven answers with dates and evidence, honest N/As, escalations queued, and negotiate the deadline if needed. Bonus: name the specific artifacts and library shape.)
2. "How do you handle a question where the honest answer is 'no'?" (Answer honestly, describe the compensating control if any, give the roadmap timeline, and — where applicable — offer an alternative that neutralizes the underlying risk in this engagement specifically.)
3. "You realize a library answer written six months ago is no longer accurate. What do you do?" (Same-day: fix the library entry, note it as stale, and if it was submitted to any customer during the stale period, notify the account team so a correction can be issued proactively. Delayed corrections are the honest move and often *strengthen* the relationship.)

## DRILL

Find a public CAIQ v4 or a SIG Lite template — they are freely available. Take 20 representative questions across access control, data protection, incident response, and vendor management. Draft library entries for each, complete with short answer, long answer, evidence artifacts you'd cite (from your real security posture or a hypothetical one), aliases, and owner. Then write two "N/A with rationale" responses for questions that don't apply to a SaaS operating model. Save the file as the seed of your Answer Library — you will grow it into your most valuable non-code asset over your career.
