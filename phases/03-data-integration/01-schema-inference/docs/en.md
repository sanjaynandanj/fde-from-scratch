# Schema Inference from Scratch: Types, Nulls, and Lies

Phase 3 · Lesson 01 · ~2h

## PROBLEM

Week two of a logistics pilot. The customer's "data dictionary" turns out to be a 2019 SharePoint page describing a schema two migrations ago. The actual export has 74 columns. You load it, cast what looks numeric, and build the first dashboard. It demos fine. Then the ops manager squints at a shipment and says: "why is this going to depot 42? We don't have a depot 42. We have depot *042*." Your loader read `dept_code` `00042` as the integer `42`, silently, on every row. Elsewhere, the `bonus` column you averaged was one-third `N/A` strings — Python happily treated them as data until the mean came out garbage — and the `hired` column parsed until row 8,431, where the format switched from ISO to `12-Mar-2019` because a different subsidiary's system fed those rows.

Customer exports never come with a truthful data dictionary. The first professional act of any integration is to *infer* the schema from the data itself — types, nullability, uniqueness — while surviving the standard lies. Doing it by eyeball across 74 columns doesn't scale; doing it wrong poisons everything downstream. So you build an inferencer.

## INTUITION

Schema inference is a voting problem with hostile voters. The design space:

**What's a null?** Not just empty string. Real exports encode missing-ness as `N/A`, `NA`, `null`, `None`, `-`, `nil`, and Excel's own `#N/A`. If you don't strip these *before* type-voting, one `N/A` in a numeric column demotes it to string. Nulls are metadata, not values.

**How do you vote on a type?** Two schools: majority voting (column is int if most values parse as int) versus unanimity (all non-null values must parse). Unanimity is stricter and correct for pilots: a column that's 99% int and 1% `TBD` is *not* an int column — it's a string column with a data-quality problem you need to surface, not hide. Majority voting silently eats exactly the rows that will embarrass you in a demo.

**In what order do you test types?** Specificity order matters because parsers overlap: `1` parses as int, float, and arguably bool. Test narrow-to-wide — bool, int, float, date — and fall through to string, the type that never lies. First unanimous winner takes the column.

**Which lies do you defend against?** Three classics, all in this lesson's data:

- *Thousands separators:* `1,250.50` is a number wearing a costume. Strip commas before parsing.
- *Leading zeros:* `00042` parses as int 42, but a leading zero is a near-certain signal of an *identifier* — zip codes, department codes, account numbers. Identifiers must stay strings or you corrupt joins forever.
- *Format-mixed dates:* one column, four date formats, because the export unions rows from multiple source systems. A single-format parser "works" until the row where it doesn't.

Beyond type, two cheap facts pay rent immediately: **nullability with a rate** (a 50% null column changes what features you promise) and **uniqueness** (candidate keys for the entity resolution coming in Lesson 05).

## BUILD IT

Run it: `python code/lesson.py`. The file is ~110 lines; here's the anatomy.

**Null detection is a set membership test.** All null spellings live in one constant, matched case-insensitively after stripping:

```python
NULL_TOKENS = {"", "n/a", "na", "null", "none", "-", "nil", "#n/a"}

def is_null(v: str) -> bool:
    return v.strip().lower() in NULL_TOKENS
```

Every customer adds a spelling or two (`UNKNOWN`, `TBD`, `--`); you extend the set, and nothing else changes. That's why it's a named constant, not inline logic.

**Each type gets a `try_*` function that returns a value or `None`.** The int parser carries the leading-zero defense:

```python
def try_int(v: str):
    s = v.strip().replace(",", "")
    if s.startswith("0") and len(s) > 1:
        return None  # leading zero => identifier, not a number
    try:
        return int(s)
    except ValueError:
        return None
```

`try_float` repeats the rule with one refinement — `s[1] != "."` — so `00042` is rejected but `0.5` still parses. `try_date` loops five formats (`%Y-%m-%d`, `%d/%m/%Y`, `%m-%d-%Y`, `%d-%b-%Y`, `%Y/%m/%d`) and returns the first hit; adding a customer's cursed format is a one-line append to `DATE_FORMATS`. `try_bool` maps `true/false/yes/no/y/n` through a dict.

