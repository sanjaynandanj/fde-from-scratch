# Drill: Write a 30-Day Pilot Plan from a Discovery Transcript

**Phase 1 · Lesson 10 · ~1.5h**

## PROBLEM

You've done 90 minutes of discovery interviews at a mid-sized commercial insurer. The customer is polite, articulate, and — like every customer — has told you a mix of aspirations, symptoms, project names, and one or two real metrics buried under three layers of context. Your manager wants a 30-day pilot plan by Friday. The exec sponsor wants a one-page memo by Monday. The champion wants to know what she's asking her team to help you with. You have exactly one artifact — a messy transcript — and you have to produce three coherent artifacts from it. This is the FDE version of a coding take-home, and it is often *literally* the take-home given in Palantir, Anthropic, and Sierra FDE interview loops.

Turning a transcript into a plan is the actual muscle of the FDE lifecycle. Every technique from this phase — discovery, scoping, pilot design, TTV, access battle — collapses into this one exercise.

## INTUITION

The transcript is not the problem statement. Extraction is the problem statement. Customers speak in surface — "we want to improve underwriting" — while the plan lives in specifics — "reduce time to quote for small-commercial submissions in the mid-Atlantic region by 40% by moving submission triage from human-first to model-first with human review, measured against Q4 baseline, owned by VP Underwriting Ops."

The extraction moves in a fixed order:

**Step 1 — Extract candidates.** Read the transcript. Underline every noun phrase that could be a metric, a system, a persona, or a workflow. Do not filter yet.

**Step 2 — Find the metric.** From the candidate metrics, pick one that is owned, measured today, movable in 30 days, and financially material. If multiple candidates qualify, pick the one whose owner has the most political air cover.

**Step 3 — Choose the persona and workflow.** One user. One workflow. Not the whole team, not the whole process. The narrowest slice that credibly moves the metric.

**Step 4 — Pick the data slice.** Time window, region, line of business — as small as defensible. If the customer processes 500k submissions a year, your pilot uses 5k from one region for one quarter.

**Step 5 — Map the access battle.** For the data slice, name every system, owner, and likely gate. This is often the biggest surprise for junior FDEs — 40% of transcript-to-plan work is access sequencing.

**Step 6 — Design weekly milestones.** Backwards from day 30. What's demoable Fri W4? Fri W3? Fri W2? Fri W1? Each milestone must be visible.

**Step 7 — Write it up in three artifacts.** The one-page exec memo, the scoping doc, the champion-facing weekly milestone chart.

Each step compresses hours of transcript into one line of plan. When it's done well, the plan reads inevitable — as if the transcript could only have led here.

## BUILD IT — do the drill

Below is a real-shape (synthetic) discovery transcript. Work the process end to end. Write the three artifacts. Give yourself 60 minutes; this matches the take-home time-box.

**Discovery transcript excerpt — commercial insurer, VP Underwriting Ops (Marisol) + her senior underwriter (Danny) + IT lead (Ravi). Duration 45 min.**

> **Marisol:** Look, our small-commercial book — that's under $250k premium — takes forever to quote. Six days on average. Our target is three. Our best competitor is under two. That gap is costing us submissions to brokers who quote us and don't come back.
>
> **Danny:** Half the time is just getting the submission from PDF into our rating engine. My team spends the morning re-typing. If the broker's ACORD 125 form has weird handwriting or the loss runs are in Excel, forget it. And every submission has like six attachments.
>
> **Marisol:** We have a rating engine — Duck Creek. It works. The bottleneck is upstream. It's the triage: does this submission fit our appetite, do we have the risk data, is anything missing.
>
> **Ravi:** The submissions come into a shared Outlook inbox and a broker portal. About 60% inbox, 40% portal. Portal ones have some structure. Inbox ones are PDFs and email bodies. We have SharePoint where attachments land.
>
> **Marisol:** If we could cut a day off, half a day off triage, that's meaningful. Our CFO is watching cycle time hard this year.
>
> **Danny:** Also we lose stuff. Broker sends five attachments, we process four, come back a week later asking for the fifth. Broker is annoyed.
>
> **Marisol:** The other thing — and this is more aspirational — I'd love if the system could tell my underwriters "this one's not in appetite, decline fast" so they spend time on the ones we actually want. Right now everyone gets the same 20 minutes of attention.
>
> **Ravi:** For access — the broker portal is our own thing, I can get you a read API in a week probably. Outlook inbox is trickier, that's IT and infosec. SharePoint I'd need to see what the attachments look like.
>
> **Marisol:** We looked at three vendors last year for this. All of them wanted a nine-month integration. That's why we're excited about the 30-day thing.

