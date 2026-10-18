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
