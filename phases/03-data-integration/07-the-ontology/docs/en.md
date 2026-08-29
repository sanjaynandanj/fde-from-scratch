# The Ontology: Modeling a Customer's World as Objects and Links

**Phase 3 · Lesson 07 · ~1.5h**

## PROBLEM

Week five of a healthcare payer pilot. You've got clean data: patients, claims, providers, plans, authorizations, denials. The Wednesday demo shows a good dashboard. Then the medical director asks a question that seems simple: "Show me all the denied claims for patients who are on plan Alpha, treated by out-of-network providers, in the last 90 days, where the same provider had a prior denial for the same procedure code within a year."

Your current data model is five tables joined ad-hoc in dashboard SQL. Every question the director asks requires a new query, a new join path, and someone (you) to know the join keys. The head of analytics can't self-serve. New questions take a day each. You realize the dashboard isn't the deliverable — the *ontology* is: a stable model of the customer's world where the entities are named, linked, and reusable.

Palantir built a company on this move. It's not database design. It's *domain* design — the objects the customer's business actually reasons about, exposed as first-class things with names their VPs use.

## INTUITION

An ontology is three ideas layered:

**Objects.** Nouns from the business. Patient, Claim, Provider, Plan, Authorization, Denial. Each object has a stable ID (from entity resolution), a set of typed properties, and a business-friendly name. The test: can a VP read the object list and see their world? If the objects are named `dim_customer_v3` and `fact_transactions_2024_q3`, no.

**Links.** Named relationships between objects, with cardinality. `Patient -[enrolled_in]-> Plan` (many-to-one). `Claim -[submitted_by]-> Provider` (many-to-one). `Claim -[against]-> Authorization` (many-to-one, optional). Links have direction *and* the reverse is queryable: from a Provider you can walk to all their Claims.

**Actions.** Verbs the business does, expressed as writes against the ontology: `flag_for_review(claim_id)`, `approve_authorization(auth_id)`. Actions are what makes the ontology a *workspace* rather than a read-only view — but for a pilot, read-only is fine and often enough.

Two design battles decide whether this works:

**Grain.** Every object needs a defined atom. Is a "Claim" a header row, or a claim-plus-line-items composite? Is a "Patient" a person, or a person-plus-eligibility-period? Wrong grain and every query gets weird. Pick grain by asking: "when a business user says the noun, what count do they mean?"

**Naming.** Use the customer's names, not yours. If they call it "member," not "patient," it's Member. Ontologies fail when engineers impose engineer-taxonomy. This costs a rename now, saves confusion forever.

**Versioning.** The ontology will change. Adding a property is safe. Adding an object is safe. Renaming is a migration. Deleting is a breaking change requiring downstream coordination. Bake versioning into the design from day one — even if you never bump the version during the pilot.

## BUILD IT

The ontology is a schema plus an accessor. Sketch:

```python
# Ontology definition — data, not code
ONTOLOGY = {
    "objects": {
        "Patient": {
            "id_field": "patient_id",
            "properties": {
                "member_id": "string",
                "name": "string",
                "dob": "date",
                "plan_id": "string",
            },
        },
        "Claim": {
            "id_field": "claim_id",
            "properties": {
                "patient_id": "string",
                "provider_id": "string",
                "procedure_code": "string",
                "amount": "float",
                "status": "enum:submitted|approved|denied",
                "service_date": "date",
            },
        },
        "Provider": {
            "id_field": "provider_id",
            "properties": {
                "name": "string",
                "network_status": "enum:in|out",
                "npi": "string",
            },
        },
    },
    "links": [
        # (from, name, to, cardinality)
        ("Claim",   "for_patient",  "Patient",  "many_to_one"),
        ("Claim",   "billed_by",    "Provider", "many_to_one"),
        ("Patient", "enrolled_in",  "Plan",     "many_to_one"),
    ],
}

class Ontology:
    def __init__(self, spec, tables):
        self.spec = spec
        self.tables = tables  # {"Patient": [...], "Claim": [...], ...}

    def get(self, object_type, id_value):
        id_field = self.spec["objects"][object_type]["id_field"]
        for row in self.tables[object_type]:
            if row[id_field] == id_value:
                return row
        return None

    def follow(self, object_type, id_value, link_name):
        """Follow a named link, return the linked object(s)."""
        for (src, name, dst, card) in self.spec["links"]:
            if src == object_type and name == link_name:
                src_row = self.get(object_type, id_value)
                if not src_row:
                    return None
                # Convention: link "for_patient" from Claim uses Claim.patient_id
                fk_field = self.spec["objects"][dst]["id_field"]
                return self.get(dst, src_row[fk_field])
        raise KeyError(f"No link {link_name} from {object_type}")
```

