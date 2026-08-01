"""DRILL 08 - Build the golden-set eval for a support-ticket classifier. Difficulty: 2/3

The customer's team labeled 12 tickets. A vendor claims their classifier
is "95% accurate". Build the eval: overall accuracy, per-class recall,
and the finding that matters - which class fails worst, and whether the
headline accuracy number is hiding it. (It is. It always is.)
"""

GOLDEN = [
    ("Payment portal shows 502 since 08:30", "outage", "outage"),
    ("All users logged out repeatedly", "outage", "outage"),
    ("Charged twice for March invoice", "billing", "billing"),
    ("Need VAT number on receipts", "billing", "billing"),
    ("Refund never arrived", "billing", "billing"),
    ("Export to Excel produces empty file", "bug", "bug"),
    ("Search returns deleted records", "bug", "other"),
    ("Mobile app crashes on photo upload", "bug", "other"),
    ("Add SSO for our Okta", "feature", "feature"),
    ("Want API rate limit raised", "feature", "feature"),
    ("How do I bulk-import contacts?", "how-to", "feature"),
    ("Where is the audit log?", "how-to", "how-to"),
]  # (text, human_label, vendor_prediction)


# ----------------------------- reference solution -----------------------------
def solve(golden) -> dict:
    per_class: dict[str, dict] = {}
    correct = 0
    for _, truth, pred in golden:
        c = per_class.setdefault(truth, {"n": 0, "hit": 0})
        c["n"] += 1
        if truth == pred:
            c["hit"] += 1
            correct += 1
    recalls = {k: round(v["hit"] / v["n"], 3) for k, v in per_class.items()}
    worst = min(recalls, key=lambda k: recalls[k])
    return {
        "accuracy": round(correct / len(golden), 3),
        "recall": recalls,
        "worst_class": worst,
        "verdict": "headline hides a failing class" if recalls[worst] <= 0.5 else "ok",
    }
# -------------------------------------------------------------------------------


def main():
    r = solve(GOLDEN)
    assert r["accuracy"] == 0.75, "the vendor's 95% claim does not survive the golden set"
    assert r["recall"]["outage"] == 1.0 and r["recall"]["billing"] == 1.0
    assert r["recall"]["bug"] == round(1 / 3, 3)
    assert r["worst_class"] == "bug"
    assert r["verdict"] == "headline hides a failing class"
    print(f"drill-08: all checks passed "
          f"(accuracy {r['accuracy']:.0%}, but bug recall {r['recall']['bug']:.0%})")


if __name__ == "__main__":
    main()
