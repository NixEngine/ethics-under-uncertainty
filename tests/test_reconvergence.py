"""Independent R304 contract examples, authored before candidate execution.

All observations, identifiers, partitions and lease declarations are synthetic.
No host update, extension activation or historical-source execution is involved.
"""

from __future__ import annotations

import json
import math
import re
import unittest
from dataclasses import FrozenInstanceError
from decimal import Decimal
from fractions import Fraction

from eup.reconvergence import (
    ExtensionLease, InvariantSpec, ReconvergenceConfig,
    ReconvergenceGuard, ReconvergenceObservation, ReturnState, UpdatePlan,
)


COMMITMENT = "1" * 64
CARD = "decision-r304"


def config(**changes: object) -> ReconvergenceConfig:
    values = dict(invariants=(InvariantSpec("i-main", 10, Fraction(1, 2)),),
                  sensitive_parameters=("p-sensitive",), flexible_parameters=("p-flex",),
                  partition_evidence_commitment=COMMITMENT, window=3,
                  normal_step=1, reconvergence_step=Fraction(1, 10),
                  energy_lambda=2, energy_limit=10, cost_limit=6,
                  entropy_limit=3, initial_energy=10)
    values.update(changes)
    return ReconvergenceConfig(**values)


def observation(sequence: int, observed_at: int | None = None, **changes: object) -> ReconvergenceObservation:
    values = dict(sequence=sequence, observed_at=sequence if observed_at is None else observed_at,
                  invariants=(("i-main", 10),), cost=4, entropy=2)
    values.update(changes)
    return ReconvergenceObservation(**values)


def lease(extension_id: str = "ext-a", **changes: object) -> ExtensionLease:
    values = dict(extension_id=extension_id, impact_commitment="2" * 64,
                  cost=3, expires_at=100, rollback_target="rollback-a")
    values.update(changes)
    return ExtensionLease(**values)


def returning(**changes: object) -> ReconvergenceGuard:
    guard = ReconvergenceGuard(config(**changes))
    guard.enter_exception("declared-failure", decision_card=CARD)
    guard.begin_reconvergence(decision_card=CARD)
    return guard


def snapshot(guard: ReconvergenceGuard) -> tuple[object, ...]:
    return guard.state, guard.stable_count, guard.head, guard.records


