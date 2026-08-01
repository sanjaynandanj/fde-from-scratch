"""DRILL 10 - The demo is in 4 hours: seed a convincing dataset. Difficulty: 2/3

Rules from the account lead: (1) zero real customer data, (2) the trend
must go up and to the right (it's a value story), (3) numbers must be
plausible for a 400-bed hospital, (4) deterministic - the demo must look
IDENTICAL in every rehearsal, (5) one seeded anomaly to "discover" live.

Generate 12 weeks of claims-processed data satisfying all five, and prove
each property with a check.
"""

import random

WEEKS = 12
BASELINE = 950          # claims/week for a 400-bed hospital: plausible band
ANOMALY_WEEK = 8        # the "discover this live" dip


# ----------------------------- reference solution -----------------------------
def solve(seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    for week in range(1, WEEKS + 1):
        trend = BASELINE + week * 30                      # up and to the right
        noise = rng.randint(-12, 12)                      # noise < slope: trend survives
        processed = trend + noise
        if week == ANOMALY_WEEK:
            processed = int(processed * 0.62)             # the seeded dip
        rows.append({
            "week": week,
            "claims_processed": processed,
            "auto_adjudicated_pct": round(min(0.55 + week * 0.02, 0.85) + rng.uniform(-0.01, 0.01), 3),
            "hospital": "Demo General (synthetic)",
        })
    return rows
# -------------------------------------------------------------------------------


def main():
    rows = solve()
    assert len(rows) == WEEKS

    # rule 1: clearly-synthetic labeling, no real names
    assert all("synthetic" in r["hospital"] for r in rows)

    # rule 2: up-and-to-the-right, ignoring the anomaly week
    clean = [r["claims_processed"] for r in rows if r["week"] != ANOMALY_WEEK]
    rises = sum(1 for a, b in zip(clean, clean[1:]) if b > a)
    assert rises >= len(clean) - 2, "trend must dominate the noise"
    assert clean[-1] > clean[0] * 1.15

    # rule 3: plausibility band for a 400-bed hospital
    assert all(500 <= r["claims_processed"] <= 1600 for r in rows)
    assert all(0.5 <= r["auto_adjudicated_pct"] <= 0.9 for r in rows)

    # rule 4: deterministic - two generations are byte-identical
    assert solve() == solve(), "rehearsal and demo must match exactly"

    # rule 5: exactly one anomaly, and it is findable by a simple detector
    dips = [r["week"] for i, r in enumerate(rows)
            if 0 < i and r["claims_processed"] < rows[i - 1]["claims_processed"] * 0.8]
    assert dips == [ANOMALY_WEEK]

    print(f"drill-10: all checks passed (12 weeks, anomaly hidden at week {ANOMALY_WEEK})")


if __name__ == "__main__":
    main()
