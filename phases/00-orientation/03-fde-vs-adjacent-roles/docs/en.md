# FDE vs SWE vs Solutions Engineer vs Consultant: The Real Boundaries

Phase 0 · Lesson 03 · ~1h

## PROBLEM

A hiring manager at an enterprise-AI startup interviews four candidates for one FDE seat. The ex-SWE builds beautifully but freezes when asked how he'd handle a customer demanding a feature that shouldn't exist. The ex-solutions engineer demos brilliantly but has never owned code past the proof-of-concept. The ex-consultant structures the problem perfectly on the whiteboard and then proposes hiring engineers to build it. The ex-sales engineer knows exactly how to win the room but treats the product as a black box. None of them is wrong for their *old* job. All of them are missing a strand of the braid. Understanding precisely where the boundaries sit is how you present your background honestly — and how you know what to backfill.

## INTUITION

Four adjacent roles, four boundary lines:

**vs. SWE.** A product SWE optimizes for the codebase surviving years; an FDE optimizes for the customer succeeding in weeks. SWEs get requirements that have been laundered through PMs; FDEs extract requirements from a VP who says "make it smarter." SWEs are judged on system quality; FDEs on customer outcomes. Crucially: FDEs still write real code — the difference is that code quality is a *means*, deliberately dialed up or down per artifact (throwaway demo vs. keepable pipeline). A great FDE is a real engineer with a different objective function, not a worse engineer.

**vs. Solutions Engineer / Sales Engineer.** SEs live pre-sale: demos, POCs, technical objection handling, then hand off when the ink dries. FDEs live *post*-sale (and during pilots that decide renewals): they own the deployment until it works in production against real data. The boundary is ownership of outcomes. An SE's demo can be smoke and mirrors by design; an FDE's pilot must survive contact with the customer's actual CSVs, actual SSO, actual compliance team. Rule of thumb: if you disappear after the contract is signed, you're an SE; if you appear then, you're an FDE.

**vs. Consultant.** Consultants sell structured thinking and recommendations; the deliverable is a deck and a roadmap, and implementation is often someone else's problem (or a follow-on contract). FDEs deliver working software; the deck exists only to explain the software. Consultants bill time; FDE economics are tied to product revenue (the pilot converts, the license renews, the platform expands). The failure mode of consulting-brain in an FDE seat: weeks of discovery and beautiful documents while the customer waits for anything to run.

**vs. Product Manager** (bonus boundary, because FDEs do PM work): FDEs do discovery, prioritization, and stakeholder management — but scoped to one customer at a time, and they build the thing themselves. The generalization step — "which of this customer's needs belong in the product for everyone" — is the FDE→product boomerang covered in Lesson 05.

The FDE is the intersection: SE's customer instincts + consultant's problem structuring + SWE's ability to actually build + PM's judgment about what's worth building. Weak in any strand, the role breaks.

## MAP IT

1. Draw a 2×2: x-axis "owns working software (no → yes)", y-axis "faces the customer (no → yes)". Place SWE, sales engineer, consultant, PM, and FDE on it. FDE should land alone in the top-right; if it doesn't, revisit the boundaries above.
2. For each of the four adjacent roles, write one sentence: "An ex-[role] moving to FDE must learn ___ and unlearn ___." (E.g., ex-consultant: learn to ship before the analysis is complete; unlearn deliverable-as-document.)
3. Locate yourself: which role is your background closest to? Write your own learn/unlearn sentence. That sentence is your behavioral-interview headline.

## FIELD NOTES

- Real orgs blur these lines. Some companies' "solutions architects" do full FDE work; some "FDEs" are SEs with a better title. In interviews, ask: "who owns the deployment after signature?" and "what percent of the role is writing code that ships?" The answers place the role on the map regardless of title.
- Customers will *also* be confused about your role. Expect to be treated as free consulting ("while you're here, can you look at our data warehouse strategy?") and as vendor support ("the dashboard is down"). Scope control — Phase 7 — is the defense.
- The consultant comparison is the one FDE candidates most often get wrong in interviews, because from the outside the jobs look similar (travel, customer sites, ambiguity). The inside difference is total: you ship.

## INTERVIEW ANGLE

Boundary questions are a standard screen — they reveal whether you actually understand the job you applied for.

Sample questions:

1. "How is this role different from a solutions engineer?" (Answer with the ownership boundary: post-sale, production outcomes, real data.)
2. "You've been a backend engineer for five years. What's going to be hardest for you here?" (Honest self-placement beats bravado; use your learn/unlearn sentence.)
3. "A customer asks you to spend two days advising on something unrelated to our product. What do you do?" (Scope judgment: relationship value vs. consulting drift; the good answer involves a small yes, a boundary, and telling your engagement lead.)

## DRILL

Take a job description for each of the four adjacent roles (real postings). For each, list the two requirements an FDE posting would *add* and the one it would *drop*. Then rewrite your own resume summary line twice: once as it reads today, once angled at the FDE intersection. Notice exactly which claims you can't yet back with evidence — those map to phases of this curriculum.
