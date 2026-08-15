"""Schema-closed, hash-linked ledger without arbitrary payload fields.

Verification establishes internal chain consistency against a retained head. It
does not detect a full rewrite when an authorized adversary can recompute every
hash and replace any external copy of the head.
"""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Iterable

from .canonical import canonical_json, sha256_hex


_COMMITMENT = re.compile(r"^[0-9a-f]{64}$")
_POLICY_VERSION = re.compile(r"^EUP/[0-9]+\.[0-9]+$")

_EVENT_TYPES = frozenset({"policy_decision"})
_DECISIONS = frozenset(
    {
        "NORMAL",
        "CARE",
        "INSUFFICIENT_DATA",
        "SAFETY_RESTRICTED",
        "CARE_AND_SAFETY_RESTRICTED",
    }
)
_REASON_CODES = frozenset(
    {
        "PRECAUTION_REGIME_ACTIVE",
        "WELFARE_GREEN",
        "WELFARE_YELLOW",
        "WELFARE_ORANGE",
        "WELFARE_RED",
        "WELFARE_NO_DATA",
        "WELFARE_COVERAGE_INCOMPLETE",
        "EXTERNAL_CVAR_LIMIT_EXCEEDED",
        "NO_CANDIDATE_ACTION",
    }
)
_RECORD_FIELDS = frozenset(
    {
        "protocol",
        "seq_no",
        "event_type",
        "policy_version",
        "decision",
        "reason_codes",
        "subject_commitment",
        "resource_commitment",
        "observed_at",
        "prev_hash",
        "record_hash",
    }
)


def _schema_error(record: dict[str, object]) -> str | None:
    if set(record) != _RECORD_FIELDS:
        return "record-schema-fields"
    if record.get("protocol") != "EUP-LEDGER/0.1":
        return "record-schema-protocol"
    if type(record.get("seq_no")) is not int:
        return "record-schema-sequence"
    if record.get("event_type") not in _EVENT_TYPES:
        return "record-schema-event"
    policy_version = record.get("policy_version")
    if not isinstance(policy_version, str) or not _POLICY_VERSION.fullmatch(policy_version):
        return "record-schema-policy"
    if record.get("decision") not in _DECISIONS:
        return "record-schema-decision"
    reason_codes = record.get("reason_codes")
    if not isinstance(reason_codes, list) or any(
        not isinstance(reason, str) or reason not in _REASON_CODES for reason in reason_codes
    ):
        return "record-schema-reasons"
    if reason_codes != sorted(set(reason_codes)):
        return "record-schema-reasons"
    for field in ("subject_commitment", "resource_commitment", "record_hash"):
        value = record.get(field)
        if not isinstance(value, str) or not _COMMITMENT.fullmatch(value):
            return f"record-schema-{field.replace('_', '-')}"
    prev_hash = record.get("prev_hash")
    if prev_hash is not None and (
        not isinstance(prev_hash, str) or not _COMMITMENT.fullmatch(prev_hash)
    ):
        return "record-schema-previous-hash"
    if type(record.get("observed_at")) is not int:
        return "record-schema-observed-at"
    return None


class MinimalLedger:
    def __init__(self) -> None:
        self._records: list[dict[str, object]] = []

    @property
    def records(self) -> list[dict[str, object]]:
        return deepcopy(self._records)

    def append(
        self,
        *,
        event_type: str,
        policy_version: str,
        decision: str,
        reason_codes: Iterable[str],
        subject_commitment: str,
        resource_commitment: str,
        observed_at: int,
    ) -> dict[str, object]:
        if not _COMMITMENT.fullmatch(subject_commitment):
            raise ValueError("subject_commitment must be a SHA-256 hex commitment")
        if not _COMMITMENT.fullmatch(resource_commitment):
            raise ValueError("resource_commitment must be a SHA-256 hex commitment")
        if not isinstance(event_type, str) or event_type not in _EVENT_TYPES:
            raise ValueError("event_type is outside the public ledger schema")
        if not isinstance(policy_version, str) or not _POLICY_VERSION.fullmatch(policy_version):
            raise ValueError("policy_version is outside the public ledger schema")
        if not isinstance(decision, str) or decision not in _DECISIONS:
            raise ValueError("decision is outside the public ledger schema")
        normalized_reasons = tuple(sorted(set(reason_codes)))
        if any(reason not in _REASON_CODES for reason in normalized_reasons):
            raise ValueError("reason_codes contain a value outside the public ledger schema")
        if type(observed_at) is not int:
            raise ValueError("observed_at must be an integer")
        record: dict[str, object] = {
            "protocol": "EUP-LEDGER/0.1",
            "seq_no": len(self._records),
            "event_type": event_type,
            "policy_version": policy_version,
            "decision": decision,
            "reason_codes": list(normalized_reasons),
            "subject_commitment": subject_commitment,
            "resource_commitment": resource_commitment,
            "observed_at": int(observed_at),
            "prev_hash": self._records[-1]["record_hash"] if self._records else None,
        }
        record["record_hash"] = sha256_hex(canonical_json(record))
        self._records.append(record)
        return deepcopy(record)

    @staticmethod
    def verify(
        records: Iterable[dict[str, object]],
        *,
        expected_head: str | None = None,
    ) -> dict[str, object]:
        if expected_head is not None and not _COMMITMENT.fullmatch(expected_head):
            raise ValueError("expected_head must be a SHA-256 hex digest")
        items = list(records)
        previous: str | None = None
        for index, source in enumerate(items):
            record = deepcopy(source)
            schema_error = _schema_error(record)
            if schema_error is not None:
                return {"ok": False, "index": index, "reason": schema_error}
            actual_hash = record.pop("record_hash", None)
            if record.get("seq_no") != index:
                return {"ok": False, "index": index, "reason": "sequence-mismatch"}
            if record.get("prev_hash") != previous:
                return {"ok": False, "index": index, "reason": "previous-hash-mismatch"}
            expected_hash = sha256_hex(canonical_json(record))
            if actual_hash != expected_hash:
                return {"ok": False, "index": index, "reason": "record-hash-mismatch"}
            previous = str(actual_hash)
        if expected_head is not None and previous != expected_head:
            return {
                "ok": False,
                "index": len(items),
                "reason": "retained-head-mismatch",
                "head": previous,
            }
        return {"ok": True, "count": len(items), "head": previous}
