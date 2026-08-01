# RAG from Scratch: Chunking, TF-IDF Retrieval, Grounded Answers

Phase 5 · Lesson 01 · ~2.5h

## PROBLEM

The ask arrives in every discovery meeting now, nearly verbatim: "We want ChatGPT, but on *our* documents." At an industrial-services customer, the previous vendor had tried the obvious thing — dump the policy wiki into a prompt, add "answer from the context," ship it. The demo dazzled. Then an employee asked about vacation rollover, the model answered from its general training instead of the customer's actual policy — off by five days — and HR caught it in week two. The next question, about a policy that wasn't in the corpus at all, got a fluent, confident, invented answer. The pilot died not because retrieval-augmented generation doesn't work, but because nobody had built the *system* around the model: retrieval you can inspect, grounding you can enforce, citations you can check, and a refusal path for questions the corpus can't answer.

RAG is not "vector database + API call." RAG is a pipeline with four failure points, and the FDE's job is making each one observable and testable — on a locked-down customer laptop, if necessary, with no vector DB and no API key. Which is exactly what this file does.

## INTUITION

The spine of every RAG system, and the decision at each stage:

**Chunking.** Models can't attend to a whole wiki, and retrieval works on pieces. Too-large chunks bury the relevant sentence in noise; too-small chunks orphan facts from their context ("the cap is 10 days" — cap on *what*?). Paragraphs are the honest default: humans already wrote them as units of one idea. Structure-aware and overlapping strategies come later (Lesson 02); every chunk needs a stable ID for citations.

**Retrieval.** The fashionable answer is embeddings in a vector database. The *field* answer is: start with lexical retrieval — TF-IDF or BM25 — because it's deterministic, explainable ("this chunk matched because it shares 'rollover' and 'vacation'"), runs anywhere, and is a shockingly strong baseline on enterprise text where the query vocabulary usually mirrors the document vocabulary. TF-IDF's core idea: weight a term by how often it appears in this chunk (term frequency) discounted by how many chunks contain it at all (inverse document frequency) — so "vacation" discriminates and "employee" doesn't. Cosine similarity ranks. Embeddings earn their complexity when vocabulary *diverges* (users say "PTO", docs say "vacation") — an upgrade you make deliberately, with an eval harness (Lesson 06), not by default.

**Grounded generation.** The prompt must do three jobs: carry the retrieved evidence, *scope* the model to that evidence ("answer ONLY from the sources"), and demand citations in a parseable format. Citations aren't decoration — they're the verification hook: if the model cites chunk IDs, you can machine-check that every cited ID was actually retrieved.

**Refusal.** The highest-stakes design decision. When retrieval confidence is low, the system must say "I don't know" *without calling the model at all* — because a fluent model handed weak evidence will improvise. A confidence threshold on the top retrieval score is crude and effective. Enterprises forgive "I don't have that information"; they do not forgive confident fabrication in front of HR.

## BUILD IT

Run it: `python code/lesson.py`. Three policy documents, six chunks, three grounded answers, one refusal — no network, no keys.

**Corpus and chunking.** `DOCS` holds three policies (vacation, expense, security) written with paragraph breaks. `chunk` splits on `\n\n` and mints stable IDs:

```python
chunks.append({"id": f"{doc_id}#{i}", "doc": doc_id, "text": para})
```

`vacation-policy#1` is a *citable address*. The test's first assertion — `len(chunks) == 6, "3 docs x 2 paragraphs"` — pins the chunking contract before anything else runs.

**Tokenization with a stopword list.** `tokenize` lowercases, extracts `[a-z0-9]+` runs, and drops ~20 stopwords. The stopword list matters more than it looks: without it, a query like "What is the…" matches every chunk a little, smearing the score distribution that the refusal threshold depends on.

**The index is TF-IDF in fifteen lines.** Document frequency is counted over *sets* of tokens per chunk (`self.df.update(set(tokenize(c["text"])))` — a term appearing five times in one chunk is still one document). Each chunk becomes a sparse dict vector:

```python
def _vec(self, text: str) -> dict:
    tf = Counter(tokenize(text))
    return {t: (1 + math.log(cnt)) * math.log(1 + self.n / self.df.get(t, self.n))
            for t, cnt in tf.items()}
```

