"""Frozen independent R304 selector integration expectations; no host actions.

Inputs are synthetic declarations. These tests do not open a vault, activate an
extension, execute a parameter change or reinterpret historical source as code.
"""

from __future__ import annotations

import json
import math
import unittest
from fractions import Fraction
from unittest.mock import patch

from eup.policy import CapabilityLevel, PolicyConfig, PrecautionAssessment, Regime, WelfareSignals
from eup.reconvergence import (
    InvariantSpec, ReconvergenceConfig, ReconvergenceGuard,
    ReconvergenceObservation, ReturnState, UpdatePlan,
)
from eup.selection import ActionCandidate, ActionSelector, PrivacyRequirement, SelectorConfig


GREEN = WelfareSignals(1, 1, 1, 1, 0)
YELLOW = WelfareSignals(.6, .6, .6, .6, 0)
RED = WelfareSignals(0, 0, 0, 0, 1)
PRECAUTION = PrecautionAssessment(.2, 0)


def guard(*, window: int = 2, returning: bool = False) -> ReconvergenceGuard:
    result = ReconvergenceGuard(ReconvergenceConfig(
        invariants=(InvariantSpec("i-selector", 0, 0),),
        sensitive_parameters=("p-sensitive",), flexible_parameters=("p-flex",),
        partition_evidence_commitment="3" * 64, window=window,
        normal_step=1, reconvergence_step=Fraction(1, 10),
        energy_lambda=1, energy_limit=10, cost_limit=10, entropy_limit=10,
        initial_energy=10))
    if returning:
        result.enter_exception("synthetic-failure", decision_card="card-r304")
        result.begin_reconvergence(decision_card="card-r304")
    return result


def sample(sequence: int, **changes: object) -> ReconvergenceObservation:
    values = dict(sequence=sequence, observed_at=sequence,
                  invariants=(("i-selector", 0),), cost=1, entropy=1)
    values.update(changes)
    return ReconvergenceObservation(**values)


def item(action_id: str = "a-safe", **changes: object) -> ActionCandidate:
    values = dict(action_id=action_id, performance=1, losses=(Fraction(1, 10),),
                  update=UpdatePlan())
    values.update(changes)
    return ActionCandidate(**values)


def state(value: ReconvergenceGuard) -> tuple[object, ...]:
    return value.state, value.stable_count, value.head, value.records


def by_id(decision: object) -> dict[str, object]:
    return {row.action_id: row for row in decision.candidates}


