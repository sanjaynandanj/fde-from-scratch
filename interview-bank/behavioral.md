# Behavioral — The FDE Competency Matrix, Questions, and STAR Stories

FDE behavioral rounds are not HR box-checking. At customer-facing companies they are
often the *deciding* round, because the failure mode they screen for — a technically
excellent engineer who damages customer relationships, hides bad news, or freezes
without a spec — is expensive in exactly the way FDE work makes expensive. Interviewers
are asking one underlying question the whole time: **can we put this person alone in a
conference room with a skeptical VP and their broken data, and trust what happens next?**

## The competency matrix

Six competencies recur across every FDE loop. Rate yourself honestly, 1–5, before
prepping; your two weakest are where interview prep time should go.

| Competency | What it means in the field | The interviewer's hidden question |
|---|---|---|
| **Customer empathy** | Understanding the customer's world, incentives, and constraints from *their* side of the table; solving their problem, not your idea of it | "Will customers trust and confide in this person?" |
| **Speed under ambiguity** | Producing forward motion when the spec, the data, and the org chart are all unclear; time-boxing discovery; shipping thin slices | "Does this person need a spec to function?" |
| **Ownership** | Treating the outcome — not the task — as yours: the unglamorous follow-through, the 2am feed failure, the thing nobody assigned | "When it breaks on Saturday, what does this person do?" |
| **Technical communication** | Translating between engineering truth and business meaning in both directions, calibrated to the audience, without dumbing down or snowing | "Can I put them in front of a CIO *and* a DBA?" |
| **Conflict navigation** | Handling stakeholder disagreement, hostility, and competing agendas without escalation-addiction or capitulation | "Will they survive a hostile room and keep the account?" |
| **Integrity around data** | Truthful numbers with their caveats attached; refusing the massage; protecting customer data even when no one is watching | "When the demo number looks better with one filter, what do they do?" |

## STAR, adapted for FDE stories

Standard STAR (Situation → Task → Action → Result) with two field-specific additions
interviewers consistently reward:

- **Stakes**: say why it mattered in money, trust, or time — FDE stories have real
  stakes and naming them separates "did a task" from "owned an outcome."
- **Retro**: one sentence of what you changed permanently afterward. Field craft is
  accumulated scar tissue; show the scar *and* the changed behavior.

Keep stories to 2–3 minutes spoken. Practice the 30-second compressed version too —
interviewers often want the short form, then drill.

---

## 1. Customer empathy

### Sample questions

1. "Tell me about a time you discovered the customer's real problem was different
   from what they asked for. What did you do about the gap?"
2. "Describe a time you had to deliver work inside a customer's constraints —
   technical, political, or process — that you personally found frustrating."
3. "Tell me about a time you changed your technical approach because of something
   you learned about how the customer's people actually work."

### Example STAR story

*(Invented but field-plausible — use its shape, not its content.)*

**Situation**: I was deployed to a regional logistics company to build a delivery-delay
prediction dashboard — that's what the contract said. The ops director wanted ML-driven
ETAs on every shipment.

**Task**: Ship a pilot in six weeks that ops would actually use. The stakes: this was
the account's first engagement, and renewal depended on daily usage, not on a signed-off
deliverable.

**Action**: Before building, I spent two days sitting in their dispatch office. What I
watched: dispatchers already *knew* which shipments would be late — their intuition was
decent — but they spent 60–90 minutes every morning manually building a call list of
affected customers from three systems, and the calls, not the predictions, were what
reduced complaints. The stated problem was "predict delays"; the real problem was "the
morning after a delay is three hours of swivel-chair work." I brought this back to the
ops director carefully — not "your spec is wrong" but "I watched Maria's morning; can I
show you what I saw?" — and proposed re-scoping the first release: an auto-generated,
prioritized customer-contact list joining shipment status to order value and contact
info, with the prediction model demoted to a phase-two ranking signal. He agreed once
he saw it framed as his team's hours back.

**Result**: The contact-list tool shipped in week three and was used every single
morning — 100% weekday adoption, dispatcher prep time down from ~90 to ~15 minutes,
measured from their own screen-recording study. The prediction model shipped later as
a sort order, where "good enough" accuracy was actually good enough. The account
renewed with a broader scope.

**Retro**: I now refuse to finalize any pilot scope until I've watched the actual
end-users work for at least half a day. The contract describes the problem someone
bought; the desk describes the problem that exists.

---

## 2. Speed under ambiguity

### Sample questions

1. "Tell me about a time you had to start delivering before the requirements were
   clear. How did you decide what to build first?"
