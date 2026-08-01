# JWT Validation from Scratch: What SSO Actually Hands You

Phase 4 · Lesson 03 · ~2h

## PROBLEM

The pilot is ready, and the customer's one non-negotiable is "it has to be behind our Okta." Fine — the identity team configures the integration, the redirect dance works, and your app starts receiving a long dotted string on every request. A contractor on the team wires it up in an afternoon: split the token, base64-decode the middle part, read `groups`, done. Demo works. Six weeks later, the customer's security review runs one scripted test — they change `"groups": ["pilot-users"]` to `"groups": ["admins"]` in the payload, re-encode it, and send it. Your app grants admin. The pentest report phrase is "authentication bypass, critical," the pilot is frozen pending remediation, and the CISO who was neutral about you is now not.

The contractor's mistake wasn't laziness; it was treating the JWT as *data* when it's actually a *cryptographic claim*. Decoding is not validating. Every FDE deploying behind enterprise SSO receives these tokens; validating one from scratch — once — is how the library you'll use in production stops being a black box you can't defend in a security review.

## INTUITION

After the SAML/OIDC ceremony completes, what your app actually receives is a JWT: three base64url segments, `header.payload.signature`. The header says how it's signed, the payload carries claims (who, issued by whom, for whom, valid when), and the signature is a MAC or digital signature over the first two segments. Validation is a *gauntlet*, and order matters:

**1. Parse strictly.** Exactly three segments or reject. Malformed tokens should die at the door with a clear error, not deep in a decoder.

**2. Pin the algorithm.** The header's `alg` field is attacker-controlled input. The infamous `alg=none` attack sends an unsigned token whose header politely announces it's unsigned; naive libraries historically honored it. There's also the RS256→HS256 confusion attack, where an attacker gets your server to verify an HMAC made with the *public* key it knows. The defense for both is the same and brutal: **you decide the allowed algorithm in server config; the token doesn't get a vote.** Expect HS256 (shared secret — common in pilots and internal services) or RS256 (issuer signs with a private key, you verify with their published JWKS — the enterprise norm).

**3. Verify the signature before believing anything.** Recompute the MAC over the exact base64url text you received and compare in constant time. Non-constant-time comparison leaks how many bytes matched through response timing — that's why `hmac.compare_digest` exists.

**4. Then check the claims.** `exp` (expired?), `nbf` (not valid yet?), `iss` (from the IdP I trust?), `aud` (meant for *my* app?). The `aud` check is the one people skip and shouldn't: within one Okta tenant, a token minted for the HR app will pass signature and issuer checks at your app — audience is the only thing making tokens non-transferable between apps.

The mental model: signature answers *"is this envelope really from the IdP, unopened?"*; claims answer *"is the letter inside addressed to me, still valid, today?"*. Both, always, in that order.

## BUILD IT

Run it: `python code/lesson.py` — one happy path, eight distinct rejections.

**Base64url, with the padding trick.** JWT uses URL-safe base64 with padding stripped; decoding needs it back:

```python
def b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
```

`-len(s) % 4` computes exactly the padding needed — a two-character idiom worth memorizing, because half of all "invalid token" bugs in the field are padding bugs.

**Signing shows what a signature *is*.** `sign` serializes header and payload with `separators=(",", ":")` (compact JSON — byte-exact serialization matters because the signature covers bytes, not meaning), then MACs the dotted pair:

```python
mac = hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest()
return f"{h}.{p}.{b64url_encode(mac)}"
```

That's all HS256 is: HMAC-SHA256 over `header.payload`.

**`validate` is the gauntlet, in the right order.** Parse (`token.split(".")` inside a try — malformed dies first). Then the algorithm pin, *before* any cryptography:

```python
if header.get("alg") != "HS256":
    raise ValueError(f"disallowed alg: {header.get('alg')}")
```

Note it's an allowlist of one, not a denylist of `none` — tomorrow's attack algorithm is also rejected. Then the signature, recomputed over the *received* base64 text and compared safely:

