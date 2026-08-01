# PII Detection and Redaction from Scratch

Phase 6 · Lesson 03 · ~2h

## PROBLEM

Week five of a support-analytics pilot. You need three things, urgently: real tickets to seed a demo for the exec review, a reproducible bug report for your product team (the parser chokes on one specific ticket), and a batch of tickets to send through an LLM for classification. All three are blocked by the same sentence in the DPA the customer's legal team spent six weeks negotiating: *customer personal data shall not leave the customer's environment.* The tickets are full of emails, phone numbers, card numbers from customers who typed them where they shouldn't, and the occasional SSN. The naive moves are all career-limiting: copying tickets into a bug report leaks PII into your company's Jira forever; pasting them into a hosted LLM is a reportable incident; hand-scrubbing 500 tickets is a week you don't have and a human error you can't rule out.

The unlock is a redactor you can run *inside* their environment: PII goes in, tokens come out, and — critically — the output is still *useful*: the same customer maps to the same token so joins and dedup still work, and cleared users can reverse it. Sixty lines of code that converts "no" into "yes, with controls." That conversion is half of what Phase 6 is about.

## INTUITION

Four design decisions:

**Detection: patterns vs. NER.** Structured PII — emails, phones, SSNs, card numbers — has *shape*, and regex catches shape with explainable behavior ("this matched because it's ddd-dd-dddd"). Names and addresses need NER models and come with false-negative anxiety; the field move is regex for structured PII first, which covers the bulk of DPA risk in operational data, then escalate if the corpus demands more. In compliance conversations, explainable detection is itself a feature — you can tell the DPO exactly what the system catches and what it doesn't.

**Precision via checksums.** The card-number regex has a false-positive problem: order numbers, tracking numbers, and internal IDs are also 13–16 digits. Redacting those destroys the analytical value you're trying to preserve. The fix is a *validator behind the matcher*: card numbers satisfy the Luhn check digit; a 16-digit order number almost never does (a random digit string passes Luhn 10% of the time — the guard cuts false positives by ~90%, and in practice more, since many ID schemes never collide). Pattern proposes, checksum disposes.

**Replacement: mask vs. pseudonym.** Masking (`***`) destroys structure: you can no longer count distinct customers, join two mentions of the same person, or follow a thread. **Consistent pseudonymization** — same input, same token, `[EMAIL_1]` — preserves the relational skeleton while removing the identity. This is the difference between "redacted data" and "redacted data you can still analyze," and it's what makes redacted corpora usable for demos, debugging, and LLM processing.

**Reversibility: vault or void.** Sometimes redaction must be one-way (data leaving the tenant forever). But for in-tenant workflows — a support engineer with clearance needs the real email to reply — you want a *vault*: the token↔original mapping, stored separately, access-controlled, so redaction becomes a permission boundary instead of information destruction. The vault is the highest-sensitivity object in the system; it *is* the PII. Where it lives and who can call `restore` is a governance decision you write down before shipping.

## BUILD IT

Run it: `python code/lesson.py`.

**Four patterns, one with teeth.** `EMAIL` and `SSN` are straightforward shapes. `PHONE` earns its complexity — optional `+1` country code, parenthesized or bare area code, three separator styles, and lookarounds (`(?<!\d)`/`(?!\d)`) so it won't bite ten digits out of the middle of a longer number. `CARD` matches 13–16 digits with optional space/dash separators — deliberately loose, because the precision comes from the validator:

```python
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
```

Textbook Luhn: right-to-left, double every second digit, fold two-digit results, sum divisible by 10. The test data is built to prove the point: `4539 1488 0343 6467` (Luhn-valid) must be redacted; `1234 5678 9012 3456` — an "order number" that fails Luhn — must *survive*, asserted explicitly.

**The `Redactor` keeps three maps.** `seen` (original→token) delivers consistency; `vault` (token→original) delivers reversibility; `counters` numbers tokens per kind:

```python
def _token(self, kind: str, original: str) -> str:
    if original in self.seen:
        return self.seen[original]
    self.counters[kind] = self.counters.get(kind, 0) + 1
    token = f"[{kind}_{self.counters[kind]}]"
    self.seen[original] = token
    self.vault[token] = original
    return token
```

The early return is the consistency guarantee. And because `seen` persists across calls, consistency spans *documents*: the test redacts a second, later document and asserts Jane's email still becomes `[EMAIL_1]` — which is exactly what lets you dedup or thread a redacted corpus.

