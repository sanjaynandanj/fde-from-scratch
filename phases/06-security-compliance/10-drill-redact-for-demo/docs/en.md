# Drill: Redact a Customer Dataset for Use in a Demo

**Phase 6 · Lesson 10 · ~1h**

## PROBLEM

Thursday morning, executive review Monday afternoon. The customer's SVP wants to see the pilot demoed against *their* data, not the seeded dataset you've been using — "so the room believes it." The DPA forbids customer personal data leaving their tenant. The customer's data has emails, phone numbers, names, addresses, four internal ID formats, free-text notes, and — you discover on inspection — one column that holds SSNs the customer swore they'd removed. You have four working days to produce a demo dataset that is (a) contractually clean, (b) still analytically meaningful (dedup works, joins work, entity counts look right), (c) visually credible (the SVP will notice if every name is "John Doe"), and (d) reproducible so you can regenerate it after the next data refresh.

This is the drill Phase 6 has been building toward. Every technique in the preceding nine lessons plays a role: classification (Lesson 02), the redactor (Lesson 03), DPA scope (Lesson 04), least-privilege access to the source (Lesson 05), audit logging every touch (Lesson 06), governance around the LLM if you use one (Lesson 07). Put them together against a real dataset in the field.

## INTUITION

Six design decisions govern demo-quality redaction.

**Do it in-tenant.** Redaction that happens after data leaves the customer's environment is theater — the DPA breach already occurred. The redactor runs where the raw data lives. Only redacted output crosses the boundary. This is the architecture decision, not a policy statement.

**Consistent pseudonymization beats masking.** Same input, same token. Preserves distinct-count, joins, threading (Lesson 03). Demos die on data that no longer joins.

**Realistic surface, safe underneath.** For visual credibility, replace tokens with *plausible* values: a real-looking-but-fake name generator ("Rowan Hayes"), a synthetic-but-valid-format phone number, an address in the right city with the wrong street. The audience sees a realistic screen; the values reveal nothing. Never use real names of celebrities, employees, or anyone else — plausible must also mean invented.

**Distribution matters.** If the source has 43% of records from California and 12% from Texas, the demo dataset should too. If the source has one customer with 800 transactions and most with fewer than 10, preserve the long tail. Distribution preservation is what makes analytics on the demo dataset *behave the same way* as production — which is what makes the demo credible.

**Small-cell suppression.** Even after redaction, a diagnosis code appearing in only one row plus a ZIP-3 plus an age can re-identify. Aggregate or suppress cells with counts below a threshold (k=5 is a common floor; k=10 is defensive). Apply per-slice, not just overall.

**Reproducible and auditable.** The redaction pipeline is code, in version control, with a seed. Regenerating tomorrow produces the same tokens for the same inputs. Every run writes an audit-log entry (Lesson 06) linking the source snapshot ID to the output snapshot ID with actor and timestamp. When the DPO asks "who touched what," you answer in one query.

## BUILD IT

Build the **Demo Redaction Pipeline** — six stages, each a small script, chained by a driver. Run it in-tenant, output only the last stage across the boundary.

```
Stage 1: PROFILE
  Input:  raw table snapshot
  Output: field inventory with class labels (Public/Internal/Confidential/Restricted)
          + regulatory overlays (PII/PHI/PCI) + null rates + distinct counts.
  Human review: DPO signs off on the classification before Stage 2 runs.

Stage 2: SCOPE
  Input:  profile + demo scenario
  Output: allowlist of fields to include; denylist explicit.
          Rule: any Restricted field either gets pseudonymized (Stage 3),
          synthesized (Stage 4), aggregated (Stage 5), or dropped.

Stage 3: PSEUDONYMIZE
  Input:  scoped rows
  Uses:   the Lesson 03 Redactor (consistent tokens, vault stays in-tenant).
  Output: rows where PII fields hold tokens like [EMAIL_1], [PHONE_1].

Stage 4: SYNTHESIZE
  Input:  pseudonymized rows
  Uses:   deterministic (seeded) fake-value generator, keyed on the token.
          [EMAIL_1] -> "rowan.hayes@examplemail.com" — same token,
          same value across every table.
  Output: rows that look real and thread correctly.

Stage 5: SUPPRESS + PERTURB
  Input:  synthesized rows
  Rules:  drop cells with k < 5 in any slice you'll demo. Add small noise
          to numeric aggregates (differential-privacy-flavored, not full DP).
          Round dates to week; round dollars to nearest ten.

Stage 6: VERIFY
  Input:  Stage 5 output
  Runs:   (a) the leak scanner — regex sweep for any residual PII patterns
             (Lesson 03 idempotency assertion, applied to the whole dataset).
          (b) the distribution-fidelity test — key aggregates from source
             within 3% of the demo dataset (proves demo is representative).
          (c) the join-integrity test — every foreign key still resolves.
          (d) small-cell audit — no cell below k threshold.
  Only after all four pass does the output artifact leave the boundary.
```

