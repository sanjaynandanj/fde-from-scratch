# The Messy CSV Survival Kit: Encodings, Delimiters, Excel Damage

**Phase 3 · Lesson 02 · ~1.5h**

## PROBLEM

Tuesday morning of week two. Your champion at a mid-sized freight broker emails you an attachment titled `customer_master_FINAL.csv` — 380KB, "the source of truth," ready for your ingestion pipeline. You double-click. Python throws `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 4127`. You force `latin-1`. It loads, but the file has 47,000 rows in a single column because someone saved it with semicolons on a German laptop and Python assumed commas. You fix the delimiter. Now the customer IDs that used to be `0034521` are `34521` because Excel silently stripped leading zeros the last time your champion opened the file to "clean it." The `notes` column has cells that look like `="ACME, Inc"` — Excel's formula-armor trick to force text formatting, which your parser now reads verbatim. And row 12,004 has a raw newline inside a quoted string, which broke your line count off by three from row 12,005 onward.

None of this is in the data dictionary. All of it is in every real CSV a customer will ever hand you.

## INTUITION

A CSV is not a format — it's a family of loosely-related dialects, plus whatever damage the last human tool inflicted on the file. The design space has four independent axes and you must detect, not assume, each one:

**Encoding.** UTF-8 is the modern default but you will see UTF-8-BOM (Excel's export flavor, with three magic bytes at the head that break naive parsers), UTF-16-LE (Excel "Unicode Text" export, with null bytes between every character), Windows-1252/Latin-1 (Western European legacy, distinguishable from UTF-8 only when a non-ASCII byte appears), and occasionally Shift-JIS or GB18030 if the customer has an Asia subsidiary. Detection order: check for BOM bytes, try UTF-8 strict, fall back to Windows-1252 (never fails, may mojibake).

**Delimiter.** Comma is the name but semicolon is common in Europe (because their decimal comma steals the field separator), tab is common in warehouse exports, and pipe `|` shows up in mainframe dumps. Sniff by counting candidate delimiters on the first ten lines and picking the one with consistent counts across lines.

**Quoting.** Fields with commas, newlines, or quotes must be quoted. RFC 4180 says double-quote with `""` to escape. Excel obeys until it doesn't (formula-armor `="..."`). Sloppy exports sometimes leave commas unquoted inside free text, which is unrecoverable without a heuristic.

**Excel damage.** The special category. Leading zeros stripped from IDs. Long numeric IDs converted to `1.23457E+15`. Dates auto-formatted from `Mar-1` (product code) into 1-March. Trailing whitespace from copy-paste. BOM prepended on save. This damage is often irreversible — the survival kit's job is to *detect* it and quarantine the file before it poisons your entities.

The philosophical move: treat the raw bytes as untrusted input. Sniff, validate, and log what you found. Never assume.

## BUILD IT

The survival kit is a small decision tree, not a big library. Sketch it as a `load_csv` function that returns `(rows, report)`:

```python
def load_csv(path):
    raw = open(path, "rb").read()

    # 1. Encoding: BOM first, then UTF-8, then Windows-1252
    if raw.startswith(b"\xef\xbb\xbf"):
        encoding, raw = "utf-8-sig", raw[3:]
    elif raw.startswith(b"\xff\xfe"):
        encoding = "utf-16-le"
    else:
        try:
            raw.decode("utf-8"); encoding = "utf-8"
        except UnicodeDecodeError:
            encoding = "cp1252"
    text = raw.decode(encoding, errors="replace")

    # 2. Delimiter: count candidates on first 10 lines, pick most consistent
    sample = text.splitlines()[:10]
    candidates = [",", ";", "\t", "|"]
    scores = {d: min(line.count(d) for line in sample) for d in candidates}
    delimiter = max(scores, key=scores.get)

    # 3. Parse with stdlib csv (handles quoting correctly)
    import csv, io
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)

    # 4. Excel damage flags
    report = {"encoding": encoding, "delimiter": delimiter}
    report["scientific_notation_ids"] = any(
        "E+" in cell for row in rows for cell in row)
    report["formula_armor"] = any(
        cell.startswith('="') for row in rows for cell in row)
    return rows, report
```

Two moves earn their keep. First, decoding with `errors="replace"` instead of `strict` — a corrupt file with three bad bytes should still load with three `?` characters and a warning, not crash the whole pipeline. Second, the report dict is the point: the FDE artifact isn't the loaded data, it's the *diagnostic* the customer's data owner needs to see. Print the report at the top of every ingestion run.

## FIELD NOTES

- Ask for the file twice — once as sent, once re-exported directly from the source system, not opened in Excel in between. Compare. The diff is your Excel-damage inventory.
- The BOM is a diplomatic issue. Your customer's data team exports from Excel, gets a BOM, and their downstream Java system rejects it. They blame you. Show them the three bytes and the fix (`utf-8-sig` on read).
- Semicolon exports from German, French, and Portuguese systems are the single biggest tripwire for US-based FDEs. Assume it if the customer's HQ is in continental Europe.
- Trailing whitespace and non-breaking spaces (`\xa0`) are invisible in most editors. Cast every field through `.strip()` before comparison, and log the raw bytes when a "should match" doesn't.
- If the file is over a few hundred MB, stream it — don't load whole into memory. The sniff logic works on the first 8KB; the parse then reads line by line.

## INTERVIEW ANGLE

Data-munging rounds love this because a candidate who says "I'd use pandas" without discussing encoding, delimiter, or Excel damage has just told you they've never actually shipped against a customer file.

Sample questions:

1. "I hand you a file called `export.csv`. Before you write parsing code, what do you check?" (Expected: encoding via BOM/decode-try, delimiter via sniff, sample the first and last few rows, look for Excel damage signals.)
2. "A customer says their IDs 'don't match' between your system and theirs. Their file has a column `id` with values like `1.23E+18`. What happened and can you recover?" (Excel opened a 19-digit ID, exceeded int64 precision in display, saved back as scientific notation — data is *lost*, not just displayed wrong. You must re-request the export from the source, not the intermediary.)
3. "Design a `sniff_dialect` function without using `csv.Sniffer`." (Tests whether you understand the counting heuristic and its failure modes — a file with commas in free text and only ten rows breaks it.)

## DRILL

1. **Extend:** add UTF-16-LE handling by detecting the `\xff\xfe` BOM and using `raw.decode("utf-16")`. Test with a file exported from Excel as "Unicode Text."
2. **Break:** feed the loader a file where row 500 has a raw newline inside a quoted field. Does `csv.reader` handle it? What if the same row is missing its closing quote?
3. **Fix:** add a `leading_zero_survivors` check to the report — scan the first "id-like" column (name matches `id`, `code`, `zip`) and flag if any value both starts with `0` and is longer than 1 character. This is your evidence artifact when the customer swears "the IDs are fine."
