"""FLAGSHIP - Incremental sync: watermarks, idempotent upserts, late arrivals.

Full re-loads die the day the table hits 10M rows. Sync incrementally:
track a watermark (max updated_at seen), pull only newer rows, upsert
idempotently, and survive the two classic traps - late-arriving rows with
old timestamps, and the same batch delivered twice.
"""


class SourceSystem:
    """The customer's system of record. You only get to query it."""

    def __init__(self):
        self.rows: dict[str, dict] = {}

    def write(self, key: str, value: str, updated_at: int):
        self.rows[key] = {"key": key, "value": value, "updated_at": updated_at}

    def query_since(self, watermark: int) -> list[dict]:
        return sorted((r for r in self.rows.values() if r["updated_at"] > watermark),
                      key=lambda r: r["updated_at"])


class SyncEngine:
    def __init__(self, source: SourceSystem):
        self.source = source
        self.target: dict[str, dict] = {}
        self.watermark = 0
        self.stats = {"pulled": 0, "applied": 0, "skipped": 0}

    def run(self, lag: int = 0) -> dict:
        """lag: re-read a window behind the watermark to catch late arrivals."""
        batch = self.source.query_since(self.watermark - lag)
        run_stats = {"pulled": len(batch), "applied": 0, "skipped": 0}
        for row in batch:
            existing = self.target.get(row["key"])
            if existing and existing["updated_at"] >= row["updated_at"]:
                run_stats["skipped"] += 1          # idempotency: replays are no-ops
            else:
                self.target[row["key"]] = dict(row)
                run_stats["applied"] += 1
            self.watermark = max(self.watermark, row["updated_at"])
        for k in run_stats:
            self.stats[k] += run_stats[k]
        return run_stats


def main():
    src = SourceSystem()
    src.write("A", "alpha-1", 100)
    src.write("B", "beta-1", 105)
    src.write("C", "gamma-1", 110)

    sync = SyncEngine(src)

    # Run 1: initial load
    r1 = sync.run()
    assert r1 == {"pulled": 3, "applied": 3, "skipped": 0}
    assert sync.watermark == 110

    # Run 2: nothing changed -> nothing pulled
    r2 = sync.run()
    assert r2 == {"pulled": 0, "applied": 0, "skipped": 0}

    # Run 3: one update, one insert
    src.write("B", "beta-2", 120)
    src.write("D", "delta-1", 125)
    r3 = sync.run()
    assert r3 == {"pulled": 2, "applied": 2, "skipped": 0}
    assert sync.target["B"]["value"] == "beta-2"
    assert sync.watermark == 125

    # Trap 1: late-arriving row with timestamp BELOW the watermark.
    # A plain watermark query misses it forever; a lag window catches it.
    src.write("E", "epsilon-1", 118)
    r4 = sync.run()
    assert r4["pulled"] == 0, "plain watermark provably misses the late row"
    r5 = sync.run(lag=10)
    assert r5["applied"] == 1 and "E" in sync.target, "lag window must recover it"

    # Trap 2: replayed batch (source resends everything > 100) must be a no-op
    r6 = sync.run(lag=30)
    assert r6["applied"] == 0 and r6["skipped"] == r6["pulled"] > 0
    assert sync.target["B"]["value"] == "beta-2", "replay must not clobber newer data"

    assert len(sync.target) == 5
    print(f"incremental-sync: all assertions passed "
          f"(6 runs, {sync.stats['pulled']} pulled, {sync.stats['applied']} applied)")


if __name__ == "__main__":
    main()
