# The Take-Home: Patterns, Time-Boxing, and the README That Wins

**Phase 9 · Lesson 04 · ~1.5h**

## PROBLEM

An engineer gets a take-home from a hot AI company on a Friday: "build a RAG system over these ~200 contracts and evaluate its accuracy. Return within one week. We estimate 6–8 hours." He spends 22 hours over five nights. He picks a fancy vector database that requires cloud setup. He writes elaborate class hierarchies. He builds a slick Next.js frontend. He never writes an eval harness because "I ran out of time." He submits at 11:58pm Sunday with a README that says "known limitation: no evals yet, will add if extended." He gets a polite rejection. The feedback: "over-engineered scaffolding, missing the assignment's core signal (eval methodology), README suggests he doesn't understand what the exercise was measuring."

Meanwhile another candidate submits in exactly seven hours: SQLite as the store, TF-IDF plus embeddings hybrid retrieval, a 40-question golden set she labeled herself, a `python eval.py` that prints per-category accuracy, and a README that opens with "the eval harness is the point; here's what it shows." She gets the offer.

Take-homes are asymmetric information: the company knows what they're grading, and most candidates don't. Fixing that asymmetry is worth more than any framework choice.

## INTUITION

Take-homes are the single most information-dense round in an FDE loop. In 6–10 hours you show — with an artifact you own, at your own pace — whether you can scope, time-box, ship, evaluate, and communicate. Every senior FDE hiring manager has read hundreds; they know within 90 seconds whether your submission signals "junior with a hammer" or "senior with judgment."

The archetypes (see [`interview-bank/take-home-patterns.md`](../../../interview-bank/take-home-patterns.md)) recur because the *skills* recur:

1. **Messy-data ingestion**: parse this file, produce clean output. Tests: fluency with real data, quarantine discipline, exit-code hygiene.
2. **Reconciliation**: two systems disagree; explain the gap. Tests: investigation discipline, definitional vs data-error triage.
3. **RAG-over-documents**: build Q&A on a corpus, with evals. Tests: chunking, retrieval quality, golden-set thinking.
4. **Open-ended dataset**: "here's data, do something interesting." Tests: problem-picking judgment, scope discipline.
5. **API-integration**: talk to system X, produce output Y, handle failures. Tests: real-world integration hygiene.

Regardless of archetype, the grading axes are near-identical:

- **Scope discipline**: did you build the thing they asked for, at the depth they asked for, in the time they estimated?
- **Correctness on messy input**: did you handle the sample data's actual pathologies, or did you assume clean-data-happy-path?
- **Evaluation and honesty**: did you measure your own work? If they gave a rubric, did you meet it? If they didn't, did you invent one?
- **README as artifact**: could a stranger clone your repo, read the README, run one command, and understand what you built and why?
- **Judgment signal**: did you make a hard trade-off explicitly (in the README) rather than hiding it?

The winning submission is *not* the most impressive tech stack. It's the one that hits the rubric cleanly, ships on time, and is honest about what it didn't do.

## BUILD IT

The take-home template. Steal this shape wholesale:

**Hour 0 — Read twice, then re-read.** Grade the assignment before you start. What's the archetype? What's the deliverable? What time did they estimate? Are there explicit rubric hints ("we care about accuracy metrics", "we'll extend it live")? Highlight every constraint. Then write a one-paragraph plan: what you'll build, what you'll skip, and why.

**Hour 1 — Walking skeleton, end-to-end.** Input → transform → output, however ugly. This mirrors the coding round: end-to-end thin slice beats one perfect stage. Commit at hour 1 with the message "walking skeleton passes." Now everything after is improvement, not construction.

**Hours 2–4 — Fill in the core signal.** For RAG: real chunking, hybrid retrieval, the eval harness — build the eval harness *third*, not last. For messy-data: real parsing, real quarantine, the correctness assertions. For reconciliation: the top-down slicing, the residual, the categorized gap. Whatever the archetype's *core signal* is, that's where hours 2–4 live.

**Hour 5 — The visible extras.** A `Makefile` with `make test` and `make run`. Sample commands in the README. One diagram if the architecture is non-obvious. A `--help` on the CLI.

**Hour 6 — The README, which is half the grade.** Structure:

```
# <Project>

## What this is
One sentence.

## Run it
One command.

## What it does, briefly
Three paragraphs: input, approach, output.

## Trade-offs I made
Three to five bullets, each naming a choice and its cost.

## What I didn't do (and would, given more time)
Three to five bullets. Honest, not defensive.

## How I evaluated it
The metric, the number, the caveats.
```

The "trade-offs" and "what I didn't do" sections are the most valuable in the whole submission. They signal that you know the depth-vs-time frontier, that you didn't hide anything, and that you have opinions about the extensions the reviewer will ask about live.

**Hour 7 — Test on a fresh clone.** `git clone` into `/tmp`, follow your own README, run the commands. If anything doesn't work, fix it. This step is skipped by 60% of candidates and separates the top quartile.

**Hour 8 — Submit early.** Submit at Sunday afternoon, not Sunday midnight. Reviewers pattern-match late submissions as scope-failures.

Time-boxing rules that hold across archetypes:

- If the company estimates 6 hours, spend 8 max. Anything past 8 is showing off and it looks anxious.
- If you're at hour 5 and the core signal isn't done, cut the frontend, cut the extras, and land the core.
- Never leave the eval harness for "if I have time." It is the assignment, not the garnish.
- No dependencies you don't need. `requirements.txt` with 30 lines and a Dockerfile signals "I couldn't decide what to build."

## FIELD NOTES

- The walkthrough round is where take-homes are actually adjudicated. Re-read your own submission the night before — you will have forgotten what your hour-3 self was thinking, and being asked "why did you choose X here?" and answering "I don't remember" is fatal.
- Extensions live. Expect: "add a second data source", "add auth", "make it handle 10x the data". Have a rough answer for each, because the interviewer's extension prompt is often chosen from a short list.
- LLM-in-take-home reality: don't use one to write the code and then get caught pretending. Some companies (Anthropic notably) have explicit policies; check with your recruiter. When you do use one, treat its output like a junior's PR: review, edit, own.
- Portfolio effect: a great take-home becomes part of your public work. Ask if you can open-source it (usually yes if their data isn't included, no if it is). A clean public repo becomes the first thing your next recruiter sees.

## INTERVIEW ANGLE

Meta-questions about take-homes that show up in walkthroughs:

1. "Walk me through a decision you'd make differently now." — never "nothing." The strong answer names one concrete choice, why it was wrong, and what you'd probe first next time.
2. "What would you build if you had another day?" — this is the roadmap question. The strong answer has three items in priority order, with rationale.
3. "How did you decide when to stop?" — the model answer is a rule: "I stopped when the eval harness was running and the README was honest — anything past that was polish, and the assignment's estimate was 8 hours."

## DRILL

Pick one archetype from `take-home-patterns.md` you haven't practiced. Set an 8-hour timer split across two evenings. Build the assignment as if it were real: walking skeleton hour 1, core signal hours 2–4, README hour 5–6, test-on-fresh-clone hour 7, submit hour 8. Then grade yourself against the five axes above. Then — this is the drill's actual value — have a friend read the README and ask three questions. If any of the three questions is "what does this do?" or "how do I run it?", your README failed and you rebuild it. Repeat until the README passes a stranger's cold read every time. That's the win condition.
