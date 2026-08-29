# Coding Rounds: Practical > Leetcode — Parsing, APIs, Data Munging

**Phase 9 · Lesson 02 · ~1.5h**

## PROBLEM

A candidate with 400 leetcode problems solved sits down for an FDE coding screen. The problem: "here's a CSV of customer records with encoding issues, duplicates, and dates in three formats — write a script that produces a deduplicated, canonicalized JSON export, and expose it behind a single-endpoint HTTP server." He freezes for four minutes trying to figure out what algorithm this is, mentally sorts through his stock repertoire — two-pointer, DP, graph BFS — and none of it fits. He eventually starts writing code, produces something that reads the file, panics about UTF-8 vs Latin-1, spends fifteen minutes on regex for date parsing, and never opens the HTTP server portion. The interviewer's rubric had three sections: parsing correctness, dedup correctness, and endpoint returned something. He scored one out of three, and the feedback said "seemed unfamiliar with practical data work."

He wasn't. He'd done all of this in his day job. The problem was that his interview reflex was pattern-match-to-leetcode, and the round was patterned like *real work*.

## INTUITION

FDE coding rounds test whether you can produce useful software fast against realistic inputs while talking. The three sub-signals interviewers collect:

- **Fluency with messy data**: do you know your standard library well enough to parse a CSV that violates RFC 4180, detect encodings, handle a mix of date formats — without stalling on syntax or googling?
- **Time-to-first-working**: do you get *something* running end-to-end in the first 20 minutes, then iterate — or do you architect for 45 minutes and produce nothing?
- **Verbalized trade-offs**: when you hit a decision (strict vs lenient parsing, in-memory vs streaming, exact vs fuzzy dedup), do you narrate the trade-off and pick, or do you silently choose and hope?

Leetcode teaches none of these. It teaches pattern recognition against clean input with a known-good algorithm. FDE coding rounds start from messy input with no known-good algorithm, and the correct move is *usually* not clever — it's a straightforward parse-clean-transform-emit pipeline that gets built in that order without gold-plating any step.

The archetypes are narrow. Roughly: (1) parse a messy file into structured records; (2) call an API, handle failures, emit structured output; (3) reconcile or dedup two datasets; (4) build a one-endpoint HTTP server over the previous three. Almost every FDE screen is a combination of these.

## BUILD IT

The template. Time-box it and internalize the shape until it's reflexive:

**Minute 0–3 — Clarify then declare defaults.** "What's the file encoding — should I detect or assume UTF-8?" "For dedup, is exact-after-normalization enough, or do you want fuzzy?" "Should the endpoint return JSON or CSV?" When they say "your call," state your default aloud and move: "I'll assume UTF-8 with a Latin-1 fallback, exact-after-normalization dedup, and JSON output." Silent choices burn.

**Minute 3–10 — Walking skeleton.** Read the file, print the first record, exit. Then read all records into a list, print the count, exit. Then the transform stage as a no-op. Then the output stage emitting whatever you have. End-to-end thin slice before any single stage is correct. This is the single biggest differentiator against leetcode-trained candidates who architect for 30 minutes and produce nothing.

**Minute 10–35 — Fill in the stages.** Real parsing (state-machine or `csv.DictReader` with the dialect detected, not `line.split(",")`). Real normalization (casefold, strip, standardize phone/email). Real dedup (dict keyed by the normalization). Real HTTP handler (`http.server.BaseHTTPRequestHandler` in stdlib, one route). Test each stage as you build it — assert on a known input, `python file.py`, iterate.

**Minute 35–50 — The visible extras.** Error rows quarantined to a side list with row numbers, count printed at the end ("parsed 1,204, quarantined 4"). Health endpoint (`/health` → 200). A README comment at the top with assumptions. A one-line self-test at the bottom (`if __name__ == "__main__": test()`).

**Minute 50–end — Extend or narrate.** If they add a follow-up ("add fuzzy matching"), you have working scaffolding to extend. If not, walk them through your assumptions and the trade-offs you didn't take. Never leave the last five minutes silent.

The stdlib toolkit to actually know cold — because typing `import csv` shouldn't be a thing you google:

- `csv.DictReader`, `csv.Sniffer` for delimiter detection.
- `json` with `default=str` for dates.
- `datetime.strptime` and a hand-rolled multi-format parser (14 formats, one loop, first-hit-wins with column-level election).
- `hashlib.sha256` for dedup keys.
- `urllib.request` for the API-call archetype (yes, you can hit real HTTP with stdlib).
- `http.server.HTTPServer` + `BaseHTTPRequestHandler` for the endpoint.
- `sqlite3` when they push you toward persistence.
- `re` for pattern-based normalization — but sparingly; regex-heavy code reads as fragile.

## FIELD NOTES

- The "practical > leetcode" claim isn't anti-algorithm — it's anti-*misapplied*-algorithm. If a round genuinely wants a sliding window or a graph traversal, code it. But recognize that most FDE screens are I/O-shaped, not CPU-shaped, and the CPU-shaped rounds are usually flagged in the invite ("expect data-structure focus").
- On the job, the same rhythm holds. A customer sends a CSV Tuesday morning; by Tuesday afternoon you want a parse-clean-emit script written in under 90 minutes, disposable, correct on the sample. Interviews are timed rehearsals of the Tuesday reflex.
- Interviewers watch the debugging loop as closely as the code. When your parser errors, do you read the traceback and fix precisely, or do you flail? Fluent debugging is a decisive positive signal — it means your day job is real.
- Do not use libraries the interviewer hasn't approved unless you ask. Pandas is fine at some companies and a red flag at others (some want to see you handle the primitives, some want you to be pragmatic). "Mind if I use pandas here, or would you prefer stdlib?" costs nothing and clarifies the rubric.

## INTERVIEW ANGLE

Meta-questions about coding rounds that show up in behavioral or the recruiter conversation:

1. "How do you approach a coding problem where the requirements are ambiguous?" — the model answer is the template above: clarify, declare defaults, walking skeleton, iterate. Say it in that language.
2. "What's your process when you don't know the answer?" — the strong reply is a debugging protocol: reproduce, isolate, read the actual error, hypothesize one thing at a time. Not "I ask the team" — you might not have a team on-site.
3. "How would you interview for this role?" — occasionally asked. The strong answer names practical scenarios and the three sub-signals above, showing you understand the round's mechanics.

## DRILL

Give yourself 60 minutes. Take any messy CSV — a public one from Kaggle, or generate one using Phase 3's data generators. The prompt: "Parse this file, dedup by email (case-insensitive, whitespace-stripped), quarantine unparseable rows, expose the deduped records at `GET /records` and the quarantine list at `GET /quarantine`, stdlib only." Set a timer. When it rings, stop and grade yourself: did you get end-to-end in 20 minutes? Did you narrate assumptions? Did you quarantine rather than silently drop bad rows? Repeat weekly with different messiness (encoding damage, embedded newlines, three date formats) until the template runs on muscle memory. When you can do it in 40 minutes without stalling, you're at interview speed.
