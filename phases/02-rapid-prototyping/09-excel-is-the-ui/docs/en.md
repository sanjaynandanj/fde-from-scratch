# Excel Is the UI: Export, Import, and Living With It

**Phase 2 · Lesson 09 · ~1h**

## PROBLEM

An FDE at an insurance carrier builds a beautiful review workflow: web UI, keyboard shortcuts, filters, bulk actions. Ships it to the underwriters in week four. Week five, usage is near zero. He asks the champion why. The champion, embarrassed, shows him: every underwriter has been downloading the CSV, opening it in Excel, marking rows with colored fills, and emailing it around. His web UI has a "reviewed" checkbox they refuse to use.

He rebuilds. The new version has one button: "Export to Excel." The Excel file has a "reviewed" column, a "notes" column, and a data validation dropdown. It also has an "Import" button that reads the modified file back. Usage in week six: 100%. The dashboard's "reviewed count" metric — the one the VP is measured on — starts moving for the first time.

Excel wasn't the enemy. Excel was the actual UI.

## INTUITION

For entire classes of enterprise users — finance, ops, underwriting, claims, procurement, most of accounting — Excel is not a tool, it is the *default surface* for structured work. They can pivot, filter, annotate, and share in it faster than they can learn any web UI you build. Fighting this is a losing battle. Embracing it is one of the highest-leverage patterns in the FDE toolkit.

Three patterns of Excel integration, in order of leverage:

- **Export.** Any table you show in your UI, export it as `.xlsx` or `.csv` with one click. This is the minimum. Users trust that they can escape your app.
- **Round-trip.** Export with mutable columns (`reviewed`, `notes`, `assigned_to`); accept the modified file back via drag-and-drop or upload; reconcile changes into your system. Users work where they want to work.
- **Excel-as-workflow.** The primary interface *is* the spreadsheet. Your app generates it, distributes it, ingests annotations, aggregates. The web UI is just for admin and reporting.

When to use which:

- Read-only reporting → export is enough.
- Human-in-the-loop review, categorization, approval → round-trip.
- Scattered users, no shared web app, or the champion says "just send me a spreadsheet" → Excel-as-workflow.

Design constraints Excel imposes:

- **No headers on row 2.** Excel users freeze row 1. Your header must be there, one row, plain text.
- **Types survive imperfectly.** Excel will helpfully turn `08234` into `8234`, `2024-03-01` into `44621`, and `SEP-3` into a date. Test round-trip with adversarial IDs.
- **Formulas break.** Never ship a file with formulas the user can accidentally overwrite. Use values.
- **Data validation is your friend.** Dropdowns constrain values; a controlled vocabulary in Excel beats free-text.

## BUILD IT

Stdlib-only Excel is a lie — `openpyxl` is where you'd go for real `.xlsx`. But for pilots, CSV plus a strong convention gets you 80% of the way, and Excel opens CSV natively.

The round-trip pattern:

```python
import csv, hashlib, pathlib

REVIEWABLE_COLS = {"reviewed", "notes", "assigned_to"}
IMMUTABLE_COLS = {"id", "vendor", "amount", "issued"}

def export_for_review(rows, out_path):
    """Write CSV with a stable ID hash so we can detect tampering with immutable cols."""
    fields = list(IMMUTABLE_COLS) + list(REVIEWABLE_COLS) + ["_row_hash"]
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:  # BOM for Excel
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            row = {k: r.get(k, "") for k in fields}
            row["_row_hash"] = _hash({k: r[k] for k in IMMUTABLE_COLS})
            w.writerow(row)

def import_reviewed(in_path, current_rows):
    """Merge only reviewable columns; reject rows whose immutable data was tampered."""
    current = {r["id"]: r for r in current_rows}
    accepted, rejected = [], []
    with open(in_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            live = current.get(row["id"])
            if not live: rejected.append((row, "unknown id")); continue
            expected = _hash({k: live[k] for k in IMMUTABLE_COLS})
            if row.get("_row_hash") != expected:
                rejected.append((row, "immutable data changed")); continue
            for c in REVIEWABLE_COLS:
                live[c] = row.get(c, "")
            accepted.append(live)
    return accepted, rejected

def _hash(d):
    s = "|".join(f"{k}={d[k]}" for k in sorted(d))
    return hashlib.sha1(s.encode()).hexdigest()[:12]
```

Notes:

- **`utf-8-sig`** writes a BOM so Excel opens the file without a wizard. Skip it and every column will land in column A.
- **Row hash** protects you from users editing immutable data by accident. The hash lives in a column; the diff catches tampering before you overwrite state.
- **Reject with reasons.** Never silently drop rows on import. The user needs to know row 47 came back wrong.
- **Preserve the user's other columns.** Users add columns (`my_notes`, `flag`). You must not blow them away on round-trip; simplest: only touch known fields on import.

For real `.xlsx` with dropdowns and freezes, `openpyxl` is worth the one dep — but for the pilot, CSV with BOM is 90% of the win.

## FIELD NOTES

- The first Excel round-trip request usually looks like "can we just get a spreadsheet?" It is almost always a bigger workflow than the champion realizes. Ask: who edits it, how many people, do they mail it around, how do we know when they're done. The answers reshape the pilot.
- Users will paste Excel columns into other Excel files. Any ID column is likely to be corrupted by Excel's helpful type coercion (leading zeros, scientific notation, date interpretation of SEP-3). Ship IDs as strings; when possible, use a prefix (`INV-00082` not `00082`).
- The champion who lives in Excel is one of your best allies. They will forward your spreadsheet to people you'll never meet, and the reach becomes your ally in the renewal conversation. Design the file to be forwardable — clear headers, a bit of instruction in row 1 as a comment, a filename with the date.
- Don't fight the "email the spreadsheet around" habit early. Instrument it: when the file comes back, log who submitted it. That telemetry proves adoption to your executive stakeholders.

## INTERVIEW ANGLE

Interviewers probe humility about who the actual user is.

Sample questions:

1. "The customer's users prefer Excel to your web app. What do you do?" (Testing: meet users where they are, round-trip the spreadsheet, treat Excel as a first-class UI.)
2. "How do you handle a user modifying immutable columns in an exported spreadsheet?" (Testing: some form of tamper detection — row hash, checksum — and clear rejection with reasons.)
3. "What are the pitfalls of Excel round-trip?" (Testing: type coercion, leading zeros, date parsing of IDs, encoding issues, users adding columns you must preserve.)

## DRILL

Take a table from any dataset. Write an `export_for_review` and `import_reviewed` pair using the pattern above. Export it, open it in Excel or Sheets, edit a few rows (mark reviewed, add notes), also tamper with one row's amount, save, and import back. Confirm your import accepts the reviews, preserves anything else, and cleanly rejects the tampered row with a reason. Now try it with an ID column like `007234` and see what Excel did to it — fix by prefixing with a letter. Save the pattern; you will use it in every pilot with a review workflow.
