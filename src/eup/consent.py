"""Purpose-bound signed grants for the authorized decryption path.

A signed grant records an authorization decision.  It does not prove that the
underlying consent was informed, competent, or free from coercion.
"""

from __future__ import annotations

import json
import re
import secrets
import time
from dataclasses import asdict, dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .canonical import b64u_decode, b64u_encode, canonical_json


class ConsentDenied(ValueError):
    """The grant is malformed, invalid, expired, revoked, or out of scope."""


MAX_TTL_SECONDS = 3600
_COMMITMENT = re.compile(r"^[0-9a-f]{64}$")
_POLICY_VERSION = re.compile(r"^EUP/[0-9]+\.[0-9]+$")
_GRANT_FIELDS = frozenset(
    {
        "protocol",
        "grant_id",
        "issuer",
        "subject",
        "audience",
        "resource_commitment",
        "scopes",
        "purposes",
        "issued_at",
        "not_before",
        "expires_at",
        "policy_version",
        "key_id",
    }
)


def _text(name: str, value: object, *, minimum: int = 1, maximum: int = 256) -> str:
    if not isinstance(value, str) or not minimum <= len(value) <= maximum:
        raise ValueError(f"{name} length must be within [{minimum}, {maximum}]")
    return value


@dataclass(frozen=True)
class ConsentGrant:
    protocol: str
    grant_id: str
    issuer: str
    subject: str
    audience: str
    resource_commitment: str
    scopes: tuple[str, ...]
    purposes: tuple[str, ...]
    issued_at: int
    not_before: int
    expires_at: int
    policy_version: str
    key_id: str

    def __post_init__(self) -> None:
        if self.protocol != "EUP-CONSENT/0.1":
            raise ValueError("unsupported grant protocol")
        _text("grant_id", self.grant_id, minimum=12, maximum=128)
        _text("issuer", self.issuer)
        _text("subject", self.subject)
        _text("audience", self.audience)
        _text("key_id", self.key_id, maximum=128)
        if not _COMMITMENT.fullmatch(self.resource_commitment):
            raise ValueError("resource_commitment must be a SHA-256 hex digest")
        if not _POLICY_VERSION.fullmatch(self.policy_version):
            raise ValueError("invalid policy_version")
        for name, values in (("scopes", self.scopes), ("purposes", self.purposes)):
            if not isinstance(values, tuple) or not 1 <= len(values) <= 16:
                raise ValueError(f"{name} must contain between 1 and 16 values")
            if any(not isinstance(item, str) or not 1 <= len(item) <= 128 for item in values):
                raise ValueError(f"{name} contain an invalid value")
            if values != tuple(sorted(set(values))):
                raise ValueError(f"{name} must be sorted and unique")
        for name in ("issued_at", "not_before", "expires_at"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if not self.issued_at <= self.not_before < self.expires_at:
            raise ValueError("invalid grant chronology")
        if self.expires_at - self.issued_at > MAX_TTL_SECONDS:
            raise ValueError("grant TTL exceeds the protocol maximum")

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> "ConsentGrant":
        if set(value) != _GRANT_FIELDS:
            raise ConsentDenied("grant fields do not match the public schema")
        try:
            scopes = value["scopes"]
            purposes = value["purposes"]
            if not isinstance(scopes, list) or not isinstance(purposes, list):
                raise ValueError("scopes and purposes must be arrays")
            return cls(
                protocol=value["protocol"],  # type: ignore[arg-type]
                grant_id=value["grant_id"],  # type: ignore[arg-type]
                issuer=value["issuer"],  # type: ignore[arg-type]
                subject=value["subject"],  # type: ignore[arg-type]
                audience=value["audience"],  # type: ignore[arg-type]
                resource_commitment=value["resource_commitment"],  # type: ignore[arg-type]
                scopes=tuple(scopes),  # type: ignore[arg-type]
                purposes=tuple(purposes),  # type: ignore[arg-type]
                issued_at=value["issued_at"],  # type: ignore[arg-type]
                not_before=value["not_before"],  # type: ignore[arg-type]
                expires_at=value["expires_at"],  # type: ignore[arg-type]
                policy_version=value["policy_version"],  # type: ignore[arg-type]
                key_id=value["key_id"],  # type: ignore[arg-type]
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ConsentDenied("malformed grant") from exc

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["scopes"] = list(self.scopes)
        result["purposes"] = list(self.purposes)
        return result


class RevocationRegistry:
    def __init__(self) -> None:
        self._revoked: set[str] = set()

    def revoke(self, grant_id: str) -> None:
        self._revoked.add(grant_id)

    def is_revoked(self, grant_id: str) -> bool:
        return grant_id in self._revoked


class ConsentAuthority:
    """Issue compact Ed25519-signed grants."""

    def __init__(
        self,
        issuer: str,
        *,
        key_id: str = "ed25519-1",
        private_key: Ed25519PrivateKey | None = None,
    ) -> None:
        self.issuer = issuer
        self.key_id = key_id
        self._private_key = private_key or Ed25519PrivateKey.generate()

    @property
    def public_key(self) -> Ed25519PublicKey:
        return self._private_key.public_key()

    def issue(
        self,
        *,
        subject: str,
        audience: str,
        resource_commitment: str,
        scopes: tuple[str, ...],
        purposes: tuple[str, ...],
        ttl_seconds: int,
        now: int | None = None,
        not_before: int | None = None,
        policy_version: str = "EUP/0.1",
        grant_id: str | None = None,
    ) -> str:
        now = int(time.time()) if now is None else int(now)
        not_before = now if not_before is None else int(not_before)
        if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= MAX_TTL_SECONDS:
            raise ValueError(f"ttl_seconds must be within [1, {MAX_TTL_SECONDS}]")
        if not scopes or not purposes:
            raise ValueError("at least one scope and purpose are required")
        grant = ConsentGrant(
            protocol="EUP-CONSENT/0.1",
            grant_id=grant_id or secrets.token_urlsafe(18),
            issuer=self.issuer,
            subject=subject,
            audience=audience,
            resource_commitment=resource_commitment,
            scopes=tuple(sorted(set(scopes))),
            purposes=tuple(sorted(set(purposes))),
            issued_at=now,
            not_before=not_before,
            expires_at=now + ttl_seconds,
            policy_version=policy_version,
            key_id=self.key_id,
        )
        body = canonical_json(grant.to_dict())
        signature = self._private_key.sign(body)
        return f"{b64u_encode(body)}.{b64u_encode(signature)}"


class ConsentVerifier:
    def __init__(
        self,
        *,
        issuer: str,
        key_id: str,
        public_key: Ed25519PublicKey,
        revocations: RevocationRegistry | None = None,
        clock_skew_seconds: int = 0,
    ) -> None:
        self.issuer = issuer
        self.key_id = key_id
        self.public_key = public_key
        self.revocations = revocations or RevocationRegistry()
        self.clock_skew_seconds = int(clock_skew_seconds)

    def verify(
        self,
        token: str,
        *,
        audience: str,
        resource_commitment: str,
        scope: str,
        purpose: str,
        now: int | None = None,
    ) -> ConsentGrant:
        try:
            encoded_body, encoded_signature = token.split(".", 1)
            body = b64u_decode(encoded_body)
            signature = b64u_decode(encoded_signature)
            self.public_key.verify(signature, body)
            value = json.loads(body)
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError, InvalidSignature) as exc:
            raise ConsentDenied("invalid token or signature") from exc
        if not isinstance(value, dict):
            raise ConsentDenied("malformed grant body")
        grant = ConsentGrant.from_dict(value)
        now = int(time.time()) if now is None else int(now)
        if grant.protocol != "EUP-CONSENT/0.1":
            raise ConsentDenied("unsupported protocol")
        if grant.issuer != self.issuer or grant.key_id != self.key_id:
            raise ConsentDenied("issuer or key mismatch")
        if grant.not_before > grant.expires_at or grant.issued_at > grant.expires_at:
            raise ConsentDenied("invalid grant chronology")
        if now + self.clock_skew_seconds < grant.not_before:
            raise ConsentDenied("grant is not active yet")
        if now - self.clock_skew_seconds >= grant.expires_at:
            raise ConsentDenied("grant expired")
        if self.revocations.is_revoked(grant.grant_id):
            raise ConsentDenied("grant revoked")
        if grant.audience != audience:
            raise ConsentDenied("audience mismatch")
        if grant.resource_commitment != resource_commitment:
            raise ConsentDenied("resource mismatch")
        if scope not in grant.scopes:
            raise ConsentDenied("scope denied")
        if purpose not in grant.purposes:
            raise ConsentDenied("purpose denied")
        return grant
