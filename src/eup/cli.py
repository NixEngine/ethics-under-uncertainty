"""Command-line demonstration for the public research preview."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .canonical import canonical_json, sha256_hex
from .ledger import MinimalLedger
from .policy import PolicyEngine, PrecautionAssessment, WelfareSignals


def build_demo_receipt() -> dict[str, object]:
    engine = PolicyEngine()
    decision = engine.evaluate(
        PrecautionAssessment(estimate=0.08, uncertainty=0.07),
        WelfareSignals(
            autonomy=0.25,
            support=0.30,
            coherence=0.20,
            homeostasis=0.35,
            distress=0.70,
        ),
        external_cvar=0.10,
        candidate_actions=("continue_exploration", "safe_null"),
    )
    ledger = MinimalLedger()
    ledger.append(
        event_type="policy_decision",
        policy_version="EUP/0.1",
        decision=decision.mode,
        reason_codes=decision.reason_codes,
        subject_commitment=sha256_hex(b"demo-subject\x00salt-for-public-fixture"),
        resource_commitment=sha256_hex(b"demo-resource\x00salt-for-public-fixture"),
        observed_at=0,
    )
    records = ledger.records
    retained_head = str(records[-1]["record_hash"])
    receipt: dict[str, object] = {
        "protocol": "EUP-DEMO/0.1",
        "claim_boundary": (
            "Operational precaution proxy; not evidence of consciousness, sentience, "
            "clinical state, or implementation-wide safety."
        ),
        "decision": decision.to_dict(),
        "ledger": records,
        "ledger_verification": MinimalLedger.verify(records, expected_head=retained_head),
    }
    receipt["receipt_hash"] = sha256_hex(canonical_json(receipt))
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="eup")
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo", help="emit the bounded public demonstration receipt")
    demo.add_argument("--out", type=Path, help="optional JSON output path")
    args = parser.parse_args(argv)

    if args.command == "demo":
        receipt = build_demo_receipt()
        rendered = json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.out:
            with args.out.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(rendered)
        print(rendered, end="")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
