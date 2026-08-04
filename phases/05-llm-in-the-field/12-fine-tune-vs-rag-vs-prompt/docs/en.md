# Fine-Tuning vs RAG vs Prompting: The Decision the Customer Asks For

**Phase 5 · Lesson 12 · ~1h**

## PROBLEM

The champion has been reading. "Should we fine-tune a model on our data?" comes up on the Tuesday call. She has heard from a peer at another company that they fine-tuned and saw big gains. Her VP has heard "fine-tuning" is how you get an "AI moat." Meanwhile, the actual pilot is prompted RAG on a hosted model, quality is 82% on the eval, and the top failure category is a vocabulary mismatch that a glossary entry would fix. The right answer is "not yet — here's why and here's what we'd do first." The wrong answer is "let's spike on fine-tuning next sprint," which will burn six weeks, cost $30k in compute and data prep, and leave you with a model that is slightly worse than the prompted RAG you had before. The customer asks the fine-tuning question every time. You need a clean framework for answering it.

## INTUITION

Three techniques, three problems they solve:

**Prompting** teaches the model *what to do*. Task definition, format, tone, constraints, vocabulary. Solves: shape of the output, adherence to policy, task framing. Cheap, fast, iterable in minutes. Fails when the model doesn't have the information or the base capability.

**RAG** teaches the model *what to know* at inference time. Injects fresh, private, or long-tail knowledge that isn't in the base weights. Solves: private knowledge, freshness, source-of-truth grounding, citation. Cheap-ish, moderate to build, iterable in hours. Fails when the retrieval fails (Lesson 03) or the base model can't reason well over the retrieved content.

**Fine-tuning** teaches the model *how to behave* at a deeper level than a prompt can express. Adjusts weights so the model naturally produces a certain format, follows a certain reasoning pattern, or handles a domain distribution shift. Solves: consistent format at scale, latency (shorter prompts), specialized reasoning styles, distribution shift where the base model underperforms on a specific text genre. Expensive, slow, hard to iterate (each experiment is hours to days), and the model becomes yours to maintain across base-model upgrades.

The default order — the one to walk the customer through — is always: **prompt first, RAG second, fine-tune last.** Each earlier step is 10x cheaper and 10x faster to iterate. Skipping to fine-tuning without evidence that prompting and RAG have hit their ceiling is how pilots die of over-engineering.

## BUILD IT

The decision tree to bring to the Tuesday call:

```
What's the failure mode on the eval?

1. Wrong task, wrong format, wrong tone?
   -> Prompting. Rewrite the prompt, add examples, add taboos.

2. Right task, wrong facts — model doesn't know your data?
   -> RAG. Chunk your corpus, ground the answer, cite sources.

3. Right task, right facts, wrong vocabulary?
   -> Glossary in the prompt (cheap) or embeddings upgrade in
      retrieval (medium). Not fine-tuning.

4. Right task, right facts, wrong style/format at scale, and
   the prompt is already 2000 tokens of examples?
   -> Consider fine-tuning to compress the examples into weights.

5. The base model just can't reason well in your domain (dense
   legal text, obscure code, non-English at a level the base
   doesn't have), and RAG doesn't help because the model can't
   use the retrieved content?
   -> Consider fine-tuning (or a bigger base model — try that first).

6. You need latency the current model can't hit, and a smaller
   fine-tuned model would work?
   -> Fine-tune a smaller model. This is often the real reason
      fine-tuning wins.
```

**A minimum eval-driven framing to bring to the meeting:**

```
Current: prompted RAG on GPT-tier hosted model.
Eval: 82% on 200-item golden set.

Failure breakdown:
  40% vocabulary mismatch    -> glossary fix, 1 day, +5-8%
  25% chunking issue         -> re-chunk, 2 days, +3-5%
  20% base model reasoning   -> upgrade model tier, 0 days, +2-4%
  10% not in corpus          -> improve refusal, 1 day, +0% acc, +trust
   5% actually needs fine-tune-level fix

Recommendation: sequence glossary -> rechunk -> upgrade tier.
Re-measure after each. Fine-tune conversation returns if
we plateau below target.
```

You are not saying "no fine-tuning." You are saying "fine-tuning after evidence." This lands with technical champions and executives alike.

## FIELD NOTES

- Fine-tuning as an "AI moat" is a bad reason. The moat, if it exists, is in the customer's data, workflows, and integrations — not in a differentiated set of weights. Weights depreciate every time the base model improves; workflows compound.
- Data prep is 80% of the fine-tuning cost. High-quality labeled examples in the tens of thousands is the honest number for a real task; hundreds is enough only for style-tuning. Customers underestimate this by an order of magnitude.
- Fine-tuning locks you into a base model. When the provider releases a better base six months later, you have to re-tune. Prompt and RAG systems port trivially; fine-tuned systems don't. Bring this to the total-cost conversation.
- Distillation is the underrated middle path. When the flagship model works well but is too slow or expensive, distill its outputs into a smaller fine-tuned model. The training data is free (generate it) and the win is real. This is the fine-tuning use case that actually pays off in enterprise deployments.
- LoRA / adapter tuning is cheaper than full fine-tuning and often enough. When the customer insists on tuning, propose LoRA first — one-tenth the cost, most of the benefit, easier to iterate.
- The champion's peer who "fine-tuned and got gains" almost always ran a bad eval before and a good eval after. Show up to that conversation with the eval-harness framing (Lesson 06); the honest apples-to-apples comparison usually collapses the moat argument.

## INTERVIEW ANGLE

Fine-tuning-vs-RAG-vs-prompting questions probe whether you can push back on a customer's premature optimization with a clean framework. Interviewers listen for the sequencing instinct and eval-driven decision-making.

Sample questions:

1. "The customer asks 'should we fine-tune?' — what do you say?" (Not yet. Prompt first, RAG second, fine-tune only if the eval shows a failure mode neither can fix. Walk through the failure taxonomy and show sequencing beats parallel spikes.)
2. "When is fine-tuning actually the right answer?" (Format consistency at scale where prompt examples don't fit, latency-driven distillation to a smaller model, genuine distribution shift the base can't handle. Note that most stated reasons are not these.)
3. "How do you compare a fine-tuned model against a prompted one?" (Same golden set, same eval harness, delta on the same metrics. Include cost, latency, and maintainability as first-class metrics — not just accuracy. Bonus: mention that a fine-tuned model has to keep winning as the base improves.)

## DRILL

Take a failure your RAG system exhibits (real or hypothetical). Classify it against the six-branch decision tree. Estimate the cost, time, and expected quality delta of the two cheapest fixes. Now estimate the same for the fine-tuning approach. Write the two-paragraph recommendation you would send the customer's technical champion. Save it — this is the memo you will send at least once per engagement.
