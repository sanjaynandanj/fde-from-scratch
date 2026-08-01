# Back-of-Envelope Engine: Estimation with Explicit Error Bars

Phase 8 · Lesson 02 · ~2h

## PROBLEM

A decomp interview at a Palantir-style loop. The case: a 400-bed hospital wants to archive its HL7 message feed — the interviewer asks, almost as an aside, "how much storage does a year of that need?" One candidate goes quiet, does invisible arithmetic, and announces: "About 10 gigabytes." The interviewer asks how confident he is. Silence. Is it 10 GB or 100 GB? Would the answer change the architecture? He doesn't know, because his estimate is a point with no structure — he can't say *which assumption* he'd check first or *how wrong* he could be.

The second candidate says: "Beds times admissions per bed-year times messages per admission times bytes per message. I'll carry a range for each — 350 to 450 beds, 40 to 60 admissions, 100 to 300 messages, 1 to 4 KB." She multiplies the bounds and lands on roughly 1.4 to 32 GB, midpoint around 10. Then the sentence that wins the round: "Even my worst case fits on one Postgres instance — so storage is a non-issue and we should spend our time on the interface question instead." Same arithmetic skill. The difference is that she estimated with *intervals* and read a *decision* off the result. Amateurs give a number; professionals give a range, show the factor tree, and say what the number decides. This lesson builds the tiny engine that makes that mechanical.

## INTUITION

Three ideas, compounding:

**Ranges, not points.** Every quantity in a field estimate is uncertain — so represent it as `[low, high]` and make arithmetic propagate the uncertainty. Interval multiplication is trivially honest: the product's floor is the product of floors, its ceiling the product of ceilings. Division has the classic twist — dividing by a *bigger* number gives a *smaller* result, so bounds cross: `[a,b] / [c,d] = [a/d, b/c]`. Getting that backwards is the most common interval-arithmetic bug, which is why it's worth building once and asserting forever.

**Multiplicative quantities live on a log scale.** For factors spanning 2–10x, the natural "middle" is the geometric mean (`sqrt(low*high)`), not the arithmetic mean: the midpoint of [1, 100] is 10, not 50.5 — "equally wrong in ratio terms" both directions. Likewise the honest width measure is the *ratio* `high/low` ("I know this to within 20x"), not the difference. And spreads compound multiplicatively: four factors each known to ~1.3–3x yield a total spread of 10–25x. That sounds terrible and is actually the point — the discipline is knowing *how* uncertain you are, and noticing that the widest input (here, messages-per-admission at 3x) is where an hour of research buys the most narrowing.

**The estimate exists to drive a decision.** A range is only useful against a threshold. "1.4–32 GB" matters because *every point in it* clears the same bar: single-instance storage, no data-lake conversation, no distributed anything. When the whole interval lands on one side of a decision boundary, uncertainty is *resolved for decision purposes* even though it's numerically huge — the deepest trick in estimation, and the sentence interviewers wait for. When the interval *straddles* the boundary, that tells you what to go measure before architecting.

Sanity-check culture completes the method: bracket the answer with a known reference point, check the range *contains* it, and state which single assumption you'd verify first.

## BUILD IT

Run it: `python code/lesson.py`. Half the file is the engine; half is a real estimate performed with it.

**`Range` is a validated interval with operator overloads.** The constructor rejects nonsense loudly — `assert 0 < low <= high` — with the *label* in the message, so a backwards range dies naming itself (the test proves it: constructing `Range(5, 2, "backwards")` must raise with "backwards" in the error). Multiplication and division do the bound-propagation:

```python
def __mul__(self, other):
    o = other if isinstance(other, Range) else Range(other, other)
    return Range(self.low * o.low, self.high * o.high)

def __truediv__(self, other):
    o = other if isinstance(other, Range) else Range(other, other)
    return Range(self.low / o.high, self.high / o.low)
```

Two details worth noting. Scalars auto-lift to degenerate ranges (`Range(x, x)`), so `beds * 365` reads naturally — an estimate mixes known constants with uncertain factors, and the engine shouldn't make you ceremonialize the constants. And division cross-multiplies (`low/o.high, high/o.low`), the bounds-crossing rule, pinned by its own assertion: `[10,20] / [2,4]` must be `[2.5, 10]`, with the message "division must cross-multiply bounds."

The three small methods encode the log-scale worldview: `mid()` is the geometric mean (comment in-source: "geometric mean fits spans of 10x" — asserted: `Range(9,16).mid() == 12.0`, not 12.5); `spread()` is `high/low`; `contains(x)` is the sanity-check hook. `__repr__` prints 3-significant-figure bounds — because printing `1.3999999999999999` in an interview artifact undermines the entire "I know what precision I have" message.

