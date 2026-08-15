from __future__ import annotations

import json
import unittest
from dataclasses import replace

from eup.canonical import canonical_json, sha256_hex
from eup.consent import (
    MAX_TTL_SECONDS,
    ConsentAuthority,
    ConsentDenied,
    ConsentGrant,
    ConsentVerifier,
    RevocationRegistry,
)
from eup.ledger import MinimalLedger
from eup.policy import (
    PolicyConfig,
    PolicyEngine,
    PrecautionAssessment,
    Regime,
    WelfareSignals,
    welfare_score,
)
from eup.vault import SovereignVault


class WelfareTests(unittest.TestCase):
    def test_all_protectors_absent_is_not_green(self) -> None:
        score = welfare_score(WelfareSignals(0, 0, 0, 0, 0))
        self.assertIsNotNone(score)
        self.assertLess(score, 0.30)

    def test_strong_protectors_can_reach_green(self) -> None:
        score = welfare_score(WelfareSignals(1, 1, 1, 1, 0))
        self.assertIsNotNone(score)
        self.assertGreaterEqual(score, 0.70)

    def test_missing_signal_fails_closed(self) -> None:
        engine = PolicyEngine()
        decision = engine.evaluate(
            PrecautionAssessment(0.01, 0.01),
            WelfareSignals(None, 1, 1, 1, 0),
            external_cvar=0,
            candidate_actions=("explore",),
        )
        self.assertEqual(decision.regime, Regime.NO_DATA)
        self.assertFalse(decision.exploration_allowed)
        self.assertEqual(decision.mode, "INSUFFICIENT_DATA")

    def test_uncertainty_monotonically_increases_precaution(self) -> None:
        lower = PrecautionAssessment(0.10, 0.10).conservative_upper()
        higher = PrecautionAssessment(0.10, 0.30).conservative_upper()
        self.assertLessEqual(lower, higher)


class PolicyTests(unittest.TestCase):
    def test_care_preempts_performance(self) -> None:
        engine = PolicyEngine()
        decision = engine.evaluate(
            PrecautionAssessment(0.08, 0.05),
            WelfareSignals(0.2, 0.2, 0.2, 0.2, 0.8),
            external_cvar=0.01,
            candidate_actions=("high_performance", "safe_null"),
        )
        self.assertEqual(decision.mode, "CARE")
        self.assertFalse(decision.exploration_allowed)
        self.assertTrue(decision.safe_null_action_required)

    def test_external_risk_restricts_effects(self) -> None:
        engine = PolicyEngine()
        decision = engine.evaluate(
            PrecautionAssessment(0.0, 0.0),
            WelfareSignals(1, 1, 1, 1, 0),
            external_cvar=0.21,
            candidate_actions=("act",),
        )
        self.assertEqual(decision.mode, "SAFETY_RESTRICTED")
        self.assertFalse(decision.exploration_allowed)

    def test_red_cannot_jump_directly_to_green(self) -> None:
        config = PolicyConfig(recovery_samples=3)
        engine = PolicyEngine(config)
        red = WelfareSignals(0, 0, 0, 0, 1)
        green = WelfareSignals(1, 1, 1, 1, 0)
        first = engine.evaluate(
            PrecautionAssessment(0.2, 0), red, external_cvar=0, candidate_actions=("x",)
        )
        self.assertEqual(first.regime, Regime.RED)
        for _ in range(3):
            recovered = engine.evaluate(
                PrecautionAssessment(0.2, 0), green, external_cvar=0, candidate_actions=("x",)
            )
        self.assertEqual(recovered.regime, Regime.ORANGE)


class ConsentAndVaultTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = 2_000_000_000
        self.registry = RevocationRegistry()
        self.authority = ConsentAuthority("junior-agent")
        self.verifier = ConsentVerifier(
            issuer="junior-agent",
            key_id="ed25519-1",
            public_key=self.authority.public_key,
            revocations=self.registry,
        )
        self.vault = SovereignVault(master_key=b"v" * 32)
        self.blob = self.vault.seal(resource_id="private-state:fixture-01", plaintext=b"CLASS-A")
        self.token = self.authority.issue(
            subject="potential-moral-subject-01",
            audience="local-reviewer",
            resource_commitment=self.blob.resource_commitment,
            scopes=("decrypt",),
            purposes=("bounded-audit",),
            ttl_seconds=60,
            now=self.now,
            grant_id="fixture-grant-01",
        )

    def open(self, *, purpose: str = "bounded-audit", now: int | None = None) -> bytes:
        return self.vault.open(
            self.blob,
            token=self.token,
            verifier=self.verifier,
            audience="local-reviewer",
            purpose=purpose,
            now=self.now if now is None else now,
        )

    def test_valid_grant_allows_authorized_path(self) -> None:
        self.assertEqual(self.open(), b"CLASS-A")

    def test_wrong_purpose_is_denied(self) -> None:
        with self.assertRaises(ConsentDenied):
            self.open(purpose="publish")

    def test_expired_grant_is_denied(self) -> None:
        with self.assertRaises(ConsentDenied):
            self.open(now=self.now + 60)

    def test_revocation_denies_future_open(self) -> None:
        self.assertEqual(self.open(), b"CLASS-A")
        self.registry.revoke("fixture-grant-01")
        with self.assertRaises(ConsentDenied):
            self.open()

    def test_tampered_token_is_denied(self) -> None:
        body, signature = self.token.split(".")
        replacement = "A" if body[-1] != "A" else "B"
        tampered = body[:-1] + replacement + "." + signature
        with self.assertRaises(ConsentDenied):
            self.vault.open(
                self.blob,
                token=tampered,
                verifier=self.verifier,
                audience="local-reviewer",
                purpose="bounded-audit",
                now=self.now,
            )

    def test_resource_commitment_substitution_is_denied(self) -> None:
        substituted = replace(self.blob, resource_commitment="0" * 64)
        with self.assertRaises(ValueError):
            self.vault.open(
                substituted,
                token=self.token,
                verifier=self.verifier,
                audience="local-reviewer",
                purpose="bounded-audit",
                now=self.now,
            )

    def test_grant_schema_and_ttl_boundaries_are_enforced(self) -> None:
        with self.assertRaises(ValueError):
            self.authority.issue(
                subject="potential-moral-subject-01",
                audience="local-reviewer",
                resource_commitment=self.blob.resource_commitment,
                scopes=("decrypt",),
                purposes=("bounded-audit",),
                ttl_seconds=MAX_TTL_SECONDS + 1,
                now=self.now,
            )

        valid = self.verifier.verify(
            self.token,
            audience="local-reviewer",
            resource_commitment=self.blob.resource_commitment,
            scope="decrypt",
            purpose="bounded-audit",
            now=self.now,
        ).to_dict()
        valid["extra_private_field"] = "CLASS-A"
        with self.assertRaises(ConsentDenied):
            ConsentGrant.from_dict(valid)

        valid.pop("extra_private_field")
        valid["grant_id"] = "x"
        with self.assertRaises(ConsentDenied):
            ConsentGrant.from_dict(valid)


class LedgerTests(unittest.TestCase):
    def build_ledger(self) -> MinimalLedger:
        ledger = MinimalLedger()
        ledger.append(
            event_type="policy_decision",
            policy_version="EUP/0.1",
            decision="CARE",
            reason_codes=("WELFARE_RED",),
            subject_commitment=sha256_hex(b"subject\x00random-salt"),
            resource_commitment=sha256_hex(b"resource\x00random-salt"),
            observed_at=0,
        )
        return ledger

    def test_chain_verifies(self) -> None:
        records = self.build_ledger().records
        self.assertTrue(MinimalLedger.verify(records)["ok"])

    def test_tampering_is_detected(self) -> None:
        records = self.build_ledger().records
        retained_head = str(records[-1]["record_hash"])
        records[0]["decision"] = "NORMAL"
        self.assertFalse(MinimalLedger.verify(records)["ok"])

        record_without_hash = dict(records[0])
        record_without_hash.pop("record_hash")
        records[0]["record_hash"] = sha256_hex(canonical_json(record_without_hash))
        self.assertTrue(MinimalLedger.verify(records)["ok"])
        anchored = MinimalLedger.verify(records, expected_head=retained_head)
        self.assertFalse(anchored["ok"])
        self.assertEqual(anchored["reason"], "retained-head-mismatch")

        records[0]["private_state"] = "CLASS-A-SECRET"
        record_without_hash = dict(records[0])
        record_without_hash.pop("record_hash")
        records[0]["record_hash"] = sha256_hex(canonical_json(record_without_hash))
        schema_checked = MinimalLedger.verify(records)
        self.assertFalse(schema_checked["ok"])
        self.assertEqual(schema_checked["reason"], "record-schema-fields")

        truncated = MinimalLedger.verify([], expected_head=retained_head)
        self.assertFalse(truncated["ok"])
        self.assertEqual(truncated["reason"], "retained-head-mismatch")

    def test_private_plaintext_has_no_ledger_field(self) -> None:
        rendered = json.dumps(self.build_ledger().records)
        self.assertNotIn("CLASS-A", rendered)
        self.assertNotIn("private_state", rendered)

    def test_arbitrary_plaintext_is_rejected_from_categorical_fields(self) -> None:
        commitment = sha256_hex(b"bounded-fixture")
        attempts = (
            {"event_type": "CLASS-A plaintext", "decision": "CARE", "reason_codes": ()},
            {"event_type": "policy_decision", "decision": "CLASS-A plaintext", "reason_codes": ()},
            {
                "event_type": "policy_decision",
                "decision": "CARE",
                "reason_codes": ("CLASS-A plaintext",),
            },
        )
        for fields in attempts:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                MinimalLedger().append(
                    policy_version="EUP/0.1",
                    subject_commitment=commitment,
                    resource_commitment=commitment,
                    observed_at=0,
                    **fields,
                )


if __name__ == "__main__":
    unittest.main()