2. "Describe a situation where you had almost no documentation, no access, or no
   help — and a deadline anyway."
3. "Tell me about a time you time-boxed an investigation. How did you decide when
   to stop learning and start building?"

### Example STAR story

**Situation**: Two weeks before a manufacturing customer's board review, their sponsor
asked us to add a "supplier risk view" to the pilot — with no definition of risk, no
identified data source, and the one person who understood their supplier master on
leave.

**Task**: Have something real and defensible in the board demo in ten working days,
without derailing the committed pilot scope. Stakes: the sponsor had personally
promised this to their CEO; an empty slide would have burned the person keeping our
pilot alive.

**Action**: I split the ten days explicitly: two days of time-boxed discovery, six of
build, two of buffer-and-rehearsal — and told the sponsor that plan on day one so the
trade-offs were shared. Discovery: instead of chasing the perfect risk definition, I
pulled what data was *reachable that week* — the ERP's supplier table, on-time-delivery
history, and single-source part flags — and drafted a strawman risk score (delivery
reliability × single-source exposure) in a spreadsheet by day two. The strawman did its
job: reviewing it, the procurement lead immediately said "that's wrong, single-source
matters far more for the parts with 12-week lead times" — which was the requirement no
one had been able to articulate in the abstract. I built exactly that: a ranked
supplier-risk table with three transparent factors, filterable by product line, with an
explicit "v1 methodology" note on the screen stating what it did and didn't consider.

**Result**: The board demo landed; the CEO's question — "why is supplier 4471 red?" —
was answerable in one click, which visibly mattered more than model sophistication.
The strawman-review trick surfaced two more requirements in that meeting alone. The
supplier-risk view later became the pilot's most-used screen.

**Retro**: Two permanent habits: I present strawmen instead of asking open questions —
people can't specify what they want, but they can correct what's wrong instantly — and
I state my time-box split to the stakeholder on day one, so discovery has a contract.

---

## 3. Ownership

### Sample questions

1. "Tell me about a time something broke in production that wasn't your fault. What
   did you do?"
2. "Describe the least glamorous piece of work that mattered most in an engagement
   you ran."
3. "Tell me about a time you caught a problem no one had assigned to you. Why did
   you pursue it?"

### Example STAR story

**Situation**: Mid-pilot at an insurance customer, I noticed our nightly claims feed
had loaded on schedule but with 12% fewer rows than the trailing average. Nothing had
alerted — the load "succeeded" — and nobody had reported anything. It was 7pm on a
Friday, and the customer's team had gone home.

**Task**: Formally, nothing — the pipeline was green and the missing rows were a
weekend-old anomaly at most. Actually: our Monday steering meeting was going to show
a claims dashboard to the CFO, and if the numbers were quietly wrong, the pilot's
credibility died in that room. The data was theirs; the number was ours.

**Action**: I dug in that evening. The row-count drop traced to their side: a source
system had been patched Thursday and the export job now silently excluded one claim
status code. Not our bug — but our dashboard. I did three things: quarantined the
affected loads and pinned the dashboard to the last verified date with a visible
banner ("data verified through Thursday — investigating a source change"), wrote up
the diagnosis with the exact status code and row counts, and sent it Saturday morning
to their data lead with a proposed fix for *their* export — written so they could
forward it internally without translation. Monday morning, before the steering
meeting, I told the sponsor what had happened and what the banner meant.

**Result**: Their team confirmed and fixed the export Monday; we backfilled the gap
by Tuesday. In the steering meeting the CFO asked about the banner — and the sponsor
told the story himself, as a positive: "they caught our bug over the weekend." That
incident bought more trust than any feature we shipped. We also added trailing-average
volume alerts to every feed — the alert that should have existed already.

**Retro**: I stopped treating "the load succeeded" as success anywhere; every feed I
ship now alerts on volume anomaly, not just on failure. And I learned the reporting
rule I've kept since: bad news, with a diagnosis, before the customer finds it —
because trust compounds precisely at the moments things break.

---

## 4. Technical communication

### Sample questions

1. "Tell me about a time you had to explain a complex technical failure to a
   non-technical executive. Walk me through what you actually said."
2. "Describe a time you had to push back on a technical decision made by someone
   more senior — or on the customer's own engineers."
3. "Tell me about a time your explanation *failed* — the audience didn't get it or
   drew the wrong conclusion. What did you change?"

### Example STAR story

**Situation**: At a retail customer, our entity-resolution pipeline merged two
genuinely different customers — same name, same city, birthdates one digit apart —
and a store associate saw another person's purchase history. The customer's VP of
digital called an urgent meeting: her, their counsel, their head of engineering,
and me.

