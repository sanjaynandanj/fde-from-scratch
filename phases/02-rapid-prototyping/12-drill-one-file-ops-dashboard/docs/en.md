# Drill: Build a One-File Ops Dashboard from a Messy Export

**Phase 2 · Lesson 12 · ~1h**

## PROBLEM

Tuesday, 4:12pm. The ops director at a mid-sized 3PL emails your champion: "Can you two put together something showing our shipment health for tomorrow's leadership meeting? Attaching the export." You look at the attachment. It's a 42MB CSV with 380,000 rows, three date formats, half the customer names duplicated with variant spellings, and a `status` column with 14 distinct values that clearly should be 4. The meeting is at 10am Wednesday. The champion CCs you. The champion is looking at you.

This is the drill. Every FDE will get this email in their first month. The goal is not perfection. The goal is a one-file dashboard, in the champion's inbox before 8am tomorrow, that answers the ops director's real question: **is anything on fire, and where?**

## INTUITION

This drill exercises every Phase 2 lesson at once, under time pressure. You have roughly 12 working hours, minus sleep. What must ship:

- A walking skeleton (Lesson 08) — end-to-end, one metric visible.
- One HTML file (Lesson 03) — the ops director will open it on her phone in an Uber.
- SQLite or in-memory (Lesson 04) — do not ask for infrastructure.
- Seeded/normalized data where messy (Lesson 06) — but no fake numbers; only cleaned real ones.
- Excel export (Lesson 09) — she will forward the numbers to her VP.
- A change-log line (Lesson 10) — even one deploy, log it.
- Telemetry (Lesson 11) — count opens so you know if it was actually read.
- A `FAKES.md` (Lesson 02) — what's real, what's approximated, so nobody misinterprets.

What must *not* happen: three hours parsing all 14 status values into a perfect canonical taxonomy. That's next week. Tonight you collapse them into 4 buckets, document the mapping, and move on.

The design space of "where's the fire":

- **On-time delivery rate**, this week vs last four weeks — the headline number.
- **Exceptions by reason**, top 5 — the "why" the director will point at.
- **Customers with the most delays**, top 10 — the accounts leadership will call.
- **Shipments in transit past ETA**, count and total value — the active fire.

Pick two of these for the dashboard, one for the Excel export, defer the fourth to a followup.

## BUILD IT

The 12-hour build plan. Not a code listing — a walkable template you can execute.

```
HOUR 0 (Tue 4:30pm) — RECONNAISSANCE
  - Open the CSV in Excel. Look at 20 random rows. Note field names, obvious garbage.
  - Ask the champion (Slack, 1 message): "For tomorrow — is the audience
    ops leadership or exec? What one number would you lead with?"
  - Don't code yet. Understand the ask.

HOUR 1 (Tue 5:30pm) — PROFILE
  - Load into SQLite via `csv.DictReader` + `INSERT`.
  - Print: row count, null rates per column, top 20 values in `status`,
    top 20 values in `customer_name`, date-format samples.
  - Decide the 4-bucket status taxonomy. Write it in FAKES.md as an assumption.

HOUR 2 (Tue 6:30pm) — NORMALIZE
  - Write one function per messy column: `norm_status()`, `norm_date()`, `norm_customer()`.
  - Materialize a `clean` table in SQLite. All downstream reads hit `clean`.
  - Skip fuzzy dedup on customer_name. Use simple lowercase-trim-collapse-spaces.
    Note in FAKES.md: "Customer dedup is exact-match on normalized name."

HOUR 3 (Tue 7:30pm) — SKELETON
  - `run.py` — stdlib http.server, two endpoints:
      /api/summary   -> on-time rate, delta vs last 4 weeks, in-transit past ETA
      /api/exceptions -> top 5 reasons, top 10 delayed customers
  - `dashboard.html` — one file, big cards + two tables. Steal Lesson 03 template.

HOUR 4-5 (Tue 8:30-10:30pm) — CONNECT + POLISH
  - Wire the queries. Test with real data.
  - Add "Export to Excel" button that dumps top-10-delayed customers as CSV
    with UTF-8 BOM (Lesson 09).
  - Add telemetry (Lesson 11) — one line per page view.

HOUR 6 (Tue 10:30-11:30pm) — SANITY
  - Compare your on-time rate to a hand-computed number from a 100-row sample.
    If they don't match to within 1%, something is wrong. Fix before sleep.
  - Take screenshots on desktop AND on phone browser. Both must be legible.
  - Sleep.

HOUR 7-8 (Wed 6:30-8:30am) — SHIP
  - Deploy to laptop-tunnel or sandbox. `python run.py` on the sandbox VM.
  - Email champion: dashboard URL, screenshot, three-line change log,
    FAKES.md as attachment. CC the ops director if the champion approves.
  - Confirm the dashboard loads on the champion's phone.
```

The deliverables at 8:30am Wednesday:

- Live URL.
- Screenshot in the email body.
- Excel export attached.
- `FAKES.md` naming the status taxonomy, the customer normalization, any other assumption.
- Change-log line in the email: "Shipped: shipment-health dashboard v1. Sources: your Tuesday export. Numbers: computed from cleaned data; see attached assumptions."

## FIELD NOTES

- The ops director will read three things: the headline number, the top customer name in the table, and whether the URL loads on her phone. Get those three right; everything else is bonus.
- Do not skip the "compare to hand-computed number" step. Getting the headline number wrong on the first delivery is a trust event you may not recover from.
- Someone in the meeting will ask "why is X on the delayed list?" You will not know. The right answer is "I can dig into that today and send you the row-level detail" — and then do it, before end-of-day, as your Wednesday change-log deploy.
- The customer will forward this dashboard to people you haven't met. Design as if the CFO will open it. Big headline, clear labels, no jargon, no debug output visible.
- Save the entire folder as a template. The next 3PL-shaped urgent ask will be 60% the same code.

## INTERVIEW ANGLE

This drill maps directly to the OpenAI/Palantir/Anthropic take-home archetype: "here is a messy CSV, build something useful by tomorrow." Interviewers grade on speed, judgment, honesty about assumptions, and end-to-end delivery.

Sample questions:

1. "You have 12 hours and a messy CSV. Walk me through your plan." (Testing: profile-normalize-skeleton-ship. Not "I'd start with the parser architecture.")
2. "How do you decide what to include vs defer?" (Testing: named audience, headline metric first, everything else is bonus; explicit deferrals go into a followup, not silence.)
3. "How do you defend the headline number if someone challenges it?" (Testing: hand-computed cross-check on a sample, `FAKES.md` assumptions, ability to drill into row-level detail.)

## DRILL

Do it. Generate or find a 50-100k-row CSV with real messiness (three date formats, dirty customer names, non-canonical status values — Phase 3's data generator will help; for now, corrupt a public dataset by hand). Give yourself 4 hours (not 12 — this is practice, not the real fire). Ship: one HTML file, one Python file, one FAKES.md, one screenshot, one email draft. Time yourself. Note where you spent time you didn't need to. Save the template. When the real Tuesday-4pm email arrives, you will have done this before.