```python
expected = hmac.new(secret, f"{h_b64}.{p_b64}".encode(), hashlib.sha256).digest()
if not hmac.compare_digest(expected, b64url_decode(sig_b64)):
    raise ValueError("bad signature")
```

Only after the signature holds does the code even parse the claims — then four checks: `exp <= now` rejects expired, `nbf > now` rejects not-yet-valid, `iss` must equal the expected issuer, `aud` the expected audience. `now` is a parameter, not `time.time()` — which is why the whole gauntlet is deterministic and testable, and it's the same design you want in production (clock injection makes expiry testable).

**The test suite is an attack suite.** `expect_rejection` asserts not just that a token dies but *why* — the error message must match, so a token failing for the wrong reason is itself a test failure. The attacks, in order: a **tampered payload** — the test decodes the real payload, sets `"groups": ["admins"]`, re-encodes, and keeps the original signature; it must die with `bad signature`, which is precisely the pentest from the war story. The **alg=none attack** — header swapped for `{"alg":"none"}`, signature stripped; it must die at `disallowed alg`, never reaching signature logic. Then expired, not-yet-valid, wrong audience, wrong issuer, **wrong key** (signed with `b"wrong-secret"` — a valid token from the wrong universe), and structural garbage (`"not.a.jwt.at.all"`). One happy path proves the gauntlet passes honest tokens and hands back usable claims (`sub`, `groups`).

Ninety lines, and every classic JWT CVE class has a named assertion.

## FIELD NOTES

- In production you'll use a vetted library — building it yourself is for understanding, not deployment. But the *configuration* of that library is your job, and every knob maps to a line in this file: allowed algorithms (the pin), expected issuer and audience, clock skew tolerance. Library defaults are historically where the vulnerabilities lived.
- Real enterprise tokens are RS256 with keys fetched from the IdP's JWKS endpoint — which adds key rotation (`kid` header selects the key) and the operational question of caching JWKS when the IdP is briefly unreachable. The claim gauntlet is unchanged.
- Add small clock-skew tolerance (±60s) on `exp`/`nbf` in real deployments; customer server clocks drift, and "everyone got logged out because our VM's NTP broke" is a real incident category.
- Never log tokens. A JWT in a log file is a bearer credential in a log file; scrub them from error reports and access logs before the security review finds them — Phase 6 territory.
- The `groups` claim's *contents* are a negotiation: the customer's IdP admin must map their AD groups into the token. Get the exact group names in writing early; "pilot-users" vs "Pilot_Users" has burned a demo morning before.

## INTERVIEW ANGLE

JWT questions appear in FDE loops both as security screening ("do you understand what SSO hands you?") and as practical coding ("validate this token, no libraries"). Depth beyond "the library does it" is exactly the differentiator.

Sample questions:

1. "Walk me through everything that must be checked before trusting a JWT." (Structure, algorithm pin, signature with constant-time compare, then exp/nbf/iss/aud — order included.)
2. "What is the alg=none attack and why did it work against real libraries?" (Attacker controls the header; libraries let the token pick its own verification method; defense is a server-side allowlist.)
3. "Your app validates signature and expiry. The customer runs three other apps on the same Okta tenant. What's still wrong?" (Missing `aud` check — tokens for other apps in the tenant pass; audience makes tokens app-specific.)

## DRILL

1. **Extend:** add clock-skew tolerance — a `leeway: int = 0` parameter applied to `exp` and `nbf`. Assert that a token expired 30 seconds ago passes with `leeway=60` and still fails with `leeway=10`.
2. **Break:** change `hmac.compare_digest` to `==` and confirm all tests still pass — then write one paragraph on why the tests *can't* catch this bug (timing side channels don't show up in functional assertions) and what that teaches about security review vs. testing.
3. **Fix:** the current code accepts a token with *no* `exp` claim… does it? Read `claims.get("exp", 0) <= now` again — a missing `exp` defaults to 0, which is ≤ now, so it's rejected. But `iss`/`aud` use `.get(...) != expected`, and `nbf` defaults to 0 (always valid). Decide the policy an enterprise reviewer would want (required claims must be *present*, not defaulted), implement a `required_claims` check, and add assertions for a token missing each one.
