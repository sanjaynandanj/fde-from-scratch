# SQLite as the Pilot Database: When It's Enough (Usually)

**Phase 2 · Lesson 04 · ~1h**

## PROBLEM

A pilot at a regional bank. The FDE, coming from a shop where every service used Postgres in RDS, opens a ticket with the bank's DBA team on day one for a Postgres instance. Three weeks later he still doesn't have credentials — security review is pending, the network segment isn't approved, and the DBA who has to provision it is on PTO. His pilot API is still hitting CSVs on disk. His demos are slow. His champion is losing patience. Meanwhile, another FDE across town at a similar bank shipped her pilot a week ago on SQLite — a single `pilot.db` file next to her Python script — and is now iterating on the second workflow.

The DBA ticket eventually resolves in week seven. By then the second FDE has already migrated her SQLite schema to their Oracle system in a two-day port, because she designed for it. The first FDE never got past demo one.

## INTUITION

SQLite is the correct answer for the pilot database question 80% of the time, and FDEs who don't know this waste weeks in access battles for infrastructure they don't yet need. It ships with Python's stdlib. It is a single file. It handles millions of rows and modest concurrent reads without complaint. It has real SQL, transactions, indexes, and JSON support. It is more reliable than most Postgres deployments you'll inherit.

The design space, ordered by "when you need to move up":

- **CSV/JSON files on disk.** Fine for week 1. Read-only, single-workflow. You will outgrow this the moment two queries need to join.
- **SQLite (`pilot.db` next to your script).** The pilot default. Works until: you need writes from multiple processes concurrently, you need row-level auth, or you need the customer's DBA team to own the data.
- **Postgres in the customer's VPC.** The right answer when the pilot converts to production, or when data volume genuinely exceeds SQLite's comfortable zone (roughly: hundreds of GB, or thousands of concurrent writers).
- **Their existing warehouse (Snowflake, BigQuery, Databricks).** When your workload is analytical and their data already lives there.

The pilot rule: **start with SQLite; design your schema and access patterns as if you might port; port only when a specific pain forces it.**

Things SQLite is genuinely bad at: many concurrent writers (one writer at a time — the WAL journal helps but doesn't remove this), high-availability failover, row-level security, network access. If your pilot needs any of these, plan the port from day one, but *still start on SQLite* while the port infrastructure is being provisioned.

## BUILD IT

The SQLite pilot pattern, in about 20 lines. Stdlib only.

```python
import sqlite3, contextlib, pathlib

DB = pathlib.Path("pilot.db")

def connect():
    c = sqlite3.connect(DB, isolation_level=None)  # autocommit; use tx explicitly
    c.execute("PRAGMA journal_mode=WAL")            # concurrent reads while writing
    c.execute("PRAGMA foreign_keys=ON")             # actually enforce FKs
    c.row_factory = sqlite3.Row                     # dict-like rows
    return c

def migrate():
    with contextlib.closing(connect()) as c, c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS invoice (
          id TEXT PRIMARY KEY, vendor TEXT NOT NULL,
          amount REAL NOT NULL, flagged INTEGER DEFAULT 0,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE INDEX IF NOT EXISTS idx_invoice_vendor ON invoice(vendor);
        """)

def upsert_invoice(row):
    with contextlib.closing(connect()) as c, c:
        c.execute("""INSERT INTO invoice(id, vendor, amount) VALUES(?, ?, ?)
                     ON CONFLICT(id) DO UPDATE SET vendor=excluded.vendor,
                     amount=excluded.amount""", (row["id"], row["vendor"], row["amount"]))
```

Notes worth internalizing:

- `PRAGMA journal_mode=WAL` is the single most important line. It lets readers proceed while a writer is committing — the difference between a pilot that feels snappy and one that stalls under demo click-throughs.
- Always `PRAGMA foreign_keys=ON`. Off by default. Bites you at port time.
- Keep DDL idempotent (`IF NOT EXISTS`) so restart is safe.
- Use parameterized queries always. SQLite makes SQL injection just as easy as any other DB.
- Backup is `cp pilot.db pilot-YYYY-MM-DD.db`. Don't overcomplicate it.

## FIELD NOTES

- Customers see "SQLite" and sometimes react as if you're using a toy. Two sentences defuses it: "This is the pilot database; it holds the full dataset, ~600k rows. We'll port to your Postgres for production." Now they hear "port plan" and relax.
- Ship the schema in a `schema.sql` file, not embedded in Python. When the customer's DBA asks "show me the tables," you email one file. When it's time to port, you rewrite one file.
- Never let the SQLite file be the source of truth. It should always be re-derivable from the customer's real source. If the champion accidentally deletes `pilot.db`, you should be able to rebuild it in one command. Design the pipeline that way from day one.
- Windows customers occasionally have antivirus tools that lock `.db` files while scanning. If a pilot hangs on write, this is why. Use `.sqlite` extension or a subdirectory the AV team can exclude.

## INTERVIEW ANGLE

Interviewers care whether you can name the level where SQLite stops working — and start pilots on it anyway.

Sample questions:

1. "You're two days into a pilot at a bank. You need a database. What do you pick and why?" (Testing: SQLite by default, port plan noted, don't wait for DBA tickets.)
2. "When would you not use SQLite for a pilot?" (Testing: concurrent writers, row-level security, or the customer's compliance team hard-requires their own DB from day one.)
3. "Your pilot data is 400 GB. Still SQLite?" (Testing: honest limits — SQLite can technically handle it, but analytical performance and backup speed argue for the warehouse if the data already lives there.)

## DRILL

Take the `BUILD IT` snippet. Load 100,000 fake invoice rows using a generator. Time three operations: single-row lookup by `id`, sum of `amount` group by `vendor`, and a concurrent write from a second process while a read is running. Document what WAL mode changes. Then write the `schema.sql` you'd hand to a customer DBA and note the three lines that would need to change for Postgres. That note is your port plan.
