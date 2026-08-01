"""FLAGSHIP - Entity resolution: normalization, blocking, fuzzy match, survivorship.

The CRM says 5,000 customers; reality says 4,100. Resolve duplicates:
normalize names, block to avoid O(n^2), score pairs with fuzzy similarity,
cluster with union-find, then pick a survivor per cluster (most complete
record wins). This tiny version carries every idea the production one needs.
"""

import re
from difflib import SequenceMatcher

ABBREV = {"st": "street", "rd": "road", "ave": "avenue", "inc": "", "llc": "",
          "ltd": "", "corp": "", "corporation": "", "co": "", "&": "and"}


def normalize(name: str) -> str:
    tokens = re.sub(r"[^\w& ]", " ", name.lower()).split()
    tokens = [ABBREV.get(t, t) for t in tokens]
    return " ".join(t for t in tokens if t)


def block_key(record: dict) -> tuple:
    norm = normalize(record["name"])
    return (record["zip"][:3], norm[:1] if norm else "?")


def similarity(a: dict, b: dict) -> float:
    name_sim = SequenceMatcher(None, normalize(a["name"]), normalize(b["name"])).ratio()
    pa, pb = re.sub(r"\D", "", a["phone"]), re.sub(r"\D", "", b["phone"])
    if pa and pb:
        return 0.7 * name_sim + 0.3 * (1.0 if pa == pb else 0.0)
    return name_sim  # a missing phone is absence of evidence, not a mismatch


class UnionFind:
    def __init__(self, n): self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b): self.parent[self.find(a)] = self.find(b)


def resolve(records: list[dict], threshold: float = 0.82) -> list[list[dict]]:
    blocks: dict[tuple, list[int]] = {}
    for i, r in enumerate(records):
        blocks.setdefault(block_key(r), []).append(i)
    uf = UnionFind(len(records))
    comparisons = 0
    for ids in blocks.values():
        for x in range(len(ids)):
            for y in range(x + 1, len(ids)):
                comparisons += 1
                if similarity(records[ids[x]], records[ids[y]]) >= threshold:
                    uf.union(ids[x], ids[y])
    clusters: dict[int, list[dict]] = {}
    for i in range(len(records)):
        clusters.setdefault(uf.find(i), []).append(records[i])
    resolve.comparisons = comparisons  # exposed for the blocking assertion
    return list(clusters.values())


def survivor(cluster: list[dict]) -> dict:
    def completeness(r): return sum(1 for v in r.values() if v)
    return max(cluster, key=completeness)


def main():
    records = [
        {"id": 1, "name": "Acme Corp.", "phone": "555-0101", "zip": "10001", "email": ""},
        {"id": 2, "name": "ACME Corporation", "phone": "(555) 0101", "zip": "10001", "email": "ops@acme.com"},
        {"id": 3, "name": "Acme Corp Inc", "phone": "", "zip": "10001", "email": ""},
        {"id": 4, "name": "Globex LLC", "phone": "555-0202", "zip": "10002", "email": "hi@globex.com"},
        {"id": 5, "name": "Globex", "phone": "5550202", "zip": "10002", "email": ""},
        {"id": 6, "name": "Initech Ltd", "phone": "555-0303", "zip": "94105", "email": ""},
        {"id": 7, "name": "Stark Industries", "phone": "555-0404", "zip": "94105", "email": ""},
    ]

    assert normalize("Acme Corp.") == "acme"
    assert normalize("Main St") == "main street" and normalize("Globex LLC") == "globex"

    clusters = resolve(records)
    sizes = sorted(len(c) for c in clusters)
    assert sizes == [1, 1, 2, 3], f"expected clusters [1,1,2,3], got {sizes}"

    # blocking must beat the naive 21 comparisons for 7 records
    assert resolve.comparisons < 21, f"blocking failed: {resolve.comparisons} comparisons"

    acme = next(c for c in clusters if len(c) == 3)
    assert {r["id"] for r in acme} == {1, 2, 3}
    assert survivor(acme)["id"] == 2, "survivor must be the most complete record"

    globex = next(c for c in clusters if len(c) == 2)
    assert {r["id"] for r in globex} == {4, 5}

    # Initech and Stark share a zip (94105) but land in different blocks - never merge
    singletons = {c[0]["id"] for c in clusters if len(c) == 1}
    assert singletons == {6, 7}

    print(f"entity-resolution: all assertions passed "
          f"(7 records -> {len(clusters)} entities, {resolve.comparisons} comparisons)")


if __name__ == "__main__":
    main()
