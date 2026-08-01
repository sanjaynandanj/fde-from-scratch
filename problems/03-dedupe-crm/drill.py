"""DRILL 03 - Deduplicate the CRM. Difficulty: 2/3

The generator builds 400 base companies, then injects ~18% duplicates with
realistic mutations: suffix changes (Inc/LLC dropped or added), punctuation,
case, and phone reformatting. Your job: cluster duplicates and report the
true entity count. The generator remembers the truth; the checks compare
your clustering against it (must reach >= 97% of exact truth, zero
over-merges across different base companies).
"""

import random
import re
from difflib import SequenceMatcher

SUFFIXES = ["Inc", "LLC", "Ltd", "Corp", ""]


def generate(seed: int = 7):
    rng = random.Random(seed)
    base_names = [f"{a}{b} {rng.choice(['Systems', 'Holdings', 'Labs', 'Logistics', 'Partners'])}"
                  for a in ["Blue", "North", "Iron", "Clear", "Vast", "Prime", "Echo", "Delta"]
                  for b in ["stone", "gate", "field", "bridge", "peak"]]
    base_names = base_names[:40]
    records, truth = [], {}
    rid = 0
    for ent_id, name in enumerate(base_names):
        phone = f"555-{rng.randint(1000, 9999)}"
        n_copies = 1 + (1 if rng.random() < 0.30 else 0)
        for c in range(n_copies):
            variant = f"{name} {rng.choice(SUFFIXES)}".strip()
            if c > 0:
                variant = variant.upper() if rng.random() < 0.5 else variant + "."
            p = phone if rng.random() < 0.8 else f"(555) {phone[4:]}"
            records.append({"id": rid, "name": variant, "phone": p})
            truth[rid] = ent_id
            rid += 1
    rng.shuffle(records)
    return records, truth


# ----------------------------- reference solution -----------------------------
def norm(name: str) -> str:
    t = re.sub(r"[^\w ]", " ", name.lower()).split()
    return " ".join(w for w in t if w not in {"inc", "llc", "ltd", "corp"})


def solve(records: list[dict]) -> list[set[int]]:
    parent = {r["id"]: r["id"] for r in records}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    blocks: dict[str, list[dict]] = {}
    for r in records:
        blocks.setdefault(norm(r["name"])[:4], []).append(r)
    for group in blocks.values():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                if SequenceMatcher(None, norm(a["name"]), norm(b["name"])).ratio() >= 0.92:
                    parent[find(a["id"])] = find(b["id"])
    clusters: dict[int, set[int]] = {}
    for r in records:
        clusters.setdefault(find(r["id"]), set()).add(r["id"])
    return list(clusters.values())
# -------------------------------------------------------------------------------


def main():
    records, truth = generate()
    true_entities = len(set(truth.values()))
    assert len(records) > true_entities, "generator must inject duplicates"

    clusters = solve(records)

    # no over-merge: a cluster may never span two different true entities
    for cluster in clusters:
        assert len({truth[i] for i in cluster}) == 1, f"over-merged cluster: {cluster}"

    # near-perfect entity count (some mutations are legitimately undecidable)
    assert true_entities <= len(clusters) <= round(true_entities * 1.03), \
        f"true={true_entities}, got={len(clusters)}"

    print(f"drill-03: all checks passed "
          f"({len(records)} records -> {len(clusters)} entities, truth={true_entities})")


if __name__ == "__main__":
    main()
