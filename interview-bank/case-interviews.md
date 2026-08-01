# Case Interviews — 5 Fully Worked Decomps

The decomp (decomposition) interview is Palantir's signature round, and every serious
FDE loop now runs a version of it. The interviewer hands you a messy, real-world
operational problem with no clean answer and watches how you think: do you ask before
you assume, structure before you solve, quantify before you promise, and ship before
you perfect?

There is no "right answer." There is absolutely a right *shape* of answer, and it looks
the same across all five cases below:

1. **Clarify** — 3–5 sharp questions that change your approach depending on the answer.
2. **Decompose** — users, data sources, entities, and the metric, before any features.
3. **80/20** — what you'd ship in week one, and what you're deliberately not doing.
4. **Estimate** — back-of-envelope with explicit ranges and stated assumptions.
5. **Risks** — what kills this, said out loud, unprompted.

Practice these aloud, timed at 25–35 minutes each. Reading them silently is about
one-third as useful.

---

## Case 1 — Hospital ER Wait Times

### The prompt, as the interviewer states it

> "A large hospital network — 12 hospitals — says their emergency room wait times are
> too long and getting worse. Patients are leaving without being seen. The COO has
> asked for help. You're on site Monday. What do you do?"

That's it. No data dictionary, no metric, no scope. That's the point.

### Clarifying questions (ask 4–6, then move — don't interrogate forever)

- **"When you say wait time, what specifically is being measured today — door to triage,
  door to doctor, door to disposition? And who looks at that number?"**
  This is the highest-value question in the case. "Wait time" is at least four different
  intervals, they have different owners, and the fix differs completely by interval.
- **"Is this a network-wide problem or is it concentrated? Do we know if 2 of the 12
  hospitals are driving it?"** — concentration determines whether this is a process
  problem at specific sites or a systemic one.
- **"What does 'patients leaving without being seen' run at today, and where is that
  recorded?"** — LWBS (left without being seen) is a standard, regulated ER metric;
  knowing they track it tells you data exists.
- **"What systems are in play — one EHR across all 12 hospitals, or several?"** — one
  Epic instance vs a patchwork changes the integration plan entirely.
- **"What's been tried already?"** — you are almost never the first attempt, and the
  corpses of prior attempts are a map of the political terrain.
- **"Who feels this pain most — the COO reading a report, or the charge nurses living
  it?"** — tells you who your users and champions are.

**Interviewer's likely answers** (typical of how this case runs): wait is measured
door-to-provider, inconsistently; three hospitals are notably worse; LWBS is around
4–6% at the bad sites (national benchmarks put ~2% as tolerable); two EHR systems
across the network (recent acquisition); a consultant produced a slide deck last year
and nothing changed.

### Decomposition

**Users** (in order of importance to the pilot):

| User | What they need | Cadence |
|---|---|---|
| Charge nurse / ER ops lead | Live view of current ER state: census, waits, bottleneck stage | Real-time, per shift |
| ER medical director | Which stage of the patient journey is the bottleneck, by hour/day pattern | Daily/weekly |
| Network COO | Cross-hospital comparison, trend, LWBS — the renewal metric | Weekly |
| Bed management / inpatient units | Boarding visibility (ER patients waiting for inpatient beds) | Real-time |

Note the trap: the COO commissioned this, but the *product* has to serve the charge
nurse or nothing changes operationally. Say this out loud in the interview.

**Data sources:**

- EHR event timestamps: arrival, triage start/end, room placement, provider assignment,
  disposition decision, departure — the ADT (admit/discharge/transfer) event stream is
  the spine.
- Bed management system (may be inside the EHR, may not): inpatient bed availability —
  because ER "wait" is often actually inpatient *boarding* backing up into the ER.
- Staffing/scheduling system: nurses and providers on shift per hour.
- LWBS records (usually EHR disposition codes, notoriously under-coded).
- Expect: two EHRs with different event vocabularies, timestamps of wildly varying
  reliability (triage time is a human clicking a button — or not clicking it until
  20 minutes late), and HL7 feeds as the realistic integration path.

**Entities / ontology:**

- **Patient visit** (the core object): arrival time, acuity (ESI 1–5 triage score),
  chief complaint category, and a chain of timestamped **stage events**.
- **Stage** — the ordered journey: arrival → triage → waiting room → room → provider →
  decision → (discharge | admit → **boarding** → inpatient bed).
- **Hospital / ER pod** — location hierarchy.
- **Shift** — staffing context linked to time windows.
- Links: visit *occurred-at* hospital, visit *during* shift, visit *transitioned*
  stage-to-stage. The killer analytical object is the **stage interval** — the elapsed
  time between consecutive events per visit — because the whole case reduces to
  "which interval blew up, where, when."

**Metric definition** — do this explicitly; it's heavily graded:

- Primary: **median and 90th-percentile door-to-provider time**, by hospital, by
  acuity band, by hour-of-week. Median for the typical experience, P90 because ER
  pain lives in the tail, acuity-banded because averaging a heart attack with a
  sprained ankle produces a meaningless number.
- Guard metric: **LWBS rate** — the "patients gave up" number, and the one the COO
  quoted, so it must appear even though it's noisy.
- Diagnostic metric: **boarding hours** (decision-to-admit until ER departure),
  because if boarding is the real problem, the ER is the symptom and the inpatient
  bed process is the disease — a genuinely common finding in real deployments.
