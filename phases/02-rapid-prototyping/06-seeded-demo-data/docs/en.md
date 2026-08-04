# Seeded Demo Data: Realistic, Impressive, and Safe

**Phase 2 · Lesson 06 · ~1.5h**

## PROBLEM

An FDE walks into a Thursday demo with the customer's CFO. He has real data — pulled Tuesday from their sandbox — piped into his dashboard. The demo starts. The CFO sees the top row. The top row is one of her direct reports' salary. The dashboard sorts descending by amount. Behind that row is her own compensation and the CEO's. The demo ends in ninety seconds. Legal calls the FDE's manager that afternoon. Whether it was technically a violation of the DPA becomes a two-week discussion.

Meanwhile, three cubicles over, another FDE demos a similar workflow — same schema, same shapes, same distribution — with data she generated the night before. Everyone in the room leans forward. Nobody's HR file is on screen. The champion asks if she can forward the demo to her VP.

Seeded data isn't a shortcut. It's the safe, better version of the demo.

## INTUITION

Demo data has three jobs: (1) prove the workflow on realistic shapes, (2) be *impressive* — the numbers should be interesting, not uniformly boring, (3) be safe to show to any human in the room. Real customer data optimizes for (1) at severe cost to (3) and often (2) — real data is boring in the middle 90% of rows.

The design space:

- **Real data, unmodified.** Highest realism, highest risk. Reserve for closed-door workshops after DPAs are signed and the audience is scoped.
- **Real data, redacted.** Names hashed, IDs perturbed. Reduces risk but doesn't eliminate re-identification. Still needs the DPA question answered.
- **Real data, resampled.** Real distributions, real value ranges, synthetic entities. Best of both worlds when done well. The most work.
- **Fully synthetic, hand-tuned.** Made-up entities, distributions matched to what you observed. Zero risk. The FDE default for external demos.
- **Fully synthetic, uniform-random.** Fastest to generate, obviously fake, undermines the demo. Avoid.

The realism dimensions you must match:

- **Shape.** Row counts, column counts, cardinalities. If the customer has 12,000 vendors, seed 12,000, not 50.
- **Distribution.** Long tails matter. If 80% of spend is with 20 vendors, seed it that way.
- **Nulls, dupes, and messiness.** Real data has 3% missing tax IDs and 60 typo variants of "Amazon Web Services." Seed those in, or the demo will look too clean and the champion will discount it.
- **Named anchors.** Include 5–10 recognizable entity names ("Acme Corp," "Metropolitan Bank") so screenshots read as demos, not as spreadsheets.

## BUILD IT

A deterministic seeder in stdlib Python. Reproducible (same seed → same data) so the demo is repeatable.

```python
import random, csv, hashlib
from datetime import date, timedelta

def seeded(seed=42):
    rng = random.Random(seed)
    vendors = _long_tail_vendors(rng, n=12000, hot=20, hot_share=0.8)
    rows = []
    start = date(2025, 1, 1)
    for i in range(180_000):
        v = _weighted_pick(rng, vendors)
        amt = round(rng.lognormvariate(6.5, 1.2), 2)     # realistic spend
        d = start + timedelta(days=rng.randint(0, 300))
        row = {
            "id": f"INV-{i:07d}",
            "vendor": v if rng.random() > 0.03 else _typo(rng, v),  # 3% typos
            "amount": amt,
            "tax_id": _tax_id(rng) if rng.random() > 0.04 else "",  # 4% missing
            "issued": d.isoformat(),
        }
        rows.append(row)
    return rows

def _long_tail_vendors(rng, n, hot, hot_share):
    names = ["Acme Corp", "Metropolitan Bank", "Northwind Logistics",
             "Globex Industries", "Initech Systems"] + [f"Vendor {i:05d}"
             for i in range(n - 5)]
    weights = [hot_share / hot] * hot + [(1 - hot_share) / (n - hot)] * (n - hot)
    return list(zip(names[:n], weights[:n]))

def _weighted_pick(rng, items):
    r, cum = rng.random(), 0.0
    for name, w in items:
        cum += w
        if r <= cum: return name
    return items[-1][0]

def _typo(rng, s):
    if len(s) < 4: return s + "."
    i = rng.randint(0, len(s) - 2)
    return s[:i] + s[i+1] + s[i] + s[i+2:]   # transpose

def _tax_id(rng):
    return f"{rng.randint(10, 99)}-{rng.randint(1000000, 9999999)}"

if __name__ == "__main__":
    rows = seeded()
    with open("throwaway/demo_invoices.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"wrote {len(rows)} rows")
```

Design notes:

- **Seed the RNG.** A named seed means Tuesday's dry run and Thursday's demo see the same anomalies. When you say "look at Acme Corp on row 47," row 47 is Acme Corp.
- **Hand-place named anchors.** Real vendors are boring. Fake ones with recognizable names carry the narrative.
- **Match the messiness.** Typos, missing tax IDs, wrong dates — enough to make the "we clean this up" story land.
- **Live in `throwaway/`.** Under version control, but clearly labeled. Never commits into the same table as real data.

## FIELD NOTES

- The customer will ask "is this our data?" Answer directly: "no, this is synthetic data with your distributions — 12k vendors, ~180k invoices, matched to what we saw in your Q3 export." Naming the shape earns trust; hiding it destroys it.
- Once you have a working seeder, generate three datasets: `small` (dev, <1s to load), `demo` (Thursday's slice, 5k rows, hand-tuned anomalies), `full` (matches production shape). Different scripts for different jobs.
- Never seed data that resembles a real, named human. "John Smith" is fine; "Jane Chen, VP Finance" — the actual VP Finance's name — is not. Keep an anti-list of your customer's real employee names and check against it.
- Save the seeded CSV as a fixture and commit it. The demo should not depend on regenerating during the meeting.
- The moment you switch a demo from seeded to real data, get a written go-ahead from your champion and log it. Don't do it silently.

## INTERVIEW ANGLE

Interviewers probe whether you know demo data is a discipline, not laziness.

Sample questions:

1. "Your demo is in 6 hours; you don't have clean access to their real data. What do you do?" (Testing: seed to their shape, hand-place anchors, deterministic. Not "wait for the data.")
2. "How do you make synthetic data feel real?" (Testing: long-tail distributions, realistic messiness, named anchors, matched cardinalities.)
3. "What's the risk of demoing real customer data internally?" (Testing: DPA scope, re-identification risk, salary/PII leakage, the CFO-in-the-room scenario.)

## DRILL

Take a CSV from any dataset you can find. Profile it: row count, column cardinalities, null rates, top values in each column. Write a seeder that reproduces those shapes without copying any real values. Hand-place five recognizable named anchors. Compare a histogram of your synthetic amounts to the real ones — if they don't overlap visually, tune your distribution. Save the seeder in `throwaway/`; you'll reuse the pattern in every pilot.