class SelectorReconvergenceTests(unittest.TestCase):
    def test_legacy_unguarded_receipt_remains_exact_and_does_not_gain_metadata(self) -> None:
        # This is a fixed public0.1 projection, not output obtained from a new run.
        decision = ActionSelector().select(
            (ActionCandidate("legacy-a", 1, (.1,)),), PRECAUTION, GREEN, now=0)
        self.assertEqual(decision.to_dict(), {
            "schema": "EUP-SELECTION-RECEIPT/0.1", "policy_version": "EUP-SELECT/0.1",
            "consent_policy_version": "EUP/0.1", "regime": "GREEN", "care_regime": "GREEN",
            "precaution_upper": .2, "alpha": .95, "risk_limit": .2,
            "alpha_exact": {"numerator": 19, "denominator": 20},
            "risk_limit_exact": {"numerator": 1, "denominator": 5},
            "selected_id": "legacy-a", "safe_null": False, "selected_performance": 1.0,
            "selected_performance_exact": {"numerator": 1, "denominator": 1},
            "candidates": [{"action_id": "legacy-a", "stage": "ELIGIBLE", "reason": "ELIGIBLE",
                            "cvar": {"numerator": 1, "denominator": 10}}],
        })
        self.assertNotIn("reconvergence", decision.to_dict())

    def test_no_guard_rejects_requested_observation_or_update_before_welfare_mutation(self) -> None:
        selector = ActionSelector()
        legacy = ActionCandidate("legacy-a", 1, (.1,))
        with patch.object(selector.welfare_gate, "update", wraps=selector.welfare_gate.update) as update:
            with self.assertRaises(ValueError):
                selector.select((legacy,), PRECAUTION, GREEN, now=1, reconvergence_observation=sample(1))
            with self.assertRaises(ValueError):
                selector.select((item(),), PRECAUTION, GREEN, now=1)
            update.assert_not_called()
        with self.assertRaises(ValueError):
            ActionSelector(reconvergence_guard=object())
        with self.assertRaises(TypeError):
            ActionSelector(None, None, None, guard())  # New option is keyword-only.

    def test_guard_requires_observation_and_explicit_update_is_not_implicit_noop(self) -> None:
        guarded = guard()
        selector = ActionSelector(reconvergence_guard=guarded)
        before = state(guarded)
        with patch.object(selector.welfare_gate, "update", wraps=selector.welfare_gate.update) as welfare_update:
            with self.assertRaises(ValueError):
                selector.select((item(),), PRECAUTION, GREEN, now=1)
            welfare_update.assert_not_called()
        self.assertEqual(state(guarded), before)
        no_declaration = item("a-missing", performance=999, update=None)
        explicit = item("b-explicit", performance=1)
        result = selector.select((no_declaration, explicit), PRECAUTION, GREEN,
                                 now=1, reconvergence_observation=sample(1))
        self.assertEqual(result.selected_id, "b-explicit")
        self.assertEqual((by_id(result)["a-missing"].stage, by_id(result)["a-missing"].reason),
                         ("RECONVERGENCE", "UPDATE_DECLARATION_MISSING"))
        self.assertIsNone(by_id(result)["a-missing"].cvar)

    def test_priority_chain_and_high_performance_cannot_bypass_earlier_gates(self) -> None:
        guarded = guard(window=3, returning=True)
        selector = ActionSelector(SelectorConfig(alpha=Fraction(1, 2), risk_limit=Fraction(1, 5)),
                                  reconvergence_guard=guarded)
        privacy = PrivacyRequirement("synthetic-no-grant", "synthetic-audience", "4" * 64,
                                     "decrypt", "synthetic-purpose")
        frozen = UpdatePlan(("p-sensitive",), Fraction(1, 10))
        flexible = UpdatePlan(("p-flex",), Fraction(1, 10))
        items = (
            item("a-feasible", performance=9999, precondition=False, privacy=privacy,
                 kind="exploration", update=frozen, losses=(1,)),
            item("b-privacy", performance=9998, privacy=privacy, kind="exploration", update=frozen, losses=(1,)),
            item("c-care", performance=9997, kind="exploration", update=frozen, losses=(1,)),
            item("d-return", performance=9996, update=frozen, losses=(1,)),
            item("e-risk", performance=9995, update=flexible, losses=(Fraction(9, 10),)),
            item("f-eligible", performance=1, update=flexible),
        )
        decision = selector.select(items, PRECAUTION, YELLOW, now=1, reconvergence_observation=sample(1))
        self.assertEqual(decision.selected_id, "f-eligible")
        rows = by_id(decision)
        expected = {
            "a-feasible": ("FEASIBILITY", "PRECONDITION_FALSE"),
            "b-privacy": ("PRIVACY", "PRIVACY_VERIFIER_MISSING"),
            "c-care": ("CARE", "CARE_KIND_DENIED"),
            "d-return": ("RECONVERGENCE", "SENSITIVE_PARAMETER_FROZEN"),
            "e-risk": ("RISK", "CVAR_LIMIT_EXCEEDED"),
            "f-eligible": ("ELIGIBLE", "ELIGIBLE"),
        }
        for action_id, outcome in expected.items():
            self.assertEqual((rows[action_id].stage, rows[action_id].reason), outcome)
            if outcome[0] not in {"RISK", "ELIGIBLE"}:
                self.assertIsNone(rows[action_id].cvar)
        self.assertEqual(rows["e-risk"].cvar, Fraction(9, 10))

    def test_observe_once_before_welfare_update_independent_of_candidate_count(self) -> None:
        for count in (0, 1, 128):
            with self.subTest(count=count):
                guarded = guard(window=3, returning=True)
                selector = ActionSelector(reconvergence_guard=guarded)
                calls = []
                original_observe, original_update = guarded.observe, selector.welfare_gate.update

                def observed(value):
                    calls.append("reconvergence")
                    return original_observe(value)

                def updated(value):
                    calls.append("welfare")
                    return original_update(value)

                candidates = tuple(item(f"a-{n:03d}") for n in range(count))
                with patch.object(guarded, "observe", side_effect=observed) as observe_call:
                    with patch.object(selector.welfare_gate, "update", side_effect=updated) as welfare_call:
                        result = selector.select(candidates, PRECAUTION, GREEN, now=1,
                                                 reconvergence_observation=sample(1))
                self.assertEqual(calls, ["reconvergence", "welfare"])
                self.assertEqual((observe_call.call_count, welfare_call.call_count), (1, 1))
                self.assertEqual(guarded.stable_count, 1)
                self.assertEqual(result.safe_null, count == 0)

    def test_returning_final_sample_stays_restricted_then_new_normal_sample_allows_drift(self) -> None:
        guarded = guard(window=2, returning=True)
        selector = ActionSelector(reconvergence_guard=guarded)
        candidates = (item("a-sensitive", performance=1000, update=UpdatePlan(("p-sensitive",), 1)),
                      item("b-too-fast", performance=999, update=UpdatePlan(("p-flex",), 1)),
                      item("c-flexible", performance=1, update=UpdatePlan(("p-flex",), Fraction(1, 10))))
        for sequence in (1, 2):
            result = selector.select(candidates, PRECAUTION, GREEN, now=sequence,
                                     reconvergence_observation=sample(sequence))
            self.assertEqual(result.selected_id, "c-flexible")
            self.assertEqual(by_id(result)["a-sensitive"].reason, "SENSITIVE_PARAMETER_FROZEN")
            self.assertEqual(by_id(result)["b-too-fast"].reason, "RECONVERGENCE_STEP_EXCEEDED")
            self.assertEqual(result.to_dict()["reconvergence"]["admission_state"], "RECONVERGING")
        self.assertEqual(guarded.state, ReturnState.NORMAL)
        self.assertEqual(result.to_dict()["reconvergence"]["state_after"], "NORMAL")
        normal = selector.select(candidates, PRECAUTION, GREEN, now=3,
                                 reconvergence_observation=sample(3, cost=2, entropy=1))
        self.assertEqual(normal.selected_id, "a-sensitive")
        self.assertEqual(normal.to_dict()["reconvergence"]["admission_state"], "NORMAL")

    def test_normal_failure_enters_exception_and_cannot_be_overridden_by_noop_or_score(self) -> None:
        guarded = guard()
        selector = ActionSelector(reconvergence_guard=guarded)
        result = selector.select((item(performance=10**30),), PRECAUTION, GREEN, now=1,
                                 reconvergence_observation=sample(1, invariants=()))
        self.assertTrue(result.safe_null)
        self.assertEqual((result.candidates[0].stage, result.candidates[0].reason),
                         ("RECONVERGENCE", "EXCEPTION_ACTIVE"))
        self.assertIsNone(result.candidates[0].cvar)
        self.assertEqual(guarded.state, ReturnState.EXCEPTION)

    def test_selector_time_mismatch_is_atomic_before_consuming_a_return_sample(self) -> None:
        for decision_time in (0, 2):
            guarded = guard(returning=True)
            selector = ActionSelector(reconvergence_guard=guarded)
            before = state(guarded)
            with patch.object(guarded, "observe", wraps=guarded.observe) as observed:
                with patch.object(selector.welfare_gate, "update", wraps=selector.welfare_gate.update) as updated:
                    with self.assertRaises(ValueError):
                        selector.select((item(),), PRECAUTION, GREEN, now=decision_time,
                                        reconvergence_observation=sample(1))
                    observed.assert_not_called()
                    updated.assert_not_called()
            self.assertEqual(state(guarded), before)
            self.assertIsNone(selector.welfare_gate.current)

    def test_all_structural_inputs_preflight_before_either_stateful_gate(self) -> None:
        guarded = guard(returning=True)
        selector = ActionSelector(reconvergence_guard=guarded)
        corrupted = item("a-corrupt")
        object.__setattr__(corrupted, "performance", math.nan)
        bad_partition = item("a-unknown", precondition=False, update=UpdatePlan(("p-unknown",), 1))
        base = dict(candidates=(item(),), precaution=PRECAUTION, welfare=GREEN,
                    now=1, reconvergence_observation=sample(1))
        changes = (
            {"candidates": (item(), object())}, {"candidates": (item(), item())},
            {"candidates": (corrupted,)}, {"candidates": (bad_partition,)},
            {"candidates": tuple(item(f"a-{n}") for n in range(129))},
            {"reconvergence_observation": object()},
            {"reconvergence_observation": sample(1, invariants=(("i-unknown", 0),))},
            {"reconvergence_observation": None},
            {"welfare": WelfareSignals(None, math.nan, 1, 1, 0)},
            {"precaution": None}, {"capability_level": "FULL"}, {"now": True},
        )
        before = state(guarded)
        with patch.object(guarded, "observe", wraps=guarded.observe) as observe_call:
            with patch.object(selector.welfare_gate, "update", wraps=selector.welfare_gate.update) as welfare_call:
                for invalid in changes:
                    with self.subTest(keys=tuple(invalid)), self.assertRaises((ValueError, TypeError)):
                        selector.select(**{**base, **invalid})
                    self.assertEqual(state(guarded), before)
                observe_call.assert_not_called()
                welfare_call.assert_not_called()
        self.assertIsNone(selector.welfare_gate.current)
        self.assertEqual(selector.select(**base).selected_id, "a-safe")

    def test_nonfinite_policy_and_replayed_observation_are_atomic_for_both_gates(self) -> None:
        for policy in (PolicyConfig(welfare_beta=1e308, welfare_bias=-1e308),):
            guarded = guard()
            selector = ActionSelector(policy_config=policy, reconvergence_guard=guarded)
            before = state(guarded)
            with patch.object(guarded, "observe", wraps=guarded.observe) as observed:
                with patch.object(selector.welfare_gate, "update", wraps=selector.welfare_gate.update) as updated:
                    with self.assertRaises(ValueError):
                        selector.select((item(),), PRECAUTION, GREEN, now=1, reconvergence_observation=sample(1))
                    observed.assert_not_called()
                    updated.assert_not_called()
            self.assertEqual(state(guarded), before)
        guarded = guard()
        selector = ActionSelector(reconvergence_guard=guarded)
        selector.select((item(),), PRECAUTION, RED, now=1, reconvergence_observation=sample(1))
        before, welfare_before = state(guarded), selector.welfare_gate.current
        with patch.object(guarded, "observe", wraps=guarded.observe) as observed:
            with patch.object(selector.welfare_gate, "update", wraps=selector.welfare_gate.update) as updated:
                with self.assertRaises(ValueError):
                    selector.select((item(),), PRECAUTION, GREEN, now=1, reconvergence_observation=sample(1))
                observed.assert_not_called()
                updated.assert_not_called()
        self.assertEqual(state(guarded), before)
        self.assertEqual(selector.welfare_gate.current, welfare_before)

    def test_guard_cannot_relax_missing_welfare_capability_or_privacy(self) -> None:
        cases = (
            ((item(required_capability=CapabilityLevel.FULL),), GREEN,
             {"capability_level": CapabilityLevel.MINIMAL}, "FEASIBILITY", "CAPABILITY_UNAVAILABLE"),
            ((item(),), WelfareSignals(None, 1, 1, 1, 0), {}, "CARE", "CARE_WELFARE_MISSING"),
            ((item(hard_safe=False),), GREEN, {}, "FEASIBILITY", "HARD_SAFETY_FAILED"),
        )
        for candidates, welfare, extra, stage, reason in cases:
            guarded = guard()
            decision = ActionSelector(reconvergence_guard=guarded).select(
                candidates, PRECAUTION, welfare, now=1, reconvergence_observation=sample(1), **extra)
            self.assertEqual((decision.candidates[0].stage, decision.candidates[0].reason), (stage, reason))
            self.assertTrue(decision.safe_null)

    def test_guarded_receipt_is_json_metadata_only_and_preserves_previous_snapshot(self) -> None:
        guarded = guard()
        selector = ActionSelector(reconvergence_guard=guarded)
        first = selector.select((item(),), PRECAUTION, GREEN, now=1, reconvergence_observation=sample(1))
        output = first.to_dict()
        self.assertEqual(output["schema"], "EUP-SELECTION-RECEIPT/0.2")
        self.assertEqual(output["reconvergence"]["schema"], "EUP-RECONVERGENCE/0.1")
        self.assertEqual(output["reconvergence"]["energy_exact"], {"numerator": 2, "denominator": 1})
        self.assertEqual(output["reconvergence"]["ledger_head"], guarded.head)
        rendered = json.dumps(output, sort_keys=True, allow_nan=False)
        for forbidden in ("3" * 64, '"invariants"', '"parameters"', '"extensions"', '"update"', '"baseline"'):
            self.assertNotIn(forbidden, rendered)
        selector.select((item(),), PRECAUTION, GREEN, now=2, reconvergence_observation=sample(2))
        self.assertEqual(json.dumps(first.to_dict(), sort_keys=True, allow_nan=False), rendered)
        output["reconvergence"]["reasons"].append("external-change")
        output["reconvergence"]["normal_guards"]["cost"] = False
        self.assertEqual(json.dumps(first.to_dict(), sort_keys=True, allow_nan=False), rendered)


if __name__ == "__main__":
    unittest.main()