Wrap it in a driver script that:

- Takes a source snapshot ID as input; refuses to run without one (no "latest" — reproducibility).
- Emits an audit event per stage (Lesson 06 schema): actor, action, resource, input snapshot, output snapshot, duration, verify results.
- Writes a **Redaction Manifest** alongside the output: source snapshot, seed, timestamp, classification map, stage results, verify pass/fail. The manifest is what the customer's DPO reviews before approving egress.
- Fails closed on any verify failure. Missing the demo is a survivable outcome. Leaking is not.

## FIELD NOTES

- The SVP will ask "is this real data?" during the demo. The correct answer is *"this is a redacted copy of your production data, generated Monday by our in-tenant pipeline; the manifest is attached to the pilot doc."* That sentence transforms a compliance risk into a professionalism signal.
- The DPO will not read the code. They will read the manifest, the classification review, and the verify results. Design those artifacts for them, not for engineers.
- Names are the perennial trap. Free-text notes contain names the schema didn't advertise. Run a name-detector pass (NER model, if available in-tenant, or a curated first-name/last-name list) and pseudonymize free-text names — or drop the free-text columns entirely for demo purposes and note the reduction.
- Dates leak identity via reasoning. "The patient admitted 2024-08-06 with diagnosis X" narrows the search space fast. Round dates aggressively; if the demo requires exact dates, ask why.
- Regenerating the demo dataset from an updated source snapshot should be one command. If it takes an engineer half a day, no one will refresh it, and stale demos rot fast. The pipeline is a product.
- Ask the champion: *what would you show a competitor if this data leaked?* Their answer sharpens the classification and often uncovers a Restricted field the schema hid. This is the best 60-second security review you'll ever run.

## INTERVIEW ANGLE

This drill is the archetype behind Phase 10 problem "redact the dataset, keep it useful" and shows up on FDE take-homes at Palantir, OpenAI-solutions, and Sierra. Interviewers evaluate whether you build a pipeline or hack a script.

1. "Walk me through how you'd produce a demo dataset from a customer's production data by Monday." (The six-stage pipeline, in-tenant execution, manifest as deliverable, verify gates that fail closed. Bonus: name the small-cell threshold and the join-integrity check.)
2. "How do you prove to the DPO that this dataset is safe to use in a demo?" (Manifest with classification, redaction lineage, verify results, and audit log — not the raw output. Emphasize *evidence*, not *assertion*.)
3. "The SVP notices the demo dataset looks slightly different from what they know is in production — what happened?" (Distribution-fidelity target, small-cell suppression, date rounding — explain each and why the trade-off is worth it. If the differences are unexplained, that's a bug in the pipeline; if they're documented in the manifest, that's the design.)

## DRILL

Take a public dataset with realistic messiness — the Kaggle synthetic healthcare dataset, the CMS provider-utilization file, or a CRM export from an earlier phase. Assume it's the customer's real production data. Build the six-stage pipeline end-to-end, in stdlib Python, with:

1. A profile output listing every field with a proposed class label.
2. A redactor (extend Lesson 03) that handles the specific PII shapes present.
3. A synthesizer that produces plausible fakes deterministic on the token.
4. Suppression at k=5 across at least one slice.
5. Verify gates (leak scan, distribution fidelity within 3%, join integrity, small-cell audit) that fail closed.
6. A Redaction Manifest as the primary artifact.

Then demo it to yourself: pretend to be the SVP asking three questions ("is this our real customers?", "why does this month's number look 6% off?", "can we send this to the auditor?"). Answer each in one paragraph, referencing the manifest. Save the pipeline and manifest — you are one weekend from producing them for a real customer, and having done it once end-to-end is what separates FDEs who ship from FDEs who apologize.
