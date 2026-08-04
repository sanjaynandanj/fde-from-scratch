# Shipping Accuracy Honestly: Confidence, Human-in-the-Loop, QA Sampling

**Phase 5 · Lesson 13 · ~1h**

## PROBLEM

The pilot review meeting is on Friday. The eval shows 87% accuracy on a 250-item golden set. The champion wants to tell the VP "we're at 87%." You know three things she doesn't: (1) the golden set was hand-picked from the easier half of real traffic, (2) the 13% miss rate contains the exact class of errors the compliance team will care about, and (3) production users will ask questions the golden set never covered. If you nod along with "87%", you are setting up a broken-trust conversation for month three. If you say "actually it's more complicated," you have to explain how without seeming like you're sandbagging your own work. The FDE's job in that meeting is neither performance theater nor false modesty — it is honest measurement, framed in a way the customer can act on. Shipping accuracy honestly is a customer-craft skill, not just an ML skill.

## INTUITION

Accuracy is a distribution, not a number. Frame it as one:

**Confidence stratification.** Report accuracy separately for high-confidence and low-confidence predictions. A system that's 95% accurate on 60% of traffic and 60% accurate on 40% of traffic — with the confidence flag visible — is often more useful than a system that's 87% accurate uniformly. Users can trust the confident answers and route the rest to review.

**Failure taxonomy.** Break the miss rate into categories: vocabulary mismatch, out-of-scope, actually wrong, refused (correctly). The categories matter more than the aggregate. "13% miss rate" invites concern; "8% correct refusal, 3% vocabulary mismatch we're fixing, 2% actually wrong" invites planning.

**Human-in-the-loop as a design choice, not a failure admission.** Any pilot with real stakes needs a review path. HITL isn't "the model isn't good enough yet"; it's the shape of the deployment. Design it in from day one. The confidence-stratified reporting *is* the HITL routing rule: high confidence goes through, low confidence gets reviewed, refused gets escalated.

**QA sampling in production.** Even a 95% accurate system on 10k requests/day makes 500 mistakes/day. Random-sample 1-5% of production outputs for human review, forever. This produces (a) a moving quality metric, (b) a stream of new golden-set candidates, and (c) early warning when quality drifts because the model provider updated something you didn't know about.

The frame to bring to executives: "The system is designed to be reliable, not to always be right. Here is what it does when it's not sure, and here is how we know it's still working."

## BUILD IT

The confidence-stratified report template:

```
Golden set: 250 items, curated to reflect production query distribution.

By confidence:
  High confidence  (retrieval score >= 0.4): 65% of set, 96% correct
  Med  confidence  (0.2 - 0.4):              22% of set, 84% correct
  Low  confidence  (< 0.2):                  13% of set, refused (correct)

Failure taxonomy (35 misses total):
   3 vocabulary mismatch  -> glossary fix in flight
   4 chunking split       -> rechunk pending
   1 hallucinated citation -> guardrail catches, refused
  27 correct refusals

Effective production behavior:
  ~78% of production traffic returns a confident, correct answer.
  ~13% returns a med-confidence answer flagged for optional review.
  ~9% is refused with an escalation path to human support.
```

That report — instead of "87%" — is what wins the Friday meeting.

**Confidence thresholding template:**

```python
def route(query):
    hits = index.search(query)
    if not hits or hits[0][0] < LOW_THRESHOLD:
        return {"path": "refuse", "reason": "no confident source"}
    if hits[0][0] < HIGH_THRESHOLD:
        answer = rag_answer(query, hits)
        return {"path": "answer_with_review_flag", "answer": answer}
    answer = rag_answer(query, hits)
    return {"path": "answer_direct", "answer": answer}
```

Thresholds are per-deployment and empirically set (Lesson 03 golden set).

**QA sampling loop, minimum:**

```python
def maybe_sample(response):
    if random.random() < QA_SAMPLE_RATE:
        review_queue.push({
            "request_id": response["request_id"],
            "query": response["query"],
            "answer": response["answer"],
            "retrieved": response["retrieved"],
            "sampled_at": now(),
        })

# Review UI shows the reviewer: the query, the answer, the sources.
# Reviewer marks: correct / wrong / needs-followup, with a category.
# Wrong + category feed back into the failure taxonomy dashboard.
```

## FIELD NOTES

- "What's the accuracy?" is the wrong single question, but the customer will ask it every week. Answer with the number *and* the framing. "87% overall; 96% on the 65% we're confident about; the rest is reviewed or refused." Do this until they start asking the better question.
- Never quote a number without saying what the eval set is. "87% on our 250-item golden set curated with your SME in June" is a defensible number. "87%" alone can be pulled out of context into a slide deck and used against you.
- HITL review UX is a real product. If the reviewer needs 90 seconds per item and you're sampling 500/day, that's 12 hours of labor. Design the review UI so a reviewer can decide in 15 seconds — surfaced context, one-click categories, keyboard shortcuts.
- Quality drift is real. Model providers update; corpus content changes; user queries evolve. Set up an alert when the QA-sampling quality metric drops by >2 points week-over-week. Investigate; usually one of the three variables has moved.
- The champion may want you to inflate the number for the VP presentation. Say no, on paper, so the record is clear. Show them the honest framing; a champion who signs off on a defensible metric survives audit. A champion who signed off on a rosy metric loses the next budget conversation.
- Refusal is not a failure — sell it. "Our system refused 9% of queries this week and escalated them to human agents. Users report higher trust in the answers they *do* get." That is a feature.

## INTERVIEW ANGLE

Accuracy-shipping questions probe whether you can navigate the customer conversation about quality without lying and without sandbagging. Interviewers listen for confidence stratification, failure taxonomy, and HITL as design.

Sample questions:

1. "How do you report accuracy to a customer executive?" (Confidence-stratified, failure-taxonomy'd, with the eval-set provenance stated. Give a single headline number only in context. Refusal rate is a positive story if framed right.)
2. "The customer wants 99% accuracy. What do you say?" (Reframe: 99% on what — the golden set, production traffic, high-confidence subset? Trade-offs among refusal rate, HITL cost, and coverage. Discuss what accuracy the human baseline is for the same task; it is rarely 99%.)
3. "How do you know if quality is drifting in production?" (QA sampling, alerting on the sample metric, plus segment-level watches on refusal rate and confidence distribution. Investigate whenever any of those move.)

## DRILL

Take an eval you have run on any classifier or RAG system. Rewrite the "accuracy = N%" line into the stratified-plus-taxonomy format above. Now draft the two-slide Friday-meeting version: slide 1 is the honest quality picture, slide 2 is the roadmap of fixes ordered by expected delta. Practice saying it out loud in under 90 seconds. This is the answer to the accuracy question for the rest of your career.
