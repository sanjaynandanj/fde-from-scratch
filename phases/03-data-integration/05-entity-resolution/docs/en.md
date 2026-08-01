# Entity Resolution I: Normalization, Blocking, Exact Match

Phase 3 · Lesson 05 · ~2h

## PROBLEM

The kickoff deck says the customer has 5,000 accounts in the CRM. Three weeks in, you join the CRM against the billing system to build the revenue dashboard, and the numbers are nonsense: "Acme Corp.", "ACME Corporation", and "Acme Corp Inc" are three CRM rows, each holding a slice of the relationship — one has the phone number, one has the email, one has last year's orders. The billing system has a fourth spelling. Your dashboard shows Acme as three small customers instead of one large one, which inverts the entire "focus on your top accounts" story the pilot was sold on. The sales VP looks at the top-10 list, doesn't see a name she knows should be there, and the room goes cold.

Every enterprise has this problem. Duplicate rate in a mature CRM runs 10–30%. Nobody inside the company can fix it by hand — 5,000 records is 12.5 million possible pairs — and every vendor before you either ignored it or quoted a six-month MDM project. The FDE who can deduplicate credibly in week three owns the engagement. The whole discipline is called entity resolution, and this small file contains every idea the production version needs.

## INTUITION

Entity resolution decomposes into four sub-problems, each with a design space:

**1. Normalization.** `"Acme Corp."` and `"ACME Corporation"` differ only in noise: case, punctuation, and legal-suffix vocabulary (`Inc`, `LLC`, `Ltd`, `Corp`). Canonicalize before comparing — lowercase, strip punctuation, expand or delete abbreviations. The subtle decision is *delete vs. expand*: `St → Street` (expand, it's meaning) but `Inc → nothing` (delete, it's legal boilerplate that carries no identity). Get this wrong and either `Main St` ≠ `Main Street` or `Acme Inc` ≠ `Acme LLC` for the wrong reason.

**2. Blocking.** Comparing all pairs is O(n²): 12.5M comparisons at 5k records, 50 *billion* at 100k. Blocking cuts the candidate space: only compare records that share a cheap key — here, zip-prefix plus first letter of the normalized name. The trade-off is recall vs. cost: a too-tight block (full zip + first 3 letters) misses true duplicates whose zip was typo'd; a too-loose one re-approaches O(n²). Production systems run *multiple* blocking passes with different keys and union the candidates.

**3. Pairwise scoring.** Within a block, score each pair. Options range from exact match on normalized names (fast, brittle) to edit-distance ratios to learned models. The field workhorse is a *weighted combination of evidence*: fuzzy name similarity plus hard identifiers (phone, email, tax ID) where present. One principle matters more than the formula: **a missing field is absence of evidence, not evidence of absence.** If one record has no phone, don't penalize the pair — fall back to name-only scoring.

**4. Clustering + survivorship.** Pair decisions must become entity groups. If A≈B and B≈C, then A, B, C are one entity even if A and C never scored (transitivity) — union-find gives you this in near-linear time. Then each cluster needs one surviving record for downstream systems; "most complete record wins" is the honest default, with per-field merge as the production refinement.

## BUILD IT

Run it: `python code/lesson.py`. Seven records, four entities, every stage observable.

**Normalization is a token pipeline.** Lowercase, strip punctuation to spaces, then map tokens through an abbreviation table where legal suffixes map to empty string:

```python
ABBREV = {"st": "street", "rd": "road", "ave": "avenue", "inc": "", "llc": "",
          "ltd": "", "corp": "", "corporation": "", "co": "", "&": "and"}

def normalize(name: str) -> str:
    tokens = re.sub(r"[^\w& ]", " ", name.lower()).split()
    tokens = [ABBREV.get(t, t) for t in tokens]
    return " ".join(t for t in tokens if t)
```

The asserts pin the two behaviors: `normalize("Acme Corp.") == "acme"` (suffix deleted) and `normalize("Main St") == "main street"` (abbreviation expanded). One table encodes the delete-vs-expand judgment call.

**Blocking is a cheap composite key.** `block_key` returns `(record["zip"][:3], norm[:1])` — 3-digit zip prefix plus first normalized letter. Records land in a dict of blocks, and comparisons only happen within a block. The test *asserts the economics*: 7 records naively need 21 comparisons; the assertion `resolve.comparisons < 21` fails if blocking ever stops working. Measuring the comparison count isn't decoration — in production it's the difference between an overnight job and a heat-death job.

