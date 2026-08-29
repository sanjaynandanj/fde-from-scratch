# System Design for FDEs: Pilot Architecture, Not Planet-Scale

**Phase 9 · Lesson 03 · ~1.5h**

## PROBLEM

A candidate walks into an FDE system-design round with two years of "design Twitter" prep behind him. The prompt: "design a document-search system for a mid-sized law firm — 200 lawyers, 500,000 documents, deployed inside their VPC." He immediately starts drawing: load balancer, three application tiers, a sharded search cluster, Kafka for indexing, a caching layer, a Redis instance for hot documents, a horizontally scalable eval service. The interviewer keeps trying to gently redirect: "how do you get the documents in the first place? What if some are scanned PDFs? What's the security review look like?" He keeps returning to throughput ("we can shard on document ID and scale to a million QPS…"). The debrief comes back: "over-engineered, no evidence he'd survive a pilot, treated the customer's constraints as noise."

Planet-scale system design is a different discipline. FDE system design is *pilot architecture*: what's the smallest coherent thing that runs against real data at a real customer inside their security constraints, and how does it graduate to production later?

## INTUITION

The FDE system-design signal is the inverse of the SWE-at-a-big-tech-company signal. Instead of "can you scale to 10 million QPS?" it's "can you ship something into a customer environment in three weeks that survives their security review and produces value the champion can point at?"

The dimensions FDE rounds actually score:

- **Data ingress path.** Where does data come from, and what's the realistic access story (SFTP drop, warehouse replica, API pull, agent-inside-their-network)? Not naming this loses immediately.
- **Deployment posture.** Where does your code run — their VPC, your cloud, on-prem, air-gapped — and what does that force? Container? Vendored dependencies? No cloud managed services?
- **Identity and access.** SSO integration path (SAML or OIDC), service-account posture for backend access, least-privilege scoping. Real interviewers push here because it's real.
- **Failure modes and observability.** How does the pilot know when the nightly feed didn't arrive? What's alerted, what's logged, what's the runbook? The "silently returning zero" failure mode should come up unprompted.
- **The graduation story.** What changes when the pilot becomes production? Database swap, auth swap, HA — you name the debt now, you don't accrete it silently.

Notice what's *not* on the list: sharding, caching layers, QPS math beyond order-of-magnitude sanity checks. A 200-user pilot doesn't need a service mesh; naming one is a negative signal.

The mental model to hold: a pilot is a walking skeleton with real data, deployed inside a real security boundary, with an honest debt ledger. Everything else is theater until the customer's own numbers demand it.

## BUILD IT

The FDE system-design template — memorize the sequence and let it structure every design round you take:

**Move 1 — Clarify the customer, not the traffic.** "How big is the customer? What's the primary user role? What environment do they want this in — their cloud, ours, on-prem? What data are we touching, and where does it live today?" These four questions do more work than any traffic estimate. Traffic follows from user count and workflow.

**Move 2 — Draw the data path first, top of the whiteboard.** Source system → ingress mechanism → landing store → transformation → serving store → API → UI. Every arrow is a place a real customer engagement can stall. Name the arrow's failure mode as you draw it: "this SFTP pull might silently not arrive; I'll add feed-freshness alerting."

**Move 3 — Overlay identity.** Who authenticates? SSO through their IdP (SAML if it's a Fortune 500, OIDC if it's newer). Service accounts for backend integration. Group claims for authorization. "Their Okta team has a six-week queue; I'd file the integration request in week one and use IP-allowlisted basic auth as a bridge."

**Move 4 — Overlay deployment.** One diagram edit: the boundary line. Everything inside is theirs, everything outside is yours. Now you can talk about network path (private link, VPN, agent-inside), secret management (their vault, not your `.env`), and container posture (pinned image, non-root, SBOM available for review).

**Move 5 — Name three failure modes and their instrumentation.** Feed missing, credential rotated, downstream number drift. For each: how do you detect, alert, degrade. This is the round's "senior" signal — junior candidates never volunteer failure modes.

**Move 6 — The graduation ledger.** "Here's what's pilot-grade: SQLite instead of Postgres, single-node ingestion, no HA. Here's the production replacement: managed Postgres in their VPC, orchestrator we agree on with their team, two-node deployment behind their load balancer. The data model and the entity-resolution rules carry forward untouched." Explicitly labeling debt reads as engineering maturity, not confession.

The stack picks worth knowing by heart for pilots:

- **Storage**: SQLite for the pilot, Postgres for production. Never Mongo unless the customer already runs it.
- **Ingestion**: cron + idempotent Python for the pilot, orchestrator (Airflow, Prefect, or theirs) for production.
- **API**: `http.server` or FastAPI single-file for the pilot; something behind their load balancer for production.
- **Frontend**: one HTML file with vanilla JS or lightweight framework for the pilot — deploys anywhere.
- **Auth**: their SSO always, with basic-auth-plus-network-restriction as the week-one bridge.
- **LLM**: hosted API by default with a DPA in place, VPC-deployed frontier model (Bedrock/Azure) when data can't leave their tenancy, on-prem open weights only when air-gapped or explicitly required.

## FIELD NOTES

- Interviewers give you the customer's constraints for a reason. When they say "regulated bank," they want to hear ATO/SR-11-7/private CA/audit logging. When they say "small startup customer," they want to hear "single container, hosted API, ship in a week." Reading the constraint accurately is half the round.
- Never propose Kafka in a pilot round. Never propose Kubernetes. Never propose a service mesh. Every one of these is a red flag the first time you say it, unless the interviewer has just described a customer that already runs it. Boring beats novel.
- The best system-design candidates ask *time* questions: "when's the demo?" "when's renewal decided?" A design that ships value in week two beats a design that ships production-quality in month six, and stating that trade-off aloud is the point.
- LLM feature? Cost estimate belongs in the design, not the "operations" round. Interviewers ask "what does this cost per month at 200 users, 10 queries a day?" and the strong answer walks through tokens per query, model tier, and gives a range with the levers named.

## INTERVIEW ANGLE

Meta-questions specific to system-design rounds:

1. "How do you know when your design is over-engineered?" — the model answer: "when a component doesn't serve a named constraint. Every box on my diagram should map to a specific pilot requirement or a specific failure mode."
2. "What do you do when you disagree with the customer's stated architecture requirement?" — interviewers watch for pushback-with-respect: raise it once with evidence, then either the customer updates or you build to their constraint and note the trade-off in the debt ledger.
3. "Walk me through a design decision you regretted." — have one ready. The best version names the wrong choice, the signal you missed, and what you'd probe for next time.

## DRILL

Give yourself 45 minutes. Prompt: "Design an entity-resolution pilot for a healthcare payer. They have three claims systems, ~2M patient records total, need to run in their AWS GovCloud VPC, primary user is a data-stewardship team of eight, must integrate with their Okta, needs to produce a merged patient view accessible via API and reviewable via a simple UI. Deploy target is six weeks." Draw the six-move sequence on paper: data path, identity, deployment boundary, failure modes, graduation ledger. Then grade yourself against these questions: did you name the ingress path realistically? Did you name their IdP integration timeline? Did you land on SQLite-or-Postgres for the pilot without over-choosing? Did you draw the security boundary line? Did you write down three failure modes with instrumentation? Repeat weekly with different scenarios (retail, logistics, government) until the six moves are reflexive.