**Then the engine earns its keep on the actual interview question.** Storage for one year of HL7 at a 400-bed hospital, as a labeled factor tree:

```python
beds = Range(350, 450, "beds")
admissions_per_bed_per_year = Range(40, 60, "admissions/bed/yr")
messages_per_admission = Range(100, 300, "HL7 msgs/admission")
bytes_per_message = Range(1_000, 4_000, "bytes/msg")

total_bytes = beds * admissions_per_bed_per_year * messages_per_admission * bytes_per_message
total_gb = total_bytes / 1e9
```

The factor tree *is* the decomposition — each line is an assumption with a name, a range, and implicit units, exactly what you'd write on the whiteboard. The assertions then perform the professional's checklist in code. Sanity bracket: a point-estimate reference (`400 * 50 * 200 * 2500 / 1e9 = 10.0` GB) must fall inside the computed range — `assert total_gb.contains(reference_gb)`. Order-of-magnitude claim: the answer is "single-digit-to-tens of GB" (`1 < low < high < 100`). Uncertainty accounting: the compounded spread lands where theory says it must — `assert 10 < total_gb.spread() < 25` — four modest input spreads multiplying into a ~23x output spread, *measured*, not hand-waved.

And the last assertion is the punchline the whole lesson exists for:

```python
# the punchline every interviewer wants: state the decision the number drives
decision = "fits on one Postgres instance; no data-lake conversation needed"
assert total_gb.high < 100, decision
```

The decision is asserted against the *upper bound* — the conclusion holds even in the worst case, which is precisely what makes it safe to say out loud in front of a customer's architect.

## FIELD NOTES

- This isn't just interview theater — it's week-one scoping. "Will the pilot's data fit in SQLite?" "Can we afford to run every ticket through the model?" "Is nightly batch fine or do we need streaming?" are all four-factor interval estimates, and the answer usually lands entirely on one side of the decision line. Estimating before building is how FDEs avoid architecting for loads that arithmetic already ruled out.
- Ranges are also a *negotiation instrument*. Present "1.4–32 GB, worst case still trivial" and nobody argues; present "10 GB" and someone who once saw a 50 GB HL7 archive calls you wrong and the meeting derails. Explicit humility is armor.
- Real factor trees mix multiplication with addition (three feed types summed), and interval addition is bound-wise too — but beware correlated inputs: if two factors move together, naive interval arithmetic overstates the spread. At whiteboard precision that's usually fine; just don't defend the spread as statistically rigorous. It's a bound, not a confidence interval.
- Where do input ranges come from? Reference points you carry (a hospital bed turns over roughly weekly; an HL7 ADT message is a few KB) plus the discipline of widening when you're guessing. Collecting domain anchor numbers is career-long FDE capital — every engagement adds a few.

## INTERVIEW ANGLE

Estimation-with-structure is the connective tissue of the Palantir-style decomp round: interviewers care little about the final number and a great deal about the factor tree, the stated assumptions, the sanity check, and whether you *read a decision off the result*. "10 GB" scores worse than "1 to 30 GB, dominated by messages-per-admission uncertainty, and either way it's one Postgres box."

Sample questions:

1. "Estimate the daily data volume from 2,000 delivery trucks reporting GPS every 10 seconds." (They want the labeled factor tree, ranges on the uncertain factors, a units check, and the decision: what does the number change?)
2. "Your estimate spans 20x. Is that a problem?" (Only if a decision boundary falls *inside* the range — otherwise it's resolved; if it does, name the widest factor and how you'd narrow it first.)
3. "Which of your assumptions would you verify first, and how?" (The one with the largest spread *and* leverage on the decision; name the human or system you'd get the real number from.)

## DRILL

1. **Extend:** add `__add__` to `Range` (bound-wise: `[a+c, b+d]`), then re-estimate with two message sources — inpatient admissions plus a separate ER-visits factor tree — summed before the bytes conversion. Assert the combined range still contains a hand-computed reference.
2. **Break:** flip `__truediv__` to the naive `Range(self.low / o.low, self.high / o.high)` and run. Which assertion catches it, and — more interesting — construct a case where the naive version produces an *invalid* range (low > high) and dies in the constructor instead. Two different failure surfaces for one bug: name which you'd rather have in production.
3. **Fix:** the engine can't represent a factor that might be zero (the constructor demands `0 < low` — correct for multiplicative estimation, limiting for "how many incidents will the pilot cause"). Add a separate `Count` range type permitting zero, define its multiplication semantics against `Range`, and write the assertion showing why zero-crossing intervals and division must never meet.
