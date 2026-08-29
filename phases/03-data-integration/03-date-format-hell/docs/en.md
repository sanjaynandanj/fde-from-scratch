# Date-Format Hell: 14 Formats, One Parser

**Phase 3 · Lesson 03 · ~1h**

## PROBLEM

A retail-analytics pilot. You've unified three years of transaction history from four subsidiaries into one warehouse table. Your Monday dashboard looks great — until a regional VP notices that Q1 revenue in the Brazil view is off by exactly one month. You dig in. The Brazilian ERP writes dates as `03/01/2023` meaning 3 January; your parser, having been trained on US-first files, read that same string as 1 March. Every January transaction moved to March. Every March moved to January. The two months don't have equal volume, so the totals are wrong in a way nobody caught until the VP eyeballed a chart.

Meanwhile, another subsidiary uses `03-JAN-23` (Oracle's default), a third uses `2023-01-03T00:00:00Z` (ISO from a modern system), and the exec team pastes numbers from a report where dates come back as Excel serials — `44927` for January 3, 2023, because Excel counts days from 1900. Fourteen different string patterns are hitting one column, and "one parser" needs to route each one to the right meaning.

## INTUITION

Date parsing has three failure modes and they compound. First, *syntax* — the string doesn't match any format you tried. Loud, easy to fix. Second, *semantics* — the string parses under two formats and you picked the wrong one silently. This is the killer: `03/01/2023` succeeds as both `%d/%m/%Y` and `%m/%d/%Y`. Third, *time zones and offsets* — `2023-01-03T00:00:00Z` is midnight UTC, which is the *previous day* in São Paulo local time; report totals shift accordingly.

The design space:

**Format detection strategy.** Two schools. *Try-all-formats-per-row*: attempt every known format on every value, first hit wins — slow, and picks arbitrary winners on ambiguous values. *Detect-per-column*: sniff the format on the whole column first, use it for every row — fast, but breaks when one column mixes formats (which happens when subsidiaries got unioned upstream).

The pragmatic answer is both: sniff per column, and if sniffing finds multiple consistent formats, escalate — either partition by source system or use range evidence (see below).

**Ambiguity resolution.** When a column parses under two formats, use *value-range evidence*. If any value has a day-part greater than 12, the ambiguity collapses — you know the day is the day. Scan the whole column; if the evidence is inconclusive, refuse to guess and surface the ambiguity to the human. Silent guessing is the bug.

**Locale sources of truth.** Ask *where* the file came from. A file exported from a German system is almost certainly `%d.%m.%Y`. A file from a US retail ERP is almost certainly `%m/%d/%Y`. Metadata beats heuristics.

**Excel serials.** Numeric dates. Excel counts days from 1900-01-01 (with a famous leap-year bug for 1900). If a column is all integers between roughly 25,000 and 60,000, it's probably Excel serials. Convert with `date(1899,12,30) + timedelta(days=n)`.

## BUILD IT

The core is a small module: a format registry, a sniff function, and a parser that reports ambiguity honestly.

```python
from datetime import datetime, date, timedelta

FORMATS = [
    ("%Y-%m-%d", "iso"),
    ("%Y-%m-%dT%H:%M:%S", "iso-dt"),
    ("%Y-%m-%dT%H:%M:%SZ", "iso-utc"),
    ("%d/%m/%Y", "eu-slash"),
    ("%m/%d/%Y", "us-slash"),
    ("%d.%m.%Y", "de-dot"),
    ("%d-%b-%Y", "oracle"),      # 03-JAN-2023
    ("%d-%b-%y", "oracle-short"),
    ("%Y%m%d", "compact"),
    ("%b %d, %Y", "us-long"),    # Jan 3, 2023
    ("%d %B %Y", "eu-long"),
]

def try_parse(s):
    hits = []
    for fmt, name in FORMATS:
        try:
            hits.append((datetime.strptime(s.strip(), fmt).date(), name))
        except ValueError:
            pass
    return hits  # may be 0, 1, or many

def sniff_column(values):
    """Return the single format that parses ALL non-null values, or None."""
    non_null = [v for v in values if v.strip()]
    if not non_null:
        return None
    format_survivors = set(name for _, name in try_parse(non_null[0]))
    for v in non_null[1:]:
        format_survivors &= set(name for _, name in try_parse(v))
        if not format_survivors:
            return None
    # If two survive, use range evidence: any day > 12?
    if len(format_survivors) > 1:
        return resolve_ambiguity(non_null, format_survivors)
    return next(iter(format_survivors)) if format_survivors else None

def excel_serial(n):
    return date(1899, 12, 30) + timedelta(days=int(n))
```

Two design points. First, `try_parse` returns *all* matching formats, not just the first — ambiguity is data, not an inconvenience. Second, `sniff_column` uses set intersection across the column: a format wins only if it parses every non-null cell. This catches the "row 8,431 switches format" bug from Lesson 01 by failing loudly instead of parsing 8,430 rows one way and 500 another.

The router: try `sniff_column` on the whole column. If it returns one format, apply it. If it returns None, split the column by source-system tag and try again. If still None, quarantine — do not guess.

## FIELD NOTES

- The two-digit year (`%y`) is a landmine — Python parses `03-JAN-23` as 2023, which is usually right, but `03-JAN-68` becomes 2068 in strptime (the pivot is at 69). If your customer has 1990s historical data, force four-digit years upstream or write a custom parser with a sensible pivot.
- Excel dates ≥ March 1, 1900 are off by one from the "true" 1900-epoch because Excel thinks 1900 is a leap year. `date(1899, 12, 30)` is the standard offset that makes modern dates come out right.
- Always store the parsed date *and* the original string, at least during pilot. When the CFO says "this row is wrong," you need to prove whether the parser lied or the source did.
- Time zones deserve their own paranoia. A "date" in one system is a "timestamp" in another; converting a UTC timestamp to a local date can shift totals by a day. When in doubt, ask the customer what timezone their reporting uses and align on it explicitly.
- `03/01/2023` in a British subsidiary is January 3; in an American one, March 1. The *same file* from a global company can contain both. Partition by source, always.

## INTERVIEW ANGLE

Date parsing is the surprise-hard question of data-munging rounds — sounds trivial, exposes judgment.

Sample questions:

1. "I give you a column of 100,000 date strings. Some are `03/01/2023`, some are `2023-03-01`, some are `44927`. Write the parser." (Expected: sniff per column with unanimity, handle Excel serials, refuse to guess ambiguous cases.)
2. "The column parses under both `%d/%m/%Y` and `%m/%d/%Y`. What do you do?" (Range evidence — any day > 12 disambiguates. If evidence is inconclusive, escalate. Silent choice is wrong.)
3. "Your dashboard shows January totals in March. Root-cause it." (Ambiguous date parse; VP caught it because volume differed. Tests whether the candidate thinks about the failure mode where the numbers are wrong but nothing crashed.)

## DRILL

1. **Extend:** add `%d/%m/%y` and `%m/%d/%y` two-digit variants, and write `resolve_ambiguity` — takes a set of surviving format names and the column values, returns the single winner or None if evidence is inconclusive.
2. **Break:** feed the parser a column where the first 500 rows are `%d/%m/%Y` and the last 500 are `%m/%d/%Y`. Watch `sniff_column` return None. Confirm your handler doesn't silently pick one.
3. **Fix:** add Excel serial detection to `sniff_column` — if all non-null values are integers in `[20000, 60000]`, tag the column as `excel-serial` and convert via `excel_serial`. Assert that `44927` becomes `date(2023, 1, 3)`.