Two moves are load-bearing. First, the ontology is *specification data* separate from access code. When the customer adds an object, they edit the spec, not the runtime. Second, `follow` walks named links using business language — `claim.follow("for_patient")` instead of `SELECT * FROM patient WHERE id = claim.patient_id`. That's what makes the ontology feel like a domain model instead of a database.

For real deployments you'd back the tables with SQL and the spec with a versioned config file. The pilot version above runs on in-memory dicts and demos the concept in an hour.

## FIELD NOTES

- Draw the object-link graph on a whiteboard with the customer's data owner and their business SME in the same room. Nothing surfaces missing objects and wrong link directions faster. The diagram is the artifact; the code follows.
- The first ontology is always too small — five objects, three links. That's fine. Ship it, use it, discover the missing objects through questions the dashboard can't answer.
- Watch for "hidden" objects — entities that exist in the business but not in any single source system. In insurance, the "case" (a group of related claims for one incident) often exists only in the claim adjuster's head. Making it a first-class ontology object is often the single biggest pilot win.
- Cardinality mistakes bite. If you model `Patient -> Plan` as many-to-one but the customer has patients with multiple simultaneous plans, every enrollment query lies. Test cardinality against real data before you commit.
- Version the ontology as `v1.0.0` from the start, even if you never bump. When you eventually need `v2`, downstream consumers can pin.

## INTERVIEW ANGLE

Palantir loops in particular probe ontology thinking — "how would you model X" is a case-round staple. The interviewer is testing whether you separate objects from tables and think in business language.

Sample questions:

1. "Model a ride-sharing company's world as an ontology. Draw it." (Expected objects: Rider, Driver, Trip, Vehicle, Payment. Links with cardinality. The candidate who says "just Rider and Trip" is missing entities; the one who adds fifteen tables is over-modeling.)
2. "Your ontology has `Claim -> Patient` as many-to-one. The customer's data has one claim linked to two patients (a mother and a newborn on one form). What do you do?" (Cardinality is wrong. Either introduce an intermediate `ClaimParticipant` object, or bump `Claim -> Patient` to many-to-many. The right choice depends on how the business reasons about it — ask them.)
3. "Why an ontology instead of a well-designed star schema?" (Business-friendly names, links as first-class navigation, extensible without breaking queries, foundation for actions and permissions. The star schema is a physical layout; the ontology is a semantic layer.)

## DRILL

1. **Extend:** add `reverse` links so `Provider.follow("submitted_claims")` returns all Claims where `provider_id` matches. This needs the ontology to know the reverse name for each link — encode it as a fourth tuple element.
2. **Break:** change `Patient -> Plan` from many-to-one to many-to-many by having a patient with two plans. Watch `follow` return only the first plan it finds. Extend the return type to a list when cardinality is many-to-many.
3. **Fix:** add an `Action` — `flag_claim_for_review(claim_id, reviewer_id, reason)`. Implement it as a function that appends to a `review_queue` list and writes an audit-log entry. Assert the audit entry captures the actor, timestamp, and reason.
