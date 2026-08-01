"""DRILL 01 - The Excel-damaged customer master. Difficulty: 1/3

The customer's "master list" lived in Excel for six years. Excel has:
  - stripped leading zeros from 5-digit customer codes ("00042" -> "42")
  - turned some codes into scientific notation ("1.02E+04" was "10200")
  - converted join dates to Excel serial numbers (days since 1899-12-30)

TASK: repair all three kinds of damage. Codes must come back as 5-char
zero-padded strings; dates as ISO "YYYY-MM-DD".
"""

from datetime import date, timedelta

DAMAGED = [
    {"code": "42",       "name": "Acme",    "joined": "44561"},
    {"code": "1.02E+04", "name": "Globex",  "joined": "2021-06-30"},
    {"code": "7",        "name": "Initech", "joined": "43854"},
    {"code": "00915",    "name": "Umbrella", "joined": "2019-01-19"},
    {"code": "3.1E+03",  "name": "Stark",   "joined": "45000"},
]

EXCEL_EPOCH = date(1899, 12, 30)


# ----------------------------- reference solution -----------------------------
def repair_code(raw: str) -> str:
    if "e" in raw.lower():
        raw = str(int(float(raw)))
    return raw.zfill(5)


def repair_date(raw: str) -> str:
    if raw.isdigit() and len(raw) == 5 and not raw.startswith("0"):
        return (EXCEL_EPOCH + timedelta(days=int(raw))).isoformat()
    return raw


def solve(rows: list[dict]) -> list[dict]:
    return [{**r, "code": repair_code(r["code"]), "joined": repair_date(r["joined"])}
            for r in rows]
# -------------------------------------------------------------------------------


def main():
    fixed = {r["name"]: r for r in solve(DAMAGED)}
    assert fixed["Acme"]["code"] == "00042"
    assert fixed["Globex"]["code"] == "10200"
    assert fixed["Initech"]["code"] == "00007"
    assert fixed["Umbrella"]["code"] == "00915", "already-good codes must survive"
    assert fixed["Stark"]["code"] == "03100"
    assert fixed["Acme"]["joined"] == "2021-12-31"
    assert fixed["Initech"]["joined"] == "2020-01-24"
    assert fixed["Stark"]["joined"] == "2023-03-15"
    assert fixed["Globex"]["joined"] == "2021-06-30", "ISO dates must pass through"
    print("drill-01: all checks passed")


if __name__ == "__main__":
    main()
