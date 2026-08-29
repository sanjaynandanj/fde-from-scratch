# Entity Resolution II: Fuzzy Matching, Scoring, Survivorship

**Phase 3 · Lesson 06 · ~1.5h**

## PROBLEM

Week four of a B2B sales-analytics pilot. Lesson 05's exact-match resolver ran on the merged CRM extracts and collapsed 18% of the duplicates cleanly — the ones with identical normalized names and matching tax IDs. Great. The remaining duplicates are the interesting ones:

- `ACME Corporation` vs `Acme Corp.` — same company, no shared identifier.
- `ACME Corporation` vs `ACME Coproration` — same company, one typo.
- `ACME Corp - Retail Division` vs `ACME Corp - Wholesale` — different divisions, same parent, and the customer's finance team insists they must stay separate.
- `John Smith, ACME Corp.` (a person record) vs `ACME Corporation` (a company record) — different entity types, and if you merge them you break the CRM.

The VP wants "one row per customer" on the pilot dashboard by Friday. Exact matching is done. What's left is a scoring problem — and once you decide two rows *are* the same entity, a second problem: which values from each source win? The Brazilian ERP has the up-to-date address but a stale tax ID; NetSuite has the current tax ID but a name typo; SAP has the oldest record and the "legal" name. You can't just union.

## INTUITION

Fuzzy matching is exact matching's messy cousin, and survivorship is its diplomatic tail. The design space:

**Similarity metrics.** Three families are worth knowing:
- *Edit distance* (Levenshtein): how many single-character edits transform A into B. Cheap, catches typos, blind to word order.
- *Token overlap* (Jaccard, cosine on token bags): treat each string as a set of words, measure overlap. Catches word reorderings, blind to typos within a word.
- *Phonetic* (Soundex, Metaphone): map strings to sound codes, compare codes. Catches spelling variants of names, useless for company legal names.

You almost always want a *blend*: normalized Jaccard on tokens plus edit distance on the joined string, weighted. No single metric wins.

**Blocking, still.** Fuzzy comparison is O(n²) in row count without blocking. Reuse Lesson 05's blocking (first-letter, first-token, or phonetic bucket), then run the expensive scorer only on within-block pairs. On 100,000 rows this is the difference between 4 seconds and 4 hours.

**Scoring and thresholds.** Compute a similarity score in `[0, 1]`. Then two thresholds: an *auto-merge* line (above which pairs are collapsed automatically) and a *review* line (between which pairs go to a human queue). Below the review line, treat as distinct. Never one threshold — the middle band is where the interesting work is.

**Survivorship rules.** Once you decide two rows are the same entity, per-field rules pick the winner:
- *Most recent*: use the record with the newest updated timestamp.
- *Longest non-null*: pick the longer non-empty value (often correct for names and addresses).
- *Source priority*: SAP wins for tax ID, NetSuite wins for email, always.
- *Trusted flag*: only accept values from records flagged `verified=true`.

The rules are per-field, per-domain, and *the customer owns them*. Your job is to expose them as a config, not to guess.

**The merged record's lineage.** The output entity must remember which source rows fed each field. When the CFO asks "why does this customer have this address," you show them: `address ← netsuite:42317, updated 2026-06-14, chosen by most-recent rule`.

## BUILD IT

Sketch of a fuzzy resolver: blocker, scorer, decider, survivor.

```python
from collections import defaultdict

def normalize(s):
    return "".join(c.lower() for c in s if c.isalnum() or c.isspace()).strip()

def tokens(s):
    return set(normalize(s).split())

def jaccard(a, b):
    A, B = tokens(a), tokens(b)
    return len(A & B) / len(A | B) if (A | B) else 0.0

def edit_ratio(a, b):
    # Simple Levenshtein ratio, stdlib difflib is close enough for a pilot
    from difflib import SequenceMatcher
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()

def score(a, b):
    return 0.6 * jaccard(a, b) + 0.4 * edit_ratio(a, b)

def block_key(row):
    n = normalize(row["name"])
    return n[:1] if n else ""

def resolve(rows, auto=0.90, review=0.75):
    blocks = defaultdict(list)
    for r in rows:
        blocks[block_key(r)].append(r)
    pairs = []  # (a, b, score, decision)
    for bucket in blocks.values():
        for i, a in enumerate(bucket):
            for b in bucket[i+1:]:
                s = score(a["name"], b["name"])
                decision = ("merge" if s >= auto
                            else "review" if s >= review
                            else "distinct")
                if decision != "distinct":
                    pairs.append((a, b, s, decision))
    return pairs
```