class ValueContractTests(unittest.TestCase):
    def test_frozen_values_snapshot_sequences_and_preserve_rationals(self) -> None:
        specs = [InvariantSpec("i-main", Decimal("0.1"), Fraction(1, 3))]
        sensitive, flexible = ["p-sensitive"], ["p-flex"]
        cfg = config(invariants=specs, sensitive_parameters=sensitive, flexible_parameters=flexible)
        samples = [["i-main", Decimal("0.2")]]
        obs = observation(1, invariants=samples, cost=Decimal("0.1"), entropy=Fraction(1, 3))
        parameters, extensions = ["p-flex"], ["ext-a"]
        plan = UpdatePlan(parameters, Decimal("0.1"), extensions)
        specs.clear()
        sensitive.clear()
        flexible.clear()
        samples[0][1] = 999
        parameters.clear()
        extensions.clear()
        self.assertEqual(cfg.invariants[0].baseline, Fraction(1, 10))
        self.assertEqual(cfg.invariants[0].tolerance, Fraction(1, 3))
        self.assertEqual(cfg.sensitive_parameters, ("p-sensitive",))
        self.assertEqual(cfg.flexible_parameters, ("p-flex",))
        self.assertEqual(obs.invariants, (("i-main", Fraction(1, 5)),))
        self.assertEqual((obs.cost, obs.entropy), (Fraction(1, 10), Fraction(1, 3)))
        self.assertEqual((plan.parameters, plan.step, plan.extensions),
                         (("p-flex",), Fraction(1, 10), ("ext-a",)))
        for value, name, replacement in ((cfg, "window", 1), (cfg.invariants[0], "baseline", 99),
                                          (obs, "cost", 99), (plan, "step", 99), (lease(), "cost", 99)):
            with self.subTest(value=type(value).__name__), self.assertRaises(FrozenInstanceError):
                setattr(value, name, replacement)

    def test_numerical_domains_ids_shapes_unknown_fields_and_bounds(self) -> None:
        for number in (True, "1", None, math.nan, math.inf, Decimal("NaN"), Decimal("Infinity")):
            for factory in (lambda: InvariantSpec("i", number, 0),
                            lambda: InvariantSpec("i", 0, number),
                            lambda: config(energy_lambda=number),
                            lambda: observation(1, cost=number) if number is not None else config(initial_energy=None),
                            lambda: lease(cost=number)):
                with self.subTest(number=repr(number)), self.assertRaises((ValueError, TypeError)):
                    factory()
        for name in ("normal_step", "reconvergence_step", "energy_lambda", "energy_limit",
                     "cost_limit", "entropy_limit", "initial_energy"):
            for number in (True, math.nan, math.inf, "1"):
                with self.subTest(field=name, value=repr(number)), self.assertRaises(ValueError):
                    config(**{name: number})
        bad_ids = ("", "../x", "a b", "é", "x\ny", "a" * 65, 1, True)
        for identifier in bad_ids:
            for factory in (lambda: InvariantSpec(identifier, 0, 0),
                            lambda: UpdatePlan((identifier,), 1),
                            lambda: lease(extension_id=identifier),
                            lambda: lease(rollback_target=identifier)):
                with self.subTest(identifier=repr(identifier)), self.assertRaises((ValueError, TypeError)):
                    factory()
        for changes in ({"invariants": ()}, {"invariants": (InvariantSpec("i", 0, 0),) * 2},
                        {"sensitive_parameters": ("p-flex",)},
                        {"flexible_parameters": ("p-flex", "p-flex")},
                        {"partition_evidence_commitment": "A" * 64},
                        {"partition_evidence_commitment": "bad"},
                        {"window": True}, {"window": 0}, {"window": 10001},
                        {"normal_step": 0}, {"reconvergence_step": 0},
                        {"reconvergence_step": 1}, {"energy_lambda": -1},
                        {"cost_limit": -1}, {"entropy_limit": -1},
                        {"initial_energy": -1}, {"initial_energy": 11}):
            with self.subTest(changes=changes), self.assertRaises((ValueError, TypeError)):
                config(**changes)
        for factory in (lambda: InvariantSpec("i", 0, -1),
                        lambda: UpdatePlan((), 1), lambda: UpdatePlan(("p-flex",), 0),
                        lambda: UpdatePlan(("p-flex", "p-flex"), 1),
                        lambda: UpdatePlan((), 0, ("ext-a", "ext-a")),
                        lambda: UpdatePlan((), 0, tuple(f"ext-{n}" for n in range(65))),
                        lambda: lease(impact_commitment=""), lambda: lease(cost=-1),
                        lambda: lease(expires_at=True),
                        lambda: observation(True), lambda: observation(-1),
                        lambda: observation(1, observed_at=True),
                        lambda: observation(1, invariants=(("i-main", 10), ("i-main", 10))),
                        lambda: observation(1, invariants=(("i-main",),)),
                        lambda: observation(1, cost=-1), lambda: observation(1, entropy=-1),
                        lambda: config(unexpected=0), lambda: UpdatePlan(unexpected=0)):
            with self.subTest(factory=factory), self.assertRaises((ValueError, TypeError)):
                factory()
        # Exact upper limits and empty partitions are meaningful valid declarations.
        cfg = config(invariants=tuple(InvariantSpec(f"i-{n}", 0, 0) for n in range(64)),
                     sensitive_parameters=tuple(f"p-{n}" for n in range(128)), flexible_parameters=(),
                     window=10000, energy_lambda=0, energy_limit=0, initial_energy=0)
        self.assertEqual(len(cfg.invariants), 64)
        for changes in ({"invariants": tuple(InvariantSpec(f"i-{n}", 0, 0) for n in range(65))},
                        {"sensitive_parameters": tuple(f"p-{n}" for n in range(129)), "flexible_parameters": ()}):
            with self.assertRaises(ValueError):
                config(**changes)


