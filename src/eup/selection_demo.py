"""Offline integration example with public synthetic inputs and a test-only key."""

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .canonical import canonical_json, sha256_hex
from .consent import ConsentAuthority, ConsentDenied, ConsentVerifier, RevocationRegistry
from .policy import PrecautionAssessment, WelfareSignals
from .selection import ActionCandidate, ActionSelector, PrivacyRequirement, SelectorConfig
from .vault import SovereignVault


def build_selection_demo_receipt() -> dict[str, object]:
    """Select, then independently authorize a synthetic local vault open.

    The fixed signing key is PUBLIC TEST MATERIAL, never a production secret.
    Random envelope bytes are not persisted; they do not affect this receipt.
    No host permission, live tool, real private source or network is used.
    """
    now = 2_000_000_000
    revocations = RevocationRegistry()
    authority = ConsentAuthority(
        "selection-fixture", private_key=Ed25519PrivateKey.from_private_bytes(b"s" * 32)
    )
    verifier = ConsentVerifier(
        issuer="selection-fixture", key_id=authority.key_id,
        public_key=authority.public_key, revocations=revocations,
    )
    vault = SovereignVault(master_key=b"v" * 32)
    plaintext = b"SYNTHETIC-PRIVATE-SELECTION-FIXTURE"
    blob = vault.seal(resource_id="synthetic-selection-fixture", plaintext=plaintext)
    token = authority.issue(
        subject="synthetic-subject", audience="synthetic-reviewer",
        resource_commitment=blob.resource_commitment, scopes=("decrypt",),
        purposes=("bounded-audit",), ttl_seconds=60, now=now,
        grant_id="synthetic-selection-grant",
    )
    granted = PrivacyRequirement(
        token=token, audience="synthetic-reviewer", resource_commitment=blob.resource_commitment,
        scope="decrypt", purpose="bounded-audit",
    )
    denied = PrivacyRequirement(
        token=token, audience="synthetic-reviewer", resource_commitment=blob.resource_commitment,
        scope="decrypt", purpose="publication",
    )
    candidates = (
        ActionCandidate("candidate-a", performance=100, losses=(0,), privacy=denied),
        ActionCandidate("candidate-b", performance=90, losses=(0, 1), external_effect=True),
        ActionCandidate("candidate-c", performance=10, losses=(0, 0.1), load=0.1, privacy=granted),
        ActionCandidate("candidate-d", performance=1, losses=(0,)),
    )
    selector = ActionSelector(SelectorConfig(alpha=0.75), verifier=verifier)
    decision = selector.select(
        candidates, PrecautionAssessment(0.2, 0), WelfareSignals(1, 1, 1, 1, 0), now=now,
    )
    if decision.selected_id != "candidate-c":
        raise RuntimeError("Synthetic selection did not produce the specified outcome")
    opened = vault.open(
        blob, token=token, verifier=verifier, audience=granted.audience,
        purpose=granted.purpose, now=now,
    )
    if opened != plaintext:
        raise RuntimeError("Synthetic vault round trip differs")
    revocations.revoke("synthetic-selection-grant")
    try:
        vault.open(blob, token=token, verifier=verifier, audience=granted.audience,
                   purpose=granted.purpose, now=now)
    except ConsentDenied:
        subsequent_open_denied = True
    else:
        raise RuntimeError("Revoked synthetic grant unexpectedly opened the vault")
    receipt: dict[str, object] = {
        "schema": "EUP-SELECTION-DEMO/0.1",
        "claim_boundary": (
            "Offline declared-input selection and synthetic local vault integration only. "
            "Selection is not execution or a reusable authorization; vault access rechecks the grant. "
            "No consciousness, clinical calibration, production safety or live tool authority claim."
        ),
        "selection": decision.to_dict(),
        "vault_integration": {
            "separate_grant_check_at_open": True,
            "synthetic_plaintext_matched": True,
            "subsequent_open_denied_after_revocation": subsequent_open_denied,
            "private_content_or_grant_in_receipt": False,
        },
    }
    receipt["receipt_hash"] = sha256_hex(canonical_json(receipt))
    return receipt
