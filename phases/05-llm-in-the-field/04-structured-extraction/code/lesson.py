"""FLAGSHIP - Structured extraction: schemas, validation, retry-on-garbage.

"Read these invoices and fill the ERP fields." Models return almost-JSON:
markdown fences, wrong types, missing fields. The harness - schema
validation plus a bounded retry loop that feeds the error back - is what
makes extraction shippable. MockLLM scripts the classic failure sequence.
"""

import json
import re

SCHEMA = {
    "invoice_id": {"type": str, "required": True},
    "vendor": {"type": str, "required": True},
    "total": {"type": float, "required": True},
    "currency": {"type": str, "required": True, "enum": ["USD", "EUR", "INR"]},
    "line_items": {"type": list, "required": False},
}


def strip_fences(raw: str) -> str:
    m = re.search(r"```(?:json)?\s*(.*?)```", raw, re.S)
    return (m.group(1) if m else raw).strip()


def validate(data: dict) -> list[str]:
    errors = []
    for field, rule in SCHEMA.items():
        if field not in data or data[field] is None:
            if rule["required"]:
                errors.append(f"missing required field '{field}'")
            continue
        value = data[field]
        if rule["type"] is float and isinstance(value, int):
            value = data[field] = float(value)
        if not isinstance(value, rule["type"]):
            errors.append(f"field '{field}' must be {rule['type'].__name__}, "
                          f"got {type(value).__name__}")
        elif "enum" in rule and value not in rule["enum"]:
            errors.append(f"field '{field}' must be one of {rule['enum']}, got '{value}'")
    for field in data:
        if field not in SCHEMA:
            errors.append(f"unknown field '{field}'")
    return errors


class MockLLM:
    def __init__(self, script: list[str]):
        self.script = list(script)
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.script.pop(0)


def extract(document: str, llm: MockLLM, max_attempts: int = 4) -> dict:
    prompt = f"Extract invoice fields as JSON matching the schema.\nDOC: {document}"
    for attempt in range(1, max_attempts + 1):
        raw = llm.complete(prompt)
        try:
            data = json.loads(strip_fences(raw))
        except json.JSONDecodeError as e:
            prompt = f"Your output was not valid JSON ({e}). Return ONLY JSON.\nDOC: {document}"
            continue
        errors = validate(data)
        if not errors:
            data["_attempts"] = attempt
            return data
        prompt = f"Fix these errors and return the full JSON again: {errors}\nDOC: {document}"
    raise ValueError(f"extraction failed after {max_attempts} attempts")


def main():
    doc = "INVOICE #INV-2207 from Globex GmbH. Total due: EUR 1,499.00"

    # The classic three-act failure: fenced prose -> wrong types -> correct
    llm = MockLLM([
        "Sure! Here is the JSON:\n```json\n{\"invoice_id\": \"INV-2207\", \"vendor\": \"Globex GmbH\"\n```",
        '{"invoice_id": "INV-2207", "vendor": "Globex GmbH", "total": "1499.00", "currency": "eur"}',
        '{"invoice_id": "INV-2207", "vendor": "Globex GmbH", "total": 1499.0, "currency": "EUR"}',
    ])
    out = extract(doc, llm)
    assert out["_attempts"] == 3
    assert out["total"] == 1499.0 and out["currency"] == "EUR"
    assert "not valid JSON" in llm.prompts[1], "attempt 2 must carry the parse error"
    assert "must be float" in llm.prompts[2] and "must be one of" in llm.prompts[2], \
        "attempt 3 must carry the validation errors"

    # happy path: int total is coerced to float, optional field accepted
    llm2 = MockLLM(['{"invoice_id": "INV-9", "vendor": "Acme", "total": 250, '
                    '"currency": "USD", "line_items": ["widget"]}'])
    out2 = extract("INVOICE #INV-9 ...", llm2)
    assert out2["_attempts"] == 1 and out2["total"] == 250.0

    # a model that never converges must raise, not loop forever
    llm3 = MockLLM(["garbage"] * 4)
    try:
        extract(doc, llm3)
        raise AssertionError("should have failed")
    except ValueError as e:
        assert "after 4 attempts" in str(e)

    # unknown-field hallucination is caught
    assert validate({"invoice_id": "X", "vendor": "V", "total": 1.0,
                     "currency": "USD", "confidence": 0.9}) == ["unknown field 'confidence'"]

    print("structured-extraction: all assertions passed (retry loop, coercion, bounded failure)")


if __name__ == "__main__":
    main()