**Now do the work:**

```
STEP 1 — CANDIDATE EXTRACTION
Metrics mentioned: <fill in>
Systems mentioned: <fill in>
Personas mentioned: <fill in>
Workflows mentioned: <fill in>
Data assets mentioned: <fill in>

STEP 2 — THE METRIC
Winner: <e.g., "Small-commercial submission triage cycle time,
        current 6d, target 3d, owner Marisol (VP UW Ops), reported to CFO">
Why not the others: <one line each>

STEP 3 — PERSONA + WORKFLOW
Persona: <one>
Workflow: <one, narrow>

STEP 4 — DATA SLICE
Source: <e.g., "broker portal submissions only (skip inbox for pilot),
        last quarter, small-commercial only">
Volume estimate: <n submissions>

STEP 5 — ACCESS BATTLE
System | Owner | Est. days | Blocker
<row per system>
Day-30 access floor: <minimum needed>

STEP 6 — WEEKLY MILESTONES
W1 Fri: <what user sees>
W2 Fri: <what user sees>
W3 Fri: <what user sees>
W4 Fri: <exec readout>

STEP 7 — ARTIFACTS
A. One-page exec memo (draft below, 250-300 words)
B. Scoping doc (use Lesson 03 template)
C. Weekly milestone chart (for the champion)
```

Write draft A in prose. It should be readable by Marisol's CFO in 90 seconds. Structure: what we heard, the metric we'll move, the 30-day pilot shape, what we need from the customer, the day-30 readout.

## FIELD NOTES

- Take-home evaluators are looking for *choice* — which candidate metric did you pick and why. A plan that tries to attack every metric mentioned in the transcript is a failing plan.
- The "aspirational" line ("tell my underwriters this one's not in appetite") is a trap. It's a real business need, but it's not the 30-day pilot. Note it in an appendix as production-phase or phase-2 scope, and stay focused on cycle time.
- The Outlook inbox path (60% of volume) is tempting — you'd cover more submissions. But Ravi flagged an access barrier. The portal path (40% of volume, week-1 access) is the correct pilot slice. Coverage in 30 days beats coverage in 90.
- Marisol's mention of losing attachments is a real symptom that maps onto the same workflow. It's a candidate demoable feature ("submission completeness check") for a mid-pilot week that adds visible value without expanding the metric.
- Ravi's willingness matters. He's a friendly IT lead who volunteered timelines. In your access battle plan, he's a green node, not a red one. Note it — it'll be true for maybe half the IT leads you meet.

## INTERVIEW ANGLE

This is often *the* live take-home for FDE loops. You're given a transcript, sometimes a video, and asked to produce a plan in 24–72 hours.

1. "You have this transcript. What's the metric you'd target and why not the others?" (They want: crisp selection, explicit rejection of alternatives, financial framing.)
2. "Walk me through your weekly milestones. Why did you pick these four and not four others?" (They want: TTV logic — week 1 demoable, backwards from day 30 readout, no invisible weeks.)
3. "What's out of scope in your plan?" (They want: a list. If you don't have one, you haven't scoped. Explicit "no" beats implicit "maybe.")

## DRILL

Do the exercise above end to end. Set a 60-minute timer. Produce the one-page memo, the scoping doc, and the milestone chart. When you finish, compare your metric choice against a peer's or against your own instinct twelve hours later. If you can't defend your pick against "why not this other metric?" in one sentence, refine. This exact exercise, at higher variance, appears in Capstone 1 (Pilot-in-a-box) and in every FDE take-home the interview bank will drill.
