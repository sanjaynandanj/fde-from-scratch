# The Eval Harness: Golden Sets from Real Customer Data

Phase 5 · Lesson 06 · ~2h

## PROBLEM

Month two of a support-automation pilot. The ticket classifier is routing customer tickets to four queues, and the team has been "improving the prompt" for three weeks. Every change follows the same ritual: someone tries five tickets by hand, says "this feels better," and ships it. Then the customer's support lead escalates: outage tickets — the category with an executive SLA — have been landing in the general queue for nine days. Nobody noticed, because the change that broke outage routing *fixed* three billing tickets someone had complained about, and those were the five tickets tested by hand. When the VP asks "what's the accuracy of this system?", the honest answer is: nobody knows, and nobody has ever known. The renewal conversation goes exactly as well as you'd expect.

"It feels better" is not a deploy criterion. Enterprises buy *numbers* — accuracy on their data, per category they care about, with proof that yesterday's working cases still work today. The machine that produces those numbers is the eval harness, and it's routinely the artifact that decides whether an LLM pilot converts. It is also — as this lesson shows — about eighty lines of code.

## INTUITION

Four components, four design decisions:

**The golden set.** A labeled sample of *the customer's real data* — their tickets, their vocabulary, their ambiguity — with expected outputs blessed by *their* expert (the support lead, not you; her labels carry political authority yours never will). Size: even 50–200 examples transforms decision-making — statistical perfection matters less than existence. Composition: cover every class the customer cares about, deliberately over-representing the rare-but-critical ones (outages are 5% of tickets and 90% of the SLA risk).

**Metrics that don't hide.** Aggregate accuracy is a marketing number; it actively conceals. The lesson's own data proves it: a classifier at 90% accuracy is carrying **50% recall on the bug class** — it misses half of them, and the 90% hides it because bugs are only 2 of 10 cases. You need per-class precision (of what I routed here, how much belonged?) and recall (of what belonged here, how much did I catch?), because the *customer's cost function* is per-class: a missed outage costs an SLA; a misrouted feature request costs nothing. The confusion matrix — who got mistaken for whom — is the diagnostic layer beneath.

**The regression gate.** The support-lead escalation happened because improvement and regression are entangled: prompt changes are global, so fixing billing can break outages. The gate makes this visible mechanically: for every golden case, compare old-version correctness to new-version correctness; a change that breaks *any previously-passing case* is blocked — or at minimum, escalated with names attached. This mirrors what enterprise buyers actually fear: not that the system is imperfect, but that it's *unstable*. "It will never get worse on the cases you've verified" is a sentence that closes renewals.

**Determinism where possible.** The system under test here is a mock classifier with keyword rules — deliberately. The harness's own logic (metrics, gate) must be testable independent of model flakiness; in production you run the same harness with temperature-zero calls and cached outputs, but you *trust* it because it was verified deterministically.

## BUILD IT

Run it: `python code/lesson.py`.

**The golden set is ten labeled tickets.** Four classes — outage, account, billing, bug, other — as `(text, expected)` pairs. Small on purpose: every metric in the file can be verified by hand-counting, which is exactly how you should first check any harness you build.

**`MockClassifier` stands in for prompt+model — with a versioned flaw.** Keyword rules make it deterministic; the constructor takes a `version`, and the difference is one branch:

```python
if self.version >= 2 and ("crash" in t or "install" in t):
    return "bug"
if self.version == 1 and "crash" in t:
    return "bug"
```

v1 doesn't know "install" tickets are bugs, so "Cannot install the mobile app on Android 14" falls through to `"other"`. v2 fixes it. Two versions of one system, one known defect between them — the minimal setup for testing a regression gate in both directions.

**`evaluate` computes everything from one confusion count.** Each prediction increments `confusion[(expected, got)]` and records per-case results. Per-class metrics fall out of the matrix:

```python
tp = confusion[(lbl, lbl)]
fp = sum(v for (e, g), v in confusion.items() if g == lbl and e != lbl)
fn = sum(v for (e, g), v in confusion.items() if e == lbl and g != lbl)
per_class[lbl] = {
    "precision": tp / (tp + fp) if tp + fp else 0.0,
    "recall": tp / (tp + fn) if tp + fn else 0.0,
}
```