**Order of operations is a real design decision.** `redact` applies patterns in sequence — email, SSN, card (with the Luhn guard), phone:

```python
text = sub("CARD", CARD, text, guard=lambda s: luhn_ok(re.sub(r"\D", "", s)))
text = sub("PHONE", PHONE, text)
```

Card runs *before* phone because the patterns overlap on digit runs — a 13-digit card could otherwise get partially eaten by the phone matcher. The `guard` mechanism is the general pattern: any detector can carry a semantic validator, and a failed guard returns the original text untouched (`return m.group()`), not a hole.

**The assertions are a compliance checklist in executable form.** One hostile ticket exercises everything: both occurrences of the same email collapse to one token (`out.count("[EMAIL_1]") == 2`); the same phone in *two formats* becomes two tokens — the test honestly documents that exact-string pseudonymization doesn't canonicalize `555-867-5309` vs `(555) 867-5309` (that's the drill); the Luhn pair behaves as designed. Then three properties that production redactors are actually judged on:

```python
assert r.restore(out) == ticket          # round trip for cleared users
assert r.redact(out) == out              # idempotency: re-redaction is a no-op
```

Round-trip proves the vault is lossless. Idempotency proves tokens don't match any PII pattern themselves — you can safely run redaction at multiple pipeline stages (belt and suspenders) without `[EMAIL_1]` mutating into `[EMAIL_2]_1`. The cross-document assertion closes it out. Note `restore`'s simple loop over vault entries is fine here; at scale you'd want a single-pass regex over token shapes — same contract, different constant factor.

## FIELD NOTES

- Run the redactor *inside the customer's environment* and export only redacted output. The architecture is the compliance argument: "PII never crosses the boundary; here is the code; here are its self-tests" is a meeting that goes well. A redactor you run on your side after the data already crossed is theater.
- Recall failures are the incidents; precision failures are the annoyances. One SSN missed because the customer's export uses `123 45 6789` (spaces, not dashes) is a breach conversation. Before trusting any pattern set, sample real data and *hunt for the format you didn't anticipate* — every enterprise has one. Then add a leak-scan step: run detection (not replacement) over your own redacted output as a tripwire.
- Free-text names are the honest gap in a regex-only redactor. "Jane" in the test ticket survives — sometimes acceptable (first names in tickets may be fine under the DPA), sometimes not. Say the limitation out loud to the DPO and decide *with* them; discovered limitations are incidents, disclosed limitations are scope.
- The vault needs governance before it needs code: where it's stored (their tenant, encrypted), who can restore (named roles), and whether restore events are audit-logged (Lesson 06 — yes). A pseudonymization vault that anyone can read is just PII with extra steps — under GDPR, pseudonymized data with an accessible key is still personal data.

## INTERVIEW ANGLE

Redaction questions test the exact intersection FDE roles live at: enough engineering to build the thing, enough compliance literacy to deploy it defensibly. The Phase 10 drill "redact the dataset, keep it useful" is a recurring take-home archetype.

Sample questions:

1. "The customer says you can't use production data for your demo. What do you do?" (Best answers offer the ladder: synthetic data, or in-tenant pseudonymization with consistent tokens — and explain why consistency preserves analytical utility.)
2. "How do you avoid redacting order numbers that look like credit cards?" (Semantic validation behind the pattern — Luhn — plus known-ID-format allowlists; pattern proposes, checksum disposes.)
3. "Is pseudonymized data still personal data? Does it matter where the mapping lives?" (Yes under GDPR if re-identification is possible; vault custody, access control, and audit define the real risk posture.)

## DRILL

1. **Extend:** canonicalize phones before tokenization — strip to digits (with country-code handling) so `555-867-5309` and `(555) 867-5309` become the *same* token. Key `seen` on the canonical form but vault the first-seen original. Update the two-token assertion to expect one, and keep round-trip passing (what does "round trip" even mean once two source spellings share a token? Decide and document).
2. **Break:** feed the redactor `"card 4539-1488-0343-6467."` (dashes, trailing period) and `"SSN: 123456789"` (no dashes). Which leaks? Write the failing leak-scan assertion first, then fix the patterns without breaking the order-number survival test.
3. **Fix:** `restore` does naive sequential string replacement — construct a pathological case where an original value itself contains text shaped like a token (a ticket that literally discusses `[EMAIL_1]`), making restore ambiguous. Fix by making token syntax collision-proof (e.g., include a random run ID: `[EMAIL_1_x7f3]`) and assert idempotency and round-trip still hold.
