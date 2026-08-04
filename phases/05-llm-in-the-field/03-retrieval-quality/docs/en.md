# Retrieval Quality: Why the Demo Worked and Production Doesn't

**Phase 5 · Lesson 03 · ~1.5h**

## PROBLEM

The demo went perfectly. The VP asked five questions, the system answered four with clean citations and refused the fifth as designed. Two weeks later the pilot users' Slack channel is on fire. "It's making things up." "It gave me the wrong SKU." "It cited a document that has nothing to do with my question." You pull the logs. Retrieval scores look fine — top-1 above the confidence threshold on every complaint. But the retrieved chunk is wrong. The user asked about "PTO carryover for interns" and got the policy for full-time employees, because the intern policy uses the phrase "unused leave" and the query uses "PTO carryover" and TF-IDF has no idea those mean the same thing. The demo worked because the champion asked questions using the corpus's exact vocabulary. Real users don't.

Retrieval that scores high but retrieves wrong is the hardest RAG failure to detect — because every downstream metric (citation validity, refusal correctness) looks green. The system is confidently, correctly-formatted, wrong.

## INTUITION

Retrieval quality decomposes into three failure modes, each with a distinct fix:

**Vocabulary mismatch.** Users say "PTO", docs say "vacation." Users say "reimbursement", docs say "expense recovery." Lexical retrieval collapses here. Two fixes: (1) a synonym / glossary layer that expands queries at retrieval time — cheap, deterministic, works. (2) Semantic embeddings, which learn that "PTO" and "vacation" live near each other in vector space. Embeddings are the "right" answer and also the expensive one; earn them with an eval that proves the upgrade beats lexical on your corpus.

**Semantic drift.** The query and the correct chunk share vocabulary, but the query is about *something else*. "What's the policy on remote work for engineering?" retrieves a chunk about remote work for sales, because both contain "remote work" and "policy." Fix: filter by metadata (section, department, document type) before scoring. Structure the corpus so retrieval can respect it.

**Retrieval-recall vs generation-precision.** Sometimes the right chunk is at rank 4, not rank 1. Widen the retrieval window (top-k = 5 or 10) and let the model discriminate. But wider windows increase cost, latency, and hallucination risk (the model may weave the wrong chunk into the answer). Balance with a second-pass re-ranker — even a simple one: score chunks by term overlap with the query *and* the presence of expected entities (dates, IDs, names extracted from the query).

The eval loop is the discipline. You cannot fix retrieval you cannot measure. Build a golden set of (query, correct-chunk-id) pairs — 30 is enough to start. Track top-1 accuracy, top-3 accuracy, and MRR (mean reciprocal rank). Every change to chunking, tokenization, retrieval, or re-ranking gets a delta against the golden set. Without this, "quality" is vibes and every fix might break something else.

## BUILD IT

The retrieval quality debugging template, five steps you run in order:

```
1. Reproduce. Take the failed query. Run retrieval with top-k = 10.
   Print (rank, score, chunk_id, first_100_chars).

2. Locate ground truth. Find the chunk that *should* have won by hand
   (grep the corpus, ask the SME). Is it in the top 10 at all?

3. Diagnose the gap.
   - Not in top 10 -> chunking or vocabulary problem.
   - In top 3-10 -> ranking problem, add re-ranker or metadata filter.
   - In top 1 but wrong -> chunking is wrong (the right *content* is
     split across two chunks, or wrapped in noise).

4. Fix the smallest thing. In order of increasing effort:
   glossary expansion -> metadata filter -> re-ranker -> re-chunk
   -> embeddings. Don't jump to embeddings first; the fix is
   usually one layer up.

5. Run the golden set. Full pass. Confirm no regression on
   previously-passing queries.
```

A minimal glossary expander in stdlib:

```python
GLOSSARY = {
    "pto": ["vacation", "paid time off", "leave"],
    "reimbursement": ["expense recovery", "expense claim"],
    "termination": ["separation", "offboarding"],
}

def expand(query: str) -> str:
    terms = query.lower().split()
    expanded = []
    for t in terms:
        expanded.append(t)
        expanded.extend(GLOSSARY.get(t, []))
    return " ".join(expanded)
```

Ugly, effective, ships tomorrow. The glossary is a customer artifact — the SME curates it, you version it, it lives next to the corpus.

## FIELD NOTES

- The demo-to-production gap is almost always a query-distribution shift. The champion knows the corpus and unconsciously uses its vocabulary. Real users use their own. Instrument production queries from day one; you will discover a vocabulary gap the eval set never covered.
- Every enterprise has jargon the corpus doesn't. A pharma customer's users say "Ph3 readout" — the docs say "Phase 3 clinical trial results." A bank says "TDR" — the docs say "troubled debt restructuring." Extract the top 100 distinct query terms after two weeks; if they're not in the corpus, they belong in the glossary.
- Section-scoping is underrated. If the customer's org has clear domains (HR / Finance / Engineering), let users filter — or infer the filter from the query. Half of retrieval failures at scale are cross-domain contamination.
- Embeddings are not a silver bullet on messy enterprise text. On short chunks with lots of numbers, codes, and part IDs, lexical often beats dense retrieval because the important tokens are exactly the ones embeddings smooth over. Test before you commit.
- The customer will ask "why did it retrieve that?" Have an answer ready. TF-IDF gives you real, printable reasoning ("matched terms: `vacation`, `rollover`, `days` with scores..."). Embeddings give you cosine similarity, which is not an explanation. Explainability is worth accuracy in regulated industries.

## INTERVIEW ANGLE

Retrieval quality questions separate people who've operated RAG in production from people who've only prototyped it. Interviewers listen for eval discipline, layered fixes, and instinct for vocabulary drift.

Sample questions:

1. "Your RAG system's demo scored 90%. Users report 40% wrong answers. How do you find the gap?" (They want: log production queries, sample failures, categorize by failure mode — vocabulary, semantic drift, chunking — and fix the biggest bucket first. Bonus: mention query-distribution shift explicitly.)
2. "When would you not use embeddings?" (Air-gapped deployment, short chunks with high-signal tokens, need for deterministic explainability, small corpus where lexical is fine, tight cost/latency budget.)
3. "Design an eval loop for retrieval." (Golden set of query-to-chunk pairs curated with SME, metrics: top-1 accuracy, top-3, MRR, delta-on-change gate before deploy. Mention that the golden set must grow to reflect production query distribution.)

## DRILL

Take the RAG system from Lesson 01. Break its retrieval on purpose: add a fourth policy document whose text uses different vocabulary for the same concepts (e.g., a policy about "leave accrual" that overlaps semantically with the vacation policy). Write five queries in the vocabulary of a hypothetical user, not the docs. Measure top-1 accuracy. Now add a glossary expander and re-measure. Track the delta. Write a two-paragraph note to the customer's SME asking them to review and extend the glossary — this is the artifact they will maintain forever after you leave.
