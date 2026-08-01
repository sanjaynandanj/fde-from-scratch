# Incremental Sync: Change Detection, Watermarks, Idempotent Upserts

Phase 3 · Lesson 08 · ~2h

## PROBLEM

The pilot's nightly load worked beautifully in month one: truncate the target, re-pull all 800k order rows from the customer's ERP, rebuild. Then the scope grew to order *lines* — 40M rows — and the full re-load started taking six hours. The customer's DBA noticed the nightly full-table scan hammering the production replica and revoked the service account "pending review." Meanwhile, the ops team started asking why a shipment updated at 4pm shows stale data at 9am — the load hadn't finished. The fix everyone reaches for — "just pull the rows that changed" — sounds trivial and hides three traps that have each, independently, corrupted real pilots: rows that change *while* you're reading, rows whose timestamps arrive late, and batches that get delivered twice.

Incremental sync done naively is worse than full re-load, because full re-load is at least *self-healing* — every night wipes yesterday's mistakes. Incremental sync accumulates them forever. This lesson builds the engine that doesn't.

## INTUITION

The design space has three independent decisions:

**Change detection — how do you know what changed?** Options in ascending order of invasiveness: an `updated_at` timestamp column you can filter on (the field default — almost every enterprise table has one, of variable trustworthiness); a version/sequence number (better, monotonic by construction); log-based CDC reading the database's transaction log (gold standard, but requires DBA cooperation you won't get in a pilot); or diffing full snapshots (when the source offers nothing — expensive but honest). Pilots almost always start with the timestamp column, so this lesson does too, *including its failure mode*.

**The watermark — where did I leave off?** Store the max `updated_at` you've seen; next run, ask for rows strictly newer. The watermark is state, and state invites the classic questions: what if the run crashes mid-batch (answer: advance the watermark only from rows you actually processed), and — the killer — what if a row *commits late* with an `updated_at` earlier than your watermark? That happens constantly in real systems: a long-running transaction stamps `updated_at` at its start, commits after your extract ran, and now a 4:58pm row lands after your 5:00pm pull already moved the watermark to 5:01. A plain watermark query misses that row *forever*. The standard field mitigation is the **lag window**: re-read a margin behind the watermark every run and rely on idempotency to make the overlap harmless.

**The write — what happens on replay?** The lag window and every real-world retry mean you *will* process the same row twice. The target write must be an idempotent upsert: applying the same change twice equals applying it once, and — subtler — applying an *old* version after a newer one must be a no-op. Compare timestamps on write; never blind-overwrite. Once writes are idempotent, a whole class of delivery problems (source resends, crash-retry, overlapping windows) collapses from "corruption" to "some skipped rows in the stats."

The deep principle: **at-least-once delivery + idempotent apply = effectively-exactly-once.** You cannot get exactly-once delivery from a timestamp poll; you *can* make duplicates free.

## BUILD IT

Run it: `python code/lesson.py`. Ninety lines, two classes, six sync runs that walk straight into both traps.

**`SourceSystem` models the constraint you actually live under.** It's the customer's system of record — you don't control writes, you only get to query:

```python
def query_since(self, watermark: int) -> list[dict]:
    return sorted((r for r in self.rows.values() if r["updated_at"] > watermark),
                  key=lambda r: r["updated_at"])
```

Strictly-greater-than filtering on `updated_at`, sorted ascending — exactly the `WHERE updated_at > :wm ORDER BY updated_at` you'd run against their replica.

**`SyncEngine.run` is the whole algorithm.** Pull, then per-row upsert with a timestamp guard:

```python
def run(self, lag: int = 0) -> dict:
    """lag: re-read a window behind the watermark to catch late arrivals."""
    batch = self.source.query_since(self.watermark - lag)
    ...
    for row in batch:
        existing = self.target.get(row["key"])
        if existing and existing["updated_at"] >= row["updated_at"]:
            run_stats["skipped"] += 1          # idempotency: replays are no-ops
        else:
            self.target[row["key"]] = dict(row)
            run_stats["applied"] += 1
        self.watermark = max(self.watermark, row["updated_at"])
```

Four decisions worth naming. (1) The guard is `>=`, not `>`: seeing the *same* version again is a skip, and an older version can never clobber a newer one. (2) `dict(row)` copies — storing a reference into someone else's mutable row is how "the source changed and my target changed with it, silently" bugs are born. (3) The watermark advances via `max(...)` per processed row, not `batch[-1]` — so a lag-window re-read of old rows can never *regress* the watermark. (4) Every run returns `{"pulled", "applied", "skipped"}`, and the engine accumulates lifetime stats — these counters are your observability; in production they're the numbers on the pilot dashboard that let you *see* a replay or a drought.

