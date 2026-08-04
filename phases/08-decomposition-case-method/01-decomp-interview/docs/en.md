# The Decomp Interview: What Palantir Actually Tests

**Phase 8 · Lesson 01 · ~1.5h**

## PROBLEM

A candidate walks into the final round at a Palantir-style loop. She's shipped hard things at real companies. The interviewer opens with a single sentence: "Hospital ER wait times are getting worse. You're on site Monday. Go." No dataset. No scope. No follow-up. She freezes for eight seconds — a lifetime in an interview — then starts sketching a machine learning model. "I'd train a random forest on historical patient throughput..." The interviewer nods politely and lets her run for four minutes before interrupting with, "What data are you training it on? Whose problem are we solving? What number would tell you it worked?" She has no answers, because she started building before she decomposed. She gets a soft rejection with the exact phrase every FDE hiring manager writes: *"Strong engineer, but didn't structure the problem."*

The frustrating part: she is a strong engineer. She would have shipped a good pilot given six weeks. The interview was measuring something else — whether she can *think in the shape of an FDE engagement* under 30 minutes of pressure, aloud, without a laptop, without notes, without permission to say "let me research this first." That skill is trainable. Nobody trained her.

## INTUITION

The decomp round exists because Palantir invented the FDE role to *walk into ambiguity and make it tractable by Friday*, and the only way to test that in an interview is to compress the discovery-scoping cycle into 30 minutes on a whiteboard. It is not a systems design interview (nobody cares about your load balancer). It is not a case interview in the McKinsey sense (nobody cares about your MECE framework). It is a simulation of the first customer meeting, where the interviewer is the COO and you have to convert "wait times are bad" into a scoped week-one deliverable.

Four things get graded, and the ratio matters:

**Clarification (25%).** The strongest signal in the first three minutes is whether you *ask* before you *assume*. Not interrogation — three-to-five sharp questions that would change your approach depending on the answer. "What do you mean by wait time — door-to-triage, door-to-provider, door-to-disposition?" is a career-defining question because "wait time" is at least four different metrics and each has a different owner and fix. Candidates who skip clarification are signalling that they'd walk into a customer site and build the wrong thing confidently.

**Structure (35%).** The heaviest weight. Interviewers listen for the same shape every strong candidate hits: users, data sources, entities, metric, 80/20 solution, risks. Not always in that order, but always all six. Weak candidates jump straight to features ("I'd build a dashboard with..."); strong ones anchor on *who uses the product* and *what data actually exists* before any feature word is spoken. The ontology — modeling the customer's world as objects and links — is the make-or-break move; it's what makes Palantir Palantir.

**Restraint (20%).** The 80/20 cut. Interviewers watch for whether you ship the boring, retrospective, read-only version in week one, or whether you propose the streaming real-time ML-powered thing that fails discovery. The right instinct — "I'd start with a batch export from three worst-performing hospitals, not real-time from all twelve" — reads as customer-facing maturity. It's also the number-one signal separating senior FDEs from senior SWEs.

**Trade-off narration (20%).** Thinking aloud without rambling. Interviewers need to hear the *choice*, not just the decision: "I'm choosing a rules-based scorer over a learned model because we have no labels yet and dealers will demand explainability — I'd revisit at month three when we have review outcomes." Silence during arithmetic reads as bluffing; monologue without decisions reads as unfocused. The professional register sits in between.

## BUILD IT

Not code — a **15-minute timeboxed decomp script**. Memorize the beats; run any prompt through it until the shape is muscle memory.

```
DECOMP SCRIPT — 30 minutes, out loud

00:00 – 03:00   CLARIFY
    Ask 3–5 questions that would change your approach:
    - What does <fuzzy word> actually mean here?
    - Is this concentrated or uniform?
    - What data exists at what grain?
    - What's been tried? Who owns it?
    - Who feels the pain — the buyer or the user?

03:00 – 06:00   USERS
    Rank 2–4 users by pilot importance. Name the trap
    (buyer commissioned it, but the user makes it work).

06:00 – 10:00   DATA + ENTITIES
    Sources at grain, expected data-quality traps.
    Draw the ontology: objects and links.
    Name the killer analytical object (the join
    that makes the answer fall out).

10:00 – 15:00   METRIC
    Primary metric with definition + slicing.
    Guard metric (against gaming).
    Diagnostic metric (leading indicator).
    Reject a wrong metric aloud.

15:00 – 22:00   80/20 SOLUTION
    Week-one build: batch/read-only/one segment.
    Say what you're deliberately NOT doing.
    Phase two and three named but not built.

22:00 – 27:00   ESTIMATE
    Factor tree with ranges.
    Sanity-check bracket.
    Read the decision off the number.

27:00 – 30:00   RISKS
    3–5 risks named unprompted, including one political.
    End with the weakest assumption and how you'd
    verify it in week one.
```

Two rules that make this script work in practice. **Say the beat name out loud** ("Let me talk about users first") — it externalizes structure and buys thinking time. **Timebox by wristwatch, not by feel** — candidates who spend 12 minutes on clarification never finish, and unfinished decomps score worse than shallow-but-complete ones.

## FIELD NOTES

- Real-life analogue: this *is* the pilot-scoping conversation. When a customer's champion says "we want the AI thing for our claims process," the FDE mentally runs the same script — clarify what claims mean here, whose problem this is, what data exists, what week-one deliverable would let us book a phase-two meeting. The interview is not simulating anything artificial; it's simulating Tuesday afternoon.
- The 30-minute compression is the artificial part. In real engagements you get two weeks of discovery calls to do what the interview asks in 30 minutes. That's why the drill matters — the shape has to be automatic so ambient stress doesn't collapse it.
- Interviewers do not want your final answer to be *correct*. They want it to be *defensible*. A wrong metric with a clear rationale beats a right metric picked randomly. This is the single most-missed lesson of the round.
- Decomps in the field are collaborative. Decomps in the interview are performative-collaborative — you invite input ("does that match what you're seeing?") but you drive the pace. Handing the marker to the interviewer is a small tell that reads as lack of ownership.

## INTERVIEW ANGLE

Sample questions from real FDE loops:

1. **"Walk me through how you'd approach a problem you know nothing about."** (Meta-question. They want the script above, described in the abstract, in under two minutes. Answer: I'd clarify the metric before solving, map the users and data, sketch the ontology, propose an 80/20 for week one, estimate with ranges, name risks. Then they hand you a real prompt.)

2. **"A retailer is losing money on shrinkage. Where do you start?"** (Live decomp. They're timing the beats. Watch for the trap: shrinkage is a residual — book inventory minus counted inventory — so if counts are bad, "shrinkage" partly measures counting error. Naming that in the clarification phase is a top-5% signal.)

3. **"You have five minutes to convince me you understand the problem. Go."** (Compression test. Some interviewers explicitly shorten the clock to see whether your structure survives. It should — that's why you drilled it.)

## DRILL

Take yesterday's news headline about an operational problem — an airline meltdown, a hospital system's IT outage, a bank's fraud disclosure. Set a 30-minute timer. Run the script out loud. Record yourself. Score against the four dimensions: clarification quality, structural completeness, 80/20 restraint, trade-off narration. Do this three times a week for the four weeks before your interview loop. The shape becomes automatic around rep 8.