Log-damped TF (a term's fifth occurrence adds little), smoothed IDF (the `1 +` avoids zero-weighting terms in every chunk). Queries are vectorized by the same function — one vocabulary, one weighting, no train/serve skew. `_cosine` handles the zero-vector edge (a query of pure stopwords scores 0.0, not a crash), and `search` returns the top-k `(score, chunk)` pairs — scores stay attached, because the confidence gate downstream needs them.

**MockLLM makes retrieval failures loud.** This is the file's sharpest idea. The mock is scripted with `(must_contain, response)` pairs:

```python
def complete(self, prompt: str) -> str:
    must_contain, response = self.script.pop(0)
    self.calls += 1
    assert must_contain in prompt, \
        f"retrieval failed: expected evidence '{must_contain}' in prompt"
    return response
```

Each scripted step asserts the prompt actually contains the evidence the answer needs. If retrieval ranked the wrong chunk, the failure isn't a subtly wrong answer you'd miss — it's an assertion naming the missing evidence. This converts "RAG quality" from vibes into a unit test, and it's the pattern to carry into production: log prompts, and assert on their contents in CI.

**`answer` wires the spine with two guardrails.** First the refusal gate — *before* any model call:

```python
hits = index.search(question)
if not hits or hits[0][0] < MIN_CONFIDENCE:
    return {"answer": "I don't have enough information...", "citations": [], "refused": True}
```

Then the grounded prompt (sources with bracketed IDs + "Answer ONLY from the sources. Cite chunk ids"), the model call, and the second guardrail — citation verification:

```python
citations = re.findall(r"\[([\w#-]+)\]", raw)
valid_ids = {c["id"] for _, c in hits}
assert all(cit in valid_ids for cit in citations), "hallucinated citation"
```

The model may only cite chunks it was actually shown. A fabricated citation — the sneakiest hallucination, because it *looks* verified — is caught mechanically.

**The test walks all four paths.** Three questions route to three different documents (proving retrieval discriminates, not just matches), each answer's citation is asserted exactly. Then the off-corpus question — "What is the weather in Singapore?" — must refuse, and the assertion `llm.calls == 3` proves the refusal happened *without invoking the model*. Refusal that still calls the model isn't refusal; it's an invitation.

## FIELD NOTES

- On real corpora, chunking is 60% of quality. Enterprise documents fight you: PDFs with tables, wikis with boilerplate headers on every page, the 40-tab spreadsheet someone calls "documentation." Budget more time for chunking than retrieval.
- `MIN_CONFIDENCE = 0.15` is honest about being a magic number. In the field you set it empirically: run 50 real questions (half answerable, half not), plot top-1 scores, place the threshold where the distributions separate. If they don't separate, your chunking or tokenization is broken — fix that first.
- The demo trap: RAG demos brilliantly on the ten questions the champion asks, because the champion asks questions the corpus answers. Production users ask about things not in the corpus — refusal behavior, not answer quality, determines whether trust survives month one. Seed the demo with an off-corpus question *on purpose* and show the refusal; it reads as integrity.
- When the customer demands "why did it answer that?", TF-IDF gives you a real answer: show the matched terms and scores. That explainability is worth real accuracy points in regulated industries — and it's why starting lexical is a strategy, not a compromise.

## INTERVIEW ANGLE

"Build/design RAG without a vector database" is now a canonical FDE interview exercise at the AI labs — precisely because it separates people who understand the pipeline from people who've only wired together hosted services.

Sample questions:

1. "Sketch RAG end to end. Where does it fail, and how do you detect each failure?" (Chunking→retrieval→grounding→refusal, with an observable check per stage: chunk IDs, retrieval scores, citation verification, model-call counts.)
2. "When is TF-IDF retrieval the right choice over embeddings?" (Determinism, explainability, air-gapped deployment, vocabulary overlap; embeddings when paraphrase/synonymy dominates — and only with an eval to prove the upgrade.)
3. "How do you stop a RAG system from answering questions it shouldn't?" (Confidence gate before the model call, scoped prompt, citation verification, and *measuring* refusal correctness on off-corpus questions.)

## DRILL

1. **Extend:** add k=3 retrieval with a *second* threshold — chunks below `MIN_CONFIDENCE` are dropped from context even when the top hit passes. Write a question where the third chunk is noise and assert it doesn't appear in the prompt (extend MockLLM with a `must_not_contain` field).
2. **Break:** remove the stopword list and rerun. Which question's retrieval degrades first, and does anything refuse that shouldn't? Watch the MockLLM assertion do its job, then restore.
3. **Fix:** the citation regex `\[([\w#-]+)\]` also matches bracketed text the model might emit that isn't a citation (e.g., "[sic]") — which would trip the hallucination assert spuriously. Tighten the contract: require citations to match retrieved-ID *format* (`doc#n`), and add a test where the model's answer contains harmless brackets.
