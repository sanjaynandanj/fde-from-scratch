# Least Privilege in the Field: Scoped Credentials, Break-Glass

**Phase 6 · Lesson 05 · ~1h**

## PROBLEM

Week four of an ERP-integration pilot at a manufacturer. The customer's DBA hands you a credential in a Teams DM — `sa` password to their SQL Server, "so you can just get started while we sort out the ticket." You use it. It works. You ship a demo Friday and everyone is thrilled. Six weeks later their internal security audit picks up your service account writing to twelve tables you never touched, and a login from a coffee shop in Barcelona (your teammate's vacation laptop). Nothing malicious happened. The audit finding is still severity-high because the credential was over-scoped and shared. The customer's CISO opens a review of "vendor access hygiene" that consumes your team for a month, and the DBA who helped you gets a formal warning. You cost a friendly stakeholder their comfort in helping the next vendor.

Least privilege is not a philosophy — it's a promise you make to the people who trusted you with keys. Getting it right in the field, at speed, without becoming the FDE who slows every engagement to a crawl, is the skill.

## INTUITION

Four principles, four failure modes.

**Scope down, scope narrow, scope short.** Every credential has three dimensions: **what** it can do (read/write/delete, which tables), **where** it can do it (which network, which host), **when** it can do it (permanent, or 8-hour session). The junior move is to accept whatever the customer offers. The senior move is to *ask smaller*: "I need read-only on these three tables for the next 30 days from these two IPs." This sounds like more work; it is less work, because when the audit hits, your access matches your job description.

**Named identities, not shared secrets.** `sa`, `admin`, `svc_pilot_shared` — any credential more than one human uses is untraceable. When something breaks or leaks, you cannot answer *who did what*. Push for named identities per human (SSO-backed if possible) plus a named service account per system, never a shared one. If the customer resists, that itself is a finding worth documenting.

**Break-glass, not backdoor.** Real work sometimes requires elevated access — a production incident at 2am, a data-recovery run, a one-time bulk fix. The mature pattern is **break-glass**: a dormant elevated credential in a sealed vault, requiring a documented reason to unseal, with automatic notifications and a short session TTL. It exists so the elevated path is *observable and temporary*, not because it's forbidden. The failure mode is a break-glass account that gets used monthly — at that point it's just an admin login with a legend.

**Rotation is the countermeasure to leakage you didn't detect.** Credentials leak — into `.env` files, logs, screenshots, notebooks, Slack DMs. Rotation limits the blast radius of the leak you never noticed. Static tokens rotated quarterly are strictly worse than short-lived tokens (STS, OIDC-issued JWTs, workload identity) that expire in hours. When the choice exists, choose ephemeral.

## BUILD IT

Build the **Access Register** — a plaintext table you maintain per engagement, updated as access changes. It is the artifact that keeps you honest with the customer's security team and yourself.

```
System         Identity         Scope             Env    Expires     Justification
-----------------------------------------------------------------------------------
Snowflake      sa.pilot.read    SELECT on 4 vw    Prod   2026-09-30  Ingest -> demo
Snowflake      sa.pilot.rw      SELECT+INSERT on  Dev    2026-09-30  Pipeline dev
                                _stage_pilot.*
Okta           user@ourco.com   SSO, no console   Prod   Rolling     Team member
GitHub         sa.pilot.deploy  Repo: pilot-erp   n/a    2026-09-30  CI deploys
Break-glass    bg.pilot         DBA on 4 tables   Prod   On-unseal   Incident only
```

Now the FDE overlay — three columns that separate hygiene theater from real access discipline:

- **Last used.** A cron/log check against the auth system. Credentials unused for 30 days should be revoked. If yours are unused, someone is going to notice before you notice; get there first.
- **Owner.** Named person on your side responsible for this credential. The person who requested it, uses it, and revokes it. If ownership is unclear, the credential outlives the engagement — the #1 source of vendor-access findings.
- **Revocation trigger.** The event that removes access: end date, engagement close, offboarding, or role change. Every credential must have one; anything else is a permanent grant in denial.

Add three ops habits:

1. **Weekly access review**, five minutes. Any row where scope is broader than the last week's work, tighten. Any row unused, revoke.
2. **The offboarding runbook.** When a teammate rotates off the engagement, one document lists every credential to revoke in what order. Practice it before you need it (Lesson 09 assumes it exists).
3. **The break-glass drill.** Every quarter, exercise the break-glass path with a fake incident. Confirm the notification fires, the TTL expires, the audit log captures the reason. Untested break-glass is a legend, not a control.

## FIELD NOTES

- The credential offered is almost always over-scoped. DBAs give you write when you asked for read; ops give you admin when you asked for operator. Say thank you, then explicitly request the smaller scope in writing. The paper trail matters more than the delay.
- Personal laptops are the leak surface. A short-lived cloud-issued token in a locked-down workspace is safer than a permanent token in `~/.env` on a laptop that syncs to iCloud. Choose the architecture, not the discipline.
- SSO integration is worth begging for in week one. Every credential behind SSO is one you don't have to remember to revoke — when the human offboards, SSO does the work. Every credential *not* behind SSO becomes yours to track forever.
- Break-glass gets abused when normal access is too painful. If your team unseals monthly, the real fix is a broader, still-scoped normal credential, not more discipline around the emergency one.
- The customer's own developers usually have worse access hygiene than you. This is a trap — don't calibrate down to their norm. When their audit runs, "everyone else did it too" is not the defense you'd hope.

## INTERVIEW ANGLE

Access questions come up in the deployment round and the security round. Interviewers are checking whether you'd embarrass the customer's CISO under audit.

1. "The customer's DBA offers you the `sa` account to move faster. What do you do?" (Thank them, decline politely, request a scoped read-only account with a specified expiry — and write down why the offered scope was declined so the audit can see your reasoning. Bonus: name the joint-controller/attribution risk.)
2. "Design a break-glass process for a small FDE team on a production engagement." (Sealed vault entry, documented unseal reason, automatic notification to a channel the customer sees, short TTL, mandatory post-use review, quarterly drill. The keyword is *observable*, not *forbidden*.)
3. "You discover a teammate is using a shared service account for personal debugging. What do you do?" (Same-day: rotate the credential, replace with per-human scoped access, add row to the register. Same-week: raise it in the retro; the process gap is more important than the person.)

## DRILL

Take a project you own — a personal project, a side gig, a homelab. Build the Access Register above for every credential you use to run it: cloud, DNS, database, deploy keys, third-party APIs. Fill in identity, scope, expiry, owner, revocation trigger, last used. Be honest. Count the rows where scope is broader than needed, where identity is shared, where there's no expiry, where the last-used date is over 30 days. Fix the top three today — rotate, scope down, or revoke. Save the register as a template; you will run this exercise on every future engagement in week one.
