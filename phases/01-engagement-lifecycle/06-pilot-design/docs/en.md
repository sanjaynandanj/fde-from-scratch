# Pilot Design: Seeded Wins, Visible Dashboards, Weekly Demos

**Phase 1 · Lesson 06 · ~1.5h**

## PROBLEM

Two FDEs are running parallel pilots at the same customer. FDE A works heads-down for four weeks and reveals a polished system on day 28. FDE B ships something ugly on day 5, demos it every Friday, and iterates in front of the customer. On day 30, FDE A's system is technically better. But FDE B's champion has been showing weekly progress to the exec sponsor for a month — three exec forwarded emails, two internal Slack shoutouts, and a mention in a VP staff meeting. Guess whose project gets the production budget. A "better" pilot loses to a *more visible* pilot every single time, because the political system that renews contracts runs on visibility, not architecture.

Pilots are not built in private and revealed. Pilots are built out loud.

## INTUITION

A pilot is a political artifact as much as a technical one. Its purpose is to move a metric *and* to generate a stream of visible evidence that the metric is moving, at a cadence the champion can weaponize inside their own org. Three design principles carry the weight:

**Seeded wins.** Day 1 of the pilot, the user should be able to see something. Not the final thing — something. A dashboard with three tiles, half real half seeded. A CSV export with real rows. A working search over a canned corpus. Seeded wins buy you two weeks of political air cover while you build the real thing behind them.

**Visible dashboards.** The pilot needs a home page. One URL the champion can send to their VP. That page must (a) load fast, (b) show the metric prominently, (c) be updated every time the pilot ships anything new. If your pilot's status lives in a Google Doc, you have no dashboard and no political leverage.

**Weekly demos.** A 30-minute standing meeting every Friday of the pilot, with a fixed audience (champion + a subset of stakeholders) and a fixed structure. Every demo shows something that didn't exist last week. Every demo ends with three asks and three commitments. Miss a demo and you lose a compounding week of trust.

The design of a pilot is really the design of a *feedback loop*. The customer sees something → they react → you incorporate → they see the next thing. The faster this loop cycles, the faster the real requirements surface and the faster the pilot converges on something worth productionizing.

## BUILD IT — the pilot design canvas

Fill this in during scoping. Post it visibly for the pilot team. Review it every Monday.

```
PILOT DESIGN CANVAS — <pilot name>

THE METRIC READOUT (headline artifact for day 30):
  Format: <dashboard tile / one-pager / live query / signed memo>
  Location: <URL / doc / room>
  Owner (customer-side who reads it): <name>

SEEDED WIN — WEEK 1:
  What the user will see on Friday of week 1: <one sentence>
  How much is real vs seeded: <e.g., "50 real rows + 150 synthetic filler">
  What we're deliberately faking: <list — CRM export, auth, refresh cadence>

VISIBLE DASHBOARD:
  URL: <where it lives>
  Update cadence: <daily / on-deploy>
  Hero tile (top-left, biggest): <the metric>
  Supporting tiles: <3-5 max — user activity, coverage, freshness>
  Anti-features: <what we deliberately DON'T show — noisy debug info,
                  half-broken workflows, "coming soon" placeholders>

WEEKLY DEMO STRUCTURE (30 min, every Friday):
  0-5   min: last week's asks -> what we did
  5-20  min: this week's new thing (live, on real data slice)
  20-25 min: metric readout (dashboard walkthrough)
  25-30 min: three asks + three commitments

STANDING ATTENDEES:
  Required: <champion, data owner>
  Rotating: <persona-of-the-week, exec sponsor once a month>

DEMO FAILURE PLAN:
  If the live demo breaks: <fallback recording, cached run, screenshot deck>
  If the champion cancels: <written status email in same structure, same day>

INSTRUMENTATION (proves the pilot is being used):
  Events tracked: <login, run-workflow, export, feedback>
  Reported in demo: <"users ran X workflow N times this week">
```

The pieces that matter most:

- **Anti-features.** New FDEs try to show everything. Great FDEs hide the ugly. A dashboard with 3 tiles that all work beats a dashboard with 8 tiles where 3 are broken.
- **The champion doesn't miss demos.** If the champion is absent, the pilot has stalled politically. Reschedule same-week. Don't drift.
- **Instrumentation from day one.** You will be asked "is anyone actually using this?" You need real numbers, not vibes.

## FIELD NOTES

- Seeded wins are not lying. You are transparent about what's real and what's placeholder. "This tile shows real data from your last quarter; this tile is a mock of what the completed integration will look like next week." Customers respect this. They resent discovering fakes on their own.
- Weekly demos should have *guests*. Every third or fourth demo, bring in a new stakeholder — an adjacent team lead, a VP, the security officer. Each guest is a new evangelist or a new blocker exposed early.
- The 30-minute cap is real. Longer demos become debates. Book a 30-min demo and a *separate* 30-min working session same day if you need to go deeper. Do not conflate them.
- Send the demo recap the same afternoon. Five bullets: what we showed, what worked, what didn't, three asks, three commitments. This becomes the paper trail that runs the pilot.
- The dashboard's uptime matters. If your champion sends the URL to their VP and it loads slow or 500s, you've spent political capital you can't refund. Cache the hero tile. Set a health check. Have a static fallback.

## INTERVIEW ANGLE

Pilot design is a favorite in decomp rounds and system-design rounds for FDE roles because it tests whether you understand pilots as social artifacts, not just software.

1. "Design a 4-week pilot for a supply-chain forecasting tool. Walk me through what the user sees each week." (They want: seeded win week 1, real-data slice by week 2, visible dashboard, weekly demo cadence, day-30 exec readout.)
2. "Your champion cancels the weekly demo two weeks in a row. What do you do?" (They want: named political risk, written escalation to sponsor, adjusted format — async video, in-person coffee — to keep visibility alive.)
3. "How do you decide what to seed vs build in week 1?" (They want: seed what's downstream of infrastructure blockers, build what's core to the metric readout; be explicit and transparent about the difference.)

## DRILL

Design a pilot for a plausible engagement — either continue your Lesson 03 scoping doc or pick a new one. Fill in the pilot design canvas above. Then draft the week-1 demo agenda in bullet form: what will be on screen at minute 6? What will you show at minute 15? What will your three asks be? Now imagine your champion emails 30 minutes before demo saying "I'm out sick — can you send a summary?" Write the summary email in the same 5-bullet structure. This drill maps directly to Capstone 1 (Pilot-in-a-box).
