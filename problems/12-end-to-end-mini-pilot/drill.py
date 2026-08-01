"""DRILL 12 - End-to-end: raw dumps -> resolved entities -> API -> metrics. Difficulty: 3/3

The graduation drill. Two raw dumps (a CRM export and a billing export)
disagree on names, share no clean key, and contain a duplicate. Pipeline:

  1. parse both dumps (one CSV-ish, one JSON-lines-ish)
  2. resolve entities across systems (name normalization)
  3. join billing onto resolved customers
  4. serve /customers and /metrics from an in-process API function
  5. metrics must reconcile to the penny with the billing source

Every stage is checked. This is the shape of week one at a customer site.
"""

import json
import re

CRM_DUMP = """id,name,tier
C-1,Acme Corp.,gold
C-2,Globex LLC,silver
C-3,ACME CORP,gold
C-4,Initech,bronze
"""

BILLING_DUMP = "\n".join([
    json.dumps({"invoice": "I-1", "customer": "Acme Corporation", "amount": 1200.50}),
    json.dumps({"invoice": "I-2", "customer": "globex", "amount": 800.00}),
    json.dumps({"invoice": "I-3", "customer": "Acme corp", "amount": 450.25}),
    json.dumps({"invoice": "I-4", "customer": "Initech Ltd", "amount": 300.00}),
])

STOP_SUFFIX = {"corp", "corporation", "llc", "ltd", "inc"}


# ----------------------------- reference solution -----------------------------
def norm(name: str) -> str:
    tokens = re.sub(r"[^\w ]", " ", name.lower()).split()
    return " ".join(t for t in tokens if t not in STOP_SUFFIX)


def build() -> dict:
    customers: dict[str, dict] = {}
    for line in CRM_DUMP.strip().splitlines()[1:]:
        cid, name, tier = line.split(",")
        key = norm(name)
        if key not in customers:
            customers[key] = {"canonical": name, "tier": tier,
                              "source_ids": [], "invoices": [], "revenue": 0.0}
        customers[key]["source_ids"].append(cid)

    unmatched = []
    for line in BILLING_DUMP.splitlines():
        inv = json.loads(line)
        key = norm(inv["customer"])
        if key in customers:
            customers[key]["invoices"].append(inv["invoice"])
            customers[key]["revenue"] = round(customers[key]["revenue"] + inv["amount"], 2)
        else:
            unmatched.append(inv["invoice"])
    return {"customers": customers, "unmatched": unmatched}


def api(state: dict, path: str):
    if path == "/customers":
        return [{"name": c["canonical"], "tier": c["tier"], "revenue": c["revenue"]}
                for c in state["customers"].values()]
    if path == "/metrics":
        return {
            "entity_count": len(state["customers"]),
            "duplicates_merged": sum(len(c["source_ids"]) - 1
                                     for c in state["customers"].values()),
            "total_revenue": round(sum(c["revenue"] for c in state["customers"].values()), 2),
            "unmatched_invoices": state["unmatched"],
        }
    return {"error": 404}
# -------------------------------------------------------------------------------


def main():
    state = build()

    # stage 2: 4 CRM rows -> 3 entities (the two Acmes merge)
    m = api(state, "/metrics")
    assert m["entity_count"] == 3
    assert m["duplicates_merged"] == 1

    # stage 3: cross-system join despite zero shared keys
    acme = state["customers"][norm("Acme Corp.")]
    assert sorted(acme["invoices"]) == ["I-1", "I-3"]
    assert acme["revenue"] == 1650.75

    # stage 5: reconciliation to the penny against the billing source
    billing_total = round(sum(json.loads(l)["amount"] for l in BILLING_DUMP.splitlines()), 2)
    assert m["total_revenue"] == billing_total == 2750.75
    assert m["unmatched_invoices"] == [], "every invoice must land on an entity"

    # stage 4: API surface behaves
    customers = api(state, "/customers")
    assert len(customers) == 3 and api(state, "/nope") == {"error": 404}

    print(f"drill-12: all checks passed "
          f"(3 entities, ${m['total_revenue']:,.2f} reconciled to the penny)")


if __name__ == "__main__":
    main()
