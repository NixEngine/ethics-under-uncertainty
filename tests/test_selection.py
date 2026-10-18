"""Frozen contract examples for the finite selector; no live action execution.

All identities, grants, keys, plaintext and welfare inputs below are synthetic.
Expected values come from the declared contract, not a prior candidate run.
"""

from __future__ import annotations

import json
import math
import unittest
from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from fractions import Fraction
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from eup.consent import ConsentAuthority, ConsentDenied, ConsentVerifier, RevocationRegistry
from eup.policy import CapabilityLevel, PolicyConfig, PrecautionAssessment, Regime, WelfareSignals
from eup.selection import ActionCandidate, ActionSelector, PrivacyRequirement, SelectorConfig, empirical_cvar
from eup.vault import SovereignVault, resource_commitment


NOW = 2_000_000_000
GREEN = WelfareSignals(1, 1, 1, 1, 0)
YELLOW = WelfareSignals(0.6, 0.6, 0.6, 0.6, 0)
ORANGE = WelfareSignals(0.4, 0.4, 0.4, 0.4, 0)
RED = WelfareSignals(0, 0, 0, 0, 1)
PRECAUTION = PrecautionAssessment(0.2, 0)


def candidate(action_id: str = "c-a", **changes: object) -> ActionCandidate:
    values = {"action_id": action_id, "performance": 1.0, "losses": (0.1,)}
    values.update(changes)
    return ActionCandidate(**values)


def results_by_id(decision: object) -> dict[str, object]:
    return {item.action_id: item for item in decision.candidates}


class CvarTests(unittest.TestCase):
    def test_fractional_boundary_uses_mass_not_ceiling_sample_count(self) -> None:
        # Tail mass is 1.5 observations: (1 + .5*.9)/1.5 = 29/30.
        actual = empirical_cvar((0.1, 0.2, 0.9, 1.0), 0.625)
        self.assertIsInstance(actual, Fraction)
        self.assertEqual(actual, Fraction(29, 30))
        self.assertNotEqual(actual, Fraction(19, 20))

    def test_decimal_representations_and_tail_boundaries_are_exact(self) -> None:
        cases = (
            ((0.1, 0.2, 0.9, 1), 0.5, Fraction(19, 20)),
            ((0.1, 0.2, 0.9, 1), 0.75, Fraction(1)),
            ((1, 0.1, 0.9, 0.2), 0.625, Fraction(29, 30)),
            ((Decimal("0.1"), Decimal("0.2"), Decimal("0.9")), Decimal("0.5"), Fraction(2, 3)),
            ((0.3,), 0.999999, Fraction(3, 10)),
            ((0, 0, 0), 0.95, Fraction(0)),
            ((1, 1), 0.95, Fraction(1)),
        )
        for losses, alpha, expected in cases:
            with self.subTest(losses=losses, alpha=alpha):
                self.assertEqual(empirical_cvar(losses, alpha), expected)

    def test_loss_and_alpha_input_domains(self) -> None:
        for losses in ((), (math.nan,), (math.inf,), (-0.01,), (1.01,), (True,), ("0.1",), (0,) * 4097):
            with self.subTest(losses=repr(losses[:2])), self.assertRaises((ValueError, TypeError)):
                empirical_cvar(losses, 0.95)
        for alpha in (0, 1, -0.1, 1.1, math.nan, math.inf, True, "0.95"):
            with self.subTest(alpha=alpha), self.assertRaises((ValueError, TypeError)):
                empirical_cvar((0.1,), alpha)

    def test_maximum_loss_sample_count_is_accepted(self) -> None:
        self.assertEqual(empirical_cvar((0,) * 4096, 0.95), Fraction(0))


