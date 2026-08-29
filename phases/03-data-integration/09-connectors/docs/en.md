# Connectors: SQL, REST, SFTP-with-a-Nightly-CSV, and SAP

**Phase 3 · Lesson 09 · ~1.5h**

## PROBLEM

Week two of a global-bank pilot. You've drawn the mapping table. Now you need the actual data flowing. You expected one connector — "just point at the warehouse." Instead you get four source systems, each with its own retrieval reality:

- The credit-risk data lives in an Oracle warehouse the DBA will grant you *read-only* access to, after a two-week ticket, over a jump host that terminates SSH sessions every 15 minutes.
- The customer profiles are exposed by a "modern" REST API that paginates with cursors, rate-limits at 5 req/sec, and returns 502s roughly once per thousand calls.
- The trade blotter is dropped as a gzipped CSV onto an SFTP server every night at 02:47 — usually. Sometimes 03:15. Sometimes not at all.
- The general ledger is in SAP. There is no API. There is a consulting company that will build you a BAPI wrapper for $180K and six months.

Every one of these is a "connector" in the architecture diagram. Every one has a completely different failure mode, latency profile, and political owner. If you architect them the same way, three of them break.

## INTUITION

A connector is a boundary object: your code on one side, the customer's system and its owner on the other. The design space:

**Retrieval model.** Push vs. pull. *Pull* (your code queries theirs on a schedule) is what you want; you control cadence, retry, and instrumentation. *Push* (their system drops files at you, or POSTs events) is what you often get, because their team owns the system and doesn't want you inside it. Design for both; the SFTP case is fundamentally push.

**Auth realities.** Rank order of friction, low to high: username+password in a config file (never do this but customers ask), API token, OAuth client credentials (2 hops), certificate-based mTLS (5 hops through their security team), Kerberos (only if you enjoy suffering), SAP RFC (see budget above). Learn what auth each system supports *before* the design meeting; you'll cut two weeks by picking the least-friction option the customer's security team already approves.

**Batching.** SQL wants big joins, REST wants small pages, SFTP wants whole files, SAP wants BAPI calls scoped by time window. The connector's job is to translate your uniform read requests into the source's native batching. Get this wrong and either rate limits kill you (REST) or query timeouts kill you (SQL).

**Idempotence and resumability.** Every connector fetch must be safely retryable. If a REST pull crashes at page 47 of 200, the next run resumes at 47 with the same watermark and produces the same output. If a SQL extract runs twice, it produces the same rows. Idempotence is baked into the *watermark* pattern from Lesson 08.

**The failure mode map.** For each connector: what fails, how often, how you detect it, and what the runbook says. SFTP-file-late is one row on that map; SQL-connection-drop is another. These aren't edge cases — they're the operational spec.

## BUILD IT

A connector is an interface with four methods: `describe`, `fetch`, `since`, and `health_check`. Sketch:

```python
class Connector:
    name = "..."
    def describe(self):
        """Return metadata: schema, cadence, auth type, expected latency."""
        raise NotImplementedError
    def fetch(self, since=None, until=None):
        """Yield rows. Watermarked, idempotent, resumable."""
        raise NotImplementedError
    def health_check(self):
        """Return (ok: bool, detail: str)."""
        raise NotImplementedError
```

Four sketches, one per source type:

```python
class SqlConnector(Connector):
    def fetch(self, since=None, until=None):
        # Use a keyset-paginated query on an indexed timestamp column
        cursor = self.conn.execute(
            "SELECT * FROM ledger WHERE updated_at > ? "
            "ORDER BY updated_at LIMIT 10000", (since,))
        yield from (dict(zip(cursor.column_names, row)) for row in cursor)

class RestConnector(Connector):
    def fetch(self, since=None, until=None):
        cursor = None
        while True:
            resp = self._get_with_retry("/customers",
                                       params={"since": since, "cursor": cursor})
            for row in resp["items"]:
                yield row
            cursor = resp.get("next_cursor")
            if not cursor:
                break

    def _get_with_retry(self, path, params, attempts=5):
        import time, urllib.request, urllib.parse, json
        for i in range(attempts):
            try:
                # ... urllib call ...
                return json.loads(response.read())
            except Exception:
                time.sleep(2 ** i)  # exponential backoff
        raise RuntimeError(f"{path} failed after {attempts} attempts")

class SftpConnector(Connector):
    def fetch(self, since=None, until=None):
        # Wait for the file, parse, mark as processed
        expected = f"blotter_{since:%Y%m%d}.csv.gz"
        if not self._file_exists(expected):
            raise FileNotReady(f"{expected} not present yet")
        with self._open_gzip(expected) as f:
            yield from csv.DictReader(f)

class SapConnector(Connector):
    """Reality: no direct connection. Reads a nightly extract dropped by SAP team."""
    def fetch(self, since=None, until=None):
        # Delegate to SFTP or shared-drive connector; SAP is a data producer, not an API
        return self.extract_reader.fetch(since, until)
```

Two moves are load-bearing. First, `fetch` yields rows lazily — you never load a whole extract into memory, and the caller decides when to stop. Second, every connector has `health_check`, because in production the operational question is not "did today's run succeed" but "is the *system* healthy so we can trust tomorrow." SFTP health is "file arrived by 04:00"; REST health is "GET /health returns 200"; SQL health is "SELECT 1 completes in <2s."

## FIELD NOTES

- The nightly-SFTP-CSV pattern is more common than any modern API in enterprise integration. It's ugly and it works. Build for it — including the case where the file doesn't arrive.
- REST rate limits vary by endpoint, not just by API. Salesforce's `/query` and `/composite` have different budgets. Read the docs, and build a per-endpoint token bucket.
- SAP is nearly always accessed by a third party. Do not design your architecture assuming direct access. Assume: someone drops a file, you consume the file, and your SLA depends on their timeliness.
- Certificate-based auth means someone in your customer's security team has to *issue* you a cert. Start the request week one. It will arrive week four.
- Log the *effective* watermark on every run — the actual max timestamp of rows you received. Compare against your requested watermark. Divergence is the earliest signal that something upstream shifted.
- Circuit-break aggressively. If a REST endpoint has returned 500s for 15 minutes, stop calling and page the on-call. Retrying forever masks outages and burns your quota.

## INTERVIEW ANGLE

System-design rounds for FDEs almost always include a connector question because it's where the pilot meets reality.

Sample questions:

1. "Design a connector for a REST API that rate-limits at 10 req/s, paginates with cursors, and occasionally returns 502s." (Expected: token bucket for rate, cursor-based pagination with resumable state, exponential backoff on 5xx, idempotent output tagged by watermark.)
2. "The nightly SFTP file didn't arrive. What does your system do?" (Detect at expected-time + grace period. Alert. Don't run downstream. Don't silently reuse yesterday's file. Have a documented manual-recovery path.)
3. "The customer says 'just query our production database.' What do you push back on?" (Read replica or dedicated user, scoped grants, statement timeouts, off-hours cadence if the extract is heavy. Production-DB access is a courtesy — treat it that way.)

## DRILL

1. **Extend:** add a `PagedRestConnector` variant that handles offset-based pagination (`?offset=0&limit=100`) instead of cursors, and stops when a page returns fewer rows than the limit.
2. **Break:** simulate the nightly file arriving at 04:30 instead of 02:47. Your scheduler runs `fetch` at 03:00. What happens? Add a `wait_until` with a hard deadline and a "file late" alert.
3. **Fix:** add a `describe` output that includes `expected_latency`, `auth_type`, `owner_contact`, and `runbook_url`. Print all connector descriptions at startup — that's your engagement's operational-map artifact.
