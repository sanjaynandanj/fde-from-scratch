"""FLAGSHIP - RAG from scratch: chunking, TF-IDF retrieval, grounded answers.

The customer wants "ChatGPT but on OUR documents." Build the whole spine
with no vector DB and no API key: paragraph chunking, TF-IDF + cosine
retrieval, a grounded prompt with citation IDs, and a refusal path when
retrieval confidence is too low. MockLLM is deterministic and scripted -
the harness around it is the real lesson.
"""

import math
import re
from collections import Counter

DOCS = {
    "vacation-policy": (
        "Employees accrue 1.5 vacation days per month of service.\n\n"
        "Unused vacation days roll over up to a maximum of 10 days per year. "
        "Days beyond the cap are forfeited on January 1."
    ),
    "expense-policy": (
        "Meal expenses during travel are reimbursed up to 75 dollars per day.\n\n"
        "All expense reports must be filed within 30 days of the trip via the "
        "finance portal. Late reports require VP approval."
    ),
    "security-policy": (
        "Production database access requires an approved ticket and expires "
        "after 8 hours.\n\nContractors are never granted production access."
    ),
}

TOKEN_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = {"what", "is", "the", "in", "a", "an", "of", "to", "for", "i",
             "can", "how", "do", "my", "per", "on", "and", "or", "are", "get"}


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


def chunk(docs: dict) -> list[dict]:
    chunks = []
    for doc_id, text in docs.items():
        for i, para in enumerate(p.strip() for p in text.split("\n\n") if p.strip()):
            chunks.append({"id": f"{doc_id}#{i}", "doc": doc_id, "text": para})
    return chunks


class TfIdfIndex:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.df: Counter = Counter()
        for c in chunks:
            self.df.update(set(tokenize(c["text"])))
        self.n = len(chunks)
        self.vectors = [self._vec(c["text"]) for c in chunks]

    def _vec(self, text: str) -> dict:
        tf = Counter(tokenize(text))
        return {t: (1 + math.log(cnt)) * math.log(1 + self.n / self.df.get(t, self.n))
                for t, cnt in tf.items()}

    @staticmethod
    def _cosine(a: dict, b: dict) -> float:
        dot = sum(v * b.get(t, 0.0) for t, v in a.items())
        na, nb = math.sqrt(sum(v * v for v in a.values())), math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    def search(self, query: str, k: int = 2) -> list[tuple[float, dict]]:
        qv = self._vec(query)
        scored = sorted(((self._cosine(qv, v), c) for v, c in zip(self.vectors, self.chunks)),
                        key=lambda x: -x[0])
        return scored[:k]


class MockLLM:
    """Deterministic stand-in. Each scripted step asserts the prompt contains
    the evidence it needs - if retrieval fed it the wrong chunk, the test dies."""

    def __init__(self, script: list[tuple[str, str]]):
        self.script = list(script)
        self.calls = 0

    def complete(self, prompt: str) -> str:
        must_contain, response = self.script.pop(0)
        self.calls += 1
        assert must_contain in prompt, \
            f"retrieval failed: expected evidence '{must_contain}' in prompt"
        return response


MIN_CONFIDENCE = 0.15


def answer(question: str, index: TfIdfIndex, llm: MockLLM) -> dict:
    hits = index.search(question)
    if not hits or hits[0][0] < MIN_CONFIDENCE:
        return {"answer": "I don't have enough information in the indexed documents.",
                "citations": [], "refused": True}
    context = "\n".join(f"[{c['id']}] {c['text']}" for _, c in hits)
    prompt = (f"Answer ONLY from the sources. Cite chunk ids in brackets.\n"
              f"SOURCES:\n{context}\nQUESTION: {question}")
    raw = llm.complete(prompt)
    citations = re.findall(r"\[([\w#-]+)\]", raw)
    valid_ids = {c["id"] for _, c in hits}
    assert all(cit in valid_ids for cit in citations), "hallucinated citation"
    return {"answer": raw, "citations": citations, "refused": False}


def main():
    chunks = chunk(DOCS)
    assert len(chunks) == 6, "3 docs x 2 paragraphs"
    index = TfIdfIndex(chunks)

    llm = MockLLM([
        ("roll over up to a maximum of 10 days",
         "Up to 10 unused vacation days roll over each year [vacation-policy#1]."),
        ("75 dollars per day",
         "Travel meals are reimbursed up to $75/day [expense-policy#0]."),
        ("Contractors are never granted",
         "No - contractors are never granted production access [security-policy#1]."),
    ])

    r1 = answer("How many vacation days can I roll over?", index, llm)
    assert not r1["refused"] and r1["citations"] == ["vacation-policy#1"]

    r2 = answer("What is the daily meal reimbursement limit for travel?", index, llm)
    assert r2["citations"] == ["expense-policy#0"]

    r3 = answer("Can contractors get production database access?", index, llm)
    assert r3["citations"] == ["security-policy#1"]

    # off-corpus question must refuse, not hallucinate - and never call the LLM
    r4 = answer("What is the weather in Singapore?", index, llm)
    assert r4["refused"] and llm.calls == 3, "refusal path must not invoke the model"

    print("rag-from-scratch: all assertions passed (3 grounded answers + 1 refusal)")


if __name__ == "__main__":
    main()
