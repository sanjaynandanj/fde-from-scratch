# Setup & Repo Tour: How the Drills, MockLLM, and Flagships Run

Phase 0 · Lesson 06 · ~1h

## PROBLEM

Every technical curriculum dies the same death: lesson 3 requires a vector database, lesson 5 requires an API key with a credit card behind it, lesson 9 requires a package that broke on Windows last Tuesday. The learner spends the evening debugging `pip` instead of learning, and never opens lesson 10. That failure mode is doubly ironic for an FDE curriculum — because working under constraint *is the job*. At a customer site you frequently get a locked-down laptop, no admin rights, no outbound network, and whatever Python ships on the box. This repo is built under exactly that constraint, on purpose.

## INTUITION

Three design rules govern everything runnable here:

**Rule 1 — stdlib only, Python 3.10+.** No `pip install`, ever. HTTP servers come from `http.server`, parsing from `csv` and `json` and `re`, crypto from `hmac` and `hashlib`, retrieval math from `math` and `collections`. This isn't asceticism: building TF-IDF or JWT validation from primitives is how you learn what the libraries actually do — and it mirrors the air-gapped customer environment where your package mirror request is stuck in a queue.

**Rule 2 — self-testing.** Every flagship and drill solution ends in a `main()` full of `assert` statements and runs with one command:

```
python lesson.py
```

It either prints a pass line (e.g., `entity-resolution: all assertions passed (7 records -> 4 entities, ...)`) or dies with an assertion message telling you exactly what broke. There is no test framework to configure, no runner to install. The assertions are also the *specification*: reading them tells you what the code must guarantee, which is how you should read every file here — assertions first, implementation second.

**Rule 3 — MockLLM instead of API keys.** LLM-dependent lessons (RAG, extraction, evals in Phase 5) ship a small deterministic `MockLLM` class inline. It's scriptable: you give it a list of canned responses, and — in the RAG lesson — each scripted step *asserts the prompt contains the evidence it needs*, so if your retrieval fed the model the wrong chunk, the test fails loudly. This teaches the real production lesson: the harness around the model is your engineering; the model is a replaceable component. Everything stays unit-testable, deterministic, and free.

**The layout**, mapped to how you'll use it:

- `phases/<NN>-<name>/<NN>-<lesson>/docs/en.md` — the 6-beat narrative (PROBLEM → INTUITION → BUILD IT → FIELD NOTES → INTERVIEW ANGLE → DRILL). Docs-only lessons stop there.
- `.../code/lesson.py` — flagship lessons only (marked ★ in the README catalog): one self-contained, runnable file.
- `problems/<NN>-<name>/` — Phase 10 field drills: a data *generator* (synthetic but realistically messy — duplicate customers, Excel-mangled IDs, three date formats), a problem statement, and a reference solution with assertions. Generate, attempt, then diff against the reference.
- `interview-bank/` — 150+ theory questions, cases, take-home patterns, behavioral templates.
- `capstones/` — six specs with milestones and rubrics; Capstone 1 is the spine.
- `ROADMAP.md` — 6/12/18-week tracks.

## MAP IT

1. Verify your environment: `python --version` (3.10+ required, nothing else is). On a locked-down machine, `python3` or the Windows `py` launcher may be the right spelling — knowing your interpreter's name is step zero of every engagement.
2. Run your first flagship: `python phases/02-rapid-prototyping/01-csv-to-api/code/lesson.py`. Watch it pass. Then open the file and break it deliberately — change a normalization line — and run again to see how the assertion tells the story.
3. Skim one `problems/` drill folder end to end: generator, statement, solution. Note the pattern; every drill repeats it.
4. Open `ROADMAP.md` and commit to a track (6, 12, or 18 weeks) in writing. Curricula without a calendar don't finish.

## FIELD NOTES

- The stdlib-only discipline pays off at real sites more often than you'd expect: government networks, bank laptops, and OT environments routinely block package installs. The FDE who can build a working tool from a bare interpreter ships while others wait on IT tickets.
- Self-testing is also a *customer* artifact pattern. Files that prove their own correctness (`python check.py` → green) are how you hand work to a customer team that doesn't trust you yet. You'll use this exact move in Phase 3 reconciliation.
- MockLLM's deeper point: if your pipeline only works with one live model on a good day, you don't have a pipeline. Determinism first, then swap in the real model behind the same interface.

## INTERVIEW ANGLE

The repo's design rules are themselves defensible engineering positions, and they come up.

Sample questions:

1. "How would you test an LLM-powered feature without flaky, expensive live-model tests?" (Answer: deterministic fake behind the model interface, assertions on prompts and outputs — exactly MockLLM.)
2. "You're on a customer laptop with no package access. How do you stand up a quick data API?" (Stdlib `http.server` + `csv` — you'll build it in Phase 2, Lesson 01.)
3. "How do you make deliverables trustworthy to a skeptical customer engineer?" (Self-verifying artifacts: scripts that assert their own correctness against agreed numbers.)

## DRILL

Write your own 30-line self-testing file from scratch: a function that parses `"1,250.50"`-style money strings into floats, plus a `main()` with five asserts including two hostile cases (empty string, `"N/A"`). One command, `python money.py`, green or dead. You've just reproduced this repo's contract — and Phase 3 will make that parser earn its living.
