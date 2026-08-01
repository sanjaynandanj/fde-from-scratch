# CSV to Working API in One File: stdlib http.server, Zero Deps

Phase 2 · Lesson 01 · ~2h

## PROBLEM

Tuesday, 4:05pm. The ops director finally emails you the export she's been promising for a week: `orders_export.csv`, dumped from a system whose vendor went out of business in 2014. The VP demo is tomorrow at 9am, and the promise your account exec made — before you were in the room — is "you'll see your orders in our platform." You're on the customer's guest Wi-Fi, on a loaner laptop where the request to install anything routes through an IT queue with a four-day SLA. `pip install fastapi` is not happening. `docker` is not installed. What you have is a Python interpreter and sixteen hours, eight of which you'd like to sleep.

The FDE who freezes here — "I can't build an API without my stack" — loses the demo. The FDE who knows the stdlib ships a queryable JSON API from one file before dinner, and spends the evening rehearsing the demo instead. This lesson is that file.

## INTUITION

The design space for "serve this CSV as an API by tomorrow" has three axes:

**Where does the data live?** Options: leave it as CSV and parse per-request (slow, but fine at 6 rows), load into memory once (right answer for pilots under ~1M rows), or load into SQLite (Phase 2 Lesson 04 — the right answer once you need filtering the customer will invent live). For a demo, in-memory wins: zero I/O in the request path, zero schema ceremony.

**What's the serving layer?** A framework buys you routing, validation, and docs — at the cost of a dependency you may not be allowed to install. Python's `http.server` buys you a working HTTP server in the standard library. Its reputation ("not for production") is deserved *for production*; for a pilot demo behind a customer's firewall serving one VP, `ThreadingHTTPServer` is exactly enough. Knowing when "not for production" doesn't apply to you is a core FDE judgment.

**Where does cleaning happen?** The export will have `NORTH`, `north`, and `North` in the same column — real exports always do. You can clean at load time (one pass, consistent forever after) or at query time (per-request, easy to forget in one code path). Clean at load. The API should serve *normalized* data so that the filter `?region=north` matches all three spellings, because the VP will type one of them tomorrow and it had better work.

One more decision that separates field code from tutorial code: **the file tests itself.** You will not have time tomorrow morning to click through endpoints manually. The script spins up its own server on a random port, hits it with `urllib`, and asserts every response. `python lesson.py` green means the demo path works.

## BUILD IT

Open `code/lesson.py` and run it: `python lesson.py`. Walk through it top to bottom.

**The data is embedded and hostile on purpose.** `RAW_EXPORT` is six order rows with the chaos pre-installed — `NORTH`, `south`, `North`, `East`, `SHIPPED`, `pending` — so the normalization has something to prove.

**Load and normalize once.** `load_records` does the single cleaning pass:

```python
records.append({
    "order_id": int(row["order_id"]),
    "customer": row["customer"].strip(),
    "region": row["region"].strip().lower(),      # normalize the chaos
    "status": row["status"].strip().lower(),
    "amount": float(row["amount"]),
})
```

Note the type coercions happen here too — `order_id` becomes `int`, `amount` becomes `float` — so every downstream consumer gets typed data, not strings. `csv.DictReader` over `io.StringIO` means the same function works whether the CSV arrives as a string, a file, or a paste from an email.

**Aggregation is a plain function, not an endpoint feature.** `summarize` folds the records into the numbers a VP actually asks for — count, total, and a breakdown:

```python
by_status[r["status"]] = round(by_status.get(r["status"], 0) + r["amount"], 2)
```

Keeping it a pure function of `records` means you can unit-test it without HTTP and reuse it in tomorrow's inevitable "can you email me just the numbers" request.

**The handler is a router with one JSON helper.** The `Api` class subclasses `BaseHTTPRequestHandler`; records hang off the class (`Api.records`) because `http.server` instantiates a fresh handler per request. `do_GET` parses the path and query string with `urlparse`/`parse_qs` and supports composable filters:

