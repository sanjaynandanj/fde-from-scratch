# Chunking Customer Documents: PDFs, Wikis, and 40-Tab Spreadsheets

**Phase 5 · Lesson 02 · ~1.5h**

## PROBLEM

The customer sends over "the docs" the day before the pilot kickoff. You open the zip. There are 312 PDFs (some scanned, some born-digital, one is a photograph of a whiteboard), a Confluence export where every page has a 400-word footer of navigation links, a SharePoint dump with three copies of the same policy under slightly different names, and one Excel file called `Master_Reference_v11.xlsx` that turns out to be a 40-tab spreadsheet with merged cells, hidden rows, and a "Notes" column containing free-form paragraphs of authoritative policy text. The vendor before you dropped all of it into a naive splitter — 1,000 characters per chunk — and shipped. In week two, a user asks about the vacation cap and gets back a chunk that starts mid-sentence, ends mid-sentence, and mixes text from two different subsidiaries. The customer's phrase for what they saw was "hallucination." It wasn't. It was chunking.

Chunking is the highest-leverage lever in RAG quality, and the one most engineers skip because it feels janitorial. It isn't. It's the ontology of the corpus expressed as retrievable units.

## INTUITION

A chunk is a *retrievable unit of one idea*, addressable by a stable ID, small enough that a model can attend to it, and complete enough that a human reading it out of context would understand what it's about. Three variables to reason about:

**Boundary.** Where you cut. Fixed-width character splits are the enemy — they slice sentences and orphan headings from bodies. Paragraphs are the honest default for prose. Structure-aware splits (H2 sections for wikis, rows for tables, cells for spreadsheets) beat paragraphs whenever the document has real structure. The rule: cut where the author already cut.

**Size.** Too big buries the answer sentence and dilutes the TF-IDF score. Too small orphans facts — "the cap is 10 days" is useless without knowing cap on what. Target 200-800 tokens for prose. Tables and spec sheets can go smaller because each row is atomic.

**Context.** Every chunk needs enough surrounding metadata to stand alone: the document title, the section heading path (`Employee Handbook > Leave > Vacation`), and the source ID. Prepend it to the chunk text or store it as sidecar metadata that gets concatenated at prompt time. Without this, "the cap is 10 days" retrieves for questions about expense caps too.

**Overlap.** Sliding-window overlap (10-20% between adjacent chunks) rescues facts that straddle a boundary. Overlap costs storage and can double-count in retrieval scoring — mitigate by deduplicating on retrieval, not indexing.

## BUILD IT

A decision tree you can apply document-by-document:

```
Is it prose (wiki, policy, contract)?
  -> Split on H2/H3 headings first, then paragraphs within.
     Prepend heading path. Overlap 1 paragraph.

Is it a table (spreadsheet, CSV extract)?
  -> One chunk per row. Prepend column headers and sheet name.
     If the sheet has a "Notes" column with paragraphs, split those out
     as their own prose chunks linked to the row's primary key.

Is it a PDF?
  -> Extract text with structure hints (font size = heading signal).
     If it's scanned, OCR first and quarantine chunks with confidence
     < 0.85 for human review — don't ship OCR garbage into retrieval.

Is it a slide deck?
  -> One chunk per slide. Concatenate title + body + speaker notes.
     Slides are already atomic units of one idea.

Is it code or config?
  -> Split on top-level definitions (function, class, YAML top key).
     Never split inside a block.
```

A template chunk record, minimal:

```python
{
    "id": "handbook-2024#leave.vacation.rollover",
    "doc": "handbook-2024",
    "path": ["Employee Handbook", "Leave", "Vacation", "Rollover"],
    "text": "Employees may roll over up to 5 unused vacation days...",
    "source": "sharepoint://hr/handbook-2024.pdf#page=42",
    "hash": "a7f3...",
}
```

The `hash` matters for incremental sync (Phase 3 Lesson 08) — when the source doc changes, you re-chunk only affected sections and invalidate their embeddings.

## FIELD NOTES

- The customer's "documents" are often the 40-tab spreadsheet. Merged cells break every off-the-shelf parser. Write a pre-processor that unmerges (propagating the top-left value down), then chunk. Budget half a day per non-trivial workbook.
- Wikis have boilerplate. Every Confluence page has a header, breadcrumb, and footer of "related links" that carries no information but shares vocabulary with every other page. Strip boilerplate before chunking or your IDF weights collapse — everything looks equally relevant to everything.
- Duplicate documents are the norm. The same policy exists in the wiki, an emailed PDF, and someone's Google Doc. Deduplicate by content hash at ingestion; keep the newest source ID. Don't rely on filenames — `Policy_FINAL_v3.pdf` and `Policy FINAL.pdf` are the same file 40% of the time.
- Version drift kills pilots in month three. If the customer updates the handbook and you don't re-index, users start getting last quarter's answers. Show the source `last_modified` in the citation UI so users can see what they're reading.
- The champion will tell you "just use the wiki, that's the source of truth." It never is. Ask for the last three questions their help desk answered, then find which document contained the actual answer. Half the time it's an email thread nobody indexed.

## INTERVIEW ANGLE

Chunking questions probe whether you've actually run RAG on real enterprise corpora or just watched the tutorial. Interviewers listen for structure-awareness, boundary reasoning, and the metadata-in-chunk instinct.

Sample questions:

1. "How would you chunk a 200-page insurance policy PDF for RAG?" (They want: heading-aware split first, paragraph within, prepend section path, overlap by one paragraph, page number in metadata for citations. Bonus: mention that scanned pages need OCR quarantine.)
2. "You're getting bad retrieval on a specific query. Walk me through diagnosing whether it's chunking or retrieval." (Print the top-k chunks. If the right answer is *in* a chunk but it didn't retrieve, it's a retrieval problem. If the right answer is split across two chunks or buried in noise, it's chunking. Concrete separation of concerns.)
3. "The customer's docs are a 40-tab Excel file. How do you approach it?" (Row-per-chunk with column headers as metadata, split any long free-text columns into their own prose chunks, handle merged cells before parsing, index sheet name as a filter.)

## DRILL

Take a real document you have handy — an employment handbook, a product spec, a term sheet. Chunk it three ways: (1) fixed 500-character splits, (2) paragraph-level, (3) heading-aware with path metadata. Write five realistic questions a user might ask. For each question, manually rank which chunking strategy retrieves the answer cleanest. Notice how (1) loses every time and (3) wins for questions that require knowing which section they're about. Save the notes — you will reuse this exact exercise when arguing with a customer about why "just use the vector DB defaults" is not the answer.
