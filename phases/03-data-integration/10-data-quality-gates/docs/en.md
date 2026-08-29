# Data Quality Gates: Quarantine, Not Rejection

**Phase 3 · Lesson 10 · ~1h**

## PROBLEM

Week six of a manufacturing pilot. The pipeline is running nightly. Wednesday morning, the customer's operations director opens the dashboard: it's empty. The overnight batch failed at 03:12 on a row where a shipment's weight was `-12.5` — the sensor sent a bad reading. Your ingestion code raised, the transaction rolled back, and 47,000 good rows never made it to the warehouse because one row was garbage.

You fix it. Two days later, a different row: a purchase-order date in the year 2029. Same failure. Empty dashboard. Angry director. This is the classic new-FDE trap: you built strict validation because "clean data in, clean data out" is what a professional does. But *strict rejection* means one bad row kills the whole load. In a pilot, that's a daily fire drill. In production, it's a page at 3am.

The correct pattern is quarantine, not rejection: bad rows are captured, tagged with the reason, and set aside for review — but they don't stop the good rows from landing.

## INTUITION

Data quality has three failure modes and a corresponding gate pattern for each:

**Hard nulls (structural).** A row missing a primary key is unusable; a claim missing a claim ID cannot exist. These get rejected — moved to a quarantine table with the reason, but not passed downstream. There's no valid recovery for the batch.

**Value violations (semantic).** Weight < 0. Date in the future. Enum value not in the expected set. Amount over 10x the historical mean. These get quarantined but are usually *recoverable* — often a sensor glitch, an entry typo, or a legitimate outlier the business should see. Never crash on them.

**Cross-row inconsistencies (referential).** A claim references a patient ID that doesn't exist in the patient table. A trade references a security not in the security master. These get flagged, sometimes quarantined, sometimes passed through with a `orphan=true` tag depending on how strict the ontology contract is.

The design space:

**Rejection vs. quarantine vs. warn.** Three tiers. Reject only when the row is structurally impossible. Quarantine (route to a side table, don't count in main output, expose in a review UI) for value violations. Warn (pass through, log, count) for soft anomalies. Loud crashes are the wrong default.

**Gates before or after transform?** Gate at multiple stages: on ingest (structural), after entity resolution (referential), after mapping (semantic checks against canonical). Layered gates catch different classes of problem at the earliest point they're detectable.

**Metrics as gates.** Beyond per-row checks, run *batch-level* gates: row count within 10% of yesterday's, null rate on a key column below 5%, distinct customer count within a known range. A batch that passes every row check but has half the expected volume should not silently ship.

**Ownership of "bad."** Quarantine only helps if someone reviews the queue. Assign an owner per source system, agree on a review SLA, and generate a weekly quarantine report. Otherwise the queue is just a landfill.

## BUILD IT

Sketch of a gate framework: rules as data, per-row evaluation, and a router.

```python
GATES = [
    # (name, level, check)
    ("has_claim_id",   "reject",    lambda r: bool(r.get("claim_id"))),
    ("valid_amount",   "quarantine", lambda r: r.get("amount", 0) >= 0),
    ("plausible_date", "quarantine", lambda r: r.get("service_date", "9999") <= today()),
    ("known_provider", "warn",      lambda r: r.get("provider_id") in provider_ids),
]

def apply_gates(rows):
    accepted, quarantined, warnings = [], [], []
    for r in rows:
        row_status = "accepted"
        row_reasons = []
        for name, level, check in GATES:
            try:
                ok = check(r)
            except Exception as e:
                ok = False
                row_reasons.append(f"{name}:error:{e}")
            if not ok:
                row_reasons.append(f"{name}:failed")
                if level == "reject":
                    row_status = "rejected"
                    break
                elif level == "quarantine":
                    row_status = "quarantined"
                elif level == "warn":
                    if row_status == "accepted":
                        warnings.append((r, name))
        if row_status == "accepted":
            accepted.append(r)
        elif row_status == "quarantined":
            quarantined.append({**r, "_reasons": row_reasons})
        # rejected: dropped, but still logged with reason
    return accepted, quarantined, warnings

# Batch-level gate: reject the whole load if volume is way off
def batch_gate(accepted, expected_range):
    lo, hi = expected_range
    if not (lo <= len(accepted) <= hi):
        raise BatchGateFailed(f"row count {len(accepted)} outside [{lo}, {hi}]")
```

Two moves earn their keep. First, gates are *data* — rows in a list, editable without a code change. That lets the customer's data steward propose a new gate and you land it in a PR. Second, the tri-state routing (accept, quarantine, reject) with per-gate level means one bad row can't stop good rows, but structurally impossible rows still can't poison the warehouse.

Quarantine writes go to a parallel table with the same schema plus `_reasons` and `_batch_id`. The dashboard shows both counts: "47,000 loaded, 12 quarantined."

## FIELD NOTES

- The single biggest cultural win with data quality gates is: never fail silently, never crash loudly, always route with a reason. Customers accept "12 rows quarantined" every day. They don't accept an empty dashboard.
- Show the quarantine count on the main dashboard, not just an ops UI. When the business sees "24 quarantined today" they investigate — often finding a real business problem (a supplier submitting bad data) that your pipeline surfaced.
- Batch-level gates catch problems row-level gates can't: an upstream system that silently switched schemas usually has clean-looking rows but weird distributions. Volume, null-rate, and cardinality checks are cheap and load-bearing.
- Don't try to auto-fix quarantined rows. That road ends in bugs where corrected values are wrong. Route to a human, keep the original, and only re-ingest after explicit approval.
- The gate config *is* the data contract. Version it, review it, keep it in git. Changing a threshold is a decision worth a PR.

## INTERVIEW ANGLE

Data quality shows up in system-design rounds and behavioral rounds — the latter because "tell me about a time bad data broke your pipeline" is a common probe.

Sample questions:

1. "One row in a nightly load has a corrupt value. Should the load fail?" (No — quarantine the row, tag with reason, proceed with the rest. Only reject when the row is structurally impossible.)
2. "How do you distinguish 'clean data with a real outlier' from 'bad data'?" (You can't perfectly. Quarantine, flag, show the business — they know their world. The wrong answer is silently dropping outliers; the second-wrong answer is silently accepting them.)
3. "The customer's data steward wants to add a new gate. Walk me through the process." (Gate defined in config, PR reviewed, dry-run against historical data to estimate quarantine volume, ship with a warn level first, escalate to quarantine after a week if behavior is expected.)

## DRILL

1. **Extend:** add a `warn` counter to the output — how many rows passed accepted-with-warnings. Print it alongside accepted/quarantined counts.
2. **Break:** set an aggressive quarantine gate that flags amounts above the 95th percentile. Run against a real skewed distribution. Observe how much of the load ends up in quarantine and decide whether the gate is worth the noise.
3. **Fix:** add a `weekly_quarantine_report` that groups quarantined rows by gate name and source system, and prints top-5 offending sources. That's your Monday artifact for the customer's data owner.