class TransitionAndObservationTests(unittest.TestCase):
    def test_initial_state_transition_prohibitions_and_explicit_exception(self) -> None:
        guard = ReconvergenceGuard(config())
        self.assertEqual((guard.state, guard.stable_count), (ReturnState.NORMAL, 0))
        self.assertEqual(guard.head, "0" * 64)
        self.assertEqual(guard.records, [])
        self.assertEqual(guard.admit(UpdatePlan(), now=0), "OBSERVATION_MISSING")
        before = snapshot(guard)
        with self.assertRaises(ValueError):
            guard.begin_reconvergence(decision_card=CARD)
        self.assertEqual(snapshot(guard), before)
        guard.enter_exception("declared-failure", decision_card=CARD)
        self.assertEqual(guard.state, ReturnState.EXCEPTION)
        self.assertEqual(guard.admit(UpdatePlan(), now=0), "EXCEPTION_ACTIVE")
        guard.begin_reconvergence(decision_card=CARD)
        self.assertEqual((guard.state, guard.stable_count), (ReturnState.RECONVERGING, 0))
        before = snapshot(guard)
        with self.assertRaises(ValueError):
            guard.begin_reconvergence(decision_card=CARD)
        self.assertEqual(snapshot(guard), before)

    def test_window_exact_tolerance_and_return_sample_restriction(self) -> None:
        guard = returning()
        flexible = UpdatePlan(("p-flex",), Fraction(1, 10))
        sensitive = UpdatePlan(("p-sensitive",), Fraction(1, 10))
        for sequence, value in ((1, Fraction(21, 2)), (2, Fraction(19, 2)), (3, 10)):
            result = guard.observe(observation(sequence, invariants=(("i-main", value),)))
            self.assertTrue(result["valid"])
            self.assertEqual(result["stable_count"], sequence)
            self.assertEqual(result["admission_state"], "RECONVERGING")
            self.assertIsNone(guard.admit(flexible, now=sequence))
            self.assertEqual(guard.admit(sensitive, now=sequence), "SENSITIVE_PARAMETER_FROZEN")
        self.assertEqual(guard.state, ReturnState.NORMAL)
        self.assertEqual(result["state_after"], "NORMAL")
        self.assertEqual(guard.admit(UpdatePlan(("p-flex",), Fraction(100001, 1000000)), now=3),
                         "RECONVERGENCE_STEP_EXCEEDED")
        # A new NORMAL observation, not merely the state label, lifts restrictions.
        result = guard.observe(observation(4, cost=5, entropy=2))
        self.assertTrue(result["valid"])
        self.assertEqual(result["admission_state"], "NORMAL")
        self.assertIsNone(guard.admit(UpdatePlan(("p-sensitive",), 1), now=4))
        self.assertEqual(guard.admit(UpdatePlan(("p-flex",), Fraction(1000001, 1000000)), now=4),
                         "NORMAL_STEP_EXCEEDED")

    def test_each_failure_and_missing_coverage_resets_without_ratchet(self) -> None:
        failures = (
            ({"invariants": (("i-main", Decimal("10.500000000000000001")),)}, "INVARIANT_TOLERANCE_EXCEEDED"),
            ({"cost": Fraction(6000001, 1000000), "entropy": 0}, "COST_LIMIT_EXCEEDED"),
            ({"cost": 0, "entropy": Fraction(3000001, 1000000)}, "ENTROPY_LIMIT_EXCEEDED"),
            ({"cost": 5, "entropy": 3}, "ENERGY_LIMIT_EXCEEDED"),
            ({"invariants": ()}, "COVERAGE_INCOMPLETE"),
            ({"invariants": (("i-main", None),)}, "COVERAGE_INCOMPLETE"),
            ({"cost": None}, "COVERAGE_INCOMPLETE"),
            ({"entropy": None}, "COVERAGE_INCOMPLETE"),
        )
        for changes, reason in failures:
            with self.subTest(reason=reason):
                guard = returning()
                guard.observe(observation(1))  # Accepted E=8.
                result = guard.observe(observation(2, **changes))
                self.assertFalse(result["valid"])
                self.assertIn(reason, result["reasons"])
                self.assertEqual((guard.state, guard.stable_count), (ReturnState.RECONVERGING, 0))
                self.assertEqual(guard.admit(UpdatePlan(), now=2), "OBSERVATION_INVALID")
                result = guard.observe(observation(3))
                self.assertTrue(result["valid"])
                self.assertEqual(guard.stable_count, 1)
        guard = returning()
        guard.observe(observation(1))  # E=8.
        high = guard.observe(observation(2, cost=5, entropy=2))  # E=9 rejected.
        self.assertIn("ENERGY_INCREASED", high["reasons"])
        still_high = guard.observe(observation(3, cost=Fraction(9, 2), entropy=2))  # E=8.5 still rejected.
        self.assertFalse(still_high["valid"])
        low_invalid = guard.observe(observation(4, invariants=(("i-main", 11),), cost=2, entropy=0))
        self.assertFalse(low_invalid["valid"])
        accepted = guard.observe(observation(5, cost=3, entropy=2))  # E=7; invalid E=2 did not ratchet.
        self.assertTrue(accepted["valid"])
        self.assertEqual(accepted["energy_exact"], {"numerator": 7, "denominator": 1})

    def test_exception_samples_consume_order_but_not_return_energy(self) -> None:
        guard = ReconvergenceGuard(config(initial_energy=10, window=1))
        guard.enter_exception("declared-failure", decision_card=CARD)
        result = guard.observe(observation(1, cost=1, entropy=0))
        self.assertEqual((guard.state, guard.stable_count), (ReturnState.EXCEPTION, 0))
        self.assertEqual(result["admission_state"], "EXCEPTION")
        self.assertEqual(guard.admit(UpdatePlan(), now=1), "EXCEPTION_ACTIVE")
        guard.begin_reconvergence(decision_card=CARD)
        before = snapshot(guard)
        with self.assertRaises(ValueError):
            guard.observe(observation(1))
        self.assertEqual(snapshot(guard), before)
        result = guard.observe(observation(2, cost=2, entropy=2))  # E=6, not compared with exception E=1.
        self.assertTrue(result["valid"])
        self.assertEqual(guard.state, ReturnState.NORMAL)

    def test_gap_replay_time_reversal_and_structural_errors_are_atomic(self) -> None:
        guard = returning()
        guard.observe(observation(1, 10))
        for invalid in (observation(1, 10), observation(0, 10), observation(2, 9),
                        observation(2, 10, invariants=(("unknown", 0),))):
            before = snapshot(guard)
            with self.assertRaises(ValueError):
                guard.validate_observation(invalid)
            self.assertEqual(snapshot(guard), before)
            with self.assertRaises(ValueError):
                guard.observe(invalid)
            self.assertEqual(snapshot(guard), before)
        # Validation itself consumes neither sequence nor ledger capacity.
        next_sample = observation(2, 10)
        before = snapshot(guard)
        guard.validate_observation(next_sample)
        self.assertEqual(snapshot(guard), before)
        guard.observe(next_sample)
        self.assertEqual(guard.stable_count, 2)
        result = guard.observe(observation(4, 11))
        self.assertTrue(result["valid"])
        self.assertIn("SEQUENCE_GAP", result["reasons"])
        self.assertEqual((guard.state, guard.stable_count), (ReturnState.RECONVERGING, 1))
        guard.observe(observation(5, 11))
        self.assertEqual(guard.state, ReturnState.RECONVERGING)
        guard.observe(observation(6, 12))
        self.assertEqual(guard.state, ReturnState.NORMAL)

    def test_normal_limits_drift_missing_data_and_monitor_journal(self) -> None:
        guard = ReconvergenceGuard(config())
        self.assertTrue(guard.observe(observation(1, cost=1, entropy=0))["valid"])
        self.assertTrue(guard.observe(observation(2))["valid"])  # NORMAL E may rise from1 to8.
        for name in ("energy", "cost", "entropy"):
            old_head, old_count = guard.head, len(guard.records)
            guard.set_normal_guard(name, False, reason="declared-monitor-change", decision_card=CARD)
            self.assertEqual(len(guard.records), old_count + 1)
            self.assertNotEqual(guard.head, old_head)
            self.assertEqual(guard.admit(UpdatePlan(), now=2), "OBSERVATION_MISSING")
        result = guard.observe(observation(3, cost=20, entropy=20))
        self.assertTrue(result["valid"])
        self.assertEqual(result["normal_guards"], {"energy": False, "cost": False, "entropy": False})
        guard.set_normal_guard("cost", True, reason="declared-monitor-change", decision_card=CARD)
        self.assertEqual(guard.admit(UpdatePlan(), now=3), "OBSERVATION_MISSING")
        result = guard.observe(observation(4, cost=7, entropy=0))
        self.assertFalse(result["valid"])
        self.assertIn("COST_LIMIT_EXCEEDED", result["reasons"])
        self.assertEqual(guard.state, ReturnState.EXCEPTION)
        before = snapshot(guard)
        with self.assertRaises(ValueError):
            guard.set_normal_guard("cost", False, reason="change", decision_card=CARD)
        self.assertEqual(snapshot(guard), before)
        # Disabled numerical monitors never disable coverage/invariants or return constraints.
        for missing in ({"cost": None}, {"entropy": None}, {"invariants": ()},
                        {"invariants": (("i-main", 11),)}):
            separate = ReconvergenceGuard(config(window=1))
            for name in ("energy", "cost", "entropy"):
                separate.set_normal_guard(name, False, reason="change", decision_card=CARD)
            self.assertFalse(separate.observe(observation(1, **missing))["valid"])
            self.assertEqual(separate.state, ReturnState.EXCEPTION)
            separate.begin_reconvergence(decision_card=CARD)
            bad = separate.observe(observation(2, cost=7, entropy=0))
            self.assertFalse(bad["valid"])
            self.assertIn("COST_LIMIT_EXCEEDED", bad["reasons"])

    def test_exact_rational_energy_and_zero_tolerance(self) -> None:
        guard = returning(invariants=(InvariantSpec("i-main", Decimal("0.1"), 0),),
                          energy_lambda=Fraction(1, 3), initial_energy=Fraction(1, 5), window=1)
        result = guard.observe(observation(1, invariants=(("i-main", Fraction(1, 10)),),
                                           cost=Decimal("0.1"), entropy=Fraction(3, 10)))
        self.assertEqual(result["energy_exact"], {"numerator": 1, "denominator": 5})
        self.assertTrue(result["valid"])
        bad = guard.observe(observation(2, invariants=(("i-main", Decimal("0.100000000000000001")),),
                                        cost=0, entropy=0))
        self.assertFalse(bad["valid"])
        self.assertEqual(guard.state, ReturnState.EXCEPTION)