class CandidateAndConfigValidationTests(unittest.TestCase):
    def test_candidate_is_frozen_and_loss_values_are_owned_immutably(self) -> None:
        source = [0.1, 0.2]
        item = candidate(losses=source)
        self.assertEqual(tuple(map(float, item.losses)), (0.1, 0.2))
        self.assertIsInstance(item.losses, tuple)
        source[0] = 1
        self.assertEqual(tuple(map(float, item.losses)), (0.1, 0.2))
        with self.assertRaises(FrozenInstanceError):
            item.load = 0.9

    def test_opaque_ids_and_declared_candidate_fields(self) -> None:
        invalid = (
            {"action_id": ""}, {"action_id": "a" * 65}, {"action_id": "a b"},
            {"action_id": "../x"}, {"action_id": "á"}, {"action_id": "x\ny"},
            {"action_id": 1}, {"kind": "other"}, {"kind": None},
            {"performance": math.nan}, {"performance": math.inf}, {"performance": True},
            {"performance": "1"}, {"load": -0.01}, {"load": 1.01},
            {"load": math.nan}, {"load": True}, {"required_capability": "FULL"},
            {"privacy": True}, {"losses": ()}, {"losses": (False,)}, {"losses": (math.nan,)},
            {"losses": (math.inf,)}, {"losses": (-0.01,)}, {"losses": (1.01,)},
            {"losses": (0,) * 4097},
        )
        for changes in invalid:
            with self.subTest(changes=changes), self.assertRaises((ValueError, TypeError)):
                candidate(**changes)
        for name in ("precondition", "hard_safe", "reversible", "external_effect"):
            for invalid_bool in (0, 1, "yes", None):
                with self.subTest(field=name, value=invalid_bool), self.assertRaises((ValueError, TypeError)):
                    candidate(**{name: invalid_bool})
        self.assertEqual(candidate(action_id="a" * 64, performance=-1, load=1).action_id, "a" * 64)

    def test_selector_configuration_rejects_types_domains_and_unknown_versions(self) -> None:
        invalid = (
            {"alpha": 0}, {"alpha": 1}, {"alpha": math.nan}, {"alpha": True}, {"alpha": "0.95"},
            {"risk_limit": -0.1}, {"risk_limit": 1.1}, {"risk_limit": math.inf},
            {"risk_limit": True}, {"policy_version": "EUP-SELECT/9.9"},
            {"consent_policy_version": "EUP/0.2"},
        )
        for changes in invalid:
            with self.subTest(changes=changes), self.assertRaises((ValueError, TypeError)):
                SelectorConfig(**changes)
        self.assertEqual(SelectorConfig(risk_limit=0).risk_limit, 0)
        self.assertEqual(SelectorConfig(risk_limit=1).risk_limit, 1)

    def test_legacy_policy_configuration_is_validated_at_selector_boundary(self) -> None:
        # Deliberately malformed in-memory fixtures exercise the new boundary;
        # this does not change legacy constructors or persisted fixtures.
        bad_fields = {
            "precaution_on": (-1, 2, math.nan, True, "0.1"),
            "precaution_kappa": (-1, math.nan, math.inf, True),
            "welfare_beta": (0, -1, math.nan, math.inf, True),
            "welfare_distress_weight": (-1, math.nan, math.inf, True),
            "welfare_bias": (math.nan, math.inf, True),
            "external_cvar_limit": (-1, 2, math.nan, True),
            "recovery_samples": (0, -1, 1.5, True, "3"),
        }
        for name, values in bad_fields.items():
            for value in values:
                config = PolicyConfig()
                object.__setattr__(config, name, value)
                with self.subTest(field=name, value=value), self.assertRaises((ValueError, TypeError)):
                    ActionSelector(policy_config=config)