**The voter enforces unanimity in specificity order.** `infer_column` filters out nulls, then runs the check ladder:

```python
checks = [
    ("bool", lambda v: try_bool(v) is not None),
    ("int", lambda v: try_int(v) is not None),
    ("float", lambda v: try_float(v) is not None),
    ("date", lambda v: try_date(v) is not None),
]
inferred = "string"
for type_name, check in checks:
    if non_null and all(check(v) for v in non_null):
        inferred = type_name
        break
```

Two subtleties are load-bearing. First, `all(...)` is the unanimity rule — one `TBD` in a thousand ints demotes the column, by design. Second, the `non_null and` guard means an *all-null* column stays `string` rather than vacuously passing the bool check (an empty `all()` is `True` — a classic trap).

The return dict carries the working facts: `type`, `nullable`, `null_rate` (rounded, so reports read cleanly), and `unique` computed on stripped non-null values.

**`infer_schema` is a transpose plus a map.** `list(zip(*rows))` flips row-major CSV data into columns; each column goes through `infer_column`. The empty-rows guard builds empty columns so headers-only files don't crash.

**The assertions encode the war stories.** The test data is one 4-row employee table containing every lie at once, and the asserts read like the field checklist: `salary` must be float despite commas; `hired` must be date across *four* formats; `dept_code` must be string (`"leading zeros mean identifier"`) and non-unique; `bonus` must be a nullable int with `null_rate == 0.5` — the `N/A` and `""` counted as nulls, not strings, so the int vote still passes. Then two edge cases: an int column with one stray `"TBD"` degrades to string (unanimity), and an all-null column reports `null_rate == 1.0` without inferring a fake type.

## FIELD NOTES

- Run inference on the *full* extract, not the first 1,000 rows. The format switch, the first null, the first Excel casualty are always in the part you didn't sample. If you must sample, sample randomly — the head of an export is the cleanest part.
- The inferred schema is a *conversation artifact*, not just code input. Printing "column `bonus`: int, 50% null" to the customer's data owner surfaces truths their own team often doesn't know, and it makes you credible in week two. Some of the best discovery meetings are just walking through an inference report together.
- Leading-zero corruption is frequently *already in the file* because someone opened it in Excel before you got it (Excel strips them on open, and mangles long numerics into `1.23457E+15`). Inference can flag the survivors, but Lesson 02's survival kit deals with the casualties.
- Dates deserve paranoia beyond this lesson: `03-01-2022` is January 3 or March 1 depending on which subsidiary wrote it. Unanimous *parseability* doesn't guarantee unanimous *meaning* — when both `%d/%m/%Y` and `%m/%d/%Y` fit, you need value-range evidence (a day > 12 disambiguates) or a human. Lesson 03 goes deep.

## INTERVIEW ANGLE

Data-munging rounds love this problem because it's small enough to code live and deep enough to expose judgment. Palantir-style loops probe it via "you receive an unknown extract — what do you do first"; lab loops often hand you a literal messy file.

Sample questions:

1. "You get a CSV with no documentation. Walk me through programmatically profiling it." (Expected: null-token handling, type voting with specificity order, null rates, uniqueness, and *why* unanimity beats majority.)
2. "A column contains `00042`. Your parser says int. What went wrong and what breaks downstream?" (Identifier vs. quantity; broken joins, dropped zeros in display, failed reconciliation.)
3. "How would you detect that one column mixes two date conventions?" (Multi-format attempts, plus ambiguity detection when multiple formats parse — and the honest answer that some rows need range evidence or a human.)

## DRILL

1. **Extend:** add a `try_currency` detector that strips `$`/`€` prefixes so `"$1,250.50"` infers as a new `currency` type ranked between float and date. Add a test column and assertions.
2. **Break:** add the value `"1e3"` to a column of plain ints. `float("1e3")` succeeds — what does the ladder infer, and is that right? Decide, then encode your decision as an assertion.
3. **Fix:** the current `unique` check compares stripped strings, so `"42"` and `"042"` count as distinct — but after your pipeline casts ints they'd collide. Add a `unique_after_cast` field that checks uniqueness on *parsed* values for typed columns, and write the assertion that catches the collision.