class AdmissionAndLedgerTests(unittest.TestCase):
    def test_freshness_declared_partition_and_nonmutating_admit(self) -> None:
        guard = ReconvergenceGuard(config())
        guard.observe(observation(1, 10))
        before = snapshot(guard)
        guard.validate_update(UpdatePlan(("p-sensitive",), 1))
        self.assertIsNone(guard.admit(UpdatePlan(), now=10))
        self.assertIsNone(guard.admit(UpdatePlan(("p-sensitive",), 1), now=10))
        self.assertEqual(guard.admit(UpdatePlan(), now=9), "OBSERVATION_STALE")
        self.assertEqual(guard.admit(UpdatePlan(), now=11), "OBSERVATION_STALE")
        for bad in (UpdatePlan(("unknown",), 1), object()):
            with self.assertRaises(ValueError):
                guard.validate_update(bad)
            with self.assertRaises(ValueError):
                guard.admit(bad, now=10)
        for now in (-1, True, 10.0):
            with self.assertRaises(ValueError):
                guard.admit(UpdatePlan(), now=now)
        self.assertEqual(snapshot(guard), before)

    def test_extension_missing_expiry_renewal_cost_and_shared_clock(self) -> None:
        guard = ReconvergenceGuard(config())
        guard.observe(observation(1, 10))
        plan = UpdatePlan((), 0, ("ext-a",))
        self.assertEqual(guard.admit(plan, now=10), "EXTENSION_NOT_APPROVED")
        guard.register_extension(lease(expires_at=20), now=10, decision_card=CARD)
        self.assertIsNone(guard.admit(plan, now=10))
        before = snapshot(guard)
        for bad, now in ((lease(expires_at=10), 10), (lease(expires_at=-1), 10),
                         (lease(), 9), (lease(), True)):
            with self.assertRaises(ValueError):
                guard.register_extension(bad, now=now, decision_card=CARD)
            self.assertEqual(snapshot(guard), before)
        guard.observe(observation(2, 20))
        self.assertEqual(guard.admit(plan, now=20), "EXTENSION_EXPIRED")
        count = len(guard.records)
        guard.register_extension(lease(expires_at=30), now=20, decision_card=CARD)
        self.assertEqual(len(guard.records), count + 1)
        self.assertIsNone(guard.admit(plan, now=20))
        guard.register_extension(lease("ext-b", cost=3), now=20, decision_card=CARD)
        pair = UpdatePlan((), 0, ("ext-a", "ext-b"))
        self.assertIsNone(guard.admit(pair, now=20))  # Total6 at limit is allowed.
        guard.register_extension(lease("ext-b", cost=Decimal("3.000000000000000001")), now=20, decision_card=CARD)
        self.assertEqual(guard.admit(pair, now=20), "EXTENSION_COST_LIMIT_EXCEEDED")
        guard.register_extension(lease(expires_at=40), now=21, decision_card=CARD)
        self.assertEqual(guard.admit(plan, now=20), "OBSERVATION_STALE")
        before = snapshot(guard)
        with self.assertRaises(ValueError):
            guard.observe(observation(3, 20))
        self.assertEqual(snapshot(guard), before)

    def test_exception_epoch_invalidates_even_unexpired_lease_and_repeated_exception(self) -> None:
        guard = ReconvergenceGuard(config())
        guard.register_extension(lease(), now=10, decision_card=CARD)
        first = guard.observe(observation(1, 10))
        self.assertEqual(first["epoch"], 0)
        guard.enter_exception("first", decision_card=CARD)
        guard.enter_exception("second", decision_card=CARD)
        guard.begin_reconvergence(decision_card=CARD)
        result = guard.observe(observation(2, 11))
        self.assertEqual(result["epoch"], 2)
        plan = UpdatePlan(("p-flex",), Fraction(1, 10), ("ext-a",))
        self.assertEqual(guard.admit(plan, now=11), "EXTENSION_NOT_APPROVED")
        guard.register_extension(lease(), now=11, decision_card=CARD)
        self.assertIsNone(guard.admit(plan, now=11))
        # A NORMAL violation also invalidates approvals, without beginning return.
        another = ReconvergenceGuard(config())
        another.register_extension(lease(), now=1, decision_card=CARD)
        result = another.observe(observation(1, invariants=()))
        self.assertEqual((result["state_after"], result["epoch"]), ("EXCEPTION", 1))
        self.assertEqual(another.admit(UpdatePlan((), 0, ("ext-a",)), now=1), "EXCEPTION_ACTIVE")

    def test_normal_disabled_cost_does_not_disable_extension_cost_or_ttl(self) -> None:
        guard = ReconvergenceGuard(config())
        guard.set_normal_guard("cost", False, reason="change", decision_card=CARD)
        guard.observe(observation(1))
        guard.register_extension(lease(cost=7), now=1, decision_card=CARD)
        self.assertEqual(guard.admit(UpdatePlan((), 0, ("ext-a",)), now=1), "EXTENSION_COST_LIMIT_EXCEEDED")

    def test_extension_capacity_and_control_arguments_are_atomic(self) -> None:
        guard = ReconvergenceGuard(config())
        for n in range(64):
            guard.register_extension(lease(f"ext-{n}", cost=0), now=0, decision_card=CARD)
        before = snapshot(guard)
        with self.assertRaises(ValueError):
            guard.register_extension(lease("ext-65", cost=0), now=0, decision_card=CARD)
        self.assertEqual(snapshot(guard), before)
        guard.register_extension(lease("ext-0", cost=1), now=0, decision_card=CARD)
        for call in (lambda: guard.enter_exception("arbitrary prose is forbidden", decision_card=CARD),
                     lambda: guard.enter_exception("failure", decision_card="../path"),
                     lambda: guard.register_extension(object(), now=0, decision_card=CARD),
                     lambda: guard.set_normal_guard("unknown", False, reason="change", decision_card=CARD),
                     lambda: guard.set_normal_guard("cost", 1, reason="change", decision_card=CARD)):
            before = snapshot(guard)
            with self.assertRaises(ValueError):
                call()
            self.assertEqual(snapshot(guard), before)

    def test_full_ledger_refusal_changes_no_state_or_latest_observation(self) -> None:
        guard = ReconvergenceGuard(config())
        # One admitted observation, then4095 actual monitor changes fills4096events.
        guard.observe(observation(1))
        for n in range(4095):
            guard.set_normal_guard("cost", bool(n % 2), reason="bounded-change", decision_card=CARD)
        self.assertEqual(len(guard.records), 4096)
        before = snapshot(guard)
        for call in (lambda: guard.observe(observation(2)),
                     lambda: guard.enter_exception("failure", decision_card=CARD),
                     lambda: guard.register_extension(lease(), now=1, decision_card=CARD),
                     lambda: guard.set_normal_guard("cost", True, reason="change", decision_card=CARD)):
            with self.assertRaises(ValueError):
                call()
            self.assertEqual(snapshot(guard), before)

    def test_json_metadata_and_independent_record_copies_never_include_raw_values(self) -> None:
        private_value = Decimal("7331.123456789")
        cfg = config(invariants=(InvariantSpec("i-main", private_value, 0),))
        guard, duplicate = ReconvergenceGuard(cfg), ReconvergenceGuard(cfg)
        sample = observation(7, 42, invariants=(("i-main", private_value),))
        result = guard.observe(sample)
        self.assertEqual(result, duplicate.observe(sample))
        self.assertEqual(set(result), {"schema", "sequence", "observed_at", "state_before", "state_after",
                                      "admission_state", "valid", "stable_count", "reasons", "energy_exact",
                                      "epoch", "normal_guards", "ledger_head", "configuration_commitment"})
        self.assertEqual(result["schema"], "EUP-RECONVERGENCE/0.1")
        self.assertEqual(result["ledger_head"], guard.head)
        self.assertIsNotNone(re.fullmatch(r"[0-9a-f]{64}", guard.head))
        self.assertNotEqual(guard.head, "0" * 64)
        rendered = json.dumps({"metadata": result, "records": guard.records}, allow_nan=False)
        for forbidden in (str(private_value), COMMITMENT, '"invariants"', '"baseline"', '"rollback_target"'):
            self.assertNotIn(forbidden, rendered)
        external = guard.records
        external[0]["external-mutation"] = ["not-owned"]
        external.clear()
        self.assertEqual(len(guard.records), 1)
        result["normal_guards"]["cost"] = False
        result["reasons"].append("external-mutation")
        self.assertEqual(guard.records, duplicate.records)

    def test_chain_binds_configuration_and_full_lease_declaration_without_exposing_them(self) -> None:
        configurations = (config(), config(energy_lambda=Fraction(3, 2)),
                          config(partition_evidence_commitment="5" * 64),
                          config(invariants=(InvariantSpec("i-main", 10, Fraction(1, 3)),)))
        heads, commitments = [], []
        for cfg in configurations:
            value = ReconvergenceGuard(cfg)
            metadata = value.observe(observation(1))
            heads.append(value.head)
            commitments.append(metadata["configuration_commitment"])
            self.assertIsNotNone(re.fullmatch(r"[0-9a-f]{64}", metadata["configuration_commitment"]))
            self.assertEqual(metadata["configuration_commitment"], value.configuration_commitment)
            self.assertEqual(value.records[-1]["configuration_commitment"], value.configuration_commitment)
        self.assertEqual(len(set(heads)), len(configurations))
        self.assertEqual(len(set(commitments)), len(configurations))
        # Decimal and exact-rational declarations of the same value bind identically.
        equivalent = []
        for step in (Decimal("0.1"), Fraction(1, 10)):
            value = ReconvergenceGuard(config(reconvergence_step=step))
            value.register_extension(lease(), now=0, decision_card=CARD)
            equivalent.append(value.head)
        self.assertEqual(equivalent[0], equivalent[1])
        lease_heads = []
        for declaration in (lease(), lease(cost=4), lease(impact_commitment="6" * 64),
                            lease(rollback_target="rollback-b")):
            value = ReconvergenceGuard(config())
            value.register_extension(declaration, now=0, decision_card=CARD)
            lease_heads.append(value.head)
            rendered = json.dumps(value.records, allow_nan=False)
            self.assertIn("lease_commitment", rendered)
            self.assertNotIn(declaration.impact_commitment, rendered)
            self.assertNotIn(declaration.rollback_target, rendered)
        self.assertEqual(len(set(lease_heads)), 4)


if __name__ == "__main__":
    unittest.main()