Survivorship as a small rule engine:

```python
SURVIVORSHIP = {
    "legal_name":  {"rule": "longest_non_null"},
    "tax_id":      {"rule": "source_priority", "order": ["sap", "netsuite"]},
    "email":       {"rule": "most_recent"},
    "address":     {"rule": "most_recent"},
}

def survive(records, field):
    rule = SURVIVORSHIP[field]["rule"]
    non_null = [r for r in records if r.get(field)]
    if not non_null:
        return None, None
    if rule == "longest_non_null":
        winner = max(non_null, key=lambda r: len(r[field]))
    elif rule == "most_recent":
        winner = max(non_null, key=lambda r: r.get("updated_at", ""))
    elif rule == "source_priority":
        order = SURVIVORSHIP[field]["order"]
        winner = min(non_null, key=lambda r: order.index(r["_source"])
                     if r["_source"] in order else 999)
    return winner[field], winner["_source"]
```

The tuple return — `(value, source)` — is the lineage seed. Every field in the merged entity carries provenance.

## FIELD NOTES

- The review queue is the killer artifact. Every FDE engagement that ships an entity resolver ships a small internal UI (one HTML file, Lesson 03 of Phase 2) that shows candidate pairs and lets a data steward click merge/split. Without it, the middle-band pairs sit forever.
- Company legal-name resolution is 80% won by normalizing suffixes: `Inc`, `Inc.`, `Incorporated`, `Ltd`, `Limited`, `LLC`, `L.L.C.`, `Corp`, `Corporation`, `GmbH`, `S.A.`, `Pte Ltd`. Strip them before scoring. Keep the original around for display.
- Person-vs-company confusion (the `John Smith, ACME Corp.` case) is a *type* problem, not a *score* problem. Add a `record_type` field early and block on it — never fuzzy-match across types.
- Tune thresholds by labeling a hundred pairs by hand and computing precision/recall. Do it in the first week. The right thresholds vary wildly by domain — hospital patient records need higher thresholds than B2B leads.
- Survivorship rules that "the business owns" often turn out to be one senior person's opinion. Get the rules in writing, in a table the data steward reviews, before you flip merges on in production.

## INTERVIEW ANGLE

Fuzzy matching questions are frequent in FDE loops because they combine algorithms, judgment, and stakeholder awareness.

Sample questions:

1. "You have 500,000 company names, and you suspect 15% are duplicates with typos. Design the pipeline." (Expected: normalize + suffix-strip, block on first letter or first token, score with a blend, two thresholds with a review queue, tune with a labeled sample.)
2. "Your merged customer record has a tax ID from SAP and an address from NetSuite. Someone updates the SAP address next week. What should happen?" (Depends on survivorship rule — most-recent would flip; source-priority would not. Tests whether the candidate thinks about the *steady-state* behavior, not just the initial merge.)
3. "Why not just use fuzzy matching without blocking?" (O(n²) blows up. On 100K rows, 5B comparisons. Blocking cuts to O(n · b) where b is avg bucket size — often 100x speedup with negligible recall loss.)

## DRILL

1. **Extend:** add a suffix-normalizer that strips `Inc`, `Ltd`, `Corp`, `GmbH`, `S.A.` (case-insensitive, with and without trailing period) before scoring. Add a test where `ACME Inc.` and `ACME Corp` score high but stay in different buckets from `ACME Bank Ltd`.
2. **Break:** add a person record with name `Acme Cortez` to a bucket full of company records for `Acme Corp`. Does it get flagged for merge? If yes, add a type field and re-block. Write the assertion.
3. **Fix:** add a `survive_entity` function that takes a list of matched source records and returns a single canonical entity plus a `_lineage` dict of `{field: source_id}`. Assert that `most_recent` picks the newer of two records, and that `source_priority` picks SAP even when NetSuite's record is newer.
