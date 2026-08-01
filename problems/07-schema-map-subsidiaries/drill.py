"""DRILL 07 - Schema-map four subsidiaries into one canonical model. Difficulty: 3/3

The group acquired three companies. Four billing systems, four schemas,
one board report due Friday. Map every source into the canonical schema:

    {customer, country, amount_usd, invoice_date (ISO), source}

Wrinkles seeded in the data: German decimal commas, EUR->USD conversion,
cents-as-integers, country codes vs names, and one source nesting the
customer under "account.holder".
"""

FX = {"EUR": 1.10, "USD": 1.0, "GBP": 1.27}

SOURCE_A = [  # US parent: clean-ish
    {"customer": "Acme Corp", "country": "US", "amount": 1200.00,
     "currency": "USD", "date": "2024-03-01"},
]
SOURCE_B = [  # German subsidiary: decimal commas, EUR, DD.MM.YYYY
    {"kunde": "Müller GmbH", "land": "Germany", "betrag": "1.250,50",
     "datum": "05.03.2024"},
]
SOURCE_C = [  # UK subsidiary: cents-as-integer (pence), GBP
    {"cust_name": "Thames Ltd", "cc": "GB", "amount_pence": 99000,
     "invoice_dt": "2024-03-07"},
]
SOURCE_D = [  # SaaS billing tool: nested JSON
    {"account": {"holder": "Nordic AS", "region": "NO"},
     "charge": {"value": 800.0, "unit": "USD"}, "ts": "2024-03-09T14:22:00Z"},
]

COUNTRY = {"US": "US", "Germany": "DE", "GB": "GB", "NO": "NO"}


# ----------------------------- reference solution -----------------------------
def to_usd(amount: float, currency: str) -> float:
    return round(amount * FX[currency], 2)


def solve() -> list[dict]:
    rows = []
    for r in SOURCE_A:
        rows.append({"customer": r["customer"], "country": COUNTRY[r["country"]],
                     "amount_usd": to_usd(r["amount"], r["currency"]),
                     "invoice_date": r["date"], "source": "A"})
    for r in SOURCE_B:
        amount = float(r["betrag"].replace(".", "").replace(",", "."))
        d, m, y = r["datum"].split(".")
        rows.append({"customer": r["kunde"], "country": COUNTRY[r["land"]],
                     "amount_usd": to_usd(amount, "EUR"),
                     "invoice_date": f"{y}-{m}-{d}", "source": "B"})
    for r in SOURCE_C:
        rows.append({"customer": r["cust_name"], "country": COUNTRY[r["cc"]],
                     "amount_usd": to_usd(r["amount_pence"] / 100, "GBP"),
                     "invoice_date": r["invoice_dt"], "source": "C"})
    for r in SOURCE_D:
        rows.append({"customer": r["account"]["holder"],
                     "country": COUNTRY[r["account"]["region"]],
                     "amount_usd": to_usd(r["charge"]["value"], r["charge"]["unit"]),
                     "invoice_date": r["ts"][:10], "source": "D"})
    return rows
# -------------------------------------------------------------------------------


def main():
    rows = {r["source"]: r for r in solve()}
    assert len(rows) == 4
    assert rows["A"]["amount_usd"] == 1200.00
    assert rows["B"] == {"customer": "Müller GmbH", "country": "DE",
                         "amount_usd": 1375.55, "invoice_date": "2024-03-05", "source": "B"}
    assert rows["C"]["amount_usd"] == 1257.30, "pence -> GBP -> USD"
    assert rows["D"]["customer"] == "Nordic AS" and rows["D"]["invoice_date"] == "2024-03-09"
    assert all(len(r["country"]) == 2 for r in rows.values()), "ISO-3166 alpha-2 everywhere"
    total = round(sum(r["amount_usd"] for r in rows.values()), 2)
    assert total == 4632.85
    print(f"drill-07: all checks passed (board number: ${total:,.2f})")


if __name__ == "__main__":
    main()
