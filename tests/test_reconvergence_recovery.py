"""Portable recovery contracts using synthetic declarations and local files.

The recovery expectations were authored independently of the implementation.
Temporary files use the platform temporary directory. A new subprocess example
checks restart integration; no selected action, extension or rollback is run.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fractions import Fraction

import eup.reconvergence_store as store
from eup.reconvergence import (
    ExtensionLease,
    InvariantSpec,
    ReconvergenceConfig,
    ReconvergenceGuard,
    ReconvergenceObservation,
    ReturnState,
    UpdatePlan,
)
from eup.selection import ActionCandidate, ActionSelector
from eup.policy import PolicyConfig, PrecautionAssessment, WelfareSignals


ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 8 * 1024 * 1024
ZERO_HEAD = "0" * 64


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def config(*, window: int = 3, **changes: object) -> ReconvergenceConfig:
    fields = dict(
        invariants=(InvariantSpec("offset", 5, Fraction(1, 4)),),
        sensitive_parameters=("fixed",), flexible_parameters=("tunable",),
        partition_evidence_commitment="c" * 64,
        window=window, normal_step=Fraction(3, 2),
        reconvergence_step=Fraction(1, 8), energy_lambda=2,
        energy_limit=30, cost_limit=20, entropy_limit=10, initial_energy=30,
    )
    fields.update(changes)
    return ReconvergenceConfig(**fields)


def observation(sequence: int, at: int, *, cost: object = 12,
                entropy: object = 3) -> ReconvergenceObservation:
    return ReconvergenceObservation(sequence, at, (("offset", 5),), cost, entropy)


def returning_guard(*, window: int = 3, observations: int = 1) -> ReconvergenceGuard:
    guard = ReconvergenceGuard(config(window=window))
    guard.enter_exception("new_interruption", decision_card="recovery-interrupt")
    guard.begin_reconvergence(decision_card="recovery-return")
    for index in range(observations):
        guard.observe(observation(40 + index, 400 + index, cost=12 - index))
    return guard


class RecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="eup-recovery-new-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def restored(self, guard: ReconvergenceGuard) -> ReconvergenceGuard:
        raw = guard.export_snapshot()
        return ReconvergenceGuard.from_snapshot(
            guard.config, raw,
            expected_snapshot_sha256=digest(raw), expected_head=guard.head,
        )

    def assert_chain(self, guard: ReconvergenceGuard) -> None:
        previous = ZERO_HEAD
        for index, record in enumerate(guard.records, 1):
            self.assertEqual(record["index"], index)
            self.assertEqual(record["previous_head"], previous)
            self.assertEqual(record["configuration_commitment"], guard.configuration_commitment)
            payload = {key: value for key, value in record.items() if key != "head"}
            self.assertEqual(record["head"], digest(canonical(payload)))
            previous = record["head"]
        self.assertEqual(guard.head, previous)

    def assert_rejected_document(self, original: ReconvergenceGuard,
                                 document: dict[str, object]) -> None:
        raw = canonical(document)
        # Matching digest deliberately excludes a trivial stale-digest refusal:
        # the loader must also check schema, shape and state/chain coherence.
        with self.assertRaises(ValueError):
            ReconvergenceGuard.from_snapshot(
                original.config, raw,
                expected_snapshot_sha256=digest(raw), expected_head=original.head,
            )

    def test_export_is_canonical_read_only_complete_and_independent(self) -> None:
        guard = returning_guard()
        old_head, old_records = guard.head, guard.records
        first, second = guard.export_snapshot(), guard.export_snapshot()
        self.assertIsInstance(first, bytes)
        self.assertEqual(first, second)
        self.assertEqual(first, canonical(json.loads(first)))
        self.assertFalse(first.startswith(b"\xef\xbb\xbf"))
        self.assertFalse(first.endswith(b"\n"))
        data = json.loads(first)
        self.assertEqual(set(data), {"schema", "config", "configuration_commitment", "guard", "records", "head"})
        self.assertEqual(data["schema"], "EUP-RECONVERGENCE-SNAPSHOT/0.1")
        self.assertEqual(data["records"], old_records)
        self.assertEqual(data["head"], old_head)
        self.assertEqual(data["guard"]["accepted_energy_exact"], {"numerator": 18, "denominator": 1})
        self.assertEqual(data["guard"]["stable_count"], 1)
        data["guard"]["stable_count"] = 99
        data["records"][0]["event"] = "not-the-event"
        self.assertEqual(guard.export_snapshot(), first)
        self.assertEqual(guard.head, old_head)
        self.assertEqual(guard.records, old_records)

    def test_restore_records_boundary_and_requires_new_observation(self) -> None:
        guard = returning_guard()
        raw, old_head, old_records = guard.export_snapshot(), guard.head, guard.records
        recovered = ReconvergenceGuard.from_snapshot(
            guard.config, raw, expected_snapshot_sha256=digest(raw), expected_head=old_head)
        self.assertIsNot(recovered, guard)
        self.assertEqual(recovered.state, ReturnState.RECONVERGING)
        self.assertEqual(recovered.stable_count, 1)
        self.assertEqual(recovered.configuration_commitment, guard.configuration_commitment)
        self.assertEqual(recovered.records[:-1], old_records)
        self.assertEqual(recovered.records[-1]["event"], "RESTORE")
        self.assertEqual(recovered.records[-1]["previous_head"], old_head)
        details = recovered.records[-1]["details"]
        self.assertEqual(details["source_snapshot_sha256"], digest(raw))
        self.assertEqual(details["source_head"], old_head)
        self.assertIs(details["discarded_latest"], True)
        self.assertEqual(details["discarded_leases"], [])
        self.assertEqual(recovered.admit(UpdatePlan(("tunable",), Fraction(1, 8)), now=400),
                         "OBSERVATION_MISSING")
        self.assertEqual(guard.export_snapshot(), raw)
        self.assert_chain(recovered)

    def test_retained_energy_refuses_increase_without_ratchet(self) -> None:
        recovered = self.restored(returning_guard())
        increased = recovered.observe(observation(41, 401, cost=13))  # E=19 > accepted 18.
        self.assertIs(increased["valid"], False)
        self.assertIn("ENERGY_INCREASED", increased["reasons"])
        self.assertEqual(increased["stable_count"], 0)
        self.assertEqual(increased["state_after"], "RECONVERGING")
        self.assertEqual(json.loads(recovered.export_snapshot())["guard"]["accepted_energy_exact"],
                         {"numerator": 18, "denominator": 1})
        accepted = recovered.observe(observation(42, 402, cost=11))  # E=17.
        self.assertIs(accepted["valid"], True)
        self.assertEqual(accepted["stable_count"], 1)
        self.assertEqual(accepted["energy_exact"], {"numerator": 17, "denominator": 1})

    def test_two_new_selector_decisions_complete_window_then_normal(self) -> None:
        recovered = self.restored(returning_guard(observations=2))
        self.assertEqual(recovered.stable_count, 2)
        selector = ActionSelector(policy_config=PolicyConfig(recovery_samples=1),
                                  reconvergence_guard=recovered)
        # The independent welfare gate is new, not a recovered consent/care state.
        self.assertIsNone(selector.welfare_gate.current)
        candidates = (
            ActionCandidate("fixed-high", 37, (0,), update=UpdatePlan(("fixed",), Fraction(1, 8))),
            ActionCandidate("tunable-low", 4, (0,), update=UpdatePlan(("tunable",), Fraction(1, 8))),
        )
        completing = selector.select(
            candidates, PrecautionAssessment(.3, 0), WelfareSignals(1, 1, 1, 1, 0),
            now=402, reconvergence_observation=observation(42, 402, cost=10))
        self.assertEqual(completing.selected_id, "tunable-low")
        self.assertEqual(completing.schema, "EUP-SELECTION-RECEIPT/0.2")
        self.assertEqual(completing.reconvergence["stable_count"], 3)
        self.assertEqual(completing.reconvergence["state_after"], "NORMAL")
        self.assertEqual(completing.reconvergence["admission_state"], "RECONVERGING")
        rejected = next(row for row in completing.candidates if row.action_id == "fixed-high")
        self.assertEqual((rejected.stage, rejected.reason), ("RECONVERGENCE", "SENSITIVE_PARAMETER_FROZEN"))
        normal = selector.select(
            candidates, PrecautionAssessment(.3, 0), WelfareSignals(1, 1, 1, 1, 0),
            now=403, reconvergence_observation=observation(43, 403, cost=10))
        self.assertEqual(normal.selected_id, "fixed-high")
        self.assertEqual(normal.reconvergence["admission_state"], "NORMAL")
        self.assertEqual(normal.reconvergence["stable_count"], 3)
        self.assert_chain(recovered)

    def test_completed_window_is_preserved_but_cached_admission_is_not(self) -> None:
        guard = returning_guard(observations=3)
        self.assertEqual(guard.state, ReturnState.NORMAL)
        recovered = self.restored(guard)
        self.assertEqual((recovered.state, recovered.stable_count), (ReturnState.NORMAL, 3))
        self.assertEqual(recovered.admit(UpdatePlan(("fixed",), Fraction(1, 8)), now=402),
                         "OBSERVATION_MISSING")
        recovered.observe(observation(43, 403, cost=10))
        self.assertIsNone(recovered.admit(UpdatePlan(("fixed",), Fraction(1, 8)), now=403))

    def test_exception_is_not_promoted_to_return_or_normal(self) -> None:
        guard = returning_guard()
        guard.enter_exception("new_failure", decision_card="recovery-second-interruption")
        epoch = json.loads(guard.export_snapshot())["guard"]["epoch"]
        recovered = self.restored(guard)
        self.assertEqual(recovered.state, ReturnState.EXCEPTION)
        self.assertEqual(recovered.stable_count, 0)
        self.assertEqual(recovered.admit(UpdatePlan(), now=401), "EXCEPTION_ACTIVE")
        denied = recovered.observe(observation(41, 401, cost=11))
        self.assertIs(denied["valid"], False)
        self.assertIn("EXCEPTION_ACTIVE", denied["reasons"])
        self.assertEqual(denied["epoch"], epoch)
        recovered.begin_reconvergence(decision_card="recovery-explicit-new-return")
        accepted = recovered.observe(observation(42, 402, cost=11))
        self.assertIs(accepted["valid"], True)
        self.assertEqual(accepted["stable_count"], 1)

    def test_sequence_and_time_frontier_errors_are_atomic_and_gap_resets(self) -> None:
        recovered = self.restored(returning_guard(observations=2))
        for sample in (observation(41, 402), observation(40, 402), observation(42, 400)):
            with self.subTest(sequence=sample.sequence, observed_at=sample.observed_at):
                before = recovered.export_snapshot()
                with self.assertRaises(ValueError):
                    recovered.observe(sample)
                self.assertEqual(recovered.export_snapshot(), before)
        gap = recovered.observe(observation(44, 404, cost=10))
        self.assertIs(gap["valid"], True)
        self.assertIn("SEQUENCE_GAP", gap["reasons"])
        self.assertEqual(gap["stable_count"], 1)
        self.assertEqual(gap["state_after"], "RECONVERGING")

    def test_operation_frontier_and_leases_are_not_revived(self) -> None:
        guard = returning_guard()
        lease = ExtensionLease("addon-recovery", "d" * 64, 2, 900, "rollback-recovery")
        guard.register_extension(lease, now=405, decision_card="recovery-lease-before-restart")
        old_data = json.loads(guard.export_snapshot())
        self.assertEqual(old_data["guard"]["last_operation_time"], 405)
        self.assertEqual(len(old_data["guard"]["leases"]), 1)
        recovered = self.restored(guard)
        details = recovered.records[-1]["details"]
        self.assertEqual(details["discarded_leases"], ["addon-recovery"])
        data = json.loads(recovered.export_snapshot())
        self.assertEqual(data["guard"]["leases"], [])
        self.assertIsNone(data["guard"]["latest"])
        self.assertEqual(data["guard"]["last_operation_time"], 405)
        before = recovered.export_snapshot()
        with self.assertRaises(ValueError):
            recovered.observe(observation(41, 404, cost=11))
        self.assertEqual(recovered.export_snapshot(), before)
        recovered.observe(observation(41, 405, cost=11))
        plan = UpdatePlan(extensions=("addon-recovery",))
        self.assertEqual(recovered.admit(plan, now=405), "EXTENSION_NOT_APPROVED")
        recovered.register_extension(lease, now=405, decision_card="recovery-new-explicit-approval")
        self.assertIsNone(recovered.admit(plan, now=405))
        self.assert_chain(recovered)

    def test_multiple_leases_are_discarded_and_recorded_in_sorted_order(self) -> None:
        guard = returning_guard()
        for name in ("z-addon", "a-addon"):
            guard.register_extension(ExtensionLease(name, "e" * 64, 1, 1000, "rollback-new"),
                                     now=400, decision_card="recovery-multiple-leases")
        recovered = self.restored(guard)
        self.assertEqual(recovered.records[-1]["details"]["discarded_leases"], ["a-addon", "z-addon"])
        recovered.observe(observation(41, 401, cost=11))
        for name in ("z-addon", "a-addon"):
            self.assertEqual(recovered.admit(UpdatePlan(extensions=(name,)), now=401), "EXTENSION_NOT_APPROVED")

    def test_numerical_monitors_and_configuration_are_preserved(self) -> None:
        guard = ReconvergenceGuard(config())
        guard.set_normal_guard("cost", False, reason="declared_trial", decision_card="recovery-monitor-card")
        guard.observe(observation(7, 70))
        recovered = self.restored(guard)
        self.assertEqual(recovered.normal_guards, {"energy": True, "cost": False, "entropy": True})
        self.assertEqual(recovered.configuration_commitment, guard.configuration_commitment)
        self.assertEqual(recovered.state, ReturnState.NORMAL)
        self.assertEqual(recovered.admit(UpdatePlan(), now=70), "OBSERVATION_MISSING")
        copied = recovered.normal_guards
        copied["cost"] = True
        self.assertIs(recovered.normal_guards["cost"], False)

    def test_normal_accepted_energy_above_limit_remains_valid_snapshot(self) -> None:
        guard = ReconvergenceGuard(config())
        guard.set_normal_guard("energy", False, reason="declared_energy_trial",
                               decision_card="recovery-energy-monitor-card")
        sample = guard.observe(observation(9, 90, cost=19, entropy=9))  # E=37 > limit 30.
        self.assertIs(sample["valid"], True)
        self.assertEqual(sample["energy_exact"], {"numerator": 37, "denominator": 1})
        recovered = self.restored(guard)
        data = json.loads(recovered.export_snapshot())
        self.assertEqual(data["guard"]["accepted_energy_exact"], {"numerator": 37, "denominator": 1})
        self.assertIs(recovered.normal_guards["energy"], False)
        self.assertEqual(recovered.state, ReturnState.NORMAL)
        self.assertEqual(recovered.admit(UpdatePlan(), now=90), "OBSERVATION_MISSING")
        fresh = recovered.observe(observation(10, 91, cost=20, entropy=9))  # E=38; same disabled monitor.
        self.assertIs(fresh["valid"], True)
        self.assertIsNone(recovered.admit(UpdatePlan(), now=91))

    def test_external_full_digest_and_head_and_config_are_required(self) -> None:
        guard = returning_guard()
        raw = guard.export_snapshot()
        for expected_sha, expected_head in (("f" * 64, guard.head), (digest(raw), "f" * 64),
                                            (None, guard.head), (digest(raw), None),
                                            (digest(raw).upper(), guard.head), (digest(raw), "no-head")):
            with self.subTest(sha=expected_sha, head=expected_head):
                with self.assertRaises(ValueError):
                    ReconvergenceGuard.from_snapshot(guard.config, raw,
                        expected_snapshot_sha256=expected_sha, expected_head=expected_head)
        with self.assertRaises(ValueError):
            ReconvergenceGuard.from_snapshot(config(window=4), raw,
                expected_snapshot_sha256=digest(raw), expected_head=guard.head)
        before = raw
        guard.observe(observation(41, 401, cost=11))
        # An authentic older file is not the current selected snapshot merely
        # because its internal chain is valid. Its old anchors remain old.
        with self.assertRaises(ValueError):
            ReconvergenceGuard.from_snapshot(guard.config, before,
                expected_snapshot_sha256=digest(guard.export_snapshot()), expected_head=guard.head)

    def test_older_file_and_older_anchors_establish_consistency_not_latestness(self) -> None:
        guard = returning_guard()
        old_raw, old_head = guard.export_snapshot(), guard.head
        guard.observe(observation(41, 401, cost=11))
        recovered_old = ReconvergenceGuard.from_snapshot(
            guard.config, old_raw, expected_snapshot_sha256=digest(old_raw), expected_head=old_head)
        self.assertEqual(recovered_old.stable_count, 1)
        self.assertEqual(guard.stable_count, 2)
        self.assertEqual(recovered_old.records[-1]["details"]["source_head"], old_head)

    def test_strict_json_schema_fields_and_noncanonical_bytes(self) -> None:
        guard = returning_guard()
        raw = guard.export_snapshot()
        data = json.loads(raw)
        variants = [b"\xff", raw[:-1], b"\xef\xbb\xbf" + raw, raw + b"\n",
                    json.dumps(data, indent=2).encode("ascii"),
                    b'{"schema":"EUP-RECONVERGENCE-SNAPSHOT/0.1",' + raw[1:]]
        for value in variants:
            with self.subTest(byte_count=len(value), first_bytes=value[:12]):
                with self.assertRaises(ValueError):
                    ReconvergenceGuard.from_snapshot(guard.config, value,
                        expected_snapshot_sha256=digest(value), expected_head=guard.head)
        for location in ("top", "guard", "config"):
            altered = copy.deepcopy(data)
            if location == "top":
                altered["unexpected"] = 1
            else:
                altered[location]["unexpected"] = 1
            with self.subTest(unknown_field=location):
                self.assert_rejected_document(guard, altered)
        altered = copy.deepcopy(data)
        altered["schema"] = "EUP-RECONVERGENCE-SNAPSHOT/999"
        self.assert_rejected_document(guard, altered)

    def test_exact_rational_and_integer_shape_rejections(self) -> None:
        guard = returning_guard()
        original = json.loads(guard.export_snapshot())
        malformed = [True, 18.0, "18", {"numerator": 18, "denominator": 0},
                     {"numerator": 18, "denominator": -1},
                     {"numerator": True, "denominator": 1},
                     {"numerator": 36, "denominator": 2},
                     {"numerator": 18, "denominator": 1, "extra": 0},
                     {"numerator": 1 << 256, "denominator": 1},
                     {"numerator": 1, "denominator": 1 << 256}]
        for rational in malformed:
            altered = copy.deepcopy(original)
            altered["guard"]["accepted_energy_exact"] = rational
            with self.subTest(rational=rational):
                self.assert_rejected_document(guard, altered)
        for value in (True, 1.0, -1, 1 << 256):
            altered = copy.deepcopy(original)
            altered["guard"]["stable_count"] = value
            with self.subTest(integer=value):
                self.assert_rejected_document(guard, altered)
        for value in (float("nan"), float("inf"), -float("inf")):
            altered = copy.deepcopy(original)
            altered["guard"]["stable_count"] = value
            bad = json.dumps(altered, sort_keys=True, separators=(",", ":"), allow_nan=True).encode("ascii")
            with self.subTest(nonfinite=str(value)):
                with self.assertRaises(ValueError):
                    ReconvergenceGuard.from_snapshot(guard.config, bad,
                        expected_snapshot_sha256=digest(bad), expected_head=guard.head)

    def test_256_bit_boundary_is_allowed_and_larger_export_refused(self) -> None:
        boundary = (1 << 256) - 1
        guard = ReconvergenceGuard(config(energy_limit=boundary, initial_energy=boundary))
        raw = guard.export_snapshot()
        recovered = ReconvergenceGuard.from_snapshot(guard.config, raw,
            expected_snapshot_sha256=digest(raw), expected_head=guard.head)
        self.assertEqual(json.loads(recovered.export_snapshot())["guard"]["accepted_energy_exact"],
                         {"numerator": boundary, "denominator": 1})
        with self.assertRaises(ValueError):
            too_large = ReconvergenceGuard(config(energy_limit=1 << 256, initial_energy=1 << 256))
            too_large.export_snapshot()

    def test_consistent_hashes_do_not_excuse_state_chain_disagreement(self) -> None:
        guard = returning_guard()
        original = json.loads(guard.export_snapshot())
        mutations = [
            ("stable_count", 2), ("state", "NORMAL"), ("epoch", 99),
            ("last_sequence", 41), ("last_observed_at", 401), ("last_operation_time", 401),
            ("accepted_energy_exact", {"numerator": 17, "denominator": 1}),
            ("normal_guards", {"energy": True, "cost": False, "entropy": True}),
            ("latest", None),
        ]
        for key, value in mutations:
            altered = copy.deepcopy(original)
            altered["guard"][key] = value
            with self.subTest(field=key):
                self.assert_rejected_document(guard, altered)
        for change in ("record_index", "record_head", "previous_head", "record_config", "drop_record", "extra_record_key"):
            altered = copy.deepcopy(original)
            if change == "record_index": altered["records"][0]["index"] = 2
            if change == "record_head": altered["records"][0]["head"] = "f" * 64
            if change == "previous_head": altered["records"][0]["previous_head"] = "f" * 64
            if change == "record_config": altered["records"][0]["configuration_commitment"] = "f" * 64
            if change == "drop_record": altered["records"].pop()
            if change == "extra_record_key": altered["records"][0]["extra"] = 1
            with self.subTest(chain_change=change):
                self.assert_rejected_document(guard, altered)

    def test_raw_input_type_and_8_mib_limit(self) -> None:
        guard = returning_guard()
        raw = guard.export_snapshot()
        for value in (raw.decode("ascii"), bytearray(raw), memoryview(raw), None,
                      b"x" * (MAX_BYTES + 1)):
            with self.subTest(kind=type(value).__name__):
                with self.assertRaises(ValueError):
                    ReconvergenceGuard.from_snapshot(guard.config, value,
                        expected_snapshot_sha256=digest(raw), expected_head=guard.head)

    def test_restoring_requires_a_slot_and_cannot_reset_the_capacity(self) -> None:
        guard = ReconvergenceGuard(config())
        for _ in range(4095):
            guard.enter_exception("capacity_trial", decision_card="recovery-capacity")
        raw = guard.export_snapshot()
        recovered = ReconvergenceGuard.from_snapshot(guard.config, raw,
            expected_snapshot_sha256=digest(raw), expected_head=guard.head)
        self.assertEqual(len(recovered.records), 4096)
        self.assertEqual(recovered.records[-1]["event"], "RESTORE")
        full = recovered.export_snapshot()
        with self.assertRaises(ValueError):
            ReconvergenceGuard.from_snapshot(recovered.config, full,
                expected_snapshot_sha256=digest(full), expected_head=recovered.head)
        with self.assertRaises(ValueError):
            recovered.enter_exception("no_more_slots", decision_card="recovery-full")
        self.assertEqual(recovered.export_snapshot(), full)
        self.assertEqual(len(guard.records), 4095)

    def test_store_round_trip_has_exact_bytes_receipt_and_no_overwrite(self) -> None:
        guard = returning_guard()
        before = guard.export_snapshot()
        target = self.directory / "new.snapshot.json"
        receipt = store.save_new_snapshot(target, guard)
        saved = target.read_bytes()
        self.assertEqual(saved, before)
        self.assertEqual(receipt["bytes"], len(saved))
        self.assertEqual(receipt["sha256"], digest(saved))
        self.assertEqual(receipt["head"], guard.head)
        self.assertEqual(Path(receipt["path"]).resolve(), target.resolve())
        self.assertEqual(guard.export_snapshot(), before)
        with self.assertRaises((ValueError, FileExistsError)):
            store.save_new_snapshot(target, guard)
        self.assertEqual(target.read_bytes(), saved)
        recovered = store.load_snapshot(target, guard.config,
            expected_snapshot_sha256=receipt["sha256"], expected_head=receipt["head"])
        self.assertEqual(recovered.state, ReturnState.RECONVERGING)
        self.assertEqual(recovered.stable_count, 1)
        self.assertEqual(recovered.records[-1]["event"], "RESTORE")
        self.assertEqual(target.read_bytes(), saved)

    def test_store_fsync_failure_has_no_success_receipt_and_retains_file(self) -> None:
        guard = returning_guard()
        before = guard.export_snapshot()
        target = self.directory / "failed-fsync.snapshot.json"
        returned = []
        with patch.object(store.os, "fsync", side_effect=OSError("synthetic-recovery-fsync")):
            with self.assertRaisesRegex(OSError, "synthetic-recovery-fsync"):
                returned.append(store.save_new_snapshot(target, guard))
        self.assertEqual(returned, [])
        self.assertTrue(target.exists())
        retained = target.read_bytes()
        self.assertEqual(guard.export_snapshot(), before)
        with self.assertRaises((ValueError, FileExistsError)):
            store.save_new_snapshot(target, guard)
        self.assertEqual(target.read_bytes(), retained)
        # A failed fsync need not truncate bytes. No durability or successful
        # save receipt is inferred even when readable bytes happen to be complete.

    def test_store_refuses_truncation_oversize_and_does_not_repair_files(self) -> None:
        guard = returning_guard()
        raw = guard.export_snapshot()
        for name, content in (("truncated.json", raw[:-9]),
                              ("oversize.json", b"x" * (MAX_BYTES + 1))):
            target = self.directory / name
            with target.open("xb") as handle:
                handle.write(content)
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    store.load_snapshot(target, guard.config,
                        expected_snapshot_sha256=digest(raw), expected_head=guard.head)
                self.assertEqual(target.read_bytes(), content)
        target = self.directory / "missing.json"
        with self.assertRaises((ValueError, OSError)):
            store.load_snapshot(target, guard.config,
                expected_snapshot_sha256=digest(raw), expected_head=guard.head)
        self.assertFalse(target.exists())



    def test_portable_example_uses_distinct_processes_and_keeps_anchors(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(ROOT / "src")
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        run = subprocess.run(
            [sys.executable, "-B", str(ROOT / "examples" / "reconvergence_recovery.py"),
             "--directory", str(self.directory)],
            cwd=ROOT, env=environment, capture_output=True, text=True,
            encoding="utf-8", timeout=45, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stderr, "")
        result = json.loads(run.stdout)
        self.assertEqual(result["schema"], "EUP-RECONVERGENCE-RECOVERY-EXAMPLE/0.1")
        self.assertIs(result["synthetic"], True)
        self.assertEqual(result["actions_executed"], 0)
        self.assertEqual(len(result["process_ids"]), 2)
        self.assertNotEqual(*result["process_ids"])
        self.assertEqual(result["selected_before_restart"], "extension")
        self.assertEqual(result["selected_after_restart"], ["flexible", "sensitive", "extension"])
        self.assertEqual(result["cached_admission_reason"], "OBSERVATION_MISSING")
        self.assertEqual(result["saved_state"]["stable_count"], 2)
        self.assertEqual(result["saved_state"]["accepted_energy_exact"], {"numerator": 12, "denominator": 1})
        self.assertEqual(result["restore_event"]["event"], "RESTORE")
        boundary = result["restore_event"]["details"]
        self.assertEqual(boundary["discarded_leases"], ["example-addon"])
        self.assertIs(boundary["discarded_latest"], True)
        self.assertEqual(boundary["stable_count"], 2)
        raw = (self.directory / "guard.snapshot.json").read_bytes()
        self.assertEqual(result["snapshot"]["bytes"], len(raw))
        self.assertEqual(result["snapshot"]["sha256"], digest(raw))
        original = json.loads(raw)
        self.assertEqual(result["snapshot"]["head"], original["head"])
        self.assertEqual(boundary["source_snapshot_sha256"], digest(raw))
        self.assertEqual(boundary["source_head"], original["head"])
        self.assertEqual(result["guard_records"][:len(original["records"])], original["records"])
        self.assertEqual(result["decisions_after_restart"][0]["reconvergence"]["admission_state"],
                         "RECONVERGING")
        self.assertEqual(result["decisions_after_restart"][1]["reconvergence"]["admission_state"],
                         "NORMAL")
        self.assertEqual(result["decisions_after_restart"][2]["selected_id"], "extension")
        # Its final approval follows a new registration, not the saved lease.
        self.assertEqual(result["guard_records"][-2]["event"], "REGISTER_EXTENSION")
        self.assertIs(result["guard_records"][-2]["details"]["renewal"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