- Anti-gaming note (say it): if you report door-to-provider alone, sites can game it
  with a "provider in triage" drive-by that starts the clock without starting care.
  Pair speed metrics with a care-outcome guard.

**80/20 week-one solution:**

Ship a **retrospective bottleneck dashboard for the three worst hospitals** — not
real-time, not predictive, not all twelve sites:

1. Pull 6–12 months of ADT event history for the 3 problem hospitals (batch export,
   no live interface needed yet — deliberately avoids the hard HL7 integration).
2. Build the visit → stage-interval model; quarantine the garbage timestamps and
   *report* the garbage rate (it will be material, and surfacing it is value).
3. One screen: stage-interval breakdown by hour-of-week heat map, acuity-banded,
   per hospital — "your Tuesday 6pm blowup is boarding, not triage."
4. Weekly working session with each site's ER director walking the findings.

Why this cut: it needs no real-time infrastructure, no writes to clinical systems, no
clinical risk review beyond read access — and it produces the "we never knew that"
moment (e.g., boarding drives 60% of the tail) that funds phase two. Phase two is the
live charge-nurse view; phase three is staffing-to-demand modeling.

**Risks (name them unprompted):**

- **Timestamp fiction**: stage events are entered late or never; if triage timestamps
  are 30% missing, the interval analysis needs honest caveats and possibly a
  time-motion sampling study to calibrate.
- **The finding indicts someone**: "boarding is the problem" moves blame from the ER
  to inpatient units — expect political resistance to the answer; brief the COO
  privately before the cross-department readout.
- **Two-EHR mapping**: event vocabularies won't align; budget real time for the
  semantic mapping and validate it with clinicians, not just the data dictionary.
- **PHI everywhere**: BAA before any data moves, minimum-necessary fields (you don't
  need diagnosis detail for flow analysis), de-identified demo materials.
- **Clinical-workflow sensitivity**: anything that later *recommends* actions
  (routing, staffing) starts touching clinical decision territory — keep the pilot
  firmly descriptive.

### Back-of-envelope estimate

State assumptions, compute in ranges, sanity-check the ends:

- A busy ER sees **150–300 visits/day**; take ~200. Three hospitals × 200 × 365 ≈
  **~220k visits/year** of history (range: 150k–330k).
- Say ~15–25 timestamped events per visit → **~3–5M event rows/year** for three
  sites. Trivial volume — SQLite-to-small-Postgres territory; the hard part is
  semantics, not scale. Say that explicitly: *"this is a small-data, hard-meaning
  problem."*
- Value sizing: if LWBS is 5% at ~200 visits/day, that's ~10 walkouts/day/site.
  Reimbursement per avoided walkout maybe $400–$1,000 → **$1.2M–$3.3M/year of
  recoverable revenue per site** if LWBS could be halved (wide range, stated as
  such) — plus the unquantified safety and reputation upside. This is the number
  that makes the COO's renewal case.

### What interviewers grade

| Signal | What strong looks like |
|---|---|
| Clarification quality | Asked what "wait time" *is* before solving it; asked what's been tried |
| Structure | Users → data → entities → metric → solution, not feature soup |
| Metric sophistication | P90 + acuity banding + guard metric; anti-gaming awareness |
| 80/20 instinct | Chose 3 hospitals retrospective over 12-hospital real-time; can say *why* |
| Domain humility | Flagged timestamp quality and boarding without pretending ER expertise |
| Political awareness | Noticed the finding has a blame arrow; planned the COO pre-brief |
| Estimation | Ranges with stated assumptions; recognized small-data/hard-meaning |
| Compliance reflex | BAA/PHI handling raised without being asked |

---

## Case 2 — Airline Irregular-Operations Recovery

### The prompt, as the interviewer states it

> "A mid-size airline — about 600 flights a day — gets crushed every time there's a
> major storm. Cancellations cascade for two or three days after the weather clears.
> Their ops team wants help recovering faster. Where do you start?"

### Clarifying questions

- **"When recovery goes badly, what's the binding constraint — aircraft out of
  position, crews timing out, or the decision process itself?"** The three have
  completely different solutions; crew legality is the usual sleeper answer.
- **"What does the ops team use today during a disruption — what screens are open in
  the operations center at hour zero of a storm?"** — you're building into an
  existing tool ecology, and the answer reveals the real workflow.
- **"Is the pain making *good* decisions, or *executing* decisions fast enough — or
  seeing the situation at all?"** — situational awareness vs optimization vs
  execution are different products.
- **"Hub-and-spoke or point-to-point? One hub or several?"** — cascade dynamics and
  recovery options differ fundamentally.
- **"What's a bad event cost — do they have a number for a 2-day irregular-ops
  (IROPS) event?"** — anchors the value case.
- **"Do they already have a recovery optimization system (there are established
  vendors) that they don't trust or don't use?"** — very common; the answer might be
  a decision-support layer, not a rival optimizer.

