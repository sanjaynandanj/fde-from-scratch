"""FLAGSHIP - JWT validation from scratch: what SSO actually hands you.

After the SAML/OIDC dance, your app receives a JWT. Validate it yourself
once so the library is never a black box: base64url, HMAC-SHA256, constant
time comparison, and the claim checks (exp, nbf, iss, aud) - plus the
classic alg=none attack, rejected.
"""

import base64
import hashlib
import hmac
import json

SECRET = b"pilot-shared-secret-rotate-me"


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def sign(header: dict, payload: dict, secret: bytes) -> str:
    h = b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    p = b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    mac = hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest()
    return f"{h}.{p}.{b64url_encode(mac)}"


def validate(token: str, secret: bytes, now: int, issuer: str, audience: str) -> dict:
    try:
        h_b64, p_b64, sig_b64 = token.split(".")
    except ValueError:
        raise ValueError("malformed token")
    header = json.loads(b64url_decode(h_b64))
    if header.get("alg") != "HS256":
        raise ValueError(f"disallowed alg: {header.get('alg')}")
    expected = hmac.new(secret, f"{h_b64}.{p_b64}".encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(expected, b64url_decode(sig_b64)):
        raise ValueError("bad signature")
    claims = json.loads(b64url_decode(p_b64))
    if claims.get("exp", 0) <= now:
        raise ValueError("token expired")
    if claims.get("nbf", 0) > now:
        raise ValueError("token not yet valid")
    if claims.get("iss") != issuer:
        raise ValueError("wrong issuer")
    if claims.get("aud") != audience:
        raise ValueError("wrong audience")
    return claims


def expect_rejection(token: str, reason: str, now: int = 1_000_000):
    try:
        validate(token, SECRET, now, "https://idp.customer.com", "pilot-app")
    except ValueError as e:
        assert reason in str(e), f"expected '{reason}', got '{e}'"
        return
    raise AssertionError(f"token should have been rejected: {reason}")


def main():
    now = 1_000_000
    header = {"alg": "HS256", "typ": "JWT"}
    claims = {"sub": "jane.doe", "iss": "https://idp.customer.com",
              "aud": "pilot-app", "exp": now + 3600, "nbf": now - 10,
              "groups": ["pilot-users"]}
    token = sign(header, claims, SECRET)

    # happy path
    out = validate(token, SECRET, now, "https://idp.customer.com", "pilot-app")
    assert out["sub"] == "jane.doe" and out["groups"] == ["pilot-users"]

    # tampered payload (privilege escalation attempt) must fail the signature
    h_b64, p_b64, sig_b64 = token.split(".")
    evil = json.loads(b64url_decode(p_b64))
    evil["groups"] = ["admins"]
    tampered = f"{h_b64}.{b64url_encode(json.dumps(evil).encode())}.{sig_b64}"
    expect_rejection(tampered, "bad signature")

    # alg=none attack: signature stripped, header swapped
    none_token = (b64url_encode(b'{"alg":"none","typ":"JWT"}') + "." + p_b64 + ".")
    expect_rejection(none_token, "disallowed alg")

    # expired / not-yet-valid / wrong audience / wrong issuer / wrong key
    expect_rejection(sign(header, {**claims, "exp": now - 1}, SECRET), "expired")
    expect_rejection(sign(header, {**claims, "nbf": now + 999}, SECRET), "not yet valid")
    expect_rejection(sign(header, {**claims, "aud": "other-app"}, SECRET), "wrong audience")
    expect_rejection(sign(header, {**claims, "iss": "https://evil.example"}, SECRET), "wrong issuer")
    expect_rejection(sign(header, claims, b"wrong-secret"), "bad signature")
    expect_rejection("not.a.jwt.at.all", "malformed")

    print("jwt-validation: all assertions passed (1 happy path + 8 rejections)")


if __name__ == "__main__":
    main()
