"""DRILL 06 - Parse the legacy fixed-width mainframe export. Difficulty: 2/3

The AS/400 exports account balances in fixed-width layout. The "copybook"
(the only documentation, from 1997):

    ACCT-ID      pos 1-8    char
    ACCT-NAME    pos 9-28   char, space padded
    BALANCE      pos 29-39  numeric 9(9)V99 - implied 2 decimals, no dot!
    SIGN         pos 40     '+' or '-'
    BRANCH       pos 41-44  char

Notes from the last person who touched it: blank lines happen; lines
starting with 'H' are headers; totals line starts with 'T' and its
balance must equal the sum of detail rows (your parser must verify this
"trailer check" - mainframe feeds rely on it).
"""

RAW = """H20240315DAILY BALANCE EXPORT
ACCT0001Meridian Cafeteria  00000125050+BR01
ACCT0002Radiology Dept      00001200000+BR01

ACCT0003Parking Trust       00000045099-BR02
ACCT0004Gift Shop           00000310750+BR02
T                           00001590701+
"""


# ----------------------------- reference solution -----------------------------
def parse_amount(digits: str, sign: str) -> float:
    value = int(digits) / 100
    return -value if sign == "-" else value


def solve(raw: str) -> dict:
    details, trailer_total = [], None
    for line in raw.splitlines():
        if not line.strip() or line.startswith("H"):
            continue
        if line.startswith("T"):
            trailer_total = parse_amount(line[28:39], line[39])
            continue
        details.append({
            "acct_id": line[0:8],
            "name": line[8:28].rstrip(),
            "balance": parse_amount(line[28:39], line[39]),
            "branch": line[40:44],
        })
    computed = round(sum(d["balance"] for d in details), 2)
    if trailer_total is None or abs(computed - trailer_total) > 0.005:
        raise ValueError(f"trailer check failed: computed {computed}, trailer {trailer_total}")
    return {"rows": details, "total": computed}
# -------------------------------------------------------------------------------


def main():
    out = solve(RAW)
    assert len(out["rows"]) == 4
    assert out["rows"][0] == {"acct_id": "ACCT0001", "name": "Meridian Cafeteria",
                              "balance": 1250.50, "branch": "BR01"}
    assert out["rows"][2]["balance"] == -450.99, "trailing sign must apply"
    assert out["total"] == 15907.01

    # a corrupted feed must FAIL the trailer check, loudly
    corrupted = RAW.replace("00000310750", "00000310759")
    try:
        solve(corrupted)
        raise AssertionError("trailer check should have caught corruption")
    except ValueError as e:
        assert "trailer check failed" in str(e)

    print("drill-06: all checks passed (4 rows, trailer check enforced)")


if __name__ == "__main__":
    main()