**Task**: Explain what happened, its scope, and the fix — to three audiences with
three different questions (legal exposure, technical cause, business risk) — in one
30-minute meeting, without minimizing and without drowning them in match-score math.
Stakes: they were deciding whether to pause the entire pilot.

**Action**: I prepared three layers of the same truth and let the room pull the depth
it needed. I opened with the plain version, worst news first: "Our system incorrectly
combined two customers' records; one associate saw one wrong profile for roughly four
hours; here is exactly what they could see." For counsel: the affected-data inventory
and access log — one viewer, one record pair, timestamps — on one page. For their
head of engineering: the actual cause — our match threshold treated
near-identical name+city with a one-digit birthdate difference as a typo correction;
I showed the specific scoring rule, why it existed, and the fix: birthdate conflicts
now block auto-merge outright and route to human review. For the VP: the systemic
answer — how many other merges had similar risk profiles (we'd re-audited overnight:
11 flagged, 0 confirmed wrong), and the new review gate. I ended with what I *couldn't*
yet promise, and when I would know.

**Result**: The pilot wasn't paused. Counsel got their inventory, engineering
validated the fix that week, and the VP later told our account lead the meeting was
why: "they told us the worst part first and answered every level of question."
The birthdate-blocking rule caught two real would-be false merges over the next
quarter.

**Retro**: I now prepare every incident briefing in three layers — headline truth,
evidence page, mechanism — and always lead with the worst sentence. Burying the lede
in a technical narrative is the communication failure executives never forgive,
because it reads as management, not explanation.

---

## 5. Conflict navigation

### Sample questions

1. "Tell me about a time two stakeholders wanted incompatible things from your
   system. How did you resolve it — and what did you *not* do?"
2. "Describe the most hostile meeting you've been in. What was your role in how it
   ended?"
3. "Tell me about a time you disagreed with your own team or leadership about how
   to handle a customer. What happened?"

### Example STAR story

**Situation**: On a hospital-network engagement, the finance department and the
clinical operations team both claimed ownership of the "readmission rate" metric our
dashboard displayed — and their definitions differed: finance counted 30-day
all-cause readmissions (the reimbursement-relevant number), clinical ops excluded
planned readmissions (the care-quality-relevant number). Each side had separately
told me the other's definition was "simply wrong," and the disagreement had escalated
into both directors emailing my sponsor to demand their version.

**Task**: Get a usable dashboard shipped without becoming the arbiter of a
inter-departmental turf question I had no standing to decide — and without the pilot
becoming the battlefield for it. Stakes: either director could stall the pilot's
adoption in their org.

**Action**: First, I declined the referee role explicitly but usefully: I told both
directors the same thing — "you're both right for your purpose; these are two metrics
wearing one name, and the system can carry both." Then I made the conflict concrete
instead of rhetorical: I computed both definitions on the same quarter of their real
data and put them side by side — 14.2% vs 11.8% — with a plain-language definition
under each. Seeing the actual delta changed the conversation's temperature: it was no
longer "whose number is right" but "these answer different questions." I proposed the
resolution in a room with both present (never shuttle diplomacy — the versions drift):
both metrics on the dashboard, explicitly labeled ("30-day all-cause" / "30-day
unplanned"), finance's version defaulting on financial views, clinical's on ops views,
one shared glossary page owned by *them* jointly. I let their CMO bless the glossary —
the decision needed an internal owner, not a vendor.

**Result**: Both directors adopted the dashboard — each got their number, correctly
labeled, and each stopped disputing the other's because the label did the arguing. The
glossary page pattern spread: they added four more contested metrics to it over the
pilot. My sponsor specifically cited "handled our politics without joining them" in
the renewal conversation.

**Retro**: Two rules I've kept. When stakeholders fight over a metric, the fight is
almost always two valid definitions sharing one name — split the name, not the
difference. And never resolve a two-party conflict in separate rooms; the joint
meeting with real data on screen is uncomfortable for ten minutes and definitive
afterward.

---

## 6. Integrity around data

### Sample questions

1. "Tell me about a time you were pressured — even gently — to present numbers more
   favorably than the data supported. What did you do?"
2. "Describe a time you discovered your own analysis or system was wrong *after*
   people had relied on it."
3. "Tell me about a time you declined to use data you technically had access to.
   Why?"

### Example STAR story

**Situation**: End of a document-extraction pilot at a lender. Our headline metric —
field-level extraction accuracy — was 91% overall, but 76% on one document class
(broker-submitted statements, ~20% of volume) that happened to be the class their
underwriting team cared most about. Two days before the executive readout, our own
account lead suggested the summary slide show "91% accuracy" and leave the breakdown
in the appendix, "since the review workflow catches the rest anyway."

**Task**: Deliver a readout that kept the renewal alive without shipping a number I
knew the audience would misread. Stakes in both directions: an honest-looking failure
could kill a renewal the product genuinely deserved; a discovered soft-pedal would
kill something worse — the customer's trust in every number we'd ever shown them,
and my own credibility inside my company.

**Action**: I pushed back internally first, with a specific prediction rather than a
principle: the underwriting director lived in broker documents daily — she would see
76% behavior in week one of production, do the arithmetic, and re-read our slide as
deception. I proposed the opposite framing and built it: lead *with* the breakdown —
"91% overall; 76% on broker statements, and here is exactly why (scanned faxes,
non-standard layouts) and the plan" — then show that the routing design already
compensated: broker documents auto-routed to human review, making the *workflow's*
end-to-end accuracy 99%+ at a measured review cost of 9 minutes per document versus
22 for full manual keying. I brought the per-class economics table so the honest
number came attached to its honest mitigation. Our account lead agreed once the
framing showed stronger, not weaker.

