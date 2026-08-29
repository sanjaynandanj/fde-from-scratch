# Incident Response When It's the Customer's Data

**Phase 6 · Lesson 09 · ~1h**

## PROBLEM

Wednesday, 6:47pm. You're closing your laptop when the alert fires: a teammate's laptop was stolen from a rental car in San Francisco. She had a local copy of a customer's redacted evaluation dataset for a bug repro; the disk was encrypted; she'd been signed in when the laptop was last on. You go through five reactions in ninety seconds — she's fine, disk encryption is fine, the data was redacted, but *was every field redacted?*, and *the DPA's breach-notification clock started at 6:47pm and runs 72 hours*. Now: what's the exact order of the next twelve moves? Who do you call first — your CEO, the customer's champion, the customer's DPO, or the police? What do you write down before you forget? What do you not put in Slack? Do you notify the customer if you're not sure it's a breach? Does the DPA say "confirmed" or "suspected"?

Incident response written on the fly is incident response you botch. Every FDE at a serious customer eventually has an incident. The senior move is having the runbook memorized before you need it, and executing it while other people react.

## INTUITION

Four principles anchor everything else.

**Time is the enemy, but calm is the answer.** DPA breach clocks are typically 24–72 hours from *discovery* — not confirmation, not investigation, not press coverage. But the first sixty minutes are where responders make the mistakes that turn a small incident into a regulatory event: destroying evidence, notifying the wrong parties, or writing something in Slack that ends up in a legal filing. Slow the *first* sixty minutes; then move fast.

**Contain, preserve, communicate, remediate — in that order.** *Contain* stops the bleeding (revoke credentials, isolate hosts, kill sessions). *Preserve* means don't wipe, don't reboot, don't overwrite — capture logs, memory, disk state before any remediation touches evidence. *Communicate* runs on a schedule to a named list of humans. *Remediate* is the last step and includes lessons learned. Doing them out of order — remediating before preserving — destroys the forensic trail regulators will ask for.

**Severity determines who wakes up.** A useful three-tier model: **Sev-1** (confirmed exposure of customer regulated data, active attacker access, or system integrity compromised) — wake the CEO, customer champion, customer security lead, and legal *now*. **Sev-2** (suspected exposure, unusual access without confirmed compromise, control failure without confirmed data impact) — email the same list within four hours, sync tomorrow. **Sev-3** (control gap discovered, near-miss, policy violation without exposure) — track and report weekly. Downgrading a Sev-1 later is fine; starting at Sev-3 and escalating is a career event.

**Written record is the deliverable.** The incident *report* — not the incident itself — is what regulators, auditors, and customers evaluate. Everything you do, in order, with timestamps, in a single append-only document. If a decision was made verbally, write it in. If a fact was unknown, write "unknown as of HH:MM" and update it. The report is the artifact that determines whether the customer keeps you.

## BUILD IT

Build the **Incident Runbook** — a printed one-page checklist, plus a template report. Two artifacts, both saved where you can grab them at 7pm on a Wednesday.

**Runbook (printed, on your desk):**

```
0.  T+0    Log start time and current known facts in the report doc.
           Assign roles: Commander (decisions), Scribe (report), Comms (out).
1.  T+5    Contain. Revoke tokens, isolate hosts, kill sessions.
           Do NOT reboot or wipe — preserve state.
2.  T+15   Preserve. Snapshot logs, memory, disk. Freeze rotation.
           Copy audit logs (Lesson 06) to safe location.
3.  T+30   Assess severity: Sev-1 / Sev-2 / Sev-3 with one-line rationale.
           If any doubt, treat as one level higher.
4.  T+45   Internal notify per severity: CEO, Sec Officer, Legal, PM.
           Use pre-agreed channel — not customer-shared Slack.
5.  T+60   Read the DPA. Confirm breach-notification clock and threshold.
           If clock started at T+0, remaining budget is 71h.
6.  T+2h   Customer notify per DPA: champion + DPO + security lead.
           Written, factual, no speculation. Template below.
7.  T+4h   Regulator? Only through Legal, only if DPA/law requires.
           Never solo.
8.  T+8h   First written update to customer.
           What we know, what we're doing, next update time.
9.  T+24h  Contain complete. Preservation confirmed. Root cause
           hypothesis. Second written update.
10. T+72h  Draft incident report. Root cause, timeline, impact,
           remediation, prevention.
11. T+7d   Post-incident review (blameless). Runbook updates.
           Customer-facing summary if requested.
12. T+30d  Verify remediation still holds. Close the ticket.
```

