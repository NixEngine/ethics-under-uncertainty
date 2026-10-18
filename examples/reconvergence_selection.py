"""Synthetic Farol return sequence through the real ActionSelector; no actions."""
import json

from eup import (
    ActionCandidate, ActionSelector, InvariantSpec, PolicyConfig,
    PrecautionAssessment, ReconvergenceConfig, ReconvergenceGuard,
    ReconvergenceObservation, UpdatePlan, WelfareSignals,
)


def run_example():
    guard = ReconvergenceGuard(ReconvergenceConfig(
        invariants=(InvariantSpec("drift", 0, 0.1),),
        sensitive_parameters=("critical",), flexible_parameters=("adaptive",),
        partition_evidence_commitment="a" * 64, window=2,
        energy_limit=10, cost_limit=8, entropy_limit=5, initial_energy=10))
    guard.enter_exception("synthetic_interrupt", decision_card="card-interrupt")
    guard.begin_reconvergence(decision_card="card-return")
    selector = ActionSelector(policy_config=PolicyConfig(recovery_samples=1),
                              reconvergence_guard=guard)
    candidates = (
        ActionCandidate("higher-performance", 100, (0,),
                        update=UpdatePlan(("critical",), 0.1)),
        ActionCandidate("flexible-update", 1, (0,),
                        update=UpdatePlan(("adaptive",), 0.1)),
    )
    output = []
    for seq, cost in enumerate((6, 7, 5, 4, 4, 9), start=1):
        sample = ReconvergenceObservation(seq, seq, (("drift", 0),), cost, 2)
        decision = selector.select(candidates, PrecautionAssessment(0.2, 0),
            WelfareSignals(1, 1, 1, 1, 0), now=seq,
            reconvergence_observation=sample)
        output.append(decision.to_dict())
    return {"schema": "EUP-RECONVERGENCE-EXAMPLE/0.1", "synthetic": True,
            "actions_executed": 0, "decisions": output,
            "guard_records": guard.records}


if __name__ == "__main__":
    print(json.dumps(run_example(), ensure_ascii=True, indent=2, allow_nan=False))
