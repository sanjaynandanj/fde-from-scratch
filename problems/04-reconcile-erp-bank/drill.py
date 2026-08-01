"""DRILL 04 - Reconcile ERP vs bank statement. Difficulty: 2/3

Finance swears the ERP is right; the bank statement disagrees. Classic
causes seeded by the generator: bank fees the ERP never saw, an ERP
invoice paid in two bank installments, a keying error (digits transposed),
and timing (a payment in transit). Produce a reconciliation report that
explains 100% of the difference.
"""

ERP = [
    ("INV-001", 1200.00), ("INV-002", 830.50), ("INV-003", 2450.00),
    ("INV-004", 990.00), ("INV-005", 1575.25), ("INV-006", 610.00),
]
BANK = [
    ("dep INV-001", 1200.00), ("dep INV-002", 830.50),
    ("dep INV-003 part1", 1500.00), ("dep INV-003 part2", 950.00),
    ("dep INV-004", 909.00),            # keying error: 990 -> 909
    ("dep INV-006", 610.00),
    ("bank fee", -45.00),               # ERP never saw this
    # INV-005 in transit: on neither side's matched list
]


# ----------------------------- reference solution -----------------------------
def solve(erp, bank):
    bank_by_inv: dict[str, float] = {}
    fees = 0.0
    for desc, amt in bank:
        if "INV-" in desc:
            inv = next(t for t in desc.split() if t.startswith("INV-"))
            bank_by_inv[inv] = round(bank_by_inv.get(inv, 0) + amt, 2)
        else:
            fees = round(fees + amt, 2)

    report = {"matched": [], "amount_mismatch": [], "in_transit": [], "bank_only_fees": fees}
    for inv, amt in erp:
        got = bank_by_inv.get(inv)
        if got is None:
            report["in_transit"].append(inv)
        elif abs(got - amt) < 0.01:
            report["matched"].append(inv)
        else:
            report["amount_mismatch"].append((inv, amt, got, round(got - amt, 2)))

    erp_total = round(sum(a for _, a in erp), 2)
    bank_total = round(sum(a for _, a in bank), 2)
    explained = round(
        sum(d for _, _, _, d in report["amount_mismatch"])
        - sum(a for i, a in erp if i in report["in_transit"])
        + report["bank_only_fees"], 2)
    report["difference"] = round(bank_total - erp_total, 2)
    report["fully_explained"] = abs(explained - report["difference"]) < 0.01
    return report
# -------------------------------------------------------------------------------


def main():
    r = solve(ERP, BANK)
    assert sorted(r["matched"]) == ["INV-001", "INV-002", "INV-003", "INV-006"], \
        "split payment INV-003 must still match after aggregation"
    assert r["in_transit"] == ["INV-005"]
    assert r["amount_mismatch"] == [("INV-004", 990.00, 909.00, -81.00)]
    # transposition fingerprint: difference divisible by 9
    assert abs(r["amount_mismatch"][0][3]) % 9 == 0, "transposed digits differ by a multiple of 9"
    assert r["bank_only_fees"] == -45.00
    assert r["fully_explained"], f"unexplained residue in {r}"
    print(f"drill-04: all checks passed (difference {r['difference']} fully explained)")


if __name__ == "__main__":
    main()
