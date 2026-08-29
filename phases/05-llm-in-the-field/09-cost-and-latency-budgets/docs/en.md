# Cost and Latency Budgets: The CFO Reads the Invoice

**Phase 5 · Lesson 09 · ~1h**

## PROBLEM

Month one of the pilot: the LLM invoice is $180. Everyone's happy. Month three: $14,000. The CFO forwards the invoice to your champion with a one-line email that reads only "?". Your champion forwards it to you. You dig in. Half the spend is one internal team who discovered the tool and now uses it for everything, including asking it to rewrite their emails. A quarter is your own eval jobs running nightly against the full golden set. The rest is real usage growing linearly with adoption. Nothing is broken; everything is expensive. The pilot is now a procurement conversation. You could have seen this in week two if you had built the cost model on day one. You did not, because "we'll figure it out later" felt reasonable when the invoice was $180.

The CFO will read the invoice. Design as if that is true from day one.

## INTUITION

Cost and latency in an LLM system decompose into a small number of levers you can move:

**Tokens in.** Prompt length dominates cost in most enterprise RAG. Fixed prefix (role, glossary, examples), retrieved context (top-k chunks), user query. The prefix is stable and cacheable; the retrieved context grows with k; the query is small.

**Tokens out.** Model output. Cheaper per-token than input on most providers, but latency-dominant — output tokens are generated serially.

**Model choice.** Bigger model = better answers, higher cost, higher latency. The cost delta between the top-tier and mid-tier model is often 5-10x. The quality delta is often 5-10%. Choose per task, not per company.

**Call count.** Retries, agent loops, batched evals, and rogue power users are the sneak-attack cost drivers. One user asking the assistant to draft 30 variants of an email costs more than 100 users asking normal questions.

**Caching.** Prompt caching (provider-supported) drops the cost of the stable prefix by 40-90% on cache hits. Response caching (your side) eliminates repeat questions entirely — common in Q&A workloads where the top 50 questions cover 40% of traffic.

Latency is a related but separate budget. Users abandon at 5-10 seconds for interactive workflows; batch jobs tolerate minutes. The dominant terms are retrieval (fast, ~50ms), first-token-latency (network + queue, ~200-800ms), and output generation (throughput-bounded, ~30-100 tokens/sec). Streaming responses is the highest-leverage UX fix — perceived latency drops even though total time is unchanged.

## BUILD IT

The cost model, back-of-envelope, on day one:

```
per_request_cost =
    (prefix_tokens * (1 - cache_hit_rate) * input_price_per_token)
  + (prefix_tokens * cache_hit_rate * cached_input_price_per_token)
  + (retrieved_context_tokens * input_price_per_token)
  + (output_tokens * output_price_per_token)

daily_cost = per_request_cost * requests_per_day * retry_multiplier
```

Plug in real numbers. For a typical enterprise RAG deployment on a mid-tier hosted model, one grounded Q&A call is $0.005-0.03. At 10,000 requests/day, that's $50-300/day, $1,500-9,000/month. Show this to your champion in week one. When adoption 10x's, the number 10x's, and nobody is surprised.

**Cost controls to ship with the pilot:**

1. **Per-user daily quota.** Configurable, default sane (e.g., 100 requests/day). Prevents runaway power users. Log quota-hits so you can talk to the humans hitting them.
2. **Response cache with TTL.** Hash `(prompt_prefix + retrieved_ids + query_normalized)`, cache the answer for 24 hours. Invalidate on corpus update.
3. **Prompt-cache prefix design.** Structure the prompt so the stable content (role, glossary, examples) is the prefix, the variable content (retrieval + query) is the suffix. Providers cache prefixes.
4. **Model tiering.** Route simple queries (classification, extraction) to a cheaper model; route hard queries (reasoning, multi-hop) to the flagship. A cheap classifier deciding the route is worth its own cost.
5. **Eval budgeting.** Nightly eval on full golden set is expensive. Sample: full run weekly, sampled run daily.

**Latency controls:**

- Stream responses (first token < 1s beats no token for 5s).
- Retrieval in parallel with query rewriting when both are needed.
- Cap top-k at what your eval says is necessary; every extra chunk is input tokens.
- If your provider offers cheaper/faster regional endpoints, use them for latency-sensitive traffic.

## FIELD NOTES

- Show the CFO the cost dashboard before they ask. In the first weekly, present: daily spend, per-user distribution, per-endpoint breakdown, projected monthly at current growth. This makes you the person who is in control of the spend, not the person the invoice is filed against.
- The eval harness itself burns budget. A 500-item golden set run against three prompt variants nightly is 1,500 calls a day. Budget it explicitly; it's an engineering-team cost, not a customer-team cost.
- Power users are a signal, not a bug. The user who submits 400 requests a day discovered a use case worth building a real product feature for. Talk to them before you throttle them.
- Streaming is often blocked by the customer's proxy or reverse-proxy stack. Test it in their environment early — nothing worse than promising a snappy UX and finding the corp firewall buffers responses.
- On-prem or VPC deployments have a different cost curve: fixed infrastructure cost, marginal cost near zero. The break-even against hosted-per-token is usually somewhere around 100k-1M requests/month depending on model size. Have the math ready when the customer's finance team asks (Lesson 10).

## INTERVIEW ANGLE

Cost/latency questions probe whether you think about the CFO conversation before it happens. Interviewers listen for the cost model on day one, layered controls, and streaming as UX.

Sample questions:

1. "You're deploying a RAG system for 500 users. How do you estimate the LLM bill?" (Walk through the cost formula: tokens in, tokens out, request rate, retry multiplier, cache hit rate. Give a number with error bars, then a control plan.)
2. "The customer's LLM spend tripled last month. Diagnose." (Look at per-user distribution, per-endpoint distribution, request-rate change, model-mix change. Talk to the top-5 users. Add per-user quotas if warranted.)
3. "How do you reduce first-token latency in a RAG system?" (Streaming, prompt caching, parallel retrieval, smaller model for simple queries, regional endpoints, cap top-k. Bonus: distinguish perceived from actual latency.)

## DRILL

Take a RAG or extraction system you have built. Compute its per-request cost with real numbers from a provider price sheet. Compute projected monthly cost at 100, 1,000, and 10,000 requests/day. Now design three cost controls you would add to keep the 10k/day scenario under a target monthly budget of your choosing. Sketch the CFO-facing dashboard: what three numbers appear at the top? Save the template — you will paste it into every weekly status once the pilot has real users.