**Scoring combines fuzzy name evidence with a hard identifier.** `difflib.SequenceMatcher` (stdlib's edit-similarity ratio) scores normalized names; phones are reduced to digits and compared exactly:

```python
pa, pb = re.sub(r"\D", "", a["phone"]), re.sub(r"\D", "", b["phone"])
if pa and pb:
    return 0.7 * name_sim + 0.3 * (1.0 if pa == pb else 0.0)
return name_sim  # a missing phone is absence of evidence, not a mismatch
```

That last line is the lesson's most important line. Record 3 (`"Acme Corp Inc"`, no phone) still joins the Acme cluster on name evidence alone; penalizing its missing phone would orphan it. The digit-stripping also means `"(555) 0101"` and `"555-0101"` agree — identifier fields need their own normalization.

**Clustering is 10 lines of union-find.** Path-halving `find`, trivial `union`. `resolve` unions every within-block pair scoring ≥ 0.82, then groups records by root. The threshold is a *tunable business decision*, not a constant of nature — 0.82 here is calibrated so "Globex LLC"/"Globex" merge on name evidence plus matching digits, while genuinely different companies never do. The final assertion set proves both directions: cluster sizes come out `[1, 1, 2, 3]`, the Acme trio is `{1, 2, 3}`, the Globex pair `{4, 5}`, and — critically — Initech and Stark (same zip code, 94105) survive as singletons. **Testing that non-duplicates stay separate is half the test.** False merges are worse than false splits in the field: unmerging poisoned data after downstream systems consumed it is a nightmare.

**Survivorship is one honest heuristic.** `survivor` returns the record with the most non-empty fields — record 2 wins Acme because it alone has an email. Production adds recency, source-system trust ranking, and per-field merge; the *shape* (cluster → one canonical record) is what downstream joins need.

## FIELD NOTES

- Show the customer the *clusters*, not the algorithm. A spreadsheet of "we believe these 3 rows are one company" reviewed with someone from sales ops for an hour is worth any amount of threshold tuning — and it converts skeptics, because they recognize the dupes instantly.
- Expect a precision/recall negotiation. Finance wants zero false merges (billing errors); sales wants zero false splits (missed account context). There is no threshold that satisfies both; there is a *review queue* for the 0.70–0.85 gray zone. Lesson 06 builds the scoring maturity for that.
- Names are the weakest identifier you'll ever match on. Fight for hard keys early: tax IDs, DUNS numbers, domains from email addresses. One hard key is worth ten points of fuzzy-match F1.
- Real blocking gets attacked by data quality itself: the zip is missing on 8% of rows, so those records block on `("", "a")` together. Always ask: where do records with *null block keys* go? (Answer: their own pass, or a fallback key.)

## INTERVIEW ANGLE

Entity resolution is arguably *the* signature FDE technical topic — Palantir-adjacent loops treat "dedupe the customer table" as a standard take-home archetype, and case interviews reach it from almost any starting problem ("how would you build a 360° customer view?").

Sample questions:

1. "You have 1M customer records and need duplicates found. Comparing all pairs is 500 billion comparisons. What do you do?" (Blocking — explain key choice, multi-pass blocking, and the recall trade-off.)
2. "Two records: same company name, different phone numbers. One record has no phone at all. How does each case affect your match score?" (Conflicting evidence penalizes; *missing* evidence must not — the absence-of-evidence principle.)
3. "Your dedup merged two companies that are actually different. Walk me through the blast radius and the fix." (Downstream contamination, the need for merge audit trails/reversibility, why false-merge cost usually exceeds false-split cost.)

## DRILL

1. **Extend:** add email-domain evidence to `similarity` — if both records have emails, matching domains add weight. Decide the new weights, then re-verify all cluster assertions still pass (they encode your regression suite).
2. **Break:** change `block_key` to use the *full* zip plus the first **3** letters of the normalized name. Run. Which true duplicate pair stops merging, and which assertion catches it? This is over-blocking, experienced firsthand.
3. **Fix:** add record 8: `{"id": 8, "name": "Acme", "phone": "555-9999", "zip": "10001", "email": ""}` — same name, *different* phone. It currently merges into the Acme cluster (name similarity is high). Adjust the scoring so a hard phone *conflict* (both present, different) subtracts evidence, and write the assertion proving record 8 stays out while record 3 (missing phone) stays in.