**Typical interviewer feed**: hub-and-spoke, one main hub; the ops center juggles
seven screens and a phone bridge; crew legality is discovered late ("we rebuilt the
aircraft plan, then found out the crews time out"); a legacy optimizer exists but
planners override it because they don't trust its assumptions; a bad storm costs
"millions" but nobody has a crisp number.

### Decomposition

**Users:**

| User | Need |
|---|---|
| IROPS duty manager (the decision-maker at hour zero) | One coherent picture: which flights are recoverable, what each option costs |
| Crew scheduling desk | Crew legality horizon: who times out when, under each scenario |
| Aircraft routing desk | Tail positions and maintenance constraints |
| Customer ops | Passenger impact per option (misconnects, stranded counts) |
| VP Ops | Post-event review: recovery time vs benchmark, decision audit |

**Data sources:**

- Flight schedule + real-time status (the operational spine; usually accessible via
  the ops database or standard aviation data feeds).
- Aircraft rotations (tail assignments) + maintenance requirements (a tail due for a
  maintenance check *must* be routed to a maintenance station — a hard constraint that
  breaks naive recovery plans).
- Crew pairings and duty-time records — the legality clock (regulatory duty-time
  limits); this data lives in crew management systems and is the most integration-hostile
  and most decision-critical source in the case.
- Passenger bookings and connections (PNR-level) for impact scoring.
- Weather feeds and airport slot/curfew constraints.

**Entities / ontology:**

- **Flight** (scheduled leg) — linked to **Aircraft (tail)**, **Crew pairing**,
  **Passengers**, origin/destination **Airports**.
- **Rotation** — the sequence of legs a tail flies; cancellations break rotations, and
  a broken rotation is how a Tuesday storm cancels a Thursday flight. This link
  structure *is* the cascade — say that sentence in the interview.
- **Crew pairing** — sequence of legs a crew works, with a running legality clock;
  a delayed inbound quietly converts a legal crew to an illegal one hours later.
- **Disruption event** — the storm, with an affected time-space window.
- **Recovery action** — cancel, delay, swap tails, reroute, reserve crew call-out —
  each with cost and constraint links.

**Metric definition:**

- Primary: **time-to-recovery** — hours from end-of-disruption until the operation
  returns to ≥98% of planned completion factor. It's measurable from history,
  benchmarkable across past events, and it's the pain as stated.
- Components worth showing separately: completion factor during the event, cancellations
  in the *post-event tail* (the cascade signature), crew-legality-caused cancellations
  specifically (the avoidable subset — this is the money metric if the hypothesis
  holds), passenger-hours of delay.
- Anti-gaming: recovery speed can be bought by pre-cancelling aggressively — a strategy
  that sometimes *is* correct — so pair time-to-recovery with total passenger disruption
  so the trade-off is visible rather than gamed.

**80/20 week-one solution:**

Do **not** build an optimizer. Week one is a **disruption situational-awareness board**
built on read-only feeds:

1. Ingest schedule, tail rotations, and crew pairings (batch snapshots every few
   minutes are fine; true streaming is phase-two polish).
2. Compute and display the two cascade views nobody has in one place: **broken-rotation
   propagation** ("this cancellation strands tail N123 in Denver; here are the next
   4 legs at risk") and the **crew legality horizon** ("14 crews time out within 6
   hours under current delays — these 9 flights lose crews before aircraft").
3. One screen for the duty manager, replayable after the event for the post-mortem.
4. Validate against the last two real IROPS events retrospectively: "our board would
   have flagged the Thursday cancellations on Tuesday at 14:00."

Why this cut: the customer's stated failure ("we discover crew timeouts late") is an
*information* failure, not an optimization failure — so the 80/20 is making the
constraint visible early. It requires no write access, competes with no incumbent
optimizer (it *feeds* human decisions, sidestepping the trust problem they already
have with black-box optimization), and the retrospective replay proves value with zero
operational risk. Recommendation-ranking comes later, once trust exists.

**Risks:**

- **Crew data access**: crew systems are legally sensitive (duty-time is regulated,
  union-visible) and technically gnarly; this is the long-pole integration — start it
  day one, ship the aircraft-side board even if crew data lags.
- **Trust transfer**: planners overrode the last system; if the board is wrong once
  in a visible way early, it's dead — so surface data freshness on-screen and
  under-claim ("decision support, not decisions").
- **Latency honesty**: minutes-old snapshots are fine for legality horizons, not for
  gate-level tactics — scope claims accordingly.
- **Storm-day availability**: the tool's whole value is during chaos; it must not
  share failure modes with the infrastructure that fails during chaos (deploy
  independent of the systems it monitors where possible).
- **Union/workforce sensitivity**: anything touching crew data gets read by labor
  relations — keep the tool descriptive about legality, never evaluative about people.

### Back-of-envelope estimate

- 600 flights/day, hub-and-spoke. A major storm hits the hub for a day: assume
  **30–50% of flights cancelled/delayed day zero** → ~200–300 disrupted flights.
- Cascade math: each broken rotation strands a tail; with ~150–200 tails and 3–4
  legs/tail/day, a hub closure misplaces maybe **40–80 tails**. Un-repositioned, each
  costs 1–3 further legs → the observed 2–3 day tail of ~100–300 knock-on
  cancellations. This is consistent with their stated pain — say the sanity check.
- Cost anchor: industry rough numbers put a cancellation's cost at **$10k–$50k+**
  (rebooking, compensation, crew repositioning, lost revenue; wide by market and
  aircraft size). If better sequencing avoids even **15–25%** of ~200 knock-on
  cancellations per event, that's **30–50 flights × $10–50k ≈ $0.3M–$2.5M per major
  event**; at 4–8 events/year: **$1M–$20M/year** — a deliberately wide range,
  stated with its drivers, and still comfortably above pilot cost at the low end.
  Cross-check plausibility: airlines report IROPS as a top-3 controllable cost;
  the low end being worth it is what makes the pilot fundable.

### What interviewers grade

| Signal | What strong looks like |
|---|---|
| Constraint identification | Found crew legality as the binding constraint via questions, not assumption |
| Restraint | Chose visibility over optimization; articulated *why* (trust, risk, incumbent) |
| Ontology as cascade | Modeled rotations/pairings so the cascade falls out of the link structure |
| Incumbent awareness | Asked about existing optimizers; positioned alongside, not against |
| Retrospective validation | Proposed replaying past events as zero-risk proof |
| Estimation | Cascade arithmetic with ranges; cost anchor with stated uncertainty |
| Operational empathy | Designed for hour-zero chaos (one screen, freshness shown, replayable) |

---

## Case 3 — Manufacturer Warranty-Claim Fraud

### The prompt, as the interviewer states it

> "A heavy-equipment manufacturer pays out about $400M a year in warranty claims
> through a network of roughly 2,000 independent dealers who perform the repairs and
> submit claims. Finance believes 5–10% of that is fraud or abuse, but the claims team
> of 25 reviewers can only inspect a fraction of claims. Help them."

### Clarifying questions

- **"What does the claim record actually contain — parts, labor hours, failure codes,
  narrative text, photos?"** — richness of the claim record determines what detection
  is even possible.
- **"What kinds of abuse do they *know* about from past investigations — inflated labor
  hours, phantom repairs, part harvesting, goodwill abuse?"** — known typologies seed
  the detection design and the eval set.
- **"What happens today when a claim looks suspicious — and what's the dealer
  relationship cost of a false accusation?"** — the action side (audit? clawback?
  dealer termination?) shapes how confident flags must be. Dealers are also
  *customers* of the manufacturer — this tension is the case's political core.
- **"Is the 5–10% belief based on anything — sampled audits, industry benchmarks,
  a gut number?"** — determines whether ground truth exists (it usually barely does).
- **"Are reviewers currently selecting claims randomly, by amount threshold, or by
  intuition?"** — the baseline you must beat is *their current targeting yield*.
- **"Any labeled history — past claims proven fraudulent through audit?"** — the
  supervised-learning question, asked without assuming the answer is yes.

**Typical feed**: claims have parts + labor + failure codes + free-text narrative;
known typologies include inflated labor and repeated part replacement; today's review
is amount-threshold plus tribal knowledge; a few hundred historically confirmed bad
claims exist from past audits; false accusations are commercially expensive — dealers
have alternatives.

### Decomposition

**Users:**

| User | Need |
|---|---|
| Claims reviewer (the 25) | A ranked queue: which claims to inspect today, *with reasons* |
| Claims/audit manager | Queue performance: yield, coverage, recovered dollars |
| Dealer relations | Defensible evidence trail before any dealer is confronted |
| Finance VP | Recovered/deterred dollars — the renewal number |

**Data sources:**

- Claims history (multi-year): claim lines with part numbers, labor operations and
  hours, failure codes, dates, amounts, free-text repair narrative.
- Dealer master (2,000 dealers; expect duplicates, ownership changes, ID reuse — an
  entity-resolution job hiding inside a fraud case: flag it).
- Equipment/telematics master: machine model, age, usage hours — a claim's
  plausibility depends on the machine's life stage; modern heavy equipment often has
  telematics (actual operating hours), which is a gift when present.
- Standard repair-time tables (the book hours for each labor operation — the anchor
  for inflated-labor detection).
- Parts shipment/inventory data (did the dealer even *stock* the part they claim to
  have installed? — phantom-repair detection).
- Past audit outcomes: the few hundred confirmed-bad labels.

**Entities / ontology:**

- **Claim** → lines of **Part** and **Labor operation**; submitted-by **Dealer**;
  against **Machine** (model, age, hours); with **Failure code** and narrative.
- **Dealer** — the behavioral unit: fraud is dealer-patterned far more than
  claim-patterned, so dealer-level aggregates are first-class objects.
- **Peer group** — dealers of similar size/region/product mix; "abnormal" only means
  something *relative to peers* — this normalization is the analytical heart.
- **Audit case** — links claim(s) → investigation → outcome; the label-generating
  machine and the system's feedback loop.

**Metric definition:**

- Primary: **review yield** — confirmed-bad rate among reviewed claims. Today's
  baseline is whatever amount-threshold targeting yields (measure it in week one —
  say maybe 5–15% of reviews find issues); the pilot's claim is "same 25 reviewers,
  2–4× the yield."
- Money metric: **recovered + deterred dollars** — recovery is measurable; deterrence
  (dealers behave better when detection visibly improves — a real, documented effect
  in warranty programs) shows up as claim-pattern shifts and should be tracked
  honestly as an estimate, not claimed as precise.
- Fairness guard: **false-accusation rate** and per-dealer flag concentration review —
  one wrongly-terminated dealer can cost more than a year of recoveries.
- Explicitly *reject* "fraud detected %" as primary — ground truth is only ever
  established by audit, so any detected-rate number is circular. Saying this earns
  points.

**80/20 week-one solution:**

Rules-first ranked queue, ML later:

1. Ingest 2–3 years of claims + dealer master (resolve dealer entities first — dedupe
   before you profile, or dealer-level stats are fiction).
2. Implement the **known typologies as transparent scored rules**: labor hours vs
   standard repair times (z-score by operation), claim rate per machine-hours vs
   peer group, repeated same-part-same-machine replacements, claims just under the
   auto-approval threshold (threshold-hugging is a classic tell), failure-code vs
   machine-age implausibility, narrative red-flag patterns.
3. Rank claims (and dealers) by combined score; ship as a **review queue with
   reasons** — "flagged: labor 3.1× standard for this operation; dealer is 97th
   percentile for this part's replacement rate" — because reviewers act on reasons,
   not scores, and the evidence trail is what dealer relations needs.
4. Feed every review outcome back as a label. The pilot *manufactures its own
   training data* — by month three you have thousands of labels and can credibly
   discuss a learned model as phase two. LLM assist enters cheaply here too:
   narrative-text summarization and inconsistency-flagging inside the review UI,
   never as an autonomous accuser.

Why this cut: transparent rules are defensible to dealers, debuggable, tunable in
days, and they beat threshold-targeting immediately; a black-box model in week one
would face the trust and label-scarcity problems simultaneously and lose both.

**Risks:**

- **Label scarcity and bias**: historical audit labels reflect what the old targeting
  *looked at* (big claims) — training or evaluating naively on them bakes in the
  blind spots; keep a random-sample review lane (~5–10% of capacity) forever, as the
  unbiased measurement floor.
- **Dealer blowback**: flags leak, dealers are customers; the system must speak in
  "anomaly, review warranted" language with evidence, never "fraud" — and
  dealer-facing action stays entirely human.
- **Feedback loops**: dealers adapt to visible rules (threshold-hugging is proof they
  already adapt); expect drift, monitor rule-hit-rate trends, refresh typologies.
- **Base-rate honesty**: if true abuse is 5%, even a good flagger produces many false
  positives per true hit at aggressive coverage — set reviewer expectations with
  precision-at-K numbers, not "fraud detector" framing.
- **The 5–10% may be wrong**: the pilot might *disprove* finance's belief, or find
  process leakage (miscoded goodwill, training gaps) rather than fraud — pre-agree
  that this counts as success, because it's worth real money too.

### Back-of-envelope estimate

- $400M/year across, say, **400k–800k claims/year** (avg claim $500–$1,000 for parts
  + labor; heavy equipment skews high — state the assumption). Take ~500k claims.
- 25 reviewers × ~8–15 claims/day × 220 days ≈ **44k–83k reviews/year** → coverage of
  roughly **6–17%** of claims. Coverage is scarce; targeting is everything — this
  arithmetic *is* the case for the product, so do it aloud.
- Value: if abuse is 5–10% of $400M ($20–40M) and better targeting converts even
  **10–20%** of it into recovery + deterrence, that's **$2M–$8M/year** against a
  pilot cost of low hundreds of thousands — a 10–40× return with all assumptions
  stated and each one halvable without killing the case. The robustness-to-halving
  point is worth making explicitly.

### What interviewers grade

| Signal | What strong looks like |
|---|---|
| Baseline thinking | Asked what current targeting yields; framed the pilot as beating it |
| Ground-truth skepticism | Caught that "fraud rate" is unknowable without audits; rejected circular metrics |
| Rules-before-ML judgment | Transparent typology rules first, with the label-manufacturing loop as the ML path |
| Label-bias awareness | Random-sample lane to correct audit-selection bias |
| Political sensitivity | Dealers-as-customers tension; "anomaly" language; human-only accusations |
| Entity-resolution reflex | Spotted the dealer-dedup problem inside the fraud problem |
| Estimation | Coverage arithmetic; value range robust to halved assumptions |

---

## Case 4 — Bank AML Alert Triage with LLMs

### The prompt, as the interviewer states it

> "A regional bank's anti-money-laundering team receives about 10,000 alerts a month
> from their transaction-monitoring system. Over 90% are false positives, but every
> alert must be dispositioned, and each takes an analyst 30–60 minutes of gathering
> and writing. They've asked whether LLMs can help. The compliance officer is
> intrigued and terrified in equal measure. Design the engagement."

### Clarifying questions

- **"Where does analyst time actually go in those 30–60 minutes — gathering data,
  analyzing it, or writing the disposition narrative?"** — the case pivots on this:
  if 70% is gathering and writing, the LLM opportunity is *assistance*, not
  *decision-making*, which is also exactly what compliance can approve.
- **"What's the regulatory posture — has the bank discussed AI in AML with their
  regulator or examiners? Any model-risk-management requirements?"** — banks run
  formal model governance (in the US, examiners scrutinize monitoring changes);
  everything you build enters that regime; asking signals you know the terrain.
- **"Can we get historical alerts with their final dispositions and the analyst
  narratives?"** — thousands of labeled cases with written rationales exist by
  construction. This is unusually good golden-set raw material — notice it aloud.
- **"Is *closing* alerts ever automatable in their view, or must every disposition
  have a human signature?"** — determines the ceiling; assume human-signs-everything
  and design for it.
- **"Which alert types dominate volume?"** — structuring, velocity, geography rules
  etc.; concentration means you can pilot on the top one or two typologies.
- **"On-prem, private cloud, or is an external LLM API even conceivable here?"** —
  banks often require VPC or on-prem inference; this shapes the architecture on day
  one.

**Typical feed**: ~70% of analyst time is gathering context from 5–7 systems and
writing the narrative; every disposition needs a human signature; historical
dispositions with narratives are available; two alert typologies are 60% of volume;
external APIs are possible only under the bank's cloud tenancy (VPC inference).

### Decomposition

**Users:**

| User | Need |
|---|---|
| AML analyst | One assembled case file per alert + a draft narrative to edit — minutes saved per alert |
| QA reviewer / team lead | Sampling view, consistency checks across analysts |
| BSA/compliance officer | Auditability, model-risk documentation, control evidence — the approver |
| Model risk management | Validation package: evals, monitoring, change control |

**Data sources:**

- Alert records from the transaction-monitoring system (rule fired, parameters,
  triggering transactions).
- Core banking: account and transaction history for the subject.
- KYC/CDD profiles: who the customer claims to be, expected activity, risk rating.
- Prior alerts and dispositions for the same subject (repeat-subject context is
  gold and analysts assemble it by hand today).
- Sanctions/watchlist screening results; adverse-media where the bank licenses it.
- The historical corpus: alerts + final dispositions + analyst narratives — the
  golden set and few-shot library.

**Entities / ontology:**

- **Alert** → generated-by **Rule** → concerning **Subject** (customer entity —
  note the entity-resolution needle: the same real-world person across accounts) →
  involving **Transactions** → linked to **Counterparties**.
- **Case file** — the assembled evidence bundle (the pilot's core artifact).
- **Disposition** — the human decision (close / escalate to SAR investigation) +
  narrative + signature + timestamps.
- Alert *history chains* per subject — the "third velocity alert this year, prior
  two closed as payroll pattern" context that changes dispositions.

**Metric definition:**

- Primary: **minutes per disposition** (measured from the case-management system's
  own timestamps, per alert type, before vs after) — target range stated honestly,
  e.g. 40 → 15–25 minutes on piloted typologies.
- Quality guards (non-negotiable in this domain, weighted equally in reporting):
  **QA agreement rate** on sampled dispositions (assisted must be ≥ unassisted),
  **escalation-rate stability** (if SAR-escalation rate shifts materially
  post-assistance, stop and investigate — drift here is a regulatory event, in
  either direction), and **draft-edit distance** (how much analysts change the
  draft — a live proxy for draft quality and for automation-complacency).
- Explicitly rejected metric: "alerts auto-closed" — the design goal is *assisted
  humans*, and saying "we deliberately do not measure or pursue auto-closure in the
  pilot" is the sentence that keeps the compliance officer in the room.

**80/20 week-one(-ish) solution:**

Two-layer build, and the first layer isn't LLM at all:

1. **Case-file assembly automation** (deterministic integration work): one click
   pulls subject KYC, 12-month transaction summary, prior-alert history, and
   screening results into a single organized view. This alone attacks the biggest
   time block with zero model risk — and it's the retrieval substrate the LLM
   needs anyway. Ship this first; it de-risks everything after it.
2. **Draft narrative generation** (the LLM layer, VPC-hosted inference): grounded
   strictly in the assembled case file, structured to the bank's narrative
   template, with **every factual sentence citing its source field**, few-shot
   prompted from the bank's own historical narratives for voice and format.
   Analyst edits and signs; edits are logged (the edit-distance metric and
   tomorrow's improvement data).
3. **Eval harness before wide rollout**: golden set of a few hundred historical
   alerts across the two pilot typologies; measure draft factual accuracy
   (claim-by-claim against source data), template compliance, and blind
   analyst preference vs historical human narratives.
4. Scope discipline: two alert typologies, one analyst pod (5–8 analysts),
   assisted-only, full audit logging of prompt/context/output/edit per alert.

**Risks:**

- **Hallucinated facts in a regulatory document**: a narrative asserting a
  transaction that doesn't exist is the nightmare; mitigations: strict grounding,
  per-sentence citations mechanically verified against the case file, and the
  human signature — but say plainly that the *system design assumes* nonzero draft
  errors and makes them catchable.
- **Automation complacency**: analysts rubber-stamping good-looking drafts; monitor
  edit-distance distributions (all-zero edits is a red flag, not a success),
  QA-sample assisted work at a *higher* rate initially.
- **Model risk / examiner scrutiny**: the assistant will be examined as a model
  under governance; build the validation package (evals, monitoring, change
  control, documented limitations) as a first-class deliverable, not paperwork
  after the fact.
- **Data movement**: subject financial data to inference infrastructure — VPC
  inference, no training on bank data, retention terms in writing, all pre-cleared
  with information security before the first token flows.
- **Bias surface**: consistency checks that dispositions aren't drifting
  differentially across customer segments — examiners can and do ask.

### Back-of-envelope estimate

- 10,000 alerts/month × ~45 min ≈ **7,500 analyst-hours/month** ≈ **45–55 FTEs** of
  disposition work (at ~140–160 productive hours/month). Sanity check: that implies
  a 50-ish analyst team or backlog pain — consistent with them seeking help.
- Pilot scope: 2 typologies ≈ 60% of volume, one pod ≈ 15% of analysts → directly
  touched work ≈ **~650–1,000 hours/month**.
- If assisted time is 40 → 20 min (range 15–25), that's **~45–60% reduction** on
  piloted work ≈ 300–500 hours/month in the pilot alone; extrapolated to full
  volume: **20–30 FTE-equivalents ≈ $2.5M–$4.5M/year** at loaded cost (state
  loading assumption, ~$120–150k) — against LLM inference costs of roughly
  10k × full rollout × a few cents-to-dimes per alert ≈ **low tens of thousands
  per year**: a rounding error against the labor line, and worth saying so.
- Compliance framing: the value narrative to the buyer isn't only cost — it's
  capacity redeployed from mechanical triage to actual investigation, which is the
  story the compliance officer can tell the examiner with pride rather than anxiety.

### What interviewers grade

| Signal | What strong looks like |
|---|---|
| Time-decomposition instinct | Asked *where* the 45 minutes goes; found the non-LLM 70% |
| Assist-not-decide judgment | Human-signs-everything by design; rejected auto-closure unprompted |
| Regulatory literacy | Model governance, examiner scrutiny, VPC inference raised naturally |
| Eval discipline | Golden set from historical dispositions; accuracy measured claim-by-claim |
| Hallucination containment | Citations + mechanical verification + edit-distance monitoring |
| Layered de-risking | Deterministic assembly shipped before any generation |
| Estimation | FTE math with sanity check; noted inference cost is negligible vs labor |

---

## Case 5 — Retailer Inventory Shrinkage

### The prompt, as the interviewer states it

> "A grocery and general-merchandise chain — 800 stores — is losing about 2.5% of
> revenue to shrinkage: theft, damage, administrative error, vendor fraud. Industry
> average is closer to 1.5%. The loss-prevention VP has budget and a mandate. Where
> do you start?"

### Clarifying questions

- **"Is the 2.5% uniform, or concentrated — by store, region, category?"** — shrink
  is almost always concentrated (some stores at 4–5%, many near benchmark); the
  concentration *is* the strategy.
- **"How is shrink measured today — cycle counts, annual physical inventory, POS
  reconciliation — and how much do they trust the measurement?"** — shrink is a
  *residual* (book inventory minus counted inventory); if counts are bad, "shrink"
  partly measures counting error. This question signals you understand the number's
  fragility.
- **"What's the assumed split between external theft, internal theft, process error,
  and vendor issues — and what's that assumption based on?"** — industry surveys
  attribute large shares to each; the mix determines the solution, and their
  assumed mix is usually a guess.
- **"What data exists at what grain — SKU-level perpetual inventory? POS transaction
  logs? Receiving records? Case-level or unit-level?"**
- **"What has loss prevention tried — cameras, EAS tags, analytics vendors?"** —
  incumbent-and-graveyard question.
- **"What action capacity exists — how many LP investigators, and what can stores
  actually change (layout, process, staffing)?"** — detection without action
  capacity is a dashboard nobody wanted.

**Typical feed**: heavily concentrated — top 100 stores drive an outsized share;
measurement is cycle counts on high-value SKUs plus twice-yearly full counts, trusted
"mostly"; attribution split is a guess based on industry surveys; SKU-level perpetual
inventory and full POS logs exist; a camera-analytics vendor pilot fizzled; ~40 LP
investigators for 800 stores.

### Decomposition

**Users:**

| User | Need |
|---|---|
| LP investigators (the 40) | A ranked target list: which stores/categories/patterns to work this month, with evidence |
| Store managers | Their store's shrink profile vs peers, and which *controllable* driver is worst |
| Regional ops | Cross-store comparison, process-fix tracking |
| LP VP | Shrink-rate trajectory on a credible measurement basis — the renewal number |

**Data sources:**

- Perpetual inventory movements (SKU × store × day: receipts, sales, adjustments,
  transfers, counts) — the spine.
- POS transaction logs, *including* voids, refunds, no-sales, discounts, and
  cashier ID — sweetheart fraud (fake voids/refunds by employees) lives here and
  is one of the most data-detectable shrink components.
- Receiving records vs vendor invoices/ASNs (short-shipping and vendor fraud live
  in this delta).
- Cycle count and physical inventory results (the measurement layer itself).
- Store attributes for peer-grouping: format, size, region, demographics, staffing.
- Employee scheduling (linking anomaly windows to shifts — handle with explicit
  care, see risks).

**Entities / ontology:**

- **SKU × Store** — the atomic shrink cell; everything aggregates up from here.
- **Inventory movement** — typed events (sale, receipt, adjustment, count-correction);
  shrink is the residual that makes the ledger balance, so movement typing quality
  *is* measurement quality.
- **Store** → **peer group** (like Case 3, "abnormal" only exists relative to peers).
- **Transaction pattern** — void/refund/discount behaviors, linkable to **register**
  and **operator** (an entity handled under strict governance).
- **Vendor** → receiving deltas.
- **Intervention** — a process change, investigation, or fix, linked to its target
  cell and tracked for effect: the object that makes this an operations tool rather
  than a report.

**Metric definition:**

- Primary: **shrink rate (% of sales at cost), by store × category, measured on a
  consistent counting basis** — with the honesty note that the pilot may *raise*
  measured shrink initially by improving counting, and the customer must be
  pre-agreed that better measurement showing worse numbers is progress, not failure.
  Getting this agreement up front is an FDE move worth stating explicitly.
- Targeting metric: **investigation yield** (confirmed findings per investigator-
  month, vs their current intuition-driven baseline) — the 40 investigators are the
  scarce resource, exactly like Case 3's reviewers.
- Leading indicators: void/refund anomaly rates, receiving-delta rates, count-
  correction frequency — these move in weeks, while true shrink confirms in
  6–12 month count cycles; the pilot needs the leading indicators to show motion
  inside pilot timelines, and you should say that timing problem out loud.

**80/20 week-one(-ish) solution:**

1. Ingest 12–24 months of inventory movements, POS logs, and receiving data for the
   **top-100 shrink stores** (concentration = scope).
2. Build the **shrink decomposition**: for each store × category, split the residual
   into its estimable components — POS-anomaly-linked (voids/refunds/sweethearting
   patterns), receiving-delta-linked (vendor short-ship), count-volatility-linked
   (process/measurement error), and unattributed remainder (external theft by
   residual). It's an estimate with stated uncertainty — but it converts "we lose
   2.5%" into "store 214 loses most of its excess in receiving, store 507 in
   refund fraud," which is the difference between anxiety and a work plan.
3. Ship two surfaces: the **investigator queue** (ranked store × pattern targets
   with evidence trails) and the **store-manager scorecard** (peer-relative,
   controllable-driver-focused, deliberately non-accusatory).
4. Measure investigation yield from month one; measure shrink-rate movement on the
   next count cycle.

Why this cut: it uses only data they already have (no cameras, no new hardware —
differentiating it from the vendor pilot that fizzled), it respects the action
bottleneck (40 investigators need targeting, not more alerts), and the decomposition
reframes the problem from "theft" (partially unsolvable) to "addressable components"
(process fixes and specific fraud patterns), where fast wins live — administrative
and process error alone is commonly a quarter-plus of shrink and is the cheapest
component to fix.

**Risks:**

- **Measurement circularity**: shrink is a residual; if the pilot changes counting
  behavior, the metric moves for measurement reasons — hold counting protocol
  constant for the evaluation set of stores, or the results are uninterpretable.
- **Employee-analytics governance**: cashier-level analysis is employee monitoring —
  legal/works-council review where applicable, human investigation before any
  action, aggregate-first reporting, and access restricted to LP — one mishandled
  accusation poisons the program.
- **Attribution overclaim**: the decomposition is estimated, not observed; present
  components with uncertainty bands, resist the deck that states them as fact.
- **Store-manager adversarialization**: if the scorecard reads as a blame tool,
  managers will fight the data (and they control the counts that feed it —
  a gameable loop); the scorecard must emphasize controllables and peer context.
- **Seasonal confounds**: shrink patterns shift with seasons and promotions;
  year-over-year comparisons, not month-over-month, for headline claims.

### Back-of-envelope estimate

- Assume ~$10M average revenue/store (grocery-anchored; range $6–15M) → chain
  revenue **~$8B** (range $5–12B). Shrink at 2.5% ≈ **$200M/year** (range
  $125–300M); the gap to the 1.5% benchmark ≈ **$80M/year** (range $50–120M).
- Concentration: if the top 100 stores run at ~4% vs 1.5% benchmark, the excess in
  just those stores ≈ 100 × $10M × 2.5pp ≈ **$25M/year** — the pilot's addressable
  pool, and a defensible one because it doesn't require fixing all 800 stores.
- Capture assumptions, stated conservatively: process/admin error is commonly a
  quarter-plus of shrink and cheaply fixable; POS-detectable fraud another
  meaningful slice. If the pilot recovers even **15–30% of the top-100 excess**
  over a year, that's **$4M–$8M/year** — 10×+ against pilot cost, with every
  assumption individually challengeable and the case surviving each challenge
  halved. Close by naming the weakest assumption (the 4% concentration figure)
  and how week one verifies it from their own data — ending an estimate with
  "and here's how we check it" is the strongest possible finish.

### What interviewers grade

| Signal | What strong looks like |
|---|---|
| Residual-metric insight | Caught that shrink is book-minus-count and partly measures measurement |
| Concentration strategy | Top-100 stores as scope; arithmetic to justify it |
| Decomposition thinking | Split one scary number into addressable components with uncertainty |
| Action-capacity realism | Designed for 40 investigators and store managers, not for a dashboard |
| Governance maturity | Employee-monitoring sensitivity raised unprompted |
| Incumbent learning | Asked why the camera pilot fizzled; differentiated on existing-data-only |
| Estimation | Chain-revenue build-up, benchmark-gap logic, capture-rate ranges, weakest-assumption named |

---

## Running these as practice

- **Timebox**: 30 minutes per case, out loud, ideally to a person; record yourself
  otherwise. The skill degrades badly when practiced silently.
- **Self-score** against each case's rubric table, one row at a time, harshly.
- **Vary the prompt**: re-run each case with one constraint flipped (the airline is
  point-to-point; the bank forbids any external inference; the hospital has one EHR).
  Strong candidates adapt the decomposition; weak ones replay the memorized one.
- **Build the muscle the rubrics share**: every case above rewards the same five
  moves — clarify the metric before solving, find the scarce resource (reviewers,
  investigators, analysts, attention), pick the concentrated 20%, estimate in ranges
  with named assumptions, and volunteer the risks including the political ones.
  That pattern *is* the decomp interview.
