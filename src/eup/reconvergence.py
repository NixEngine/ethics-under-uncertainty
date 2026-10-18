"""Finite, declared reconvergence checks; no update or host action is executed.

The invariant references, partition, costs, entropy, impact review and rollback
routes are caller declarations. Commitments do not establish their truth. The
bounded in-memory hash chain is ordinary local integrity, not authentication,
durable storage or protection against a hostile writer. No physical, clinical
or subjective-welfare calibration is claimed.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from fractions import Fraction


_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z")
_COMMITMENT = re.compile(r"[0-9a-f]{64}\Z")
_MAX_INVARIANTS = 64
_MAX_PARAMETERS = 128
_MAX_EXTENSIONS = 64
_MAX_EVENTS = 4096
_NORMAL_GUARDS = ("energy", "cost", "entropy")
_ZERO_HEAD = "0" * 64
_SNAPSHOT_SCHEMA = "EUP-RECONVERGENCE-SNAPSHOT/0.1"
_SNAPSHOT_MAX_BYTES = 8 * 1024 * 1024
_SNAPSHOT_INTEGER_BITS = 256


def _identifier(name: str, value: object) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValueError(f"{name} must be a short opaque ASCII identifier")
    return value


def _commitment(name: str, value: object) -> str:
    if not isinstance(value, str) or not _COMMITMENT.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase SHA-256 commitment")
    return value


def _fraction(name: str, value: object, *, nonnegative: bool = False) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal, Fraction)):
        raise ValueError(f"{name} must be a finite number")
    try:
        result = Fraction(str(value))
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if nonnegative and result < 0:
        raise ValueError(f"{name} must be nonnegative")
    return result


def _integer(name: str, value: object, *, nonnegative: bool = True) -> int:
    if type(value) is not int or (nonnegative and value < 0):
        raise ValueError(f"{name} must be an {'nonnegative ' if nonnegative else ''}integer")
    return value


def _sequence(name: str, values: object, maximum: int) -> tuple:
    # Do not consume generators or potentially unbounded iterables.
    if not isinstance(values, (tuple, list)) or len(values) > maximum:
        raise ValueError(f"{name} must be a tuple/list with at most {maximum} entries")
    return tuple(values)


def _identifiers(name: str, values: object, maximum: int) -> tuple[str, ...]:
    result = tuple(_identifier(name, item) for item in _sequence(name, values, maximum))
    if len(set(result)) != len(result):
        raise ValueError(f"{name} identifiers must be unique")
    return result


def _rational(value: Fraction | None) -> dict[str, int] | None:
    return None if value is None else {"numerator": value.numerator, "denominator": value.denominator}


def _canonical_commitment(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True, allow_nan=False).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _snapshot_integer(value: object, *, nonnegative: bool = True) -> int:
    if type(value) is not int or value.bit_length() > _SNAPSHOT_INTEGER_BITS or (nonnegative and value < 0):
        raise ValueError("snapshot integer outside the exact bounded domain")
    return value


def _snapshot_keys(value: object, names: set[str]) -> dict:
    if type(value) is not dict or set(value) != names:
        raise ValueError("snapshot object has unexpected fields")
    return value


def _snapshot_rational(value: object, *, nonnegative: bool = False) -> Fraction:
    data = _snapshot_keys(value, {"numerator", "denominator"})
    numerator = _snapshot_integer(data["numerator"], nonnegative=False)
    denominator = _snapshot_integer(data["denominator"])
    if denominator <= 0:
        raise ValueError("snapshot rational denominator must be positive")
    result = Fraction(numerator, denominator)
    if (result.numerator, result.denominator) != (numerator, denominator) or (nonnegative and result < 0):
        raise ValueError("snapshot rational must be reduced and in range")
    return result


def _snapshot_encode(value: object) -> bytes:
    pending, count = [(value, 0)], 0
    while pending:
        item, depth = pending.pop()
        count += 1
        if depth > 16 or count > 524288:
            raise ValueError("snapshot structure exceeds bounds")
        if item is None or type(item) is bool:
            continue
        if type(item) is int:
            _snapshot_integer(item, nonnegative=False)
        elif type(item) is str:
            if len(item) > 256:
                raise ValueError("snapshot string exceeds bounds")
        elif type(item) is list:
            pending.extend((child, depth + 1) for child in item)
        elif type(item) is dict:
            if any(type(key) is not str or len(key) > 256 for key in item):
                raise ValueError("snapshot keys must be bounded strings")
            pending.extend((child, depth + 1) for child in item.values())
        else:
            raise ValueError("snapshot values must be exact JSON values")
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True, allow_nan=False).encode("ascii")
    if len(raw) > _SNAPSHOT_MAX_BYTES:
        raise ValueError("snapshot exceeds 8 MiB")
    return raw


def _snapshot_decode(raw: bytes) -> dict:
    if type(raw) is not bytes or not 0 < len(raw) <= _SNAPSHOT_MAX_BYTES:
        raise ValueError("snapshot requires bounded nonempty bytes")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("snapshot duplicate JSON key")
            result[key] = value
        return result

    def integer(text):
        if len(text.lstrip("-")) > 78:
            raise ValueError("snapshot integer exceeds bounds")
        return _snapshot_integer(int(text), nonnegative=False)

    def forbidden(_value):
        raise ValueError("snapshot JSON requires integers, not floats/constants")

    try:
        value = json.loads(raw.decode("ascii", "strict"), object_pairs_hook=unique,
                           parse_int=integer, parse_float=forbidden, parse_constant=forbidden)
        if _snapshot_encode(value) != raw:
            raise ValueError("snapshot bytes are not canonical")
    except (UnicodeError, RecursionError, OverflowError) as error:
        raise ValueError("invalid snapshot encoding or structure") from error
    if type(value) is not dict:
        raise ValueError("snapshot root must be an object")
    return value


class ReturnState(str, Enum):
    NORMAL = "NORMAL"
    EXCEPTION = "EXCEPTION"
    RECONVERGING = "RECONVERGING"


@dataclass(frozen=True)
class InvariantSpec:
    name: str
    baseline: Fraction
    tolerance: Fraction

    def __post_init__(self) -> None:
        _identifier("invariant name", self.name)
        object.__setattr__(self, "baseline", _fraction("baseline", self.baseline))
        object.__setattr__(self, "tolerance", _fraction("tolerance", self.tolerance, nonnegative=True))


@dataclass(frozen=True)
class ReconvergenceConfig:
    invariants: tuple[InvariantSpec, ...]
    sensitive_parameters: tuple[str, ...]
    flexible_parameters: tuple[str, ...]
    partition_evidence_commitment: str
    window: int = 3
    normal_step: Fraction = 1
    reconvergence_step: Fraction = 0.1
    energy_lambda: Fraction = 1
    energy_limit: Fraction = 100
    cost_limit: Fraction = 100
    entropy_limit: Fraction = 100
    initial_energy: Fraction = 100

    def __post_init__(self) -> None:
        supplied = _sequence("invariants", self.invariants, _MAX_INVARIANTS)
        if not supplied or any(not isinstance(spec, InvariantSpec) for spec in supplied):
            raise ValueError("invariants require at least one InvariantSpec")
        specs = tuple(InvariantSpec(spec.name, spec.baseline, spec.tolerance) for spec in supplied)
        if len({spec.name for spec in specs}) != len(specs):
            raise ValueError("invariant identifiers must be unique")
        sensitive = _identifiers("sensitive_parameters", self.sensitive_parameters, _MAX_PARAMETERS)
        flexible = _identifiers("flexible_parameters", self.flexible_parameters, _MAX_PARAMETERS)
        if len(sensitive) + len(flexible) > _MAX_PARAMETERS or set(sensitive) & set(flexible):
            raise ValueError("parameter partitions must be disjoint and contain at most 128 entries")
        _commitment("partition_evidence_commitment", self.partition_evidence_commitment)
        window = _integer("window", self.window)
        if not 1 <= window <= 10000:
            raise ValueError("window must lie in [1, 10000]")
        normal = _fraction("normal_step", self.normal_step)
        reduced = _fraction("reconvergence_step", self.reconvergence_step)
        if not 0 < reduced < normal:
            raise ValueError("steps require 0 < reconvergence_step < normal_step")
        object.__setattr__(self, "invariants", specs)
        object.__setattr__(self, "sensitive_parameters", sensitive)
        object.__setattr__(self, "flexible_parameters", flexible)
        object.__setattr__(self, "normal_step", normal)
        object.__setattr__(self, "reconvergence_step", reduced)
        for name in ("energy_lambda", "energy_limit", "cost_limit", "entropy_limit", "initial_energy"):
            object.__setattr__(self, name, _fraction(name, getattr(self, name), nonnegative=True))
        if self.initial_energy > self.energy_limit:
            raise ValueError("initial_energy must not exceed energy_limit")


@dataclass(frozen=True)
class ReconvergenceObservation:
    sequence: int
    observed_at: int
    invariants: tuple[tuple[str, Fraction | None], ...]
    cost: Fraction | None
    entropy: Fraction | None

    def __post_init__(self) -> None:
        _integer("sequence", self.sequence)
        _integer("observed_at", self.observed_at)
        pairs: list[tuple[str, Fraction | None]] = []
        for pair in _sequence("observation invariants", self.invariants, _MAX_INVARIANTS):
            if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                raise ValueError("observation invariants must contain name/value pairs")
            name = _identifier("observed invariant name", pair[0])
            value = None if pair[1] is None else _fraction("observed invariant", pair[1])
            pairs.append((name, value))
        if len({name for name, _ in pairs}) != len(pairs):
            raise ValueError("observed invariant identifiers must be unique")
        object.__setattr__(self, "invariants", tuple(pairs))
        for name in ("cost", "entropy"):
            value = getattr(self, name)
            object.__setattr__(self, name, None if value is None else _fraction(name, value, nonnegative=True))


@dataclass(frozen=True)
class UpdatePlan:
    parameters: tuple[str, ...] = ()
    step: Fraction = 0
    extensions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        parameters = _identifiers("update parameters", self.parameters, _MAX_PARAMETERS)
        extensions = _identifiers("update extensions", self.extensions, _MAX_EXTENSIONS)
        step = _fraction("step", self.step, nonnegative=True)
        if (not parameters and step != 0) or (parameters and step <= 0):
            raise ValueError("no parameters requires step 0; parameters require step > 0")
        object.__setattr__(self, "parameters", parameters)
        object.__setattr__(self, "extensions", extensions)
        object.__setattr__(self, "step", step)


@dataclass(frozen=True)
class ExtensionLease:
    extension_id: str
    impact_commitment: str
    cost: Fraction
    expires_at: int
    rollback_target: str

    def __post_init__(self) -> None:
        _identifier("extension_id", self.extension_id)
        _commitment("impact_commitment", self.impact_commitment)
        object.__setattr__(self, "cost", _fraction("extension cost", self.cost, nonnegative=True))
        _integer("expires_at", self.expires_at, nonnegative=False)
        _identifier("rollback_target", self.rollback_target)


@dataclass(frozen=True)
class _LatestObservation:
    observed_at: int
    admission_state: ReturnState
    valid: bool


class ReconvergenceGuard:
    """Validate a finite declared sequence and proposed updates, without execution.

    This single-owner reference object is not a concurrent transaction service.
    Every state-changing public operation appends one bounded event before its
    associated change. Validation and admission methods do not append or mutate.
    """

    def __init__(self, config: ReconvergenceConfig) -> None:
        if not isinstance(config, ReconvergenceConfig):
            raise ValueError("config must be a ReconvergenceConfig")
        self._config = ReconvergenceConfig(
            config.invariants, config.sensitive_parameters, config.flexible_parameters,
            config.partition_evidence_commitment, config.window, config.normal_step,
            config.reconvergence_step, config.energy_lambda, config.energy_limit,
            config.cost_limit, config.entropy_limit, config.initial_energy)
        config_payload: dict[str, object] = {
            "schema": "EUP-RECONVERGENCE-CONFIG/0.1",
            "invariants": [{"name": spec.name, "baseline_exact": _rational(spec.baseline),
                            "tolerance_exact": _rational(spec.tolerance)}
                           for spec in sorted(self._config.invariants, key=lambda spec: spec.name)],
            "sensitive_parameters": sorted(self._config.sensitive_parameters),
            "flexible_parameters": sorted(self._config.flexible_parameters),
            "partition_evidence_commitment": self._config.partition_evidence_commitment,
            "window": self._config.window,
        }
        for name in ("normal_step", "reconvergence_step", "energy_lambda", "energy_limit",
                     "cost_limit", "entropy_limit", "initial_energy"):
            config_payload[name + "_exact"] = _rational(getattr(self._config, name))
        self._configuration_commitment = _canonical_commitment(config_payload)
        self._snapshot_configuration = config_payload
        self._state = ReturnState.NORMAL
        self._stable_count = 0
        self._accepted_energy = self._config.initial_energy
        self._epoch = 0
        self._last_sequence: int | None = None
        self._last_observed_at: int | None = None
        self._last_operation_time: int | None = None
        self._latest: _LatestObservation | None = None
        self._normal_guards = dict.fromkeys(_NORMAL_GUARDS, True)
        self._leases: dict[str, tuple[ExtensionLease, int]] = {}
        self._records: list[dict[str, object]] = []
        self._head = _ZERO_HEAD

    @property
    def config(self) -> ReconvergenceConfig:
        return self._config

    @property
    def configuration_commitment(self) -> str:
        return self._configuration_commitment

    @property
    def state(self) -> ReturnState:
        return self._state

    @property
    def stable_count(self) -> int:
        return self._stable_count

    @property
    def records(self) -> list[dict[str, object]]:
        # Recursively independent JSON-safe copies; no raw observation retained.
        return json.loads(json.dumps(self._records, allow_nan=False))

    @property
    def head(self) -> str:
        return self._head

    @property
    def normal_guards(self) -> dict[str, bool]:
        return dict(self._normal_guards)

    def _room(self) -> None:
        if len(self._records) >= _MAX_EVENTS:
            raise ValueError("reconvergence ledger capacity exceeded")

    def _append(self, event: str, details: dict[str, object]) -> None:
        self._room()
        payload = {"index": len(self._records) + 1, "previous_head": self._head,
                   "configuration_commitment": self._configuration_commitment,
                   "event": event, "details": details}
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode("ascii")
        digest = hashlib.sha256(encoded).hexdigest()
        record = {**payload, "head": digest}
        self._records.append(record)
        self._head = digest

    def enter_exception(self, reason: str, *, decision_card: str) -> None:
        _identifier("reason", reason)
        _identifier("decision_card", decision_card)
        self._append("ENTER_EXCEPTION", {"reason": reason, "decision_card": decision_card,
            "state_before": self._state.value, "state_after": ReturnState.EXCEPTION.value,
            "epoch": self._epoch + 1})
        self._state = ReturnState.EXCEPTION
        self._stable_count = 0
        self._latest = None
        self._epoch += 1

    def begin_reconvergence(self, *, decision_card: str) -> None:
        _identifier("decision_card", decision_card)
        if self._state is not ReturnState.EXCEPTION:
            raise ValueError("reconvergence can begin only from EXCEPTION")
        self._append("BEGIN_RECONVERGENCE", {"decision_card": decision_card,
            "state_before": ReturnState.EXCEPTION.value,
            "state_after": ReturnState.RECONVERGING.value, "epoch": self._epoch})
        self._state = ReturnState.RECONVERGING
        self._stable_count = 0
        self._latest = None

    def register_extension(self, lease: ExtensionLease, *, now: int, decision_card: str) -> None:
        if not isinstance(lease, ExtensionLease):
            raise ValueError("lease must be an ExtensionLease")
        checked = ExtensionLease(lease.extension_id, lease.impact_commitment, lease.cost,
                                 lease.expires_at, lease.rollback_target)
        _integer("now", now)
        _identifier("decision_card", decision_card)
        if self._last_operation_time is not None and now < self._last_operation_time:
            raise ValueError("extension operation time must not decrease")
        if checked.expires_at <= now:
            raise ValueError("extension expiry must be strictly later than now")
        if checked.extension_id not in self._leases and len(self._leases) >= _MAX_EXTENSIONS:
            raise ValueError("at most 64 extension identifiers may be registered")
        lease_commitment = _canonical_commitment({
            "schema": "EUP-RECONVERGENCE-LEASE/0.1", "extension_id": checked.extension_id,
            "impact_commitment": checked.impact_commitment, "cost_exact": _rational(checked.cost),
            "expires_at": checked.expires_at, "rollback_target": checked.rollback_target,
        })
        self._append("REGISTER_EXTENSION", {"extension_id": checked.extension_id,
            "now": now, "expires_at": checked.expires_at, "decision_card": decision_card,
            "renewal": checked.extension_id in self._leases, "epoch": self._epoch,
            "lease_commitment": lease_commitment})
        self._leases[checked.extension_id] = (checked, self._epoch)
        self._last_operation_time = now

    def set_normal_guard(self, name: str, enabled: bool, *, reason: str, decision_card: str) -> None:
        if not isinstance(name, str) or name not in _NORMAL_GUARDS:
            raise ValueError("normal guard must be energy, cost or entropy")
        if type(enabled) is not bool:
            raise ValueError("enabled must be an exact boolean")
        _identifier("reason", reason)
        _identifier("decision_card", decision_card)
        if self._state is not ReturnState.NORMAL:
            raise ValueError("normal guards may change only in NORMAL")
        self._append("SET_NORMAL_GUARD", {"name": name, "enabled": enabled,
            "reason": reason, "decision_card": decision_card, "epoch": self._epoch})
        self._normal_guards[name] = enabled
        self._latest = None

    def _checked_observation(self, observation: ReconvergenceObservation) -> ReconvergenceObservation:
        if not isinstance(observation, ReconvergenceObservation):
            raise ValueError("observation must be a ReconvergenceObservation")
        checked = ReconvergenceObservation(observation.sequence, observation.observed_at,
            observation.invariants, observation.cost, observation.entropy)
        declared = {spec.name for spec in self._config.invariants}
        if any(name not in declared for name, _ in checked.invariants):
            raise ValueError("observation names an undeclared invariant")
        if self._last_sequence is not None and checked.sequence <= self._last_sequence:
            raise ValueError("observation sequence must strictly increase")
        if self._last_observed_at is not None and checked.observed_at < self._last_observed_at:
            raise ValueError("observation time must not decrease")
        if self._last_operation_time is not None and checked.observed_at < self._last_operation_time:
            raise ValueError("observation precedes the latest operation")
        self._room()
        return checked

    def validate_observation(self, observation: ReconvergenceObservation) -> None:
        self._checked_observation(observation)

    def observe(self, observation: ReconvergenceObservation) -> dict[str, object]:
        checked = self._checked_observation(observation)
        config = self._config
        before = self._state
        values = dict(checked.invariants)
        missing = (any(values.get(spec.name) is None for spec in config.invariants)
                   or checked.cost is None or checked.entropy is None)
        energy = (None if checked.cost is None or checked.entropy is None
                  else checked.cost + config.energy_lambda * checked.entropy)
        reasons: list[str] = []
        if before is ReturnState.EXCEPTION:
            reasons.append("EXCEPTION_ACTIVE")
        else:
            if missing:
                reasons.append("COVERAGE_INCOMPLETE")
            if any(values.get(spec.name) is not None
                   and abs(values[spec.name] - spec.baseline) > spec.tolerance
                   for spec in config.invariants):
                reasons.append("INVARIANT_TOLERANCE_EXCEEDED")
            returning = before is ReturnState.RECONVERGING
            if checked.cost is not None and (returning or self._normal_guards["cost"]) and checked.cost > config.cost_limit:
                reasons.append("COST_LIMIT_EXCEEDED")
            if checked.entropy is not None and (returning or self._normal_guards["entropy"]) and checked.entropy > config.entropy_limit:
                reasons.append("ENTROPY_LIMIT_EXCEEDED")
            if energy is not None and (returning or self._normal_guards["energy"]) and energy > config.energy_limit:
                reasons.append("ENERGY_LIMIT_EXCEEDED")
            if returning and energy is not None and energy > self._accepted_energy:
                reasons.append("ENERGY_INCREASED")
        valid = not reasons
        gap = (self._last_sequence is not None and checked.sequence > self._last_sequence + 1)
        after = before
        stable_count = self._stable_count
        epoch = self._epoch
        if before is ReturnState.RECONVERGING:
            stable_count = (1 if gap else self._stable_count + 1) if valid else 0
            if stable_count >= config.window:
                after = ReturnState.NORMAL
        elif before is ReturnState.NORMAL and not valid:
            after = ReturnState.EXCEPTION
            stable_count = 0
            epoch += 1
        elif before is ReturnState.EXCEPTION:
            stable_count = 0
        if gap:
            # A skipped sample interrupts the window, not a sound new step.
            reasons.append("SEQUENCE_GAP")
        admission_state = (ReturnState.RECONVERGING if before is ReturnState.RECONVERGING
                           else after)
        metadata: dict[str, object] = {
            "schema": "EUP-RECONVERGENCE/0.1", "configuration_commitment": self._configuration_commitment,
            "sequence": checked.sequence,
            "observed_at": checked.observed_at, "state_before": before.value,
            "state_after": after.value, "admission_state": admission_state.value,
            "valid": valid, "stable_count": stable_count, "reasons": reasons,
            "energy_exact": _rational(energy), "epoch": epoch,
            "normal_guards": dict(self._normal_guards),
        }
        latest = _LatestObservation(checked.observed_at, admission_state, valid)
        self._append("OBSERVE", metadata)
        self._state = after
        self._stable_count = stable_count
        self._epoch = epoch
        self._last_sequence = checked.sequence
        self._last_observed_at = checked.observed_at
        self._last_operation_time = checked.observed_at
        self._latest = latest
        if valid:
            self._accepted_energy = energy  # Complete coverage made energy non-None.
        # Do not expose the ledger's internal nested dictionaries through output.
        return {**json.loads(json.dumps(metadata)), "ledger_head": self._head}

    def _checked_update(self, plan: UpdatePlan) -> UpdatePlan:
        if not isinstance(plan, UpdatePlan):
            raise ValueError("plan must be an UpdatePlan")
        checked = UpdatePlan(plan.parameters, plan.step, plan.extensions)
        declared = set(self._config.sensitive_parameters) | set(self._config.flexible_parameters)
        if any(name not in declared for name in checked.parameters):
            raise ValueError("update names an undeclared parameter")
        return checked

    def validate_update(self, plan: UpdatePlan) -> None:
        self._checked_update(plan)

    def admit(self, plan: UpdatePlan, *, now: int) -> str | None:
        checked = self._checked_update(plan)
        _integer("now", now)
        if self._state is ReturnState.EXCEPTION:
            return "EXCEPTION_ACTIVE"
        if self._latest is None:
            return "OBSERVATION_MISSING"
        if now != self._latest.observed_at or (self._last_operation_time is not None and now < self._last_operation_time):
            return "OBSERVATION_STALE"
        if not self._latest.valid:
            return "OBSERVATION_INVALID"
        returning = self._latest.admission_state is ReturnState.RECONVERGING
        if returning and set(checked.parameters) & set(self._config.sensitive_parameters):
            return "SENSITIVE_PARAMETER_FROZEN"
        if returning and checked.step > self._config.reconvergence_step:
            return "RECONVERGENCE_STEP_EXCEEDED"
        if not returning and checked.step > self._config.normal_step:
            return "NORMAL_STEP_EXCEEDED"
        leases: list[ExtensionLease] = []
        for name in checked.extensions:
            registration = self._leases.get(name)
            if registration is None or registration[1] != self._epoch:
                return "EXTENSION_NOT_APPROVED"
            lease = registration[0]
            if now >= lease.expires_at:
                return "EXTENSION_EXPIRED"
            leases.append(lease)
        if sum((lease.cost for lease in leases), Fraction(0)) > self._config.cost_limit:
            return "EXTENSION_COST_LIMIT_EXCEEDED"
        return None

    def _snapshot_guard(self) -> dict[str, object]:
        return {
            "state": self._state.value, "stable_count": self._stable_count,
            "accepted_energy_exact": _rational(self._accepted_energy), "epoch": self._epoch,
            "last_sequence": self._last_sequence, "last_observed_at": self._last_observed_at,
            "last_operation_time": self._last_operation_time,
            "normal_guards": dict(self._normal_guards),
            "latest": None if self._latest is None else {
                "observed_at": self._latest.observed_at,
                "admission_state": self._latest.admission_state.value, "valid": self._latest.valid},
            "leases": [{"extension_id": lease.extension_id,
                "impact_commitment": lease.impact_commitment, "cost_exact": _rational(lease.cost),
                "expires_at": lease.expires_at, "rollback_target": lease.rollback_target,
                "epoch": epoch} for _, (lease, epoch) in sorted(self._leases.items())],
        }

    def export_snapshot(self) -> bytes:
        """Return canonical bounded bytes without changing this guard or writing files."""
        document = {"schema": _SNAPSHOT_SCHEMA, "config": self._snapshot_configuration,
                    "configuration_commitment": self._configuration_commitment,
                    "guard": self._snapshot_guard(), "records": self.records, "head": self._head}
        raw = _snapshot_encode(document)
        # Validate internal/chain coherence too; this does not restore or append.
        type(self)._validated_snapshot(self._config, raw,
            expected_snapshot_sha256=hashlib.sha256(raw).hexdigest(), expected_head=self._head)
        return raw

    @classmethod
    def from_snapshot(cls, config: ReconvergenceConfig, raw: bytes, *,
                      expected_snapshot_sha256: str, expected_head: str) -> ReconvergenceGuard:
        """Validate caller-anchored local data and append one explicit recovery boundary."""
        guard = cls._validated_snapshot(config, raw,
            expected_snapshot_sha256=expected_snapshot_sha256, expected_head=expected_head)
        guard._room()  # No usable restored guard without a recorded RESTORE slot.
        details = {"source_snapshot_sha256": expected_snapshot_sha256, "source_head": guard._head,
                   "discarded_latest": guard._latest is not None,
                   "discarded_leases": sorted(guard._leases), "state": guard._state.value,
                   "stable_count": guard._stable_count,
                   "accepted_energy_exact": _rational(guard._accepted_energy), "epoch": guard._epoch}
        guard._append("RESTORE", details)
        guard._latest = None
        guard._leases.clear()
        return guard

    @classmethod
    def _validated_snapshot(cls, config: ReconvergenceConfig, raw: bytes, *,
                            expected_snapshot_sha256: str, expected_head: str) -> ReconvergenceGuard:
        _commitment("expected_snapshot_sha256", expected_snapshot_sha256)
        _commitment("expected_head", expected_head)
        if type(raw) is not bytes or len(raw) > _SNAPSHOT_MAX_BYTES:
            raise ValueError("snapshot requires bounded bytes")
        if hashlib.sha256(raw).hexdigest() != expected_snapshot_sha256:
            raise ValueError("snapshot digest differs from caller anchor")
        document = _snapshot_decode(raw)
        _snapshot_keys(document, {"schema", "config", "configuration_commitment", "guard", "records", "head"})
        guard = cls(config)
        if (document["schema"] != _SNAPSHOT_SCHEMA
                or document["configuration_commitment"] != guard._configuration_commitment
                or _snapshot_encode(document["config"]) != _snapshot_encode(guard._snapshot_configuration)
                or document["head"] != expected_head):
            raise ValueError("snapshot schema, configuration or head does not match")
        records = document["records"]
        if type(records) is not list or len(records) > _MAX_EVENTS:
            raise ValueError("snapshot event capacity exceeded")
        registrations: dict[str, dict] = {}
        for record in records:
            _snapshot_keys(record, {"index", "previous_head", "configuration_commitment", "event", "details", "head"})
            if (_snapshot_integer(record["index"]) != len(guard._records) + 1
                    or record["previous_head"] != guard._head
                    or record["configuration_commitment"] != guard._configuration_commitment):
                raise ValueError("snapshot ledger linkage is inconsistent")
            payload = {key: value for key, value in record.items() if key != "head"}
            if _commitment("record head", record["head"]) != _canonical_commitment(payload):
                raise ValueError("snapshot ledger hash mismatch")
            guard._recover_event(record["event"], record["details"], registrations)
            guard._records.append(record)
            guard._head = record["head"]
        if guard._head != expected_head:
            raise ValueError("snapshot terminal ledger head mismatch")
        state = _snapshot_keys(document["guard"], set(guard._snapshot_guard()))
        leases = state["leases"]
        if type(leases) is not list or len(leases) > _MAX_EXTENSIONS:
            raise ValueError("snapshot lease collection is invalid")
        names = []
        for item in leases:
            _snapshot_keys(item, {"extension_id", "impact_commitment", "cost_exact", "expires_at", "rollback_target", "epoch"})
            lease = ExtensionLease(item["extension_id"], item["impact_commitment"],
                _snapshot_rational(item["cost_exact"], nonnegative=True),
                _snapshot_integer(item["expires_at"], nonnegative=False), item["rollback_target"])
            epoch = _snapshot_integer(item["epoch"])
            registered = registrations.get(lease.extension_id)
            commitment = _canonical_commitment({"schema": "EUP-RECONVERGENCE-LEASE/0.1",
                "extension_id": lease.extension_id, "impact_commitment": lease.impact_commitment,
                "cost_exact": _rational(lease.cost), "expires_at": lease.expires_at,
                "rollback_target": lease.rollback_target})
            if (registered is None or registered["epoch"] != epoch
                    or registered["expires_at"] != lease.expires_at
                    or registered["lease_commitment"] != commitment):
                raise ValueError("snapshot lease does not match its last registration")
            guard._leases[lease.extension_id] = (lease, epoch)
            names.append(lease.extension_id)
        if names != sorted(set(names)) or set(names) != set(registrations):
            raise ValueError("snapshot leases are not complete, unique and ordered")
        _snapshot_rational(state["accepted_energy_exact"], nonnegative=True)
        # Canonical comparison also distinguishes bool from int and unknown fields.
        if _snapshot_encode(state) != _snapshot_encode(guard._snapshot_guard()):
            raise ValueError("snapshot state does not agree with its event history")
        return guard

    def _recover_event(self, event: object, details: object, registrations: dict[str, dict]) -> None:
        """Check recorded transitions, not unavailable raw numerical observations."""
        if event == "ENTER_EXCEPTION":
            data = _snapshot_keys(details, {"reason", "decision_card", "state_before", "state_after", "epoch"})
            _identifier("reason", data["reason"])
            _identifier("decision_card", data["decision_card"])
            if (data["state_before"] != self._state.value or data["state_after"] != "EXCEPTION"
                    or _snapshot_integer(data["epoch"]) != self._epoch + 1):
                raise ValueError("inconsistent exception transition")
            self._state, self._stable_count, self._latest = ReturnState.EXCEPTION, 0, None
            self._epoch += 1
        elif event == "BEGIN_RECONVERGENCE":
            data = _snapshot_keys(details, {"decision_card", "state_before", "state_after", "epoch"})
            _identifier("decision_card", data["decision_card"])
            if (self._state is not ReturnState.EXCEPTION or data["state_before"] != "EXCEPTION"
                    or data["state_after"] != "RECONVERGING" or _snapshot_integer(data["epoch"]) != self._epoch):
                raise ValueError("inconsistent reconvergence transition")
            self._state, self._stable_count, self._latest = ReturnState.RECONVERGING, 0, None
        elif event == "REGISTER_EXTENSION":
            data = _snapshot_keys(details, {"extension_id", "now", "expires_at", "decision_card", "renewal", "epoch", "lease_commitment"})
            name = _identifier("extension_id", data["extension_id"])
            _identifier("decision_card", data["decision_card"])
            _commitment("lease_commitment", data["lease_commitment"])
            now = _snapshot_integer(data["now"])
            expiry = _snapshot_integer(data["expires_at"], nonnegative=False)
            if (type(data["renewal"]) is not bool or data["renewal"] != (name in registrations)
                    or _snapshot_integer(data["epoch"]) != self._epoch or expiry <= now
                    or (self._last_operation_time is not None and now < self._last_operation_time)
                    or (name not in registrations and len(registrations) >= _MAX_EXTENSIONS)):
                raise ValueError("inconsistent extension registration")
            registrations[name] = data
            self._last_operation_time = now
        elif event == "SET_NORMAL_GUARD":
            data = _snapshot_keys(details, {"name", "enabled", "reason", "decision_card", "epoch"})
            _identifier("reason", data["reason"])
            _identifier("decision_card", data["decision_card"])
            if (self._state is not ReturnState.NORMAL or data["name"] not in _NORMAL_GUARDS
                    or type(data["enabled"]) is not bool or _snapshot_integer(data["epoch"]) != self._epoch):
                raise ValueError("inconsistent monitor change")
            self._normal_guards[data["name"]] = data["enabled"]
            self._latest = None
        elif event == "OBSERVE":
            self._recover_observation(details)
        elif event == "RESTORE":
            data = _snapshot_keys(details, {"source_snapshot_sha256", "source_head", "discarded_latest", "discarded_leases", "state", "stable_count", "accepted_energy_exact", "epoch"})
            _commitment("source_snapshot_sha256", data["source_snapshot_sha256"])
            if (data["source_head"] != self._head or type(data["discarded_latest"]) is not bool
                    or data["discarded_latest"] != (self._latest is not None)
                    or data["discarded_leases"] != sorted(registrations)
                    or data["state"] != self._state.value
                    or _snapshot_integer(data["stable_count"]) != self._stable_count
                    or _snapshot_rational(data["accepted_energy_exact"], nonnegative=True) != self._accepted_energy
                    or _snapshot_integer(data["epoch"]) != self._epoch):
                raise ValueError("inconsistent recovery boundary")
            registrations.clear()
            self._latest = None
        else:
            raise ValueError("unknown snapshot event")

    def _recover_observation(self, details: object) -> None:
        data = _snapshot_keys(details, {"schema", "configuration_commitment", "sequence", "observed_at", "state_before", "state_after", "admission_state", "valid", "stable_count", "reasons", "energy_exact", "epoch", "normal_guards"})
        sequence, now = _snapshot_integer(data["sequence"]), _snapshot_integer(data["observed_at"])
        if (data["schema"] != "EUP-RECONVERGENCE/0.1" or data["configuration_commitment"] != self._configuration_commitment
                or data["state_before"] != self._state.value or type(data["valid"]) is not bool
                or _snapshot_encode(data["normal_guards"]) != _snapshot_encode(self._normal_guards)
                or (self._last_sequence is not None and sequence <= self._last_sequence)
                or (self._last_observed_at is not None and now < self._last_observed_at)
                or (self._last_operation_time is not None and now < self._last_operation_time)):
            raise ValueError("inconsistent observation frontier")
        order = ("EXCEPTION_ACTIVE", "COVERAGE_INCOMPLETE", "INVARIANT_TOLERANCE_EXCEEDED",
                 "COST_LIMIT_EXCEEDED", "ENTROPY_LIMIT_EXCEEDED", "ENERGY_LIMIT_EXCEEDED",
                 "ENERGY_INCREASED", "SEQUENCE_GAP")
        reasons = data["reasons"]
        if (type(reasons) is not list or any(type(reason) is not str or reason not in order for reason in reasons)
                or len(set(reasons)) != len(reasons) or reasons != sorted(reasons, key=order.index)):
            raise ValueError("invalid observation reason codes")
        gap = self._last_sequence is not None and sequence > self._last_sequence + 1
        base = [reason for reason in reasons if reason != "SEQUENCE_GAP"]
        if ("SEQUENCE_GAP" in reasons) != gap or data["valid"] != (not base):
            raise ValueError("inconsistent observation validity")
        energy = None if data["energy_exact"] is None else _snapshot_rational(data["energy_exact"], nonnegative=True)
        returning = self._state is ReturnState.RECONVERGING
        if self._state is ReturnState.EXCEPTION:
            if base != ["EXCEPTION_ACTIVE"]:
                raise ValueError("exception observations cannot be accepted")
        else:
            if ("EXCEPTION_ACTIVE" in base or (energy is None and "COVERAGE_INCOMPLETE" not in base)
                    or (("ENERGY_LIMIT_EXCEEDED" in base) !=
                        (energy is not None and (returning or self._normal_guards["energy"]) and energy > self._config.energy_limit))
                    or (("ENERGY_INCREASED" in base) !=
                        (returning and energy is not None and energy > self._accepted_energy))
                    or ("COST_LIMIT_EXCEEDED" in base and not returning and not self._normal_guards["cost"])
                    or ("ENTROPY_LIMIT_EXCEEDED" in base and not returning and not self._normal_guards["entropy"])):
                raise ValueError("inconsistent recorded numerical guards")
        after, stable, epoch = self._state, self._stable_count, self._epoch
        if returning:
            stable = (1 if gap else stable + 1) if data["valid"] else 0
            if stable >= self._config.window:
                after = ReturnState.NORMAL
        elif self._state is ReturnState.NORMAL and not data["valid"]:
            after, stable, epoch = ReturnState.EXCEPTION, 0, epoch + 1
        elif self._state is ReturnState.EXCEPTION:
            stable = 0
        admission = ReturnState.RECONVERGING if returning else after
        if (data["state_after"] != after.value or data["admission_state"] != admission.value
                or _snapshot_integer(data["stable_count"]) != stable or _snapshot_integer(data["epoch"]) != epoch):
            raise ValueError("inconsistent return window or state")
        self._state, self._stable_count, self._epoch = after, stable, epoch
        self._last_sequence, self._last_observed_at, self._last_operation_time = sequence, now, now
        self._latest = _LatestObservation(now, admission, data["valid"])
        if data["valid"]:
            if energy is None:
                raise ValueError("accepted observation requires energy")
            self._accepted_energy = energy
