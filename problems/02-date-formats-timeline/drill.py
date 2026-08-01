"""DRILL 02 - Three date formats, one timeline. Difficulty: 1/3

Three departments log shipments. Logistics uses ISO, sales uses US
"MM/DD/YYYY", the warehouse uses "DD-Mon-YY". Merge all events into one
chronologically-sorted timeline. Ambiguity rule from the customer:
anything with a slash is US format, full stop.
"""

from datetime import datetime

EVENTS = [
    ("logistics", "2024-03-05", "container cleared customs"),
    ("sales", "02/28/2024", "PO-1181 confirmed"),
    ("warehouse", "01-Mar-24", "goods received dock 4"),
    ("sales", "03/12/2024", "PO-1190 confirmed"),
    ("warehouse", "28-Feb-24", "staging area full"),
    ("logistics", "2024-02-27", "vessel departed"),
]


# ----------------------------- reference solution -----------------------------
def parse_any(raw: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%b-%y"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    raise ValueError(f"unparseable date: {raw}")


def solve(events) -> list[tuple[str, str, str]]:
    parsed = [(parse_any(d).date().isoformat(), src, msg) for src, d, msg in events]
    return sorted(parsed)
# -------------------------------------------------------------------------------


def main():
    timeline = solve(EVENTS)
    assert [t[0] for t in timeline] == [
        "2024-02-27", "2024-02-28", "2024-02-28", "2024-03-01", "2024-03-05", "2024-03-12"]
    assert timeline[0][2] == "vessel departed"
    assert timeline[-1][2] == "PO-1190 confirmed"
    # the two Feb-28 events: sorted() tiebreak on source is fine, both must be present
    feb28 = {t[1] for t in timeline if t[0] == "2024-02-28"}
    assert feb28 == {"sales", "warehouse"}
    print("drill-02: all checks passed")


if __name__ == "__main__":
    main()