```python
if "status" in qs:
    data = [r for r in data if r["status"] == qs["status"][0]]
if "region" in qs:
    data = [r for r in data if r["region"] == qs["region"][0]]
```

List comprehensions as a query engine — at pilot scale, this *is* the query engine, and it's debuggable at 8:55am in front of the VP. The `_json` helper centralizes status code, `Content-Type`, `Content-Length`, and encoding so no endpoint can get framing wrong. Unknown paths get a JSON 404, not a stack trace, because the customer's IT person will absolutely poke `/admin`. `log_message` is overridden to silence per-request stderr noise during the demo.

**The self-test is the demo rehearsal.** `main` binds to port 0 — the OS picks a free port, so the test never collides with whatever else is running on the loaner laptop:

```python
server = ThreadingHTTPServer(("127.0.0.1", 0), Api)
threading.Thread(target=server.serve_forever, daemon=True).start()
```

`ThreadingHTTPServer` matters even here: the test client and server share a process, and a single-threaded server can deadlock serving yourself. Then five assertions walk the exact demo script: all records; `?status=shipped` returns 3 — proving case normalization merged `SHIPPED`/`shipped` (`assert len(body) == 3, "case-normalization must merge SHIPPED/shipped"`); a *combined* filter `?region=north&status=pending` isolates order 1005; `/summary` returns to-the-cent totals (`5080.84`); and `/nope` 404s. If any line of tomorrow's demo can fail, it fails tonight, on your screen, with a message.

Total: ~118 lines, zero imports outside the standard library, one command to prove it works.

## FIELD NOTES

- The real export will be worse than `RAW_EXPORT`: BOM characters, semicolon delimiters, a disclaimer row above the header, amounts like `"1.250,50"`. Phase 3 is the survival kit; the architecture here — clean at load, serve normalized — doesn't change.
- Bind to `127.0.0.1` until you *decide* otherwise. The moment you bind `0.0.0.0` on a customer network, you've "deployed software" in the eyes of their security team, and that's a conversation (Phase 4), not an accident.
- This file is *labeled throwaway* (Phase 2 Lesson 05). Say so out loud in the demo: "this is a one-day prototype against your real export — production gets auth, a real database, and your SSO." That sentence builds trust and pre-sells the re-architecture conversation.
- The move that wins the room is not the API — it's that the filters work on *their* data, with *their* region names, live, taking requests from the audience. Rehearse taking a filter suggestion you haven't tested.

## INTERVIEW ANGLE

Rapid-prototyping rounds at FDE loops are practical: "here's a CSV, stand up an API" is a real take-home and a real live-coding prompt at multiple companies. Interviewers watch for stdlib fluency, load-time normalization, and whether you test what you built.

Sample questions:

1. "Without any frameworks, how would you serve a CSV as a JSON API in Python? What breaks first as it grows?" (Expected: `http.server` + in-memory records; first breaks are query flexibility → SQLite, then auth, then concurrency.)
2. "Your demo API filters on `status`, and the customer's data has `SHIPPED`, `Shipped`, and `shipped `. Where do you fix that and why?" (Load-time normalization; fixing at query time forgets a code path, fixing in the source data isn't yours to do — yet.)
3. "How do you make sure a demo you built at midnight works at 9am?" (Self-testing script exercising the exact demo path; assertion messages that diagnose, not just fail.)

## DRILL

1. **Extend:** add a `/customers` endpoint that returns per-customer order count and total amount, with an assertion that Acme Corp shows 2 orders totaling 1660.60. Then add an `amount_gte` query param — note how the "query engine" starts wanting SQLite.
2. **Break:** append a row with amount `"1,250.50"` (comma) to `RAW_EXPORT` and run. Watch where it dies. Fix `load_records` to survive it, and add the row to the assertions.
3. **Fix:** the API returns filtered lists but no count metadata. Change `/records` to return `{"count": N, "records": [...]}` — then fix every assertion the change breaks. Feel the cost of changing a response shape *after* clients exist; that's why Phase 4 Lesson 10 talks about versioning even pilots.