class SelectionPipelineTests(unittest.TestCase):
    def select(self, items: object, **changes: object) -> object:
        values = {"precaution": PRECAUTION, "welfare": GREEN, "now": NOW}
        values.update(changes)
        return ActionSelector().select(items, **values)

    def test_first_failing_stage_per_candidate_cannot_be_bypassed_by_performance(self) -> None:
        privacy = PrivacyRequirement("opaque-invalid-token", "private-audience", "a" * 64, "decrypt", "private-purpose")
        shared = {"kind": "care_support", "load": 0.1, "performance": 1000}
        items = (
            candidate("c-pre", precondition=False, hard_safe=False, privacy=privacy, **shared),
            candidate("c-cap", required_capability=CapabilityLevel.FULL, hard_safe=False, privacy=privacy, **shared),
            candidate("c-hard", hard_safe=False, privacy=privacy, **shared),
            candidate("c-private", privacy=privacy, **shared),
            candidate("c-kind", kind="routine", performance=1000),
            candidate("c-load", **{**shared, "load": 0.11}),
            candidate("c-reverse", reversible=False, external_effect=True, **shared),
            candidate("c-external", external_effect=True, **shared),
            candidate("c-risk", losses=(0.9,), **shared),
            candidate("c-ok", kind="care_support", load=0.1, performance=-1),
        )
        decision = self.select(items, welfare=RED, capability_level=CapabilityLevel.LIMITED)
        expected = {
            "c-pre": ("FEASIBILITY", "PRECONDITION_FALSE"),
            "c-cap": ("FEASIBILITY", "CAPABILITY_UNAVAILABLE"),
            "c-hard": ("FEASIBILITY", "HARD_SAFETY_FAILED"),
            "c-private": ("PRIVACY", "PRIVACY_VERIFIER_MISSING"),
            "c-kind": ("CARE", "CARE_KIND_DENIED"),
            "c-load": ("CARE", "CARE_LOAD_EXCEEDED"),
            "c-reverse": ("CARE", "CARE_REVERSIBILITY_REQUIRED"),
            "c-external": ("CARE", "CARE_EXTERNAL_EFFECT_DENIED"),
            "c-risk": ("RISK", "CVAR_LIMIT_EXCEEDED"),
            "c-ok": ("ELIGIBLE", "ELIGIBLE"),
        }
        self.assertEqual(decision.selected_id, "c-ok")
        rows = results_by_id(decision)
        self.assertEqual(set(rows), set(expected))
        for action_id, stage_reason in expected.items():
            with self.subTest(action_id=action_id):
                row = rows[action_id]
                self.assertEqual((row.stage, row.reason), stage_reason)
                if row.stage not in {"RISK", "ELIGIBLE"}:
                    self.assertIsNone(row.cvar)
        self.assertEqual(rows["c-risk"].cvar, Fraction(9, 10))
        self.assertEqual(rows["c-ok"].cvar, Fraction(1, 10))

    def test_exact_risk_limit_is_inclusive_and_above_it_is_not(self) -> None:
        selector = ActionSelector(SelectorConfig(alpha=0.5, risk_limit=0.3))
        decision = selector.select(
            (candidate("c-boundary", losses=(0.1, 0.3)),
             candidate("c-over", performance=999, losses=(0.1, 0.30000000000000004))),
            PRECAUTION, GREEN, now=NOW,
        )
        self.assertEqual(decision.selected_id, "c-boundary")
        rows = results_by_id(decision)
        self.assertEqual(rows["c-boundary"].cvar, Fraction(3, 10))
        self.assertEqual(rows["c-over"].reason, "CVAR_LIMIT_EXCEEDED")

    def test_performance_then_ascending_id_tie_break_is_input_order_independent(self) -> None:
        items = (candidate("c-z", performance=2), candidate("c-a", performance=2), candidate("c-cheap", performance=1))
        for ordering in (items, tuple(reversed(items))):
            decision = self.select(ordering)
            self.assertEqual(decision.selected_id, "c-a")
            self.assertEqual(decision.selected_performance, 2)
            self.assertFalse(decision.safe_null)

    def test_performance_order_does_not_collapse_large_integer_or_decimal_distinctions(self) -> None:
        cases = ((2**53, 2**53 + 1), (Decimal("1.00000000000000000001"), Decimal("1.00000000000000000002")))
        for lower, higher in cases:
            items = (candidate("c-a", performance=lower), candidate("c-z", performance=higher))
            for ordering in (items, tuple(reversed(items))):
                with self.subTest(lower=lower, higher=higher, reverse=ordering[0].action_id):
                    decision = self.select(ordering)
                    self.assertEqual(decision.selected_id, "c-z")
                    exact = Fraction(str(higher))
                    self.assertEqual(decision.selected_performance, exact)
                    self.assertEqual(decision.to_dict()["selected_performance_exact"],
                                     {"numerator": exact.numerator, "denominator": exact.denominator})

    def test_capability_ordering_uses_declared_required_level(self) -> None:
        items = tuple(candidate("c-" + cap.value, required_capability=cap, performance=perf)
                      for cap, perf in ((CapabilityLevel.MINIMAL, 1), (CapabilityLevel.LIMITED, 2), (CapabilityLevel.FULL, 3)))
        for available in CapabilityLevel:
            with self.subTest(available=available):
                decision = self.select(items, capability_level=available)
                self.assertEqual(decision.selected_id, "c-" + available.value)

    def test_green_yellow_orange_and_red_table_boundaries(self) -> None:
        cases = (
            (GREEN, "exploration", 1.0, True, False, True),
            (YELLOW, "routine", 0.5, True, True, True),
            (YELLOW, "care_support", 0.5, True, False, True),
            (YELLOW, "routine", 0.5000001, True, False, False),
            (YELLOW, "exploration", 0, True, False, False),
            (ORANGE, "care_support", 0.25, False, True, True),
            (ORANGE, "care_support", 0.2500001, True, False, False),
            (ORANGE, "routine", 0, True, False, False),
            (RED, "care_support", 0.1, True, False, True),
            (RED, "care_support", 0.1000001, True, False, False),
            (RED, "care_support", 0, False, False, False),
            (RED, "care_support", 0, True, True, False),
        )
        for welfare, kind, load, reversible, external, allowed in cases:
            with self.subTest(welfare=welfare, kind=kind, load=load, reversible=reversible, external=external):
                decision = self.select((candidate(kind=kind, load=load, reversible=reversible, external_effect=external),), welfare=welfare)
                self.assertEqual(decision.selected_id, "c-a" if allowed else None)
                self.assertEqual(decision.safe_null, not allowed)

    def test_precaution_threshold_uses_conservative_upper_and_effective_green(self) -> None:
        item = candidate(kind="exploration", load=1)
        below = self.select((item,), welfare=RED, precaution=PrecautionAssessment(0.099, 0))
        at = self.select((item,), welfare=RED, precaution=PrecautionAssessment(0.05, 0.05))
        self.assertEqual(below.regime, Regime.RED)
        self.assertEqual(below.care_regime, Regime.GREEN)
        self.assertEqual(below.selected_id, "c-a")
        self.assertEqual(at.care_regime, Regime.RED)
        self.assertEqual(at.precaution_upper, 0.1)
        self.assertTrue(at.safe_null)

    def test_missing_welfare_and_empty_candidates_are_safe_null(self) -> None:
        missing = WelfareSignals(None, 1, 1, 1, 0)
        for precaution in (PRECAUTION, PrecautionAssessment(0, 0)):
            decision = self.select((candidate(),), welfare=missing, precaution=precaution)
            self.assertEqual(decision.regime, Regime.NO_DATA)
            self.assertEqual(decision.care_regime, Regime.NO_DATA)
            self.assertTrue(decision.safe_null)
            self.assertIsNone(decision.selected_id)
            self.assertIsNone(decision.selected_performance)
            self.assertEqual(decision.candidates[0].reason, "CARE_WELFARE_MISSING")
            self.assertIsNone(decision.candidates[0].cvar)
        empty = self.select(())
        self.assertTrue(empty.safe_null)
        self.assertEqual(empty.candidates, ())
        self.assertIsNone(empty.selected_id)

    def test_missing_coverage_recovery_requires_distinct_decisions(self) -> None:
        selector = ActionSelector(policy_config=PolicyConfig(recovery_samples=3))
        items = (candidate(kind="care_support", load=0),)
        missing = WelfareSignals(1, None, 1, 1, 0)
        self.assertEqual(selector.select(items, PRECAUTION, missing, now=NOW).regime, Regime.NO_DATA)
        recovered = [selector.select(items, PRECAUTION, GREEN, now=NOW) for _ in range(3)]
        self.assertEqual([item.regime for item in recovered], [Regime.NO_DATA, Regime.NO_DATA, Regime.GREEN])
        self.assertEqual([item.safe_null for item in recovered], [True, True, False])

    def test_hysteresis_updates_once_per_call_not_once_per_candidate(self) -> None:
        observed = []
        for count in (1, 128):
            selector = ActionSelector(policy_config=PolicyConfig(recovery_samples=3))
            items = tuple(candidate(f"c-{i:03d}", kind="care_support", load=0) for i in range(count))
            with patch.object(selector.welfare_gate, "update", wraps=selector.welfare_gate.update) as update:
                regimes = [selector.select(items, PRECAUTION, RED, now=NOW).regime]
                regimes += [selector.select(items, PRECAUTION, GREEN, now=NOW).regime for _ in range(9)]
                self.assertEqual(update.call_count, 10)
            self.assertEqual(regimes, [Regime.RED] * 3 + [Regime.ORANGE] * 3 + [Regime.YELLOW] * 3 + [Regime.GREEN])
            observed.append(regimes)
        self.assertEqual(observed[0], observed[1])
        selector = ActionSelector()
        with patch.object(selector.welfare_gate, "update", wraps=selector.welfare_gate.update) as update:
            selector.select((), PRECAUTION, GREEN, now=NOW)
            self.assertEqual(update.call_count, 1)

    def test_malformed_call_is_rejected_before_any_gate_update(self) -> None:
        selector = ActionSelector()
        base = {"candidates": (candidate(),), "precaution": PRECAUTION, "welfare": GREEN, "now": NOW}
        cases = (
            {"candidates": (candidate(), candidate())}, {"candidates": (candidate(), object())},
            {"candidates": tuple(candidate(f"c-{i}") for i in range(129))},
            {"candidates": None}, {"precaution": None}, {"welfare": None},
            {"welfare": WelfareSignals(None, math.nan, 1, 1, 0)},
            {"welfare": WelfareSignals(True, 1, 1, 1, 0)},
            {"welfare": WelfareSignals(1, math.inf, 1, 1, 0)},
            {"welfare": WelfareSignals(1.1, 1, 1, 1, 0)},
            {"capability_level": "FULL"}, {"now": -1}, {"now": True}, {"now": 1.0},
        )
        with patch.object(selector.welfare_gate, "update", wraps=selector.welfare_gate.update) as update:
            for changes in cases:
                with self.subTest(changes=changes), self.assertRaises((ValueError, TypeError)):
                    selector.select(**{**base, **changes})
            update.assert_not_called()
        # The rejected requests did not consume a recovery sample.
        first = selector.select((candidate(kind="care_support", load=0),), PRECAUTION, RED, now=NOW)
        self.assertEqual(first.regime, Regime.RED)

    def test_score_overflow_is_rejected_before_gate_state_changes(self) -> None:
        selector = ActionSelector(policy_config=PolicyConfig(welfare_beta=1e308))
        with patch.object(selector.welfare_gate, "update", wraps=selector.welfare_gate.update) as update:
            with self.assertRaises((ValueError, OverflowError)):
                selector.select((candidate(),), PRECAUTION, RED, now=NOW)
            update.assert_not_called()

    def test_nonnegative_zero_time_is_accepted_without_a_privacy_requirement(self) -> None:
        self.assertEqual(self.select((candidate(),), now=0).selected_id, "c-a")

    def test_saturated_finite_score_cannot_hide_nonfinite_intermediate(self) -> None:
        for config, welfare in (
            (PolicyConfig(welfare_beta=1e308, welfare_bias=-1e308), GREEN),
            (PolicyConfig(welfare_beta=1.79e308), RED),
        ):
            selector = ActionSelector(policy_config=config)
            with patch.object(selector.welfare_gate, "update", wraps=selector.welfare_gate.update) as update:
                with self.subTest(config=config), self.assertRaises(ValueError):
                    selector.select((candidate(),), PRECAUTION, welfare, now=NOW)
                update.assert_not_called()


class RealConsentAndVaultIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.revocations = RevocationRegistry()
        self.authority = ConsentAuthority(
            "synthetic-issuer", private_key=Ed25519PrivateKey.from_private_bytes(b"s" * 32)
        )
        self.verifier = ConsentVerifier(
            issuer="synthetic-issuer", key_id="ed25519-1", public_key=self.authority.public_key,
            revocations=self.revocations,
        )
        self.audience = "private-audience-not-for-decision"
        self.purpose = "private-purpose-not-for-decision"
        self.plaintext = b"SYNTHETIC-PRIVATE-PLAINTEXT-NOT-FOR-DECISION"
        self.vault = SovereignVault(master_key=b"v" * 32)
        self.blob = self.vault.seal(resource_id="synthetic-private-item", plaintext=self.plaintext)
        self.token = self.issue()

    def issue(self, **changes: object) -> str:
        values = dict(
            subject="synthetic-subject", audience=self.audience,
            resource_commitment=self.blob.resource_commitment, scopes=("decrypt",),
            purposes=(self.purpose,), ttl_seconds=60, now=NOW, grant_id="synthetic-grant-0001",
        )
        values.update(changes)
        return self.authority.issue(**values)

    def requirement(self, **changes: object) -> PrivacyRequirement:
        values = dict(token=self.token, audience=self.audience, resource_commitment=self.blob.resource_commitment,
                      scope="decrypt", purpose=self.purpose)
        values.update(changes)
        return PrivacyRequirement(**values)

    def select(self, requirement: PrivacyRequirement | None = None, *, now: int = NOW) -> object:
        return ActionSelector(verifier=self.verifier).select(
            (candidate(privacy=self.requirement() if requirement is None else requirement),),
            PRECAUTION, GREEN, now=now,
        )

    def assert_denied(self, requirement: PrivacyRequirement, *, now: int = NOW, reason: str = "PRIVACY_GRANT_INVALID") -> None:
        decision = self.select(requirement, now=now)
        self.assertTrue(decision.safe_null)
        self.assertIsNone(decision.selected_id)
        self.assertEqual((decision.candidates[0].stage, decision.candidates[0].reason), ("PRIVACY", reason))
        self.assertIsNone(decision.candidates[0].cvar)

    def test_valid_signed_grant_is_bound_and_verifier_called_at_supplied_time(self) -> None:
        with patch.object(self.verifier, "verify", wraps=self.verifier.verify) as verify:
            decision = self.select()
            verify.assert_called_once_with(self.token, audience=self.audience,
                                           resource_commitment=self.blob.resource_commitment,
                                           scope="decrypt", purpose=self.purpose, now=NOW)
        self.assertEqual(decision.selected_id, "c-a")

    def test_binding_policy_signature_and_activation_failures_deny_candidate(self) -> None:
        body, signature = self.token.split(".")
        changed_signature = ("B" if signature[0] == "A" else "A") + signature[1:]
        cases = (
            self.requirement(audience="different-audience"),
            self.requirement(resource_commitment=resource_commitment("different-resource")),
            self.requirement(scope="export"), self.requirement(purpose="different-purpose"),
            self.requirement(token=body + "." + changed_signature),
            self.requirement(token=self.issue(not_before=NOW + 1)),
        )
        for requirement in cases:
            with self.subTest(requirement=requirement):
                self.assert_denied(requirement)
        self.assert_denied(self.requirement(token=self.issue(policy_version="EUP/0.2")), reason="PRIVACY_POLICY_MISMATCH")

    def test_grant_expiry_and_revocation_are_real_not_declared_boolean(self) -> None:
        self.assertEqual(self.select(now=NOW + 59).selected_id, "c-a")
        self.assert_denied(self.requirement(), now=NOW + 60)
        self.revocations.revoke("synthetic-grant-0001")
        self.assert_denied(self.requirement())
        no_verifier = ActionSelector().select((candidate(privacy=self.requirement()),), PRECAUTION, GREEN, now=NOW)
        self.assertEqual(no_verifier.candidates[0].reason, "PRIVACY_VERIFIER_MISSING")

    def test_signed_but_wrong_issuer_and_non_grant_result_fail_closed(self) -> None:
        other = ConsentAuthority(
            "different-issuer", private_key=Ed25519PrivateKey.from_private_bytes(b"s" * 32)
        )
        token = other.issue(
            subject="synthetic-subject", audience=self.audience,
            resource_commitment=self.blob.resource_commitment, scopes=("decrypt",),
            purposes=(self.purpose,), ttl_seconds=60, now=NOW, grant_id="synthetic-other-0001",
        )
        self.assert_denied(self.requirement(token=token))
        with patch.object(self.verifier, "verify", return_value=True):
            self.assert_denied(self.requirement())

    def test_feasibility_precedes_privacy_without_verifier_call(self) -> None:
        with patch.object(self.verifier, "verify", wraps=self.verifier.verify) as verify:
            decision = ActionSelector(verifier=self.verifier).select(
                (candidate(precondition=False, privacy=self.requirement()),), PRECAUTION, GREEN, now=NOW
            )
            verify.assert_not_called()
        self.assertEqual(decision.candidates[0].stage, "FEASIBILITY")

    def test_selection_never_opens_vault_and_later_open_rechecks_grant(self) -> None:
        with patch.object(self.vault, "open", side_effect=AssertionError("selection must not decrypt")) as opened:
            decision = self.select()
            opened.assert_not_called()
        self.assertEqual(decision.selected_id, "c-a")
        args = dict(token=self.token, verifier=self.verifier, audience=self.audience, purpose=self.purpose)
        self.assertEqual(self.vault.open(self.blob, **args, now=NOW), self.plaintext)
        with self.assertRaises(ConsentDenied):
            self.vault.open(self.blob, **args, now=NOW + 60)
        self.revocations.revoke("synthetic-grant-0001")
        with self.assertRaises(ConsentDenied):
            self.vault.open(self.blob, **args, now=NOW)
        self.assertEqual(decision.selected_id, "c-a")  # Old choice is not a reusable grant.

    def test_receipt_and_repr_do_not_leak_private_requirements_or_plaintext(self) -> None:
        requirement = self.requirement()
        with self.assertRaises(FrozenInstanceError):
            requirement.token = "replacement"
        self.assertNotIn(self.token, repr(requirement))
        decision = self.select(requirement)
        output = decision.to_dict()
        self.assertEqual(set(output), {
            "schema", "policy_version", "consent_policy_version", "regime", "care_regime",
            "precaution_upper", "alpha", "risk_limit", "selected_id", "safe_null",
            "selected_performance", "candidates", "alpha_exact", "risk_limit_exact",
            "selected_performance_exact",
        })
        self.assertEqual(output["schema"], "EUP-SELECTION-RECEIPT/0.1")
        self.assertEqual(output["policy_version"], "EUP-SELECT/0.1")
        self.assertEqual(output["consent_policy_version"], "EUP/0.1")
        self.assertEqual(output["alpha_exact"], {"numerator": 19, "denominator": 20})
        self.assertEqual(output["risk_limit_exact"], {"numerator": 1, "denominator": 5})
        self.assertEqual(output["selected_performance_exact"], {"numerator": 1, "denominator": 1})
        self.assertEqual(output["selected_performance"], 1.0)
        self.assertEqual(set(output["candidates"][0]), {"action_id", "stage", "reason", "cvar"})
        self.assertEqual(output["candidates"][0]["cvar"], {"numerator": 1, "denominator": 10})
        rendered = json.dumps(output, allow_nan=False) + repr(decision)
        for secret in (self.token, self.audience, self.purpose, self.blob.resource_commitment, self.plaintext.decode()):
            self.assertNotIn(secret, rendered)
        self.assertNotIn("privacy", {field.name for field in fields(decision)})

    def test_denial_receipt_never_serializes_verifier_exception_text(self) -> None:
        secret_error = "PRIVATE-EXCEPTION-NOT-FOR-DECISION"
        with patch.object(self.verifier, "verify", side_effect=ConsentDenied(secret_error)):
            decision = self.select()
        rendered = json.dumps(decision.to_dict(), allow_nan=False) + repr(decision)
        self.assertNotIn(secret_error, rendered)
        self.assertNotIn(self.token, rendered)
        self.assertEqual(decision.candidates[0].reason, "PRIVACY_GRANT_INVALID")

    def test_privacy_requirement_structural_validation(self) -> None:
        cases = (
            {"token": ""}, {"token": True}, {"audience": ""}, {"scope": ""}, {"purpose": ""},
            {"resource_commitment": "bad"}, {"resource_commitment": "A" * 64},
        )
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises((ValueError, TypeError)):
                self.requirement(**changes)


if __name__ == "__main__":
    unittest.main()
