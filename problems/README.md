# Field Drills

Twelve self-checking, real-world problem sets. Each drill is one file:

```
problems/<NN>-<name>/drill.py
```

The file contains, in order:

1. **The problem statement** (module docstring) — read it, then STOP.
2. **The generator** — deterministic, seeded; produces the messy data.
3. **A `solve()` stub area** — delete the reference solution and write your own.
4. **The checks** — assertions that grade any correct solution.

Run with `python drill.py`. Python 3.10+, stdlib only.

**How to practice honestly:** run the generator, look at the data, write your
own `solve()` without reading the reference. The reference solution is there
for when you're done (or stuck for 30+ minutes — this is training, not an exam).

| # | Drill | Feeds from | Difficulty |
|---|-------|-----------|------------|
| 01 | excel-damaged-customer-master | Phase 3 L02 | ● |
| 02 | date-formats-timeline | Phase 3 L03 | ● |
| 03 | dedupe-crm | Phase 3 L05–06 | ●● |
| 04 | reconcile-erp-bank | Phase 3 L11 | ●● |
| 05 | sftp-feed-gaps | Phase 3 L09 | ●● |
| 06 | fixed-width-mainframe | Phase 3 L02 | ●● |
| 07 | schema-map-subsidiaries | Phase 3 L04 | ●●● |
| 08 | golden-set-eval | Phase 5 L06 | ●● |
| 09 | redact-dataset | Phase 6 L03 | ●● |
| 10 | seed-demo-dataset | Phase 2 L06 | ●● |
| 11 | pipeline-drift-debug | Phase 3 L12–13 | ●●● |
| 12 | end-to-end-mini-pilot | everything | ●●● |