Read the definitions off the code: false positives are cases *routed to* this label that didn't belong (`g == lbl and e != lbl`); false negatives belonged but went elsewhere. The guarded divisions handle empty classes without crashing — a real concern when a golden set slice has zero predicted cases. The return bundles `accuracy`, `per_class`, per-case `results`, and the raw `confusion` dict — keep the raw matrix; every "why is recall low?" conversation ends up there.

**`regression_gate` is a set difference over per-case correctness.** Not a metric comparison — a *case-level* comparison:

```python
broke = [t for t in new["results"]
         if old["results"][t][0] == old["results"][t][1]      # was correct
         and new["results"][t][0] != new["results"][t][1]]    # now wrong
```

`fixed` is the mirror image, and `"passes": not broke` is the policy: fixes don't buy forgiveness for breaks. This is stricter than "accuracy must not decrease" — a change that fixes two and breaks one *raises* accuracy and still fails the gate, by design, because the broken case was one the customer had verified. The gate returns the broken cases *by name*, which turns a blocked deploy from an argument into a work item.

**The assertions tell the war story in miniature.** v1 scores `accuracy == 0.9` with `bug` recall `0.5` and the confusion entry `("bug", "other") == 1` — the Android ticket, found by coordinates. v2 hits 1.0 and passes the gate (`one fixed, nothing broke`). Then the direction flip — evaluating v1 against v2 as baseline — must *fail* (`not gate_bad["passes"]`), proving the gate catches degradation and not just applauding improvement. The final assertion is the thesis, stated as code: `90% accuracy hid a 50% recall on the class the customer cares about`.

## FIELD NOTES

- Building the golden set is a *customer engagement activity*, not a coding task. Two hours with the support lead labeling 100 tickets does three things at once: produces the set, transfers ownership ("these are *your* labels"), and surfaces definitional fights early — you will discover the customer's own team disagrees on what counts as an "outage," and resolving that ambiguity is worth more than any model improvement.
- Expect label noise. When the harness flags a "failure," a third of the time the *label* is wrong. Build a lightweight relabel path; a golden set is a living asset, versioned like code (because it gates code).
- The harness is a demo weapon. A dashboard showing "accuracy on your data, per category, trend since week one" is the single most credible artifact in a renewal meeting — it converts the pilot from vibes to evidence, and it inoculates you when a stakeholder cherry-picks one bad output ("yes, that's one of the 4% — here's the queue where humans catch those").
- Gate policy needs an escape hatch in practice: sometimes a break is acceptable (the label was wrong, or the class was re-defined). The mechanism: gate failures require *explicit sign-off with the named cases*, never silent override. The gate's job is making regressions a decision, not an accident.

## INTERVIEW ANGLE

Eval design is now a defining interview theme for lab FDE roles — arguably *the* theme at Anthropic- and OpenAI-style loops, where "how would you know it works?" follows every system-design answer. The repo's Phase 10 drill 08 (golden-set eval for a ticket classifier) is this lesson under exam conditions.

Sample questions:

1. "The customer asks: what's the accuracy of your system? Walk me through how you'd produce a number you can defend." (Golden set from their data, labeled by their expert, per-class metrics, and honest caveats about set size and drift.)
2. "Your classifier's accuracy is 92%. The customer is furious. What might the aggregate be hiding?" (Class imbalance and per-class recall — the rare class they care about is failing; ask for their cost function, show the confusion matrix.)
3. "How do you ship prompt changes without breaking what already works?" (Case-level regression gate in CI, block-on-break with named cases, sign-off path for intentional changes.)

## DRILL

1. **Extend:** add an F1 score per class and a `macro_f1` aggregate to `evaluate`, with assertions for v1 (compute the expected values by hand from the confusion matrix — that's the point). Note where macro-F1 disagrees with accuracy about which version is "better."
2. **Break:** add a new golden case that v1 gets right *by accident* — e.g., "The invoice download crashes" labeled `billing`, which v1's keyword order happens to route correctly. Now watch a "fix" to crash-handling break it. What does this teach about keyword-coincidence correctness in the golden set, and how would you flag brittle cases?
3. **Fix:** `regression_gate` assumes both evaluations ran the *same* golden set — if a case was added between runs, `old["results"][t]` raises `KeyError`. Handle set drift explicitly: new cases can't "break," removed cases get reported, and the gate output gains an `"added"`/`"removed"` accounting. Assert all three paths. (Golden sets are living assets; the gate must survive their evolution.)
