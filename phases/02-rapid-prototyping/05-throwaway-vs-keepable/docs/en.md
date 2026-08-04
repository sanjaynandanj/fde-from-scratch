# Throwaway vs Keepable Code: Labeling Your Own Tech Debt

**Phase 2 · Lesson 05 · ~1h**

## PROBLEM

Month three of a pilot. The FDE — solid, promoted twice at a good SaaS company — is being asked to prep the pilot for production handoff. He opens the repo he's been shipping to for eight weeks and realizes he cannot tell which parts were meant to survive. The parser that grew four `if customer_variant == ...` branches. The dashboard endpoint that talks directly to the CSV loader because early on there was no database. The `TODO` from week two that got copy-pasted into three more files. Every function he touches, he has to reason about whether removing it will break a demo path he's forgotten about.

The colleague on his engagement, meanwhile, opens her repo and points to a directory called `throwaway/`. Everything in there is disposable; everything outside was written to last. Her handoff takes a week. His takes a month, and two production bugs later he still isn't sure what's safe to delete.

## INTUITION

FDEs write two kinds of code and must know which is which as they type. The pilot is *supposed* to produce throwaway code — that is not a failure, it is the point. The failure is not labeling it, and letting it silently become production.

The two kinds:

- **Throwaway.** Written to make a demo work, prove a hypothesis, get the champion excited, or unblock a stakeholder in the meeting. Lifetime: days to weeks. Not tested. Not generalized. Not documented beyond a header comment. Will be deleted or rewritten before production.
- **Keepable.** Written because it belongs in the eventual product: the entity resolution logic, the schema mapping, the parser for the customer's export format, the API contract the customer's team will call. Tested. Documented. Reviewed as if it were.

The trap is that throwaway code accretes. A demo endpoint gets called by a real user. A hardcoded CSV path becomes the pipeline's actual source. A `# TODO: replace with proper auth` sits for eleven weeks and then a security review lands. Every FDE has done this. The senior ones have a system that makes the drift visible.

The system: **name the drawer, before the code goes in.** Every file, every function, every commit gets one of two labels. When the pilot becomes production, you know exactly what to delete and what to promote.

## BUILD IT

Three lightweight conventions. Adopt them on day one; they cost nothing.

**1. Directory drawer.** Split the repo:

```
src/                # keepable — reviewed, tested
throwaway/          # demo scaffolding, seed scripts, one-off munging
scripts/            # keepable operational tools
```

Nothing in `src/` imports from `throwaway/`. If it wants to, promote the code first. This one rule catches 80% of the drift.

**2. Header labels.** Every file starts with one line:

```python
# STATUS: keepable — parser for customer export v3, tested in test_parser.py
# STATUS: throwaway — seed script for the Nov 14 exec demo; delete after
# STATUS: keepable-but-fragile — hardcoded to their sandbox schema, needs config
```

Grep-able. When you hand over, run `grep -r "STATUS: throwaway" .` and the delete list writes itself.

**3. The `THROWAWAY.md` ledger.** One file at the repo root. Every fake, every hack, every "we'll clean this up." Append-only during the pilot, burned down before production.

```
| Date       | Location                       | What                        | Why                         | Kill by     |
|------------|--------------------------------|-----------------------------|-----------------------------|-------------|
| 2026-03-04 | api/summary.py                 | hardcoded user_id           | demo before SSO ticket      | prod cutover|
| 2026-03-07 | throwaway/seed_demo_data.py    | fake vendors for finance demo| real data not yet cleaned  | week 6      |
| 2026-03-11 | src/parser.py (line 84)        | if customer=="acme": skip   | one bad row we can't explain| investigate |
```

The ledger is boring and it is the difference between a clean handoff and a month of archaeology.

## FIELD NOTES

- Throwaway code is not a moral failing. Pilots that don't produce it are pilots that took too long. The failing is untracked throwaway code.
- You will be tempted to promote a throwaway function because "it works." Resist unless you also add tests and rewrite it to the contract you'd have written on day one. Promotion is a rewrite, not a rename.
- The customer's engineering team, if they take over your code, will judge you by the ratio of `keepable` to `throwaway` and by whether the ledger matches reality. A clean ledger buys you enormous credibility.
- Never let a demo-only script write to the production database. Have `throwaway/` connect to a separate `pilot.db`, or to nothing at all. This is the single most important boundary.

## INTERVIEW ANGLE

Interviewers probe self-awareness about pace vs quality. They want engineers who can move fast *and* clean up.

Sample questions:

1. "You've been shipping a pilot for six weeks. How do you know what to throw away when it converts to production?" (Testing: some form of labeling from day one — headers, directory split, ledger. Not "we'll figure it out.")
2. "Walk me through a time you shipped throwaway code that you later regretted keeping." (Testing: self-awareness, and the fix — usually "we started labeling.")
3. "How do you resist the temptation to over-engineer during a pilot?" (Testing: the reverse — do you know what *should* be quick and dirty? Correct answer names surfaces the customer won't touch this quarter.)

## DRILL

Take a repo you have shipped — pilot or production. Walk through every file and label it `keepable`, `throwaway`, or `keepable-but-fragile` in a header comment. Create a `THROWAWAY.md` reconstructing every fake and hack you can remember, with a "kill by" date. Count the ratio. If throwaway is more than 40% and unlabeled, you have found your next week's cleanup work. Keep the ledger habit; you will start every new pilot with a blank one.