**Result**: In the readout, the underwriting director's first question was — exactly
as predicted — "what about broker docs?" Being *ahead* of that question, with the
number and the plan on the same slide, turned the toughest audience member into the
renewal's advocate: she told the CFO "they measure like we do." The renewal signed
with an expanded document scope, including funding to fix the broker-document class
properly — which the honest breakdown had effectively scoped for us.

**Retro**: The permanent rule: every topline number I present now travels with its
worst segment and that segment's mitigation, on the same slide. If the story can't
survive its own breakdown, the story is wrong — and it is always cheaper to learn
that before the customer does.

---

## Mining your own experience

You don't need Palantir field deployments to build this story bank. The competencies
transfer from ordinary engineering work — the interviewer cares about the behavior,
not the logo. Mine these veins:

**Where to dig:**

- **Internal customers count.** The analytics team you built a pipeline for, the
  support org whose tool you maintained, the PM whose vague request you decomposed —
  every "customer empathy" and "conflict" competency has internal-stakeholder
  versions, and they are fully valid FDE stories if you tell them with the same
  stakes-and-users framing.
- **Incidents are ownership gold.** Every on-call story where you went past your
  formal responsibility, communicated during the fire, and changed something
  afterward maps to the ownership and communication rows.
- **Any data-quality discovery** — the metric that was silently wrong, the double
  count you caught, the dashboard someone trusted that you had to correct — is an
  integrity story. So is any time you added a caveat someone wanted removed.
- **Side projects, freelance work, and hackathons** legitimately cover speed-under-
  ambiguity: no spec, no infrastructure, a deadline, and a demo is precisely the
  FDE condition.
- **Teaching and writing** cover technical communication if you can point to
  calibration — the same content delivered differently to different audiences.

**How to prepare the bank:**

1. Write 8–10 stories, not 6 — you want at least two per competency because
   interviewers ask follow-ups ("tell me about *another* time...") and because one
   story often serves two competencies (label which).
2. For each, write the STAR + Stakes + Retro skeleton in bullet form — not a script.
   Memorized scripts collapse under interruption, and FDE interviewers interrupt
   deliberately, because customers do.
3. Attach a *number* to every result. "Adoption went from 2 users to 9 of 11
   dispatchers" — if you don't remember the number, reconstruct a defensible
   estimate and say "roughly." Unquantified results read as unverified.
4. Rehearse the 30-second and 3-minute versions of each aloud. The 30-second
   version is the answer to "tell me briefly about..."; the 3-minute version is
   the follow-up.
5. Pressure-test each story against the follow-ups a good interviewer will ask:
   "What would you do differently?", "What was *your* specific contribution?" (the
   'we' that never becomes 'I' is the classic red flag), "What did the other person
   think happened?", and "What did this cost?"
6. Audit the bank against the hidden questions in the matrix table. If none of your
   stories would make an interviewer believe "I can leave this person alone with an
   angry VP," that's the gap — and it's better discovered now, because there is
   usually a real story in your history that shows it; it's just filed in your memory
   under "bad week" instead of under "evidence."

One last calibration: the strongest behavioral answers in FDE loops are not hero
stories. They are *judgment* stories — situations with real trade-offs where you can
articulate what you gave up, what you protected, and what you permanently changed.
Interviewers at these companies have all had engagements go sideways; a candidate
whose every story ends in unqualified triumph reads as either inexperienced or
unreliable. The scar plus the changed behavior is the credential.
