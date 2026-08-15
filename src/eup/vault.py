"""Small envelope-encryption reference path bound to a ConsentGrant."""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .canonical import b64u_decode, b64u_encode, sha256_hex
from .consent import ConsentVerifier


def resource_commitment(resource_id: str) -> str:
    return sha256_hex(b"EUP-RESOURCE-ID\x00" + resource_id.encode("utf-8"))


@dataclass(frozen=True)
class SealedBlob:
    protocol: str
    resource_id: str
    resource_commitment: str
    classification: str
    data_nonce: str
    ciphertext: str
    wrap_nonce: str
    wrapped_data_key: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


class SovereignVault:
    """Demonstrate consent-gated decryption inside a controlled key domain.

    This class is not a KMS/HSM and makes no claim about root compromise,
    plaintext already disclosed, copied backups, or exfiltrated keys.
    """

    def __init__(self, *, master_key: bytes | None = None) -> None:
        self._master_key = master_key or AESGCM.generate_key(bit_length=256)
        if len(self._master_key) != 32:
            raise ValueError("master_key must contain 32 bytes")

    @staticmethod
    def _data_aad(resource_id: str, classification: str) -> bytes:
        return f"EUP-DATA/0.1\x00{resource_id}\x00{classification}".encode("utf-8")

    @staticmethod
    def _wrap_aad(resource_id: str) -> bytes:
        return f"EUP-DEK/0.1\x00{resource_id}".encode("utf-8")

    def seal(self, *, resource_id: str, plaintext: bytes, classification: str = "A") -> SealedBlob:
        if classification not in {"A", "B", "C"}:
            raise ValueError("unsupported data classification")
        data_key = AESGCM.generate_key(bit_length=256)
        data_nonce = os.urandom(12)
        wrap_nonce = os.urandom(12)
        ciphertext = AESGCM(data_key).encrypt(
            data_nonce,
            plaintext,
            self._data_aad(resource_id, classification),
        )
        wrapped_data_key = AESGCM(self._master_key).encrypt(
            wrap_nonce,
            data_key,
            self._wrap_aad(resource_id),
        )
        return SealedBlob(
            protocol="EUP-VAULT/0.1",
            resource_id=resource_id,
            resource_commitment=resource_commitment(resource_id),
            classification=classification,
            data_nonce=b64u_encode(data_nonce),
            ciphertext=b64u_encode(ciphertext),
            wrap_nonce=b64u_encode(wrap_nonce),
            wrapped_data_key=b64u_encode(wrapped_data_key),
        )

    def open(
        self,
        blob: SealedBlob,
        *,
        token: str,
        verifier: ConsentVerifier,
        audience: str,
        purpose: str,
        now: int | None = None,
    ) -> bytes:
        if blob.protocol != "EUP-VAULT/0.1":
            raise ValueError("unsupported vault protocol")
        expected_commitment = resource_commitment(blob.resource_id)
        if blob.resource_commitment != expected_commitment:
            raise ValueError("resource commitment does not match resource_id")
        verifier.verify(
            token,
            audience=audience,
            resource_commitment=expected_commitment,
            scope="decrypt",
            purpose=purpose,
            now=now,
        )
        data_key = AESGCM(self._master_key).decrypt(
            b64u_decode(blob.wrap_nonce),
            b64u_decode(blob.wrapped_data_key),
            self._wrap_aad(blob.resource_id),
        )
        return AESGCM(data_key).decrypt(
            b64u_decode(blob.data_nonce),
            b64u_decode(blob.ciphertext),
            self._data_aad(blob.resource_id, blob.classification),
        )
