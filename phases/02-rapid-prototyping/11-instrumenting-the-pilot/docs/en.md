# Instrumenting the Pilot: Usage Telemetry That Proves Value

**Phase 2 · Lesson 11 · ~1.5h**

## PROBLEM

Week ten of a pilot. Renewal conversation coming up in two weeks. The FDE walks into the meeting with a beautiful dashboard, seven completed workflows, and a champion who says "the team loves it." The customer's economic buyer — the VP the champion reports to — asks two questions: "How much time is this saving?" and "How often are people using it?" The FDE has no answer. He knows the tool works. He can't *prove* anyone uses it. The VP nods politely. The renewal gets pushed to next quarter to "gather more data." Next quarter never comes.

A different pilot at the same firm. The other FDE instrumented every page load, every action, every export from week two. Her renewal meeting opens with one slide: "127 users, 43% weekly active, 380 reviews last week vs 42 before the pilot, average review time 47 seconds vs 3 minutes in the old process." The renewal is signed in the room. Nobody asks her how the tool works. The numbers ended the discussion.

## INTUITION

Usage telemetry in a pilot is not "nice to have for observability." It is the artifact you will demand in the renewal conversation, and if you did not instrument from week two you will not have it. The instinct to add it "when we have time" is the mistake. Add it before the second demo.

The design space, from cheapest to most useful:

- **Web-server access logs.** You get this for free from `http.server` or nginx. Counts requests. Better than nothing. Cannot distinguish user actions from asset loads.
- **Structured JSON event logs.** Every action in the app writes one line: timestamp, user, event, context. This is the FDE default. Grep-able, aggregable, ships without a third party.
- **Backend metric counters.** A `counts.db` SQLite table with `event, count, day`. Aggregates for you. Useful for weekly reports.
- **Third-party analytics (PostHog, Mixpanel, Amplitude).** Overkill in the pilot, often blocked by the customer's egress or DPA. Save for post-pilot.

The events you must instrument on day one:

- **User arrival.** Session start, distinguished by user identifier or best-guess (hashed IP + user-agent for very early pilots without auth).
- **Primary action.** The thing you'd point to in the renewal meeting. "Review submitted." "Report exported." "Decision recorded." Whatever your walking-skeleton metric measures.
- **Time-to-action.** Time from arrival to primary action. This is where the "3 minutes → 47 seconds" story comes from.
- **Return visits.** Same user, next day. Weekly active user count is the metric executives read.
- **Errors.** Every 500 or client-side failure, logged. Not for debugging — for showing "0 errors in the last 30 days" as a reliability story.

What you should *not* instrument in a pilot: everything else. Deep event schemas rot. Ten well-chosen events beat 200 speculative ones.

## BUILD IT

The whole telemetry system, stdlib only, in about 30 lines. Ship in the walking skeleton.

```python
import json, sqlite3, time, hashlib, pathlib

DB = pathlib.Path("telemetry.db")

def _init():
    c = sqlite3.connect(DB); c.execute("PRAGMA journal_mode=WAL")
    c.execute("""CREATE TABLE IF NOT EXISTS events(
                   ts REAL, user TEXT, event TEXT, context TEXT)""")
    c.execute("CREATE INDEX IF NOT EXISTS idx_ev ON events(event, ts)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_user ON events(user, ts)")
    c.close()
_init()

def log_event(user, event, **context):
    c = sqlite3.connect(DB, isolation_level=None)
    c.execute("INSERT INTO events VALUES(?,?,?,?)",
              (time.time(), user or "anon", event, json.dumps(context)))
    c.close()

def user_id_from_request(handler):
    # Real: SSO subject claim. Pilot: hash of IP + UA.
    src = f"{handler.client_address[0]}|{handler.headers.get('user-agent','')}"
    return hashlib.sha1(src.encode()).hexdigest()[:12]

# In your request handler:
def do_GET(self):
    log_event(user_id_from_request(self), "page_view", path=self.path)
    # ... existing logic ...

# Weekly report — one query, one number, one email:
def weekly_report():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    week = time.time() - 7*86400
    wau = c.execute("SELECT COUNT(DISTINCT user) FROM events WHERE ts > ?",
                    (week,)).fetchone()[0]
    actions = c.execute("""SELECT event, COUNT(*) FROM events
                           WHERE ts > ? GROUP BY event ORDER BY 2 DESC""",
                        (week,)).fetchall()
    return {"weekly_active_users": wau,
            "actions": [dict(a) for a in actions]}
```

Design notes:

- **SQLite, not a third-party.** Ships with you. Zero customer egress questions. Zero DPA discussion.
- **Hash IPs.** Even in the pilot, do not store raw IPs unless the DPA covers it. The 12-char hash is enough to identify unique users.
- **Never log sensitive fields.** Names, dollar amounts, IDs — leave them out of context. Only log what event fired and cheap dimensions (path, referrer, latency).
- **Weekly report as a script.** Run it before every customer meeting. Paste the output into the deck. The three numbers you always report: weekly active users, primary action count, error count.
- **Time-to-action** is computable from the events table by joining a user's first `page_view` in a session to their first primary action. One SQL query. Enormous story.

## FIELD NOTES

- Bring one telemetry slide to every weekly customer sync starting week three. "Last week: 34 active users, 118 reviews, 0 errors." Watch the champion's posture change. They now have ammunition for their own internal politics.
- Instrumentation lets you catch the *absence* of use. If the primary action count dropped this week, ask why before the meeting. Silent decline is how pilots die.
- Never instrument something you cannot tell the customer you're logging. If they ask "what do you record about my users?" you should be able to answer with the exact event schema. Ship a `TELEMETRY.md` file listing every event.
- Customers with strong privacy postures will push back. Address it directly: hashed identifiers, aggregate counts, retention policy, and — critically — offer to disable it if they insist. Then find another proxy for use, like counting exports processed.
- The "time saved" number is the one executives quote in board decks. Compute it honestly (median action time × action count vs the old process baseline the champion gave you at discovery) and cite the assumptions. FDEs who fudge this number get caught and lose renewals.

## INTERVIEW ANGLE

Interviewers probe whether you understand pilots must produce quantitative evidence, not just working software.

Sample questions:

1. "You're two weeks from a renewal conversation. What data would you want?" (Testing: WAU, primary action count, time-to-action delta vs baseline, error rate. Not just "positive feedback.")
2. "How do you instrument a pilot without a third-party tool?" (Testing: SQLite events table, structured JSON logs, minimal schema, weekly report script.)
3. "The customer's privacy team objects to telemetry. What now?" (Testing: hashed identifiers, aggregate-only, retention policy, or fall back to counting server-side artifacts like exports rather than user actions.)

## DRILL

Instrument the walking skeleton from Lesson 08 with the pattern above. Simulate 50 sessions with a script — some users returning, some abandoning after the landing page. Then write the weekly report and format it as three lines for a customer email. If your report reads more like debug output than a customer update, rewrite it until an executive would understand it in ten seconds. Save `TELEMETRY.md` describing every event; you will hand this to every customer's privacy team.
