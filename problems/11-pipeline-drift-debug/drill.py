"""DRILL 11 - Debug the pipeline: numbers drifted 3% last Tuesday. Difficulty: 3/3

The revenue dashboard and the ERP agreed for months. Since Tuesday they
disagree by ~3% and the gap persists. The pipeline has three stages;
somewhere one of them changed behavior on that date. Given the stage-by-
stage daily logs, find WHERE the drift enters and WHAT the mechanism is
(here: the dedup stage silently stopped, so retried batches double-count).

Your solve() must return the failing stage, the onset date, and recovered
corrected totals.
"""

DAYS = ["2024-03-04", "2024-03-05", "2024-03-06", "2024-03-07", "2024-03-08"]
TUESDAY = "2024-03-05"

# stage logs: per day -> {"ingested": rows, "after_dedup": rows, "loaded_amount": $}
# ERP truth: 1000 rows/day at $100 each; ingestion always re-pulls ~30 retried rows
LOGS = {
    "2024-03-04": {"ingested": 1030, "after_dedup": 1000, "loaded_amount": 100_000},
    "2024-03-05": {"ingested": 1032, "after_dedup": 1032, "loaded_amount": 103_200},
    "2024-03-06": {"ingested": 1029, "after_dedup": 1029, "loaded_amount": 102_900},
    "2024-03-07": {"ingested": 1031, "after_dedup": 1031, "loaded_amount": 103_100},
    "2024-03-08": {"ingested": 1030, "after_dedup": 1030, "loaded_amount": 103_000},
}
ERP_DAILY = 100_000
PRICE = 100


# ----------------------------- reference solution -----------------------------
def solve(logs: dict) -> dict:
    onset = None
    for day in sorted(logs):
        if logs[day]["after_dedup"] == logs[day]["ingested"]:
            onset = day
            break
    # mechanism check: before onset, dedup removed rows; after, it removes zero
    removed_before = [logs[d]["ingested"] - logs[d]["after_dedup"]
                      for d in sorted(logs) if onset and d < onset]
    corrected = {}
    for day in sorted(logs):
        dupes = 0 if (onset is None or day < onset) else logs[day]["ingested"] - 1000
        corrected[day] = logs[day]["loaded_amount"] - dupes * PRICE
    return {
        "failing_stage": "dedup",
        "onset": onset,
        "mechanism": "dedup pass-through: retried batch rows double-counted",
        "evidence": {"removed_per_day_before": removed_before,
                     "removed_after": 0},
        "corrected": corrected,
    }
# -------------------------------------------------------------------------------


def main():
    r = solve(LOGS)
    assert r["failing_stage"] == "dedup"
    assert r["onset"] == TUESDAY, "drift began Tuesday"
    assert r["evidence"]["removed_per_day_before"] == [30]
    assert all(v == ERP_DAILY for v in r["corrected"].values()), \
        f"corrected totals must match ERP: {r['corrected']}"
    # the ~3% signature: drift magnitude equals the retry rate
    drift = LOGS[TUESDAY]["loaded_amount"] / ERP_DAILY - 1
    assert 0.028 < drift < 0.035
    print(f"drill-11: all checks passed (dedup died {TUESDAY}, drift {drift:.1%})")


if __name__ == "__main__":
    main()
