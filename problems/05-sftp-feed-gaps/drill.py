"""DRILL 05 - The nightly SFTP feed that sometimes doesn't arrive. Difficulty: 2/3

The lab system drops one file per night: LAB_YYYYMMDD.csv. Except when it
doesn't. Or drops the same night twice (a retry). Or arrives a day late
with yesterday's date in the name. Given 30 days of arrival logs, produce
the operational report: missing dates, duplicate deliveries, late
arrivals, and the exact replay-request list to send the lab vendor.
"""

from datetime import date, timedelta

WINDOW_START, WINDOW_DAYS = date(2024, 3, 1), 30

# (filename, arrived_at date) - generator output, deterministic
ARRIVALS = []
_d = WINDOW_START
for i in range(WINDOW_DAYS):
    day = WINDOW_START + timedelta(days=i)
    name = f"LAB_{day.strftime('%Y%m%d')}.csv"
    if day.day in (5, 17, 26):
        continue                                   # never arrived
    elif day.day == 9:
        ARRIVALS.append((name, day + timedelta(days=2)))   # late
    elif day.day == 12:
        ARRIVALS.append((name, day))
        ARRIVALS.append((name, day))               # duplicate delivery
    else:
        ARRIVALS.append((name, day))


# ----------------------------- reference solution -----------------------------
def solve(arrivals, start: date, days: int) -> dict:
    expected = {start + timedelta(days=i) for i in range(days)}
    seen: dict[date, list[date]] = {}
    for name, arrived in arrivals:
        file_date = date(int(name[4:8]), int(name[8:10]), int(name[10:12]))
        seen.setdefault(file_date, []).append(arrived)
    missing = sorted(d for d in expected if d not in seen)
    duplicates = sorted(d for d, a in seen.items() if len(a) > 1)
    late = sorted(d for d, a in seen.items() if min(a) > d)
    return {
        "missing": missing,
        "duplicates": duplicates,
        "late": late,
        "replay_request": [f"LAB_{d.strftime('%Y%m%d')}.csv" for d in missing],
        "on_time_rate": round((len(expected) - len(missing) - len(late)) / len(expected), 3),
    }
# -------------------------------------------------------------------------------


def main():
    r = solve(ARRIVALS, WINDOW_START, WINDOW_DAYS)
    assert [d.day for d in r["missing"]] == [5, 17, 26]
    assert [d.day for d in r["duplicates"]] == [12]
    assert [d.day for d in r["late"]] == [9]
    assert r["replay_request"] == ["LAB_20240305.csv", "LAB_20240317.csv", "LAB_20240326.csv"]
    assert r["on_time_rate"] == round(26 / 30, 3)
    print(f"drill-05: all checks passed (on-time rate {r['on_time_rate']:.1%})")


if __name__ == "__main__":
    main()
