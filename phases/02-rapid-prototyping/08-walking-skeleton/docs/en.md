# The Walking Skeleton: End-to-End Thin Slice First

**Phase 2 · Lesson 08 · ~1.5h**

## PROBLEM

An FDE at a logistics company spends her first two weeks building the "ingestion layer." It parses their four export formats, handles the encoding disasters, resolves entities across three subsidiaries. She's proud of it. It's genuinely good code. Week three she starts on the API. Week four she starts on the dashboard. Week five, at her first real demo, she realizes the metric her champion actually cares about — on-time delivery rate — requires joining two data sources she never wired together. Two weeks of ingestion work needs rearchitecting. The demo is a slideshow.

The other FDE on the engagement, on day *four*, had a working URL that showed one number (on-time rate for one region, hardcoded to the last week), computed by a five-line function reading one CSV. It looked laughable. But by week two he was iterating on the number the champion cared about, and by week five the pipeline behind it had grown into the real one — because he'd shaped it from the demo backwards.

## INTUITION

The walking skeleton — Alistair Cockburn's term, adopted by every good FDE — is an end-to-end system that does the thinnest possible version of the whole workflow. Ingest one file, one field. Store one row. Serve one endpoint. Render one number. It has no features. It has *shape.*

Why it wins on pilots:

- **The customer sees something real by end of week one.** Even one number, live, beats a beautiful architecture diagram.
- **You discover integration pain early.** The pain always lives at the seams. A skeleton reveals every seam on day three.
- **You shape the pipeline toward the metric that matters.** Bottom-up architecture optimizes for wrong things because you haven't met the number yet.
- **You get feedback while it's cheap.** The champion sees the skeleton and says "actually the number should be per-region, not global." Cost of pivot: one hour. Same feedback three weeks later: rewrite.

The design space of "how thin":

- **Bone-thin.** Hardcoded input, hardcoded computation, hardcoded output. Just proves the wire runs. Ship day 1.
- **Loaded skeleton.** Real input file (one), real computation for one metric, real UI showing that metric. Ship day 3-5.
- **Wobbly walker.** Real ingestion pipeline, real DB, real API, real UI — but one metric, one source. Ship end of week 1.
- **Standing product.** Multiple metrics, multiple sources, real auth. This is the pilot at week 4-6, not week 1.

The FDE mistake is starting at "standing product" and building bottom-up. The right start is bone-thin *before* the first customer meeting and wobbly-walker by the end of week 1.

## BUILD IT

The skeleton as a checklist. Every pilot starts with this list. Every item is deliberately trivial.

```
WALKING SKELETON CHECKLIST — target: end of day 3
[ ] 1. One input file lives in the repo (real customer sample or seeded).
[ ] 2. One Python script reads it, computes one number.
[ ] 3. One HTTP endpoint (stdlib http.server) returns that number as JSON.
[ ] 4. One HTML page fetches that endpoint and displays the number.
[ ] 5. The number displayed is the one your champion mentioned first
      in discovery (or your best guess if you haven't asked yet).
[ ] 6. `python run.py` starts everything with no config.
[ ] 7. There is a README that says: what number, what source, what to run.
[ ] 8. It runs on the FDE's laptop AND on the customer sandbox.
```

The template — 40 lines, one file:

```python
# STATUS: keepable — pilot skeleton for OTR (on-time rate)
import csv, json, http.server, socketserver, pathlib

DATA = pathlib.Path("data/deliveries_sample.csv")

def compute_otr():
    total, on_time = 0, 0
    with DATA.open() as f:
        for row in csv.DictReader(f):
            total += 1
            if row["status"] == "on_time":
                on_time += 1
    return {"metric": "on_time_rate",
            "value": round(on_time / total, 4) if total else 0.0,
            "n": total, "source": str(DATA)}

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/otr":
            body = json.dumps(compute_otr()).encode()
            self.send_response(200); self.send_header("content-type", "application/json")
            self.end_headers(); self.wfile.write(body); return
        if self.path == "/":
            self.send_response(200); self.send_header("content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""<!doctype html><meta charset=utf-8>
              <h1>On-Time Rate</h1><div id=n>...</div>
              <script>fetch('/api/otr').then(r=>r.json()).then(d=>
                document.getElementById('n').textContent =
                (d.value*100).toFixed(1) + '% (n=' + d.n + ')');</script>""")
            return
        self.send_response(404); self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", 8000), H) as s:
        print("http://localhost:8000"); s.serve_forever()
```

That's it. Ship it. Now grow.

**Growth discipline:** every next feature — a second metric, a real ingestion pipeline, a database — should keep the skeleton *walking* the whole time. Never have a state where "the ingestion works but the UI is down for the week." That's a coma, not a skeleton.

## FIELD NOTES

- The champion often doesn't know what number matters most until they see one displayed. The skeleton is a way to *elicit* that answer, not just serve it.
- Resist the urge to make the skeleton pretty on day 3. Fifty percent of skeletons never survive to week 2 because the metric changes; the ugly one is easier to rewrite.
- The `python run.py` rule is load-bearing. If setup takes more than one command, the customer's engineer can't reproduce it, and neither can you at 2am from a hotel.
- When you demo a skeleton, name it: "this is the walking skeleton — real data, one metric, so we can iterate on the number, not the plumbing." Champions who understand the concept become allies against scope creep.
- The skeleton is also your rollback point. If a week goes badly, you can always demo the skeleton — it always works.

## INTERVIEW ANGLE

Interviewers probe whether you build top-down from a metric or bottom-up from architecture. FDE loops strongly reward top-down.

Sample questions:

1. "You've got two weeks and a customer expecting a demo. Walk me through what you build in what order." (Testing: walking skeleton end-to-end in days, iterate on metric.)
2. "Why not build the ingestion layer first?" (Testing: integration pain lives at seams; without the seam you don't find it; you also don't know which fields the metric needs.)
3. "How do you decide which metric to hardcode into the skeleton?" (Testing: the one the champion mentioned first, or the one the renewal will hinge on. Not the easiest to compute.)

## DRILL

Take a dataset you have — any CSV. Pick one metric a hypothetical champion would care about. Build the skeleton above: one CSV, one number, one endpoint, one HTML page, one `run.py`. Time yourself. Anything over 90 minutes means you over-engineered — start over. Then hand the code to a colleague and see if they can start it with one command. If not, fix the setup, not the code. Save this template; you will start every pilot with it.
