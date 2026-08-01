"""FLAGSHIP - The eval harness: golden sets from real customer data.

"It feels better" is not a deploy criterion. Build the harness: a golden
set labeled with the customer, accuracy + per-class precision/recall, a
confusion matrix, and a regression gate that blocks any change that breaks
previously-passing cases - the metric enterprise buyers actually care about.
"""

from collections import defaultdict

GOLDEN_SET = [
    ("Server is down, nobody can log in", "outage"),
    ("Please reset my password", "account"),
    ("Invoice 442 charged twice", "billing"),
    ("App crashes when exporting to PDF", "bug"),
    ("How do I add a new user seat?", "account"),
    ("Refund for the duplicate charge please", "billing"),
    ("Dashboard shows 500 error since 9am", "outage"),
    ("Feature request: dark mode", "other"),
    ("Payment failed but money deducted", "billing"),
    ("Cannot install the mobile app on Android 14", "bug"),
]


class MockClassifier:
    """Stands in for prompt+model. Keyword rules make it deterministic;
    v2 deliberately fixes one case and breaks another."""

    def __init__(self, version: int):
        self.version = version

    def predict(self, text: str) -> str:
        t = text.lower()
        if "down" in t or "500" in t or "outage" in t:
            return "outage"
        if any(w in t for w in ("invoice", "charge", "refund", "payment")):
            return "billing"
        if "password" in t or "user seat" in t or "log in" in t:
            return "account"
        if self.version >= 2 and ("crash" in t or "install" in t):
            return "bug"
        if self.version == 1 and "crash" in t:
            return "bug"
        return "other"


def evaluate(clf, golden: list[tuple[str, str]]) -> dict:
    confusion = defaultdict(int)
    results = {}
    for text, expected in golden:
        got = clf.predict(text)
        confusion[(expected, got)] += 1
        results[text] = (expected, got)
    labels = sorted({e for _, e in golden})
    per_class = {}
    for lbl in labels:
        tp = confusion[(lbl, lbl)]
        fp = sum(v for (e, g), v in confusion.items() if g == lbl and e != lbl)
        fn = sum(v for (e, g), v in confusion.items() if e == lbl and g != lbl)
        per_class[lbl] = {
            "precision": tp / (tp + fp) if tp + fp else 0.0,
            "recall": tp / (tp + fn) if tp + fn else 0.0,
        }
    accuracy = sum(1 for e, g in results.values() if e == g) / len(golden)
    return {"accuracy": accuracy, "per_class": per_class,
            "results": results, "confusion": dict(confusion)}


def regression_gate(old: dict, new: dict) -> dict:
    broke = [t for t in new["results"]
             if old["results"][t][0] == old["results"][t][1]
             and new["results"][t][0] != new["results"][t][1]]
    fixed = [t for t in new["results"]
             if old["results"][t][0] != old["results"][t][1]
             and new["results"][t][0] == new["results"][t][1]]
    return {"broke": broke, "fixed": fixed, "passes": not broke}


def main():
    v1 = evaluate(MockClassifier(1), GOLDEN_SET)
    # v1 misses the Android install bug (falls to "other")
    assert v1["accuracy"] == 0.9
    assert v1["per_class"]["bug"]["recall"] == 0.5
    assert v1["per_class"]["billing"]["precision"] == 1.0
    assert v1["confusion"][("bug", "other")] == 1

    v2 = evaluate(MockClassifier(2), GOLDEN_SET)
    assert v2["accuracy"] == 1.0
    gate = regression_gate(v1, v2)
    assert gate["passes"] and len(gate["fixed"]) == 1 and not gate["broke"]

    # simulate a bad "improvement": v1 evaluated against v2 as baseline
    gate_bad = regression_gate(v2, v1)
    assert not gate_bad["passes"] and len(gate_bad["broke"]) == 1, \
        "the gate must block changes that break passing cases"

    # per-class metrics must expose what a single accuracy number hides
    assert v1["accuracy"] == 0.9 and v1["per_class"]["bug"]["recall"] == 0.5, \
        "90% accuracy hid a 50% recall on the class the customer cares about"

    print("eval-harness: all assertions passed "
          f"(v1 acc={v1['accuracy']:.0%}, v2 acc={v2['accuracy']:.0%}, gate works both ways)")


if __name__ == "__main__":
    main()