**Report template (append-only doc, timestamps every entry):**

```
INCIDENT #INC-2026-0007
Discovered:   2026-08-06 18:47 PT
Reported by:  <name>
Commander:    <name>
Scribe:       <name>
Severity:     Sev-2 (updated to Sev-1 at 19:22 — see entry)
DPA clock:    Starts 18:47 PT; 72h expires 2026-08-09 18:47 PT

SUMMARY (one paragraph, updated as facts change)

TIMELINE
18:47 PT — Discovery: teammate reports laptop stolen from rental car.
18:49 PT — SSO revoked for the account.
18:52 PT — Snapshot: laptop was signed in at last check-in 18:20 PT.
...

FACTS KNOWN                   FACTS UNKNOWN
- Disk encryption enabled     - Whether disk was unlocked at time of theft
- Data on laptop redacted     - Whether all fields in redacted set were
- SSO revoked at 18:49          fully redacted (verifying with vault log)

DECISIONS
[Time, Decider, Decision, Rationale, one line each]

CUSTOMER COMMUNICATIONS
[Time, Recipient, Channel, Summary, Link to sent artifact]

REMEDIATION ACTIONS
[Immediate + Long-term]
```

Three FDE-specific habits that separate a real runbook from a printed policy:

- **Practice it.** Twice a year, run a tabletop with your team on a fabricated incident. The first tabletop is embarrassing; the third one is fast. Never touch the runbook for real without having practiced it.
- **Own the customer notification template.** Legal will finalize the wording, but you should have a draft on your laptop that includes: what happened (facts only), when discovered, immediate containment actions, current assessment, what you're doing next, next update time, and one named contact. Sending a template is fast; drafting from zero at 8pm is slow.
- **Never speculate in writing.** Every written entry uses only confirmed facts. Speculation goes verbally, in the incident channel, marked as such. "Unknown" is a valid entry; "probably fine" is not.

## FIELD NOTES

- Most "incidents" are not incidents. Alerts, control failures, policy violations, and near-misses vastly outnumber real breaches — but you run the same first three steps for each (log, contain, assess) because you don't know which one this is until step 3.
- The first person you tell inside your company is your security officer or their delegate, not your CEO. The chain matters — CEO reactions can inadvertently trigger customer notification before you've read the DPA. Path the information correctly.
- Customer champions often want to help but are the wrong first contact. Their DPO/CISO is who the DPA obligates you to notify. Notify both — but do not treat the champion as the compliance channel.
- The blameless post-mortem is real. If your teammate whose laptop was stolen fears retaliation, she will hide the next incident, and the next one might be worse. Blame the missing control, not the person. Every finding becomes a runbook update.
- Regulator notification is Legal's decision, always. Never make it yourself — even when the answer feels obvious. Regulator relationships outlive incidents.

## INTERVIEW ANGLE

Incident-response questions come up in the customer round and — increasingly — in security-round scenarios. Interviewers listen for the *sequence*, not the panic.

1. "A teammate loses a laptop with customer data on it. Walk me through the first hour." (Log, contain, preserve, assess, notify internally, read the DPA — in that order and with rough timestamps. Bonus: name the DPA clock and the difference between suspected and confirmed exposure.)
2. "The customer's DPA requires 24-hour breach notification, but you're not sure yet if this is a breach. What do you do?" (Notify anyway with what's known — DPAs typically require notification of *suspected* incidents; under-notification is the career risk, over-notification is a repairable relationship. Coordinate with Legal on wording.)
3. "How do you run a blameless post-mortem when the root cause was a teammate's mistake?" (Focus on the missing control that let one mistake reach production; write the finding as a system-level gap; update the runbook. If someone leaves the meeting feeling blamed, the culture just lost.)

## DRILL

Take a system you own — personal or professional. Draft the runbook checklist above, customized to your stack: which credentials to revoke, which logs to snapshot, which humans to notify. Then run a tabletop against yourself: "at 6:47pm you learn that <plausible incident>." Set a timer for 60 minutes and execute the first six runbook steps *in writing* — no shortcuts, no phone calls, actually write the notification email drafts. Save what you produced. When a real incident hits, you'll have muscle memory instead of adrenaline making decisions.
