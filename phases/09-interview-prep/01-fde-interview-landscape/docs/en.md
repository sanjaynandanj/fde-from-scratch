# The FDE Interview Landscape: Loops at Palantir, OpenAI, Anthropic, Scale, Sierra

**Phase 9 · Lesson 01 · ~1h**

## PROBLEM

A senior backend engineer, five years at a fintech, decides to pivot to FDE work. She applies to Palantir, OpenAI, and Scale in the same week — same resume, same generic prep plan she used for her last job hunt: a hundred leetcode problems, a couple of textbook system-design mocks, and a re-read of *Cracking the Coding Interview*. Palantir's first-round decomp interview asks her how she'd approach cargo theft at a port authority; she reflexively starts writing code on the shared doc, and the interviewer politely tells her the round has no coding. OpenAI's take-home wants a working RAG system with an eval harness in one weekend; she ships a slick chatbot with no evals and gets a rejection with the line "the harness was the assignment." Scale's screen dwells on how she'd get labeled data for a fine-tune; she has no answer. Three companies, three rejections, and the same root cause: she prepped for the wrong loop.

FDE loops are not SWE loops with the word "customer" sprinkled in. Each company's loop is a coherent signal-collection instrument, and if you don't know what it's measuring, you can't route your energy.

## INTUITION

Every FDE loop is asking one meta-question: *if we drop you into a customer's world alone, what happens?* But each company weights the sub-signals differently based on what its FDEs actually do.

Palantir's loop is decomp-heavy because their FDEs walk into government agencies and industrial customers whose problem statement is a sentence ("we lose containers") and whose data model has to be excavated. The decomp round exists because the job is decomp.

OpenAI and Anthropic loops are LLM-application-heavy because their FDEs ship RAG systems and evals against enterprise documents; the take-home is the loop's centerpiece precisely because building-with-the-API in a weekend is a large fraction of the actual work.

Scale's loop leans data-and-labeling because their historical strength is the data engine; asking "how would you get labels for this?" is not trivia, it's the muscle.

Sierra's loop probes agent-specific judgment — conversational flows, tool safety, escalation design — because that is the product surface.

The generic AI-startup loop compresses everything: one practical coding screen, one high-stakes take-home, one customer scenario, one founder chat. At startups, the take-home is disproportionately decisive because the team can't afford to hire someone whose artifact was unimpressive.

Read [`interview-bank/company-loops.md`](../../../interview-bank/company-loops.md) before this lesson — it is the source of truth for loop shapes. This lesson exists to teach you how to *read* that file strategically.

## BUILD IT

The exercise is a prep-routing worksheet. For each company you're targeting, produce a one-page plan with five fields:

1. **Loop shape** (recruiter → screens → onsite). Copy from `company-loops.md`, then email the recruiter and ask "can you walk me through the stages and what each evaluates?" — a normal, expected question.
2. **Rounds ranked by weight**. For Palantir, decomp is loop-deciding; for OpenAI, the take-home is; for Sierra, the agent design round is. Mark each round ●●● (loop-deciding), ●● (graded), or ● (background) and prep proportionally.
3. **Prep asset per round**. Decomp round → Phase 8 + case file drills. Take-home → the archetype most likely (RAG for OpenAI/Anthropic, messy-data for Scale, agent for Sierra). Behavioral → the two weakest of the six competencies in [`behavioral.md`](../../../interview-bank/behavioral.md).
4. **"Why this company," honestly**. Palantir and Anthropic explicitly select for candidates who've thought about mission — a purely opportunistic answer lands worse than an honest one, even a hesitant honest one.
5. **The one story you'll retell everywhere**. Pick your strongest customer-facing project and rehearse it in three lengths: 30 seconds, 3 minutes, 15 minutes. It appears in behavioral, in the demo round, and in the "tell me about yourself" opener.

Do not skip the "ask the recruiter" step. Loops change quarterly; a preparation plan built from a nine-month-old blog post is a plan aimed at the wrong target.

## FIELD NOTES

- The signal a loop collects mirrors the signal the job needs. If you notice Palantir isn't asking you to write code, that isn't disrespect for engineers — it's that their FDE role is more decomp-per-week than code-per-week, and the loop is honest about that.
- Loops leak information both ways. The rounds a company runs tell you what they think the job is; if their answer doesn't match yours after a few conversations, that mismatch is data — sometimes it's a signal you don't want the job.
- Contractor and staffing paths (Delta at Palantir vs shorter-term deployment-strategist paths, OpenAI's various solutions tracks) can have overlapping loops with different weight — ask which track you're in, and don't assume.
- Small AI startups often collapse the recruiter and founder screen into one call. That call is disproportionately decisive because the founder is often the deciding vote, and the founder's "gut" runs on autonomy evidence and a plausible war story.

## INTERVIEW ANGLE

Meta-questions about interviewing itself do come up — often at the end, framed as culture-fit signals:

1. "What kinds of interview rounds do you think you're weakest at, and what have you done about it?" — they want self-knowledge plus evidence of deliberate practice, not "leetcode" as a stock answer.
2. "Are you interviewing elsewhere, and how are you thinking about your options?" — the honest answer with reasoning ("yes, I'm most interested in the deployment-motion role — that's why I'm here") reads as maturity; obfuscation reads as game-playing.
3. "What would make you turn down an offer from us?" — the strong answer names a real dealbreaker (travel, mission mismatch, product surface) rather than a fake weakness dressed as a preference.

## DRILL

Pick your top three target companies. For each, produce the one-page prep-routing worksheet above in 20 minutes total. Then time-audit your last two weeks of prep: how many hours went into rounds you now know are loop-deciding, versus rounds you now know are background? If more than 30% of your time went to the wrong rounds, rebuild your calendar for the next two weeks against the ranked list, and email each recruiter this week with the "walk me through the stages" question. Save the responses — they are the ground truth this lesson can't be.
