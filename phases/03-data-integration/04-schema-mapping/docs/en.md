# Schema Mapping: Source → Canonical, and Who Owns Canonical

**Phase 3 · Lesson 04 · ~1.5h**

## PROBLEM

Week three of a supply-chain pilot at a manufacturer with four operating subsidiaries. Each subsidiary runs a different ERP: SAP in Germany, NetSuite in the US, a homegrown Oracle in Brazil, and a decade-old Microsoft Dynamics in the UK. Your job is one customer master. You start mapping columns. SAP has `KUNNR` (customer number) and `NAME1` (name). NetSuite has `Customer ID` and `Company Name`. Oracle has `CLI_CODIGO` and `RAZAO_SOCIAL`. Dynamics has `CustomerNo` and `Name`.

Fine. You write a mapping table. Then you hit the second-order questions: the SAP `KUNNR` is 10 characters, NetSuite's `Customer ID` is 8 characters, and Oracle's `CLI_CODIGO` is a 6-digit integer. Which is *the* customer ID? Someone has to decide. When a legal name differs across systems (`ACME Ltd.` vs `ACME LIMITED` vs `Acme, Inc.`), which is *the* name? When SAP has 47 customer fields and NetSuite has 23, does the canonical model have 47, 23, the union, or the intersection?

You could keep asking the customer. But by day three of the mapping meeting, three VPs disagree, the data steward from Brazil hasn't been invited, and the head of IT wants to know when you'll "be done." The mapping isn't a technical problem — it's a political problem you have to structure and then execute.

## INTUITION

Schema mapping is where FDE meets diplomacy. The design space:

**Canonical vs. federated.** A *canonical* model is one target schema; every source maps into it, downstream reads only it. A *federated* model keeps each source's schema and provides a query layer that resolves at read time. Canonical wins for pilots — it's simpler, it's demoable, it forces the political conversation early. Federated is what you migrate toward at scale.

**Union, intersection, or 80/20?** The union of all source fields is bloated and full of nulls where systems disagree on what they track. The intersection is small and loses valuable data. The pragmatic canonical is 80/20: the fields that every source has (natural intersection) *plus* the fields any one source has that materially matter for the pilot's KPI. Everything else waits.

**Who owns canonical?** This is the load-bearing question. If nobody owns it, every new source becomes a re-negotiation. Options: (a) the customer's data governance team (correct answer, rarely exists); (b) a designated business owner per domain (customer master owned by sales ops, product master by manufacturing) — the practical answer; (c) you, the FDE (the trap — you leave, ownership vanishes). Force option (b) explicitly before the second mapping meeting.

**Mapping metadata.** Every mapping row needs six things: source system, source column, source type, canonical field, transform (identity, cast, lookup, concat, custom), and confidence. The confidence field is the surprise workhorse — a mapping marked "guessed, needs SME confirmation" gets escalated in the weekly, and drives the customer's data steward to review before you go live.

