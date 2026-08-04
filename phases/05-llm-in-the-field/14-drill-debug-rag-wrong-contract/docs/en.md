# Drill: Debug a RAG System That Answers from the Wrong Contract

**Phase 5 · Lesson 14 · ~1.5h**

## PROBLEM

Tuesday morning, the customer's contracts-team lead pings your champion. Screenshot attached. The RAG assistant answered a question about the master services agreement for Client A with a payment-term clause that comes from Client B's contract. The clauses are similar but not identical — 30 days vs 45 days. The user, a paralegal, caught it because he was already looking at Client A's contract in another window; the model was confident, cited a chunk ID, and cited the wrong document. The champion wants an incident report by end of day and a fix by end of week. This is a good, ordinary field crisis: a real production failure with a bounded time box, several plausible root causes, and a customer who is watching how you handle it. The drill is: work through it the way you would in the field.

This is a field drill, not a flagship. Read the setup, walk through the diagnosis, then implement the fix and verify.

## INTUITION

The failure mode is **cross-document contamination**: retrieval returned a chunk from the wrong document because two documents share vocabulary that matters to the query. The candidate root causes, in the order to check them:

1. **Missing metadata scoping.** The chunks don't carry a `client_id` or `document_id` that retrieval can filter on. The user's query "what's the payment term for Client A" gets matched purely on lexical overlap — and "payment terms are 45 days" scores high whether it's Client A's or Client B's contract.

2. **Chunk boundary problem.** The chunk that scored highest doesn't contain the client name — the client is only mentioned in the document title or the first paragraph, and the chunk with the payment-term clause is three paragraphs deep. Without the client name in the chunk, there's no discriminator.

3. **Query under-specification.** The user asked "what's the payment term" without saying which client, expecting the UI's context to filter (they had Client A selected in the app). The RAG backend never received that filter.

4. **Ranking noise.** The right chunk (Client A's payment term) is in the top-5 but not top-1 because Client B's clause has slightly higher lexical density on the query terms.

Diagnosis order matters. Check metadata first because it's the cheapest to verify and the most common cause. Check chunking second. Query and ranking are downstream fixes.

## BUILD IT

The drill walkthrough. Assume you have the RAG system from Lesson 01 as your starting point. Extend it with a two-document corpus that reproduces the bug:

```python
DOCS = {
    "client-a-msa": """
    Master Services Agreement between Acme Corp and Client A.

    Payment Terms. Client A shall pay all invoices within thirty (30) days
    of receipt. Late payments accrue interest at 1.5% per month.

    Confidentiality. Both parties agree to maintain confidentiality...
    """,
    "client-b-msa": """
    Master Services Agreement between Acme Corp and Client B.

    Payment Terms. Client B shall pay all invoices within forty-five (45) days
    of receipt. Late payments accrue interest at 1.0% per month.

    Confidentiality. Both parties agree to maintain confidentiality...
    """,
}
```

Chunk on paragraphs. Query: "what's the payment term for Client A?" — depending on tokenization, the top-1 hit might be either document because both chunks contain "payment", "term", "client", "shall", "invoices", etc. — the discriminating tokens "A" and "thirty" (or "30") are single tokens against a lot of shared noise.

**Step 1: Reproduce.** Run the query, print top-3 chunks with scores. Confirm the wrong document ranks high. If it doesn't reproduce, the bug is in the customer's specific data — get their exact chunk IDs.

**Step 2: Diagnose with metadata.** Look at the wrong-ranked chunk. Does it contain "Client B"? If yes, the retrieval failed to weight it; if no, the discriminator isn't in the chunk. In our example, "Payment Terms. Client B shall pay..." — the client name is in the chunk but so is "Client B" as noise on Client-A queries.

**Step 3: Apply the fix layer.** In order of least to most invasive:

**Fix 3a — Metadata filter.** Every chunk carries a `client_id` derived from the document. The query carries a `client_id` from the UI context. Retrieval is `[c for c in chunks if c.client_id == query.client_id]`. This is the correct fix in most enterprise RAG deployments where documents belong to distinct entities:

```python
def search_scoped(self, query: str, client_id: str, k: int = 3):
    qv = self._vec(query)
    scored = [
        (self._cosine(qv, self._vec(c["text"])), c)
        for c in self.chunks
        if c["client_id"] == client_id
    ]
    scored.sort(reverse=True, key=lambda x: x[0])
    return scored[:k]
```

**Fix 3b — Prepend client to chunk.** If metadata scoping isn't available (some corpora don't have clean entity boundaries), prepend the document's discriminating context to every chunk before indexing:

