# Identity: SAML, OIDC, and "Just Use Our Okta"

**Phase 4 · Lesson 02 · ~1.5h**

## PROBLEM

Two weeks into a pilot with a large healthcare payer, the champion says the line every FDE hears: "just use our Okta, we do this with every vendor, it takes an afternoon." Fine. The identity team schedules a call and asks which protocol you speak. You say OIDC because that's what your app was built with. There's a long pause. The customer's Okta tenant is set up for SAML across all internal apps — SCIM provisioning, group mapping, JIT — and their identity team hasn't stood up a new OIDC app in eighteen months. They can do it, but it needs a change ticket, a review with the SSO governance board, and a compatibility check with their session-management proxy. Five weeks pass. The pilot goes cold. When the ticket finally clears, group names in the token are `CN=pilot_users,OU=Groups,DC=payer,DC=corp` and your role logic breaks because you were expecting `pilot-users`.

The trap: identity in the enterprise is not a protocol choice you make on your side. It's a negotiation with a team whose posture, tooling, and playbooks were set years before your product existed. Show up knowing what they'll offer, what breaks in each option, and what to ask for by name.

## INTUITION

Two protocols dominate enterprise SSO: **SAML 2.0** and **OIDC** (OpenID Connect, built on OAuth 2.0). A third concern — **provisioning** — usually rides alongside via SCIM.

**SAML 2.0.** XML-based, browser-redirect flow, 2005-era. The IdP posts a signed XML assertion to your app's ACS URL. Assertions carry attributes (email, groups, department) and an audience restriction. SAML is the incumbent for internal enterprise apps and still the default at most large organizations, especially in banking, healthcare, and government. If your customer is a Fortune 500, assume SAML until proven otherwise. Gotchas: XML signature validation is subtle (XML Signature Wrapping attacks are real), assertions are big, and the metadata XML you exchange is the source of truth.

**OIDC.** JSON, redirect + token exchange, 2014-era, built on OAuth 2.0. The IdP hands you an ID token (JWT — see lesson 03) and typically an access token. Native to modern SaaS, mobile, and machine-to-machine flows. Simpler libraries, better docs, but many enterprise IdP teams still treat it as the "new thing" and route it through more review.

**SCIM.** System for Cross-domain Identity Management. This is *provisioning* — the IdP pushes user create/update/deactivate events to your app so a user off-boarded at the customer disappears from your app within minutes, not months. Enterprises with mature identity practice will require SCIM; auditors ask about it explicitly. If you don't support it, the customer's answer is often "then we'll do quarterly CSV exports," which is worse for everyone.

**JIT provisioning** is the fallback: the user shows up via SSO, and your app creates them on the fly from the token's attributes. Fine for pilots. Not fine for enterprises with tight off-boarding SLAs — a JIT-created user only disappears when *they try to log in and can't*, which is the wrong direction.

The mental model: **SSO gets users in. SCIM keeps the list clean. Groups drive authorization.** All three must be designed together, or the pilot will look great on day one and fail its first access review 90 days later.

## MAP IT

Build a one-page identity decision brief before the customer's IdP team meeting.

1. **Protocol matrix.** Two columns (SAML, OIDC), three rows (my app supports today, customer prefers, my recommendation). If your app only speaks OIDC and the customer is SAML-first, the "recommendation" is *add SAML this quarter* or *lose the deal to a competitor who already has it*.
2. **Attribute map.** List the fields your app needs from the token: `sub` (stable user id), `email`, `groups` or `roles`, `department` or `tenant`. Beside each, write the customer's exact source attribute (`sAMAccountName`, `mail`, `memberOf`). Do this in writing before the ticket goes in.
3. **Group naming contract.** Write the exact group strings your app will match. `pilot-users` vs `Pilot_Users` vs `CN=pilot_users,OU=Groups,DC=payer` are three different strings. Enterprise IdPs often ship the full DN. Decide whether your app normalizes or the IdP transforms — put it in the config, not the code.
4. **Provisioning plan.** Pick one: SCIM (best), JIT with off-boarding automation (acceptable), CSV imports (last resort, document the SLA gap). Match to the customer's off-boarding SLA — hours vs days vs weeks.
5. **Failure modes.** Write down two: "IdP metadata rotates and we don't notice", "group name changes upstream and our roles silently regress." Design monitoring for both.

## FIELD NOTES

- The customer's identity team is a real gatekeeper. Their calendar is booked out weeks. Book the meeting in week one of the engagement — before you know if you need it. Cancelling later is cheap; waiting six weeks for a slot is fatal.
- "Just use our Okta" from the champion translates in reality to *the identity team gets a Jira ticket, prioritizes it against thirty other vendors, and you get an hour of their attention two weeks later.* Plan around this cadence.
- Metadata is the contract. Both sides exchange metadata XML (SAML) or discovery URLs (OIDC). Store the customer's metadata in your repo — versioned, reviewed, alertable when it changes. The IdP will rotate signing keys on their schedule and forget to tell you.
- Group names in real tokens are ugly. AD often ships full distinguished names. Okta may prefix everything. Azure AD group claims are GUIDs by default unless the IdP admin turns on display-name emission. Pin the exact strings early or your role checks will fail silently.
- Test off-boarding before production. Have the customer disable a test account in their IdP and confirm your app loses access within the promised window. Do this as a scripted exercise, not a promise.
- SAML XML signature validation is a security-review magnet. Use a vetted library, pin the expected issuer and audience, and never process assertions without checking the signature. XML Signature Wrapping attacks target apps that parse and validate in the wrong order — mirror lesson 03's JWT gauntlet mentality: signature *first*, then claims.

## INTERVIEW ANGLE

Identity questions surface in FDE loops as both practical ("wire this up") and system-design ("what's the right posture"). Interviewers are checking you know the enterprise reality, not just the protocol RFCs.

Sample questions:

1. "The customer says 'we use Okta, integrate with us.' What's your first meeting with their identity team look like?" (Confirm SAML vs OIDC, get their attribute schema, ask about SCIM, ask about group naming, confirm ACS/redirect URLs and cert rotation cadence.)
2. "Your app supports OIDC. The customer is SAML-only and won't budge. What are your options?" (Add SAML support, use an identity broker like Auth0/WorkOS as an adapter, or descope. Explain the trade-offs — brokers are fast but add a vendor to their security review.)
3. "Why is SCIM important and what happens without it?" (Off-boarding SLA drift — deactivated users linger in your app; audit finding; access review pain. Without SCIM the customer either does JIT-plus-manual or CSV batch, both worse.)

## DRILL

Take your own product (or a fictional one). Write the *customer-facing SSO onboarding doc*: one page, listing supported protocols, required IdP-side configuration, exact attribute names you consume, group naming expectations, and the off-boarding contract. Include a "test account" checklist for the customer to run through before go-live. This doc will save you three weeks of back-and-forth on every deployment; the customers who don't need it will thank you anyway, and the ones who do need it will forward it to their identity team unchanged.
