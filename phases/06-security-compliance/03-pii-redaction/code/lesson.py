"""FLAGSHIP - PII detection and redaction from scratch.

You need customer data in a demo, a bug report, or an LLM prompt - and the
DPA says PII never leaves their tenant. Build the redactor: pattern
detectors (email, phone, SSN, credit card with Luhn), consistent
pseudonyms (same input -> same token, so joins survive), and a reversible
vault for the people with clearance.
"""

import re

EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")
SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
PHONE = re.compile(r"(?<!\d)(?:\+?1[ .-]?)?(?:\(\d{3}\)|\d{3})[ .-]?\d{3}[ .-]?\d{4}(?!\d)")
CARD = re.compile(r"\b(?:\d[ -]?){13,16}\b")


def luhn_ok(digits: str) -> bool:
    total, alt = 0, False
    for d in reversed(digits):
        n = int(d)
        if alt:
            n *= 2
            if n > 9:
                n -= 9
        total += n
        alt = not alt
    return total % 10 == 0


class Redactor:
    def __init__(self):
        self.vault: dict[str, str] = {}     # token -> original
        self.seen: dict[str, str] = {}      # original -> token
        self.counters: dict[str, int] = {}

    def _token(self, kind: str, original: str) -> str:
        if original in self.seen:
            return self.seen[original]
        self.counters[kind] = self.counters.get(kind, 0) + 1
        token = f"[{kind}_{self.counters[kind]}]"
        self.seen[original] = token
        self.vault[token] = original
        return token

    def redact(self, text: str) -> str:
        def sub(kind, pattern, txt, guard=None):
            def repl(m):
                if guard and not guard(m.group()):
                    return m.group()
                return self._token(kind, m.group())
            return pattern.sub(repl, txt)

        text = sub("EMAIL", EMAIL, text)
        text = sub("SSN", SSN, text)
        text = sub("CARD", CARD, text,
                   guard=lambda s: luhn_ok(re.sub(r"\D", "", s)))
        text = sub("PHONE", PHONE, text)
        return text

    def restore(self, text: str) -> str:
        for token, original in self.vault.items():
            text = text.replace(token, original)
        return text


def main():
    r = Redactor()
    ticket = (
        "Customer Jane (jane.doe@acme.com, 555-867-5309) reports her card "
        "4539 1488 0343 6467 was charged twice. SSN on file 123-45-6789. "
        "Order number 1234 5678 9012 3456 unaffected. "
        "Alt contact: jane.doe@acme.com or (555) 867-5309."
    )
    out = r.redact(ticket)

    assert "jane.doe@acme.com" not in out and "123-45-6789" not in out
    assert "4539 1488 0343 6467" not in out, "valid Luhn card must be redacted"
    assert "1234 5678 9012 3456" in out, "order number (Luhn-invalid) must survive"
    assert out.count("[EMAIL_1]") == 2, "same email -> same token, both occurrences"
    assert "[SSN_1]" in out and "[CARD_1]" in out

    # phone appears in two formats; exact-string tokens differ but both redacted
    assert "555-867-5309" not in out and "(555) 867-5309" not in out
    assert "[PHONE_1]" in out and "[PHONE_2]" in out

    # round trip for cleared users
    assert r.restore(out) == ticket

    # idempotency: redacting redacted text changes nothing
    assert r.redact(out) == out

    # consistency across documents: Jane's email gets the SAME token in doc 2
    doc2 = r.redact("Follow-up from jane.doe@acme.com re: refund.")
    assert "[EMAIL_1]" in doc2

    print(f"pii-redaction: all assertions passed "
          f"({len(r.vault)} distinct PII values vaulted, round-trip verified)")


if __name__ == "__main__":
    main()