**The test is six runs that tell the whole story.** Runs 1–3 are the happy path: initial load (3 pulled, 3 applied, watermark 110), an empty run proving quiescence costs nothing, then an update+insert batch that bumps `B` to `beta-2`. Then the traps:

```python
# Trap 1: late-arriving row with timestamp BELOW the watermark.
src.write("E", "epsilon-1", 118)          # watermark is already 125
r4 = sync.run()
assert r4["pulled"] == 0, "plain watermark provably misses the late row"
r5 = sync.run(lag=10)
assert r5["applied"] == 1 and "E" in sync.target, "lag window must recover it"
```

Run 4 *proves the failure* — the assertion documents that a plain watermark misses `E` forever — and run 5 proves the cure: `lag=10` re-reads back to 115 and recovers it. Run 6 is Trap 2: a huge `lag=30` replays essentially everything since 100, and the assertions demand `applied == 0`, `skipped == pulled > 0`, and — the line that matters most — `sync.target["B"]["value"] == "beta-2"`: the replay carried the *old* `beta-1` row past the upsert guard and the guard held. Replay is a no-op, not a corruption.

Note what the lag window costs: run 6 pulled rows it didn't need. Lag size is a dial — big enough to cover your source's worst commit skew, small enough not to re-read the world. That trade-off is a *number you negotiate with reality*, usually by measuring the source's actual late-arrival distribution for a week.

## FIELD NOTES

- The `updated_at` column will lie to you in at least one of these ways: it's app-maintained and some batch job skips it; it's a `DATE` with no time part; it's local time with DST jumps; deletes don't touch it at all. Ask early: "what updates this column, and does *every* write path do it?" The answer is always more interesting than the schema.
- **Deletes are the silent killer.** A deleted source row simply stops appearing in `query_since` — your target keeps it forever. You need soft-delete flags, a periodic full-key reconciliation sweep, or CDC. Budget for this in week one, because the customer *will* find the ghost row during UAT.
- Never trust the clock that stamps rows to agree with the clock that runs your sync. Watermark on the *source's* values only (as this engine does — it advances from row timestamps, never `now()`), or clock skew will open a permanent blind spot.
- The full re-load isn't dead — keep it as the weekly self-healing backstop and the backfill path. Incremental for freshness, periodic full reconciliation for truth; Lesson 11 (reconciliation) is the proof layer on top.

## INTERVIEW ANGLE

Sync design is a staple of FDE system-design rounds because it's small enough to whiteboard and deep enough to expose whether you've operated real pipelines. "Design a connector that keeps our copy of the customer's table fresh" is a near-verbatim prompt.

Sample questions:

1. "You're syncing a table using an `updated_at` watermark. What breaks?" (Late-arriving commits below the watermark, untracked deletes, clock/timezone skew, crash mid-batch. The lag-window + idempotent-upsert answer, plus periodic reconciliation, is the complete response.)
2. "The source resends yesterday's entire batch. What must be true of your system for this to be safe?" (Idempotent apply with a version/timestamp guard; at-least-once + idempotency = effectively exactly-once.)
3. "How would you detect that your sync has been silently missing rows for a month?" (Row-count and checksum reconciliation against the source, freshness metrics per key, alerting on applied/pulled ratios — the stats dict, grown up.)

## DRILL

1. **Extend:** add delete handling — give `SourceSystem` a `delete(key, deleted_at)` that writes a tombstone row (`{"deleted": True}`), and make the engine remove the target key on apply. Assert that a replayed tombstone skips, and that a *late* tombstone still beats an older update.
2. **Break:** make the source stamp one row with `updated_at` in the future (say 10,000 ahead — a misconfigured app server clock). Run a normal sync, then a normal update. What happens to every subsequent pull, and which assertion should have existed to catch the watermark poisoning? Write it.
3. **Fix:** the engine advances the watermark even when a row is *skipped*, which is correct — but it also advances it row-by-row mid-batch, so a crash between rows loses nothing yet a crash between "apply" and "advance" is impossible to represent here. Refactor `run` to two-phase: process the whole batch, then persist `(watermark, target)` together, and write a simulated-crash test (process half the batch, "crash", re-run) proving no row is lost or double-applied.
