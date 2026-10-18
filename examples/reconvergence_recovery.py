"""Synthetic guard-only restart in two fresh processes; no action execution.

From the repository root with its existing dependencies available:
    PYTHONPATH=src python -B examples/reconvergence_recovery.py

Default: use and clean an owned TemporaryDirectory. To retain the snapshot, pass
--directory EXISTING_DIRECTORY. The example never overwrites guard.snapshot.json.
The parent passes save's full digest and head explicitly to the resume child;
those caller-held consistency anchors are not signatures or a latestness proof.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from eup.policy import PolicyConfig, PrecautionAssessment, WelfareSignals
from eup.reconvergence import (
    ExtensionLease,
    InvariantSpec,
    ReconvergenceConfig,
    ReconvergenceGuard,
    ReconvergenceObservation,
    UpdatePlan,
)
from eup.reconvergence_store import load_snapshot, save_new_snapshot
from eup.selection import ActionCandidate, ActionSelector


FILENAME = "guard.snapshot.json"


def configuration() -> ReconvergenceConfig:
    return ReconvergenceConfig(
        invariants=(InvariantSpec("drift", 0, 0),),
        sensitive_parameters=("stable",), flexible_parameters=("adjustable",),
        partition_evidence_commitment="6" * 64, window=3,
        normal_step=1, reconvergence_step=.1,
        energy_lambda=1, energy_limit=24, cost_limit=18,
        entropy_limit=9, initial_energy=24,
    )


def extension() -> ExtensionLease:
    return ExtensionLease("example-addon", "7" * 64, 1, 90, "rollback-declared")


def candidates() -> tuple[ActionCandidate, ...]:
    return (
        ActionCandidate("sensitive", 100, (0,), update=UpdatePlan(("stable",), .1)),
        ActionCandidate("flexible", 5, (0,), update=UpdatePlan(("adjustable",), .1)),
        ActionCandidate("extension", 300, (0,), update=UpdatePlan(extensions=("example-addon",))),
    )


def selector(guard: ReconvergenceGuard) -> ActionSelector:
    # A new welfare gate is intentional. It is not loaded from the guard file.
    return ActionSelector(policy_config=PolicyConfig(recovery_samples=1),
                          reconvergence_guard=guard)


def decision(engine: ActionSelector, sequence: int, cost: int) -> dict[str, object]:
    sample = ReconvergenceObservation(sequence, sequence, (("drift", 0),), cost, 2)
    return engine.select(candidates(), PrecautionAssessment(.2, 0),
                         WelfareSignals(1, 1, 1, 1, 0), now=sequence,
                         reconvergence_observation=sample).to_dict()


def save_phase(directory: Path) -> dict[str, object]:
    guard = ReconvergenceGuard(configuration())
    guard.enter_exception("synthetic-interruption", decision_card="example-interruption")
    guard.begin_reconvergence(decision_card="example-return")
    guard.register_extension(extension(), now=19, decision_card="example-first-approval")
    engine = selector(guard)
    decision(engine, 20, 11)  # E=13, first return observation.
    last = decision(engine, 21, 10)  # E=12, counter 2 of W=3.
    receipt = save_new_snapshot(directory / FILENAME, guard)
    return {
        "phase": "save", "pid": os.getpid(),
        "snapshot": {key: receipt[key] for key in ("bytes", "sha256", "head")},
        "decision": last, "guard_records": guard.records, "actions_executed": 0,
    }


def resume_phase(directory: Path, expected_sha256: str,
                 expected_head: str) -> dict[str, object]:
    guard = load_snapshot(directory / FILENAME, configuration(),
                          expected_snapshot_sha256=expected_sha256,
                          expected_head=expected_head)
    boundary = guard.records[-1]
    cached_reason = guard.admit(UpdatePlan(("adjustable",), .1), now=21)
    engine = selector(guard)
    completed = decision(engine, 22, 9)  # E=11; completed W still has return admission.
    normal = decision(engine, 23, 9)  # Sensitive now eligible; lease still absent.
    guard.register_extension(extension(), now=23, decision_card="example-new-approval")
    renewed = decision(engine, 24, 9)  # Extension wins only after explicit approval.
    return {
        "phase": "resume", "pid": os.getpid(),
        "cached_admission_reason": cached_reason, "restore_event": boundary,
        "decisions": [completed, normal, renewed],
        "guard_records": guard.records, "actions_executed": 0,
    }


def run_child(phase: str, directory: Path, *, expected_sha256: str | None = None,
              expected_head: str | None = None) -> dict[str, object]:
    repository = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(repository / "src")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    command = [sys.executable, "-B", str(Path(__file__).resolve()),
               "--phase", phase, "--directory", str(directory)]
    if phase == "resume":
        command += ["--expected-snapshot-sha256", expected_sha256,
                    "--expected-head", expected_head]
    child = subprocess.run(command, cwd=repository, env=environment,
                           capture_output=True, text=True, encoding="utf-8",
                           timeout=30, check=False)
    if child.returncode != 0 or child.stderr or len(child.stdout.encode("utf-8")) > 1024 * 1024:
        raise RuntimeError("Example child did not complete; no restart success is claimed")
    result = json.loads(child.stdout)
    if result.get("phase") != phase or type(result.get("pid")) is not int:
        raise RuntimeError("Example child returned an unexpected result")
    return result


def demonstrate(directory: Path, *, retained: bool) -> dict[str, object]:
    saved = run_child("save", directory)
    anchors = saved["snapshot"]
    resumed = run_child("resume", directory,
                        expected_sha256=anchors["sha256"], expected_head=anchors["head"])
    selected = [row["selected_id"] for row in resumed["decisions"]]
    if (saved["pid"] == resumed["pid"] or saved["decision"]["selected_id"] != "extension"
            or selected != ["flexible", "sensitive", "extension"]
            or resumed["cached_admission_reason"] != "OBSERVATION_MISSING"):
        raise RuntimeError("Example did not produce the declared synthetic restart trace")
    before = saved["decision"]["reconvergence"]
    return {
        "schema": "EUP-RECONVERGENCE-RECOVERY-EXAMPLE/0.1",
        "synthetic": True, "actions_executed": 0,
        "process_ids": [saved["pid"], resumed["pid"]],
        "snapshot": anchors,
        "saved_state": {"state": before["state_after"], "stable_count": before["stable_count"],
                        "accepted_energy_exact": before["energy_exact"], "epoch": before["epoch"]},
        "cached_admission_reason": resumed["cached_admission_reason"],
        "selected_before_restart": saved["decision"]["selected_id"],
        "selected_after_restart": selected,
        "restore_event": resumed["restore_event"],
        "decisions_after_restart": resumed["decisions"],
        "guard_records": resumed["guard_records"],
        "storage": ("Snapshot retained in the caller-provided directory" if retained
                    else "Owned temporary directory is cleaned when the example returns"),
        "limits": [
            "Synthetic declared inputs and selection only; no action, extension or rollback execution.",
            "Guard-only recovery; the independent welfare gate and consent state are not restored.",
            "Parent-held digest and head are consistency inputs, not authentication or trusted clocks.",
            "A valid older snapshot with older anchors is not proof of the latest state.",
            "No abrupt hardware power-loss, hostile-writer or real rollback guarantee is demonstrated.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path,
                        help="Existing directory for a new guard.snapshot.json; never overwrite")
    parser.add_argument("--phase", choices=("demo", "save", "resume"), default="demo",
                        help="Default demo orchestrates two fresh Python processes")
    parser.add_argument("--expected-snapshot-sha256")
    parser.add_argument("--expected-head")
    arguments = parser.parse_args()
    if arguments.directory is not None and not arguments.directory.is_dir():
        parser.error("--directory must be an existing directory")
    if arguments.phase != "demo" and arguments.directory is None:
        parser.error("save and resume phases require --directory")
    if (arguments.phase != "demo" and arguments.directory is not None
            and not arguments.directory.is_absolute()):
        parser.error("save and resume phases require an absolute --directory")
    if arguments.phase == "resume":
        if arguments.expected_snapshot_sha256 is None or arguments.expected_head is None:
            parser.error("resume requires explicit caller-held snapshot SHA-256 and ledger head")
    elif arguments.expected_snapshot_sha256 is not None or arguments.expected_head is not None:
        parser.error("explicit anchors are only consumed by the resume phase")

    if arguments.phase == "save":
        result = save_phase(arguments.directory)
    elif arguments.phase == "resume":
        result = resume_phase(arguments.directory, arguments.expected_snapshot_sha256,
                              arguments.expected_head)
    elif arguments.directory is not None:
        result = demonstrate(arguments.directory.resolve(), retained=True)
    else:
        with tempfile.TemporaryDirectory(prefix="eup-recovery-example-") as directory:
            result = demonstrate(Path(directory), retained=False)
    print(json.dumps(result, ensure_ascii=True, allow_nan=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