```python
chunk_text = f"[{client_name}] {paragraph_text}"
```

Now "Client A" is in every one of Client A's chunks, and the query "for Client A" matches on brand-name overlap.

**Fix 3c — Query rewriting.** If the UI can't pass metadata but the user's session includes the context, rewrite the query server-side: `"what's the payment term"` + selected-client `"Client A"` becomes `"what's the payment term for Client A"`. This puts the client name in the query.

**Step 4: Verify.** Add both queries to the golden set: `("payment term for Client A", "client-a-msa#...")` and same for B. Rerun. Both must top-1 the correct document.

**Step 5: Write the incident report.** Five lines:

```
INCIDENT: RAG cross-document contamination on Client A/B payment-terms queries.
CAUSE:    Retrieval ranked Client B's chunk higher due to shared clause vocabulary
          and missing document-level metadata scoping.
IMPACT:   1 known user, 0 downstream contract errors (caught in QA).
FIX:      Added client_id metadata filter to retrieval; verified on golden set.
FOLLOWUP: Extending golden set to cover cross-client contamination class;
          adding QA-sampling flag when retrieved chunks span multiple client_ids.
```

That report — sent to the champion within 24 hours — is the artifact the customer remembers.

## FIELD NOTES

- Cross-document contamination is nearly universal in enterprise RAG. Any customer with per-entity documents (contracts, patient records, accounts, tickets) will see it. Design metadata scoping *before* the first pilot user, not after the first incident.
- The paralegal who caught this is now your best QA source. Ask her for three more "borderline" queries she has caught the assistant on. Add them to the golden set. Send her a note thanking her — power users who catch errors are worth their weight in champions.
- "Chunks span multiple client_ids" is a great production alert. When it fires, either the metadata is wrong or the query is ambiguous. Either way, investigate before it becomes an incident.
- Do not push the fix Friday afternoon without the golden-set delta. "We fixed it" without evidence invites the next incident to feel bigger than it is. "We fixed it, golden-set accuracy on this failure class went from 40% to 100%, and here's the new alert we added" invites trust.
- The incident report is a customer-facing artifact. Write it in five lines like the FDE Friday email in Phase 0 — shipped, learned, blocked, next, ask.

## INTERVIEW ANGLE

RAG-debugging questions in FDE loops are increasingly common because the failure modes are subtle and interviewers want to see the diagnostic instinct.

Sample questions:

1. "A RAG system is returning answers from the wrong document. Walk through your diagnosis." (Reproduce, print top-k with scores and chunk content, check metadata presence, check chunking, check query. Fix in order of least-invasive: metadata filter > prepend > query rewriting > rechunk.)
2. "How would you prevent this class of bug in the first place?" (Metadata scoping by design, chunk-level context (prepend document/entity name), golden set covers cross-entity contamination cases, production alert on multi-entity retrieval.)
3. "Walk me through the incident report you'd send the customer." (Five-line format: incident, cause, impact, fix, followup. Emphasize impact quantification and the follow-up preventive action, not the heroic debugging story.)

## DRILL

1. **Reproduce.** Build the two-client MSA corpus in the code above, run the ambiguous query, confirm the wrong document ranks top-1.
2. **Fix with metadata scoping.** Add `client_id` to each chunk, add a `search_scoped` method, verify the correct chunk wins.
3. **Fix with prepended context.** Undo (1) and instead prepend `[Client A]` / `[Client B]` to every chunk of each document. Rerun the same query; confirm it also wins (this fix works when metadata is unavailable).
4. **Extend the golden set.** Add three more cross-contamination queries (different clauses: confidentiality, termination, indemnification). Confirm all pass under both fixes.
5. **Write the incident report** in the five-line format above.

Save the extended RAG code and the incident report template. You will reuse both, unchanged, on the next engagement.
