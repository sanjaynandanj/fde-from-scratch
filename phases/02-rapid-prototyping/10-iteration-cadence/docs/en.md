# Iteration Cadence: Shipping Daily to a Customer Sandbox

**Phase 2 · Lesson 10 · ~1h**

## PROBLEM

Two engagements running in parallel at the same firm. Engagement A: the FDE ships to the customer sandbox on Fridays. Every Friday, one deploy, a week's worth of changes. Every Monday, the customer comes back with feedback that's a week stale, and half the week's work turns out to have been aimed at the wrong requirement. Engagement B: the FDE deploys daily, sometimes twice a day, and shares a two-line change log in Slack after each deploy. By week 3, engagement B has shipped 14 iterations, engagement A has shipped 3, and the champion on B is forwarding change-log messages to their VP as evidence the project is moving. Engagement A is losing the renewal argument. Engagement B is negotiating a Phase 2 expansion.

The code volume was the same. The *cadence* was the difference the customer felt.

## INTUITION

Pilots die when they go quiet. A working demo two weeks ago is worse than a broken demo yesterday, because "moving" is the only signal a busy stakeholder registers. Daily deploys to a customer sandbox — not weekly, not "when it's ready" — are the highest-leverage habit an FDE can adopt.

The design space of cadence:

- **Deploy-when-done.** The default from most SWE backgrounds. Wrong for pilots. Optimizes for polish over presence.
- **Weekly deploy.** The most common failure mode. Feels disciplined; is actually invisible.
- **Daily deploy, silent.** Better, but the customer doesn't see it unless they log in. Half the value lost.
- **Daily deploy with a two-line notification.** The FDE default. "Deployed: added vendor column to flagged view; fixed date parsing for their Q2 export." Cheap. Cumulative. Visible.
- **Continuous deploy on push.** Requires infrastructure that most pilots don't have. Overkill; the daily rhythm is what matters, not the automation.

What makes daily work:

- **A running customer sandbox from week 1.** Not "we'll set it up next week." Day 3 at the latest. This is the credential-battle lesson from Phase 1 — you cannot deploy daily without an environment to deploy to.
- **A one-command deploy.** `bash deploy.sh` or `python deploy.py`. If it takes more than one command, you will skip days, and the cadence dies.
- **A change-log habit.** After every deploy, one message: what changed, who asked for it (name), where to look. Post it where the champion sees it — Slack, Teams, email, whatever they read. Copy the champion by name.
- **A rollback plan.** Daily means you will break things. A `deploy.sh --rollback` that reverts to the previous version in one command is what lets you deploy Friday afternoon before boarding a flight.

The change-log format that works (one per deploy):

```
Pilot update — Mar 14, 2:40pm
Shipped:
  • Added "assigned reviewer" column to flagged invoices view (per Sara's ask on Tuesday)
  • Fixed timestamp parsing for the Q2 export — earlier rows now show the right date
Next:
  • Wiring the "notes" round-trip to Excel — target end of day tomorrow
Sandbox: https://pilot.customer.internal
Rollback if needed: ping me.
```

Three sentences of change. Two minutes to write. Weeks of accumulated proof that the pilot is alive.

## BUILD IT

The daily-deploy playbook, as a checklist. Adopt on day one.

```
DAILY DEPLOY CHECKLIST
[ ] Customer sandbox exists and reachable (day 3 at the latest).
[ ] `deploy.sh` — one command; syncs code + restarts the pilot service.
[ ] `deploy.sh --rollback` — reverts to previous version; tested at least once.
[ ] Change-log template in a text file; copy-paste and send after every deploy.
[ ] Named champion + one backup on the notification list.
[ ] Screenshot each visible change; attach to the log entry.
[ ] Log every deploy in `DEPLOYS.md` — date, sha or version, summary, who asked.
```

The minimal `deploy.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
VER=$(date +%Y%m%d-%H%M%S)
ssh sandbox "cd /opt/pilot && cp -r current previous-$VER && git pull && \
             pkill -f 'python run.py' || true && nohup python run.py > log 2>&1 &"
echo "deployed $VER"
```

The rollback (`deploy.sh --rollback`):

```bash
ssh sandbox "cd /opt/pilot && LATEST=\$(ls -td previous-* | head -1) && \
             rm -rf current && mv \$LATEST current && \
             pkill -f 'python run.py' || true && nohup python run.py > log 2>&1 &"
```

Both are ugly. Both work. Both take three minutes to write. Neither requires infrastructure the customer hasn't already provisioned.

The `DEPLOYS.md` log — a running append-only file — becomes both your changelog for the customer AND your evidence trail when someone asks "when did that behavior start?" three weeks later.

## FIELD NOTES

- Daily doesn't mean big. Some deploys are one-line fixes. Ship them anyway. The cadence is the product.
- Wednesday-Thursday deploys carry the most weight — they land right before the weekly customer sync, where the champion will demo your changes. Save the risky work for Monday-Tuesday.
- Never deploy on Friday afternoon without a rollback plan tested that morning. "Deployed, going dark for the weekend" is how you come back Monday to angry emails.
- If your customer doesn't have a sandbox yet, deploy to a laptop-sized cloud VM you own, tunnel it, share the URL. Do not wait for their infrastructure. Waiting is death.
- Watch what deploys the champion mentions in weekly meetings. Those are the changes that mattered. Notice the ones you thought were important but they never referenced — that's data about what the pilot is actually solving.

## INTERVIEW ANGLE

Interviewers probe whether you know pilots are as much a communication rhythm as a code rhythm.

Sample questions:

1. "How often should you deploy during a pilot?" (Testing: daily, or more; and why — visibility, tight feedback loop, evidence of progress.)
2. "What's the first thing you set up in a new pilot repo?" (Testing: sandbox + one-command deploy + rollback + change-log template. Not the parser, not the schema.)
3. "You deployed something at 4:45pm Friday. What's your Monday-morning workflow?" (Testing: rollback plan tested, change-log with your phone number, monitoring, or the answer 'I wouldn't deploy at 4:45 Friday' with rationale.)

## DRILL

Set up the daily-deploy pattern on a local pilot. Write `deploy.sh` and `deploy.sh --rollback`. Deploy your walking skeleton from Lesson 08 five times, each with a one-line change, and write a change-log message for each. On the fifth deploy, deliberately break something, then rollback via one command. Keep the change-log messages; if they don't read as customer-facing communication, rewrite them until they do. The rhythm is the skill.