**Transforms that pay rent.** Identity (copy across), cast (string to date), lookup (Brazilian state code `SP` → `São Paulo`), concat (first + last → full name), and enum-remap (SAP's status `X01` → canonical `active`). Anything more complex is a code path, not a mapping entry — split it out.

## BUILD IT

The map itself is data, not code. A minimal representation:

```python
# canonical schema: what your downstream world reads
CANONICAL = {
    "customer_id":   {"type": "string", "required": True,  "unique": True},
    "legal_name":    {"type": "string", "required": True},
    "country":       {"type": "string", "required": True},
    "tax_id":        {"type": "string", "required": False},
    "created_date":  {"type": "date",   "required": False},
}

# one mapping per (source_system, canonical_field)
MAPPINGS = [
    # SAP
    ("sap", "KUNNR",    "customer_id",  "identity", 1.0),
    ("sap", "NAME1",    "legal_name",   "identity", 1.0),
    ("sap", "LAND1",    "country",      "lookup:sap_country", 0.95),
    ("sap", "STCEG",    "tax_id",       "identity", 0.9),
    # NetSuite
    ("netsuite", "Customer ID",   "customer_id", "identity", 1.0),
    ("netsuite", "Company Name",  "legal_name",  "identity", 1.0),
    ("netsuite", "Country",       "country",     "identity", 1.0),
    ("netsuite", "VAT Number",    "tax_id",      "identity", 0.9),
    ("netsuite", "Created Date",  "created_date","cast:date", 1.0),
    # Oracle (homegrown)
    ("oracle", "CLI_CODIGO",      "customer_id", "cast:string", 0.9),
    ("oracle", "RAZAO_SOCIAL",    "legal_name",  "identity", 1.0),
    ("oracle", "CNPJ",            "tax_id",      "identity", 1.0),
    # ... Dynamics ...
]

LOOKUPS = {
    "sap_country": {"DE": "Germany", "US": "United States", "BR": "Brazil"},
}

def apply(source_system, row):
    out = {}
    for sys, src, canon, transform, conf in MAPPINGS:
        if sys != source_system or src not in row:
            continue
        v = row[src]
        if transform == "identity":
            out[canon] = v
        elif transform.startswith("cast:"):
            out[canon] = cast(v, transform.split(":")[1])
        elif transform.startswith("lookup:"):
            out[canon] = LOOKUPS[transform.split(":")[1]].get(v, v)
    return out
```

Two moves are load-bearing. First, the mapping table is data — it can be a CSV the customer's data steward edits, reviewed in a git PR. Politics get externalized to the artifact instead of buried in Python. Second, confidence per row lets you generate a "needs review" report automatically: filter for `conf < 1.0` and hand the list to the SME.

The `apply` function is deliberately simple; complex transforms (splitting a full-name field into first/last, deriving canonical status from multiple flag columns) go in named functions in a `transforms.py` module, called from a `custom:` transform tag.

## FIELD NOTES

- The mapping table is a *conversation artifact*. Print it and walk the customer's data owner through it row by row. You will learn things about their data no ETL tool would ever tell you — "oh, `KTOKD` is the account group, we stopped using it in 2019 but it's still populated."
- Reserve one canonical field for `_source_system` and one for `_source_id`. Downstream, when someone asks "where did this customer come from," you can answer. Lineage (Lesson 13) depends on it.
- The union-of-fields temptation is strong when a stakeholder says "we might need X someday." Refuse. Canonical fields cost forever — every source has to either populate or explicitly null them. Add on demand, not on speculation.
- When two sources disagree on the *same* customer's legal name, that's not a mapping problem — that's a survivorship problem for entity resolution (Lesson 06). Don't try to fix it in the mapping layer.
- Version the canonical. `v1` shipped with the pilot, `v2` added `industry_code` after quarter two, `v3` renamed `country` to `country_code` when Iran wanted three-letter ISO. Migrations are inevitable; make them explicit.

## INTERVIEW ANGLE

Palantir decomp rounds love this exact scenario because it's where data engineering meets stakeholder management.

Sample questions:

1. "A customer has four ERPs. Design the schema mapping process — the meetings, the artifact, and the code." (Expected: canonical target, mapping table as data, per-source mappings with confidence, named owner for the canonical, a review cadence.)
2. "SAP has 200 customer fields. Your pilot needs six. Which do you map?" (The six, plus source ID and source system for lineage. Refuse to speculate. Show how you'd add more on evidence.)
3. "Two source systems disagree on a customer's legal name. Where in the pipeline do you handle it?" (Survivorship in entity resolution — not schema mapping. The mapping layer's job is to translate; conflict resolution is a separate concern.)

## DRILL

1. **Extend:** add a `concat` transform (`"concat:first_name,last_name"`) that joins two source columns with a space. Add a test that maps a Dynamics row with `FirstName` + `LastName` to canonical `legal_name`.
2. **Break:** add a source column to the mapping table that doesn't exist in the source data (typo: `KUNRR` instead of `KUNNR`). Watch `apply` silently produce a row with missing `customer_id`. Add a startup check that validates every mapping against a sample of the source and prints missing sources.
3. **Fix:** generate the "needs SME review" report — a CSV listing every `(source_system, source_column, canonical_field)` where `conf < 1.0`, plus three sample values from the source. Hand this to the customer's data owner; that's your week-three artifact.
