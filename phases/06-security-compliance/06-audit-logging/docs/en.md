# Audit Logging: Who Saw What, When, and Can You Prove It

**Phase 6 · Lesson 06 · ~1h**

## PROBLEM

Ten weeks into a regional-bank pilot. The champion sends a Sunday-evening Slack: "our compliance team has questions about vendor access to customer records — can you produce a report by Tuesday of every record any of your team members viewed in September, with timestamps and reasons?" You have application logs. You have no idea whether they capture PII-record access with the fields compliance wants. You spend Monday grepping through JSON with a lump in your throat and produce a partial answer Tuesday afternoon — accurate for API calls but missing the console sessions where two teammates queried the database directly. Compliance flags a control gap. The bank's regulator is doing their own audit next month. Your pilot becomes an exhibit.

Audit logging is the boring lesson that saves careers. It is written before you need it because you cannot write it after. And "we have logs" is not the same as *audit-quality* logs — the difference is what compliance and regulators actually want to see.

## INTUITION

Four things separate an audit log from a debug log.

**Non-repudiation.** An audit event answers: *who* (named identity, not `system`), *what* (specific action and resource), *when* (server-side timestamp with timezone), *where* (source IP or workload), and *why* if the action requires justification (break-glass, DSAR fulfillment, override). "Who" is the most-often botched field — logs full of `svc_pilot` tell you nothing. Use SSO subject IDs, service-account IDs with attribution back to a human deployer, request IDs that trace to a session.

**Immutability.** Audit logs must be tamper-evident. Debug logs live in the app's control plane; audit logs live somewhere the app can *append to but not modify or delete*. In practice: append-only cloud logging (CloudWatch, Cloud Logging with retention lock), write-once object storage, or a hash-chained log where each event includes the hash of the previous. The property you're proving is *"nothing was silently removed."*

**Retention with a defensible policy.** SOC 2 wants at least one year; HIPAA six years; some financial regimes seven. Retention that's too short fails audit; retention that's too long creates liability (a subject-access request under GDPR will demand that data too). Write the policy down and let the storage system enforce it. Do not rely on humans remembering.

**Coverage of the high-risk verbs.** Not every event needs an audit trail. Focus on: authentication (login, logout, failure, MFA challenge), authorization changes (grants, revocations), data reads of restricted classes (per record, not per query), all writes and deletes of regulated data, admin actions, exports (the query, the count, the destination), consent changes, and — for FDE-y systems — model interactions (prompt in, response out, model version). If a control review would ask "did anyone read this record?", the answer must be traceable to one identity.

## BUILD IT

Build the **Audit Event Schema** — an eight-field JSONL record you can drop into any pilot in an hour and defend in an audit meeting.

```json
{
  "ts": "2026-08-12T14:33:07.412Z",
  "actor": {
    "id": "sso|okta|00u3xn...",
    "kind": "user",
    "email": "sanjay@ourco.com",
    "session_id": "sess_9c2f..."
  },
  "action": "record.read",
  "resource": {
    "type": "claim",
    "id": "CLM-84213",
    "class": "PHI"
  },
  "outcome": "allow",
  "reason": "case_review:CR-2226",
  "context": {
    "ip": "10.24.7.44",
    "workload": "pilot-api@v1.4.2",
    "request_id": "req_a9d3e..."
  },
  "prev_hash": "b7f0...",
  "self_hash": "3ec1..."
}
```

Design notes for each field:

- `ts` — server-side, UTC, ISO 8601 with milliseconds. Never trust the client.
- `actor` — SSO subject preferred; email is a *display* attribute (people rename). `session_id` binds a stream of events to one login.
- `action` — verb.noun, from a fixed vocabulary you publish (`record.read`, `record.export`, `role.grant`, `auth.login`, `llm.invoke`, `break_glass.unseal`).
- `resource` — type, ID, and **class label** (Confidential, PHI, PII). The class label is what lets compliance run "show me every PHI read this quarter" without joining to another system.
- `outcome` — `allow` / `deny` / `error`. Denies are half the audit value; they show the *system worked as designed*.
- `reason` — required for privileged verbs; free text tied to a ticket ID.
- `context` — network + workload attribution. `request_id` lets you correlate to debug logs when needed.
- `prev_hash` / `self_hash` — hash-chain the log file. Each event's `self_hash = sha256(prev_hash + canonical_json(event))`. Any deletion or edit breaks the chain and is detectable. Verification is one linear scan.

Then the FDE overlay — three habits that turn the schema into a real control:

1. **Emit at the boundary, not the app.** Wrap the data access layer (repository, ORM, HTTP handler) so every read of a classified resource emits an audit event automatically. If audit logging is per-endpoint discipline, it will drift.
2. **Test the queries.** Write and store the exact SQL/log-query for "every read of PHI records in the last 30 days by human X" and run it as a self-test in CI. Auditors do not want to see you invent the query under time pressure.
3. **Redact the log too.** Free-text reasons and query strings can themselves contain PII. Run the redactor (Lesson 03) on the fields most likely to leak.

## FIELD NOTES

- Auditors ask for *evidence of the control*, not the log itself. That evidence is often: a screenshot of the log query, the query text, a sample of matching events, and the retention policy setting. Prepare the evidence pack, not raw dumps.
- SSO integration in Lesson 03 of Phase 4 is what makes `actor.id` non-repudiable. Without SSO, every audit log is a debate about who was actually logged in.
- Log volume is a governance question. A high-traffic read log will be huge; sampling breaks audit non-repudiation. The move is to log full for restricted classes and sample for lower classes — with the sampling ratio written down.
- Logs that live only in the same account as the app are not a control. If a compromise gives the attacker access to the app, they also delete the logs. Ship audit logs to a separate account/tenant that the app account has *append-only* permission to.
- The single most common gap: read-only console sessions (Snowflake worksheet, RDS query editor, mongo shell) that bypass the app-level audit. Either federate console access through SSO with audit forwarding, or accept the gap in writing and add compensating controls.

## INTERVIEW ANGLE

Audit-log questions show up in the deployment round and the customer round. Interviewers listen for whether you understand the *evidence* aspect, not just the logging aspect.

1. "The customer asks for a report of every user who accessed patient records last month. Walk me through what you need to produce it." (Schema fields, log location, retention, query, evidence pack. Bonus: acknowledge and cover the console-access gap.)
2. "Design an audit-logging system for a pilot that will graduate to production. What's the minimum you'd ship in week one, and what would you add for GA?" (Week one: schema, boundary emit, separate storage, retention. GA: hash chain, alerting on anomalous access patterns, DSAR-fulfillment tooling.)
3. "How do you make logs tamper-evident without a full SIEM?" (Hash chain plus append-only storage; explain what each defends against — chain detects edits, append-only prevents deletions. Then honestly state the limits.)

## DRILL

Take a small API you own — a personal project or a Phase 2 pilot. Add the eight-field audit event schema above to every read/write of a "classified" resource. Ship events to a separate append-only file. Implement `prev_hash`/`self_hash` chaining and write a verifier that walks the file and fails on any break. Then run three self-tests: (1) can you answer "who read record X last week?" in one query? (2) does the verifier catch a deliberately edited event? (3) does the retention setting actually delete events older than the policy? Save the code and the schema; you will paste both into three future engagements.
