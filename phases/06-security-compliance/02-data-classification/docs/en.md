# Data Classification: What You May See, Store, and Ship

**Phase 6 · Lesson 02 · ~1h**

## PROBLEM

Wednesday morning of week three. You're debugging a stubborn parser bug in a claims pipeline and the fastest reproduction is a real record from production — a claim with a member ID, a diagnosis code, a dollar figure. You paste six rows into a Slack DM to a teammate, ask "seeing this on your side?", and get an answer in ninety seconds. Bug fixed by lunch. On Friday your customer's DPO — routine monthly log review — flags six rows of Protected Health Information in an external messaging platform. Your account manager gets the call. Legal wants a written incident report. The pilot is paused pending "process review." You did not think of it as PHI; you thought of it as *six rows*. That was the mistake.

Every FDE hits a version of this moment. The fix is not more caution — you'll still need to move fast. The fix is a classification reflex that runs before your fingers do: *what class is this data, and what am I allowed to do with it?*

## INTUITION

Data classification is the operating system underneath every compliance framework. Get the class right and the rules follow; get it wrong and no amount of encryption saves you. Four things to internalize.

**Classes, not files.** Data doesn't have a class as an object — a *field* has a class within a *context*. A member ID alone might be pseudonymous; a member ID next to a diagnosis code becomes PHI. Classification is compositional. The naïve tag ("this table is confidential") loses to the compositional truth ("these three columns joined create a regulated combination").

**The common ladder.** Most customers, whether they've formalized it or not, run a 4-tier scheme: **Public** (marketing materials, published docs) → **Internal** (org charts, non-sensitive ops data) → **Confidential** (customer lists, contracts, pricing) → **Restricted / Regulated** (PII, PHI, PCI, financial account numbers, source code, credentials). The exact labels vary — some use Green/Yellow/Orange/Red, Palantir historically used a numeric scheme — but the ladder is the same. Learn to translate from the customer's labels to this mental model on day one.

**Regulated overlays.** On top of the ladder sit regulatory tags: **PII** (personally identifiable), **PHI** (HIPAA), **PCI** (cardholder data), **CUI** (controlled unclassified — federal), **MNPI** (material non-public — finance), **SPI** (sensitive personal — some jurisdictions). A field is *both* Confidential *and* PHI. The overlays drive the specific controls (BAA, PCI DSS scope, MNPI walls); the ladder drives the general handling.

**Verbs matter more than nouns.** The interesting question is not "what class is it?" — it's "what class is it, and can I *see / copy / store / transmit / process with an LLM / show in a demo*?" Each verb has different rules. You may be allowed to *see* PHI on a customer VM but not *copy* it to your laptop, allowed to *store* it in the customer tenant but not *transmit* it to a hosted LLM, allowed to *aggregate* it into counts but not *display* individual rows. Build the reflex to name the verb before you act.

## BUILD IT

Build the **Data Handling Matrix** — a customer-specific artifact you produce inside week one and update as you learn. Rows are data classes. Columns are verbs. Cells are either "yes," "no," or "yes with condition." One sheet, no more.

Template:

| Class | See | Copy to laptop | Store in our SaaS | Transmit to hosted LLM | Show in demo | Discuss in Slack |
|---|---|---|---|---|---|---|
| Public | Y | Y | Y | Y | Y | Y |
| Internal | Y | Y with NDA | Y | Y | Aggregated only | Y (private) |
| Confidential | Y | No | In-tenant only | No | Synthetic only | Redacted only |
| Restricted / PII | Y with justification | No | In-tenant only | No — pseudonymize first | Synthetic or pseudonymized | Never |
| Restricted / PHI | Y with BAA + role | No | In-tenant only | Only if LLM under BAA | Synthetic only | Never |
| Credentials / Keys | Only via vault | No | Vault only | Never | Never | Never |

Now the FDE overlay — three columns most templates skip but you will need:

- **Where the data lives by default.** ("Customer's Snowflake, our read-only role.") Being explicit about location prevents accidental copies.
- **Who decides on exceptions.** ("DPO for PHI; Security Champion for Confidential.") Named humans, not roles floating in air.
- **The escape hatch.** For every "no," write the "yes-with-controls" alternative — pseudonymize (Lesson 03), aggregate, synthesize, run in-tenant. A matrix full of "no" gets ignored; a matrix full of *alternatives* becomes the playbook.

Sign it with your champion in week one. When you're mid-debug at 11pm and want to paste six rows into Slack, you consult the matrix, not your judgment.

## FIELD NOTES

- Customers underclassify by default. Everything they own feels "internal" until you point out the diagnosis-plus-member-ID composition and their eyes widen. Bring examples from *their* data to the classification conversation — abstract debates go nowhere.
- Screenshots are the silent leak. A dashboard screenshot for a bug report contains PHI just as much as the underlying row. The rule "no restricted data in screenshots or slides" saves more careers than any other single rule. Enforce it on yourself.
- Aggregation is not automatic anonymization. Small-cell counts (fewer than N patients in a diagnosis) can re-identify individuals; k-anonymity has a floor. When in doubt, suppress small cells or add rounding.
- Derived fields inherit the strictest parent class. If you compute a risk score from PHI, the risk score is PHI. The junior FDE move is to treat derived data as fresh; the senior FDE move is to track lineage all the way back (Phase 3 Lesson 13).
- Free-text fields are the worst offenders. A "notes" column technically labeled Internal will contain SSNs, credit cards, and diagnoses because *users type whatever they type*. Always assume free-text is Restricted until proven otherwise.

## INTERVIEW ANGLE

Classification questions show up in the customer round and often as a warm-up in the security round. Interviewers are not looking for a taxonomy quote — they're looking for the reflex.

1. "A customer sends you a CSV to help debug. What do you do before opening it?" (Ask about class and jurisdiction; confirm handling terms in writing; open on an approved machine only; never on the airport wifi. Bonus: name the specific control — local disk encryption, no personal cloud sync.)
2. "You need to test your LLM prompt with real data. The customer says the data is 'internal.' Is that enough?" (No — probe for regulated overlays: any PII, PHI, PCI? Ask about the DPA's LLM clause. Offer pseudonymized-in-tenant as the alternative.)
3. "How do you handle a field the customer swears is anonymous but you suspect isn't?" (Compositional risk: check joins to other tables, small-cell counts, quasi-identifiers. Raise it as a finding, not an accusation.)

## DRILL

Take a dataset you know well — from a past job, a public Kaggle set, or the CRM extract from a Phase 3 lesson. Do three things:

1. List every column and classify it: Public / Internal / Confidential / Restricted, plus any regulatory overlay. Where compositional risk exists, note the field combinations.
2. Fill out the Data Handling Matrix above for that dataset in your current work setup (laptop, cloud accounts, Slack). Be honest about the gaps.
3. Write the two-sentence escalation you'd send your champion if you discovered a Restricted field mislabeled as Internal. Keep it non-accusatory, action-oriented, and time-boxed ("proposed re-labeling by EOD Thursday; no analytical impact"). Save the template — you will use it verbatim someday.
