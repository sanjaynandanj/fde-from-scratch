"""DRILL 09 - Redact the dataset, keep it useful. Difficulty: 2/3

Legal approved using support tickets for the demo IF: no emails, no
phones, no SSNs survive - but ticket routing must still work, meaning the
same person must map to the same pseudonym across tickets (joins survive
redaction). Prove both properties mechanically.
"""

import re

TICKETS = [
    {"id": 1, "text": "jane@corp.com cannot reset password, call 555-201-3344"},
    {"id": 2, "text": "Follow-up for jane@corp.com - still locked out"},
    {"id": 3, "text": "bob@corp.com reports SSN 123-45-6789 shown in profile page!"},
    {"id": 4, "text": "555-201-3344 called again, escalate"},
]

PATTERNS = {
    "EMAIL": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "PHONE": re.compile(r"\b\d{3}-\d{3}-\d{4}\b"),
}


# ----------------------------- reference solution -----------------------------
def solve(tickets) -> list[dict]:
    mapping: dict[str, str] = {}
    counters: dict[str, int] = {}

    def token(kind: str, value: str) -> str:
        if value not in mapping:
            counters[kind] = counters.get(kind, 0) + 1
            mapping[value] = f"<{kind}_{counters[kind]}>"
        return mapping[value]

    out = []
    for t in tickets:
        text = t["text"]
        for kind in ("EMAIL", "SSN", "PHONE"):   # SSN before PHONE: patterns overlap
            text = PATTERNS[kind].sub(lambda m, k=kind: token(k, m.group()), text)
        out.append({"id": t["id"], "text": text})
    return out
# -------------------------------------------------------------------------------


def main():
    redacted = solve(TICKETS)
    joined = " ".join(t["text"] for t in redacted)

    # property 1: nothing sensitive survives
    for kind, pat in PATTERNS.items():
        leaks = pat.findall(joined)
        assert not leaks, f"{kind} leaked: {leaks}"

    # property 2: joins survive - jane is the same token in tickets 1 and 2
    t = {r["id"]: r["text"] for r in redacted}
    jane_1 = re.search(r"<EMAIL_\d+>", t[1]).group()
    jane_2 = re.search(r"<EMAIL_\d+>", t[2]).group()
    assert jane_1 == jane_2, "same person must get the same pseudonym"
    bob = re.search(r"<EMAIL_\d+>", t[3]).group()
    assert bob != jane_1, "different people must get different pseudonyms"

    # the repeated phone joins tickets 1 and 4
    phone_1 = re.search(r"<PHONE_\d+>", t[1]).group()
    phone_4 = re.search(r"<PHONE_\d+>", t[4]).group()
    assert phone_1 == phone_4

    # SSN redacted as SSN, not mangled as phone
    assert "<SSN_1>" in t[3]
    print("drill-09: all checks passed (zero leaks, joins preserved)")


if __name__ == "__main__":
    main()
