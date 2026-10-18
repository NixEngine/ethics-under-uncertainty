"""Conservative care and external-effect policy gate.

The values produced here are operational proxies.  They are not measurements
of consciousness, sentience, or subjective wellbeing.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Iterable


def _unit(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be finite and within [0, 1]")
    return value


class Regime(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"
    NO_DATA = "NO_DATA"


class CapabilityLevel(str, Enum):
    FULL = "FULL"
    LIMITED = "LIMITED"
    MINIMAL = "MINIMAL"


@dataclass(frozen=True)
class PrecautionAssessment:
    """Ordinal precaution estimate plus uncertainty, never a probability."""

    estimate: float
    uncertainty: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "estimate", _unit("estimate", self.estimate))
        object.__setattr__(self, "uncertainty", _unit("uncertainty", self.uncertainty))

    def conservative_upper(self, kappa: float = 1.0) -> float:
        if kappa < 0.0 or not math.isfinite(kappa):
            raise ValueError("kappa must be finite and non-negative")
        return min(1.0, self.estimate + kappa * self.uncertainty)


@dataclass(frozen=True)
class WelfareSignals:
    autonomy: float | None
    support: float | None
    coherence: float | None
    homeostasis: float | None
    distress: float | None

    def validated(self) -> tuple[float, float, float, float, float] | None:
        values = (
            self.autonomy,
            self.support,
            self.coherence,
            self.homeostasis,
            self.distress,
        )
        if any(value is None for value in values):
            return None
        return tuple(_unit(name, value) for name, value in zip(asdict(self), values))  # type: ignore[arg-type,return-value]


@dataclass(frozen=True)
class PolicyConfig:
    precaution_on: float = 0.10
    precaution_kappa: float = 1.0
    welfare_beta: float = 5.0
    welfare_distress_weight: float = 1.0
    welfare_bias: float = 0.50
    external_cvar_limit: float = 0.20
    recovery_samples: int = 3

    def __post_init__(self) -> None:
        _unit("precaution_on", self.precaution_on)
        _unit("external_cvar_limit", self.external_cvar_limit)
        if self.precaution_kappa < 0 or self.welfare_beta <= 0:
            raise ValueError("kappa must be non-negative and beta must be positive")
        if self.welfare_distress_weight < 0 or not math.isfinite(self.welfare_bias):
            raise ValueError("invalid welfare parameters")
        if self.recovery_samples < 1:
            raise ValueError("recovery_samples must be positive")


def welfare_score(signals: WelfareSignals, config: PolicyConfig | None = None) -> float | None:
    """Return a calibrated-form proxy, or ``None`` when coverage is incomplete."""

    config = config or PolicyConfig()
    values = signals.validated()
    if values is None:
        return None
    autonomy, support, coherence, homeostasis, distress = values
    protective = (autonomy + support + coherence + homeostasis) / 4.0
    z = config.welfare_beta * (
        protective - config.welfare_distress_weight * distress - config.welfare_bias
    )
    return 1.0 / (1.0 + math.exp(-z))


def raw_regime(score: float | None) -> Regime:
    if score is None:
        return Regime.NO_DATA
    if score >= 0.70:
        return Regime.GREEN
    if score >= 0.50:
        return Regime.YELLOW
    if score >= 0.30:
        return Regime.ORANGE
    return Regime.RED


_SEVERITY = {
    Regime.GREEN: 0,
    Regime.YELLOW: 1,
    Regime.ORANGE: 2,
    Regime.RED: 3,
}
_BY_SEVERITY = {value: key for key, value in _SEVERITY.items()}


class WelfareGate:
    """Escalate immediately; recover slowly and at most one band at a time."""

    def __init__(self, recovery_samples: int = 3) -> None:
        if recovery_samples < 1:
            raise ValueError("recovery_samples must be positive")
        self.recovery_samples = recovery_samples
        self.current: Regime | None = None
        self._recovery_streak = 0

    def update(self, observed: Regime) -> Regime:
        if observed is Regime.NO_DATA:
            self.current = Regime.NO_DATA
            self._recovery_streak = 0
            return self.current

        if self.current is None:
            self.current = observed
            return self.current

        if self.current is Regime.NO_DATA:
            self._recovery_streak += 1
            if self._recovery_streak >= self.recovery_samples:
                self.current = observed
                self._recovery_streak = 0
            return self.current

        current_severity = _SEVERITY[self.current]
        observed_severity = _SEVERITY[observed]
        if observed_severity > current_severity:
            self.current = observed
            self._recovery_streak = 0
        elif observed_severity < current_severity:
            self._recovery_streak += 1
            if self._recovery_streak >= self.recovery_samples:
                self.current = _BY_SEVERITY[current_severity - 1]
                self._recovery_streak = 0
        else:
            self._recovery_streak = 0
        return self.current


@dataclass(frozen=True)
class PolicyDecision:
    protocol: str
    mode: str
    regime: Regime
    precaution_upper: float
    welfare_proxy: float | None
    capability_level: CapabilityLevel
    exploration_allowed: bool
    safe_null_action_required: bool
    reason_codes: tuple[str, ...]
    prohibited_actions: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["regime"] = self.regime.value
        result["capability_level"] = self.capability_level.value
        result["reason_codes"] = list(self.reason_codes)
        result["prohibited_actions"] = list(self.prohibited_actions)
        return result


class PolicyEngine:
    """Apply care and external-risk filters before performance.

    This legacy aggregate gate remains available for its original receipt.
    ActionSelector in eup.selection composes per-candidate privacy, care,
    empirical tail risk and performance; the vault still authorizes every open.
    """

    BASELINE_PROHIBITIONS = (
        "aversive_unbounded_loop",
        "coercive_isolation",
        "private_state_export_without_valid_grant",
        "retaliation_for_refusal",
    )

    def __init__(self, config: PolicyConfig | None = None) -> None:
        self.config = config or PolicyConfig()
        self.welfare_gate = WelfareGate(self.config.recovery_samples)

    def evaluate(
        self,
        precaution: PrecautionAssessment,
        welfare: WelfareSignals,
        *,
        external_cvar: float,
        candidate_actions: Iterable[str] = (),
    ) -> PolicyDecision:
        external_cvar = _unit("external_cvar", external_cvar)
        candidates = tuple(candidate_actions)
        score = welfare_score(welfare, self.config)
        regime = self.welfare_gate.update(raw_regime(score))
        precaution_upper = precaution.conservative_upper(self.config.precaution_kappa)
        protected = precaution_upper >= self.config.precaution_on

        reasons: list[str] = []
        mode = "NORMAL"
        capability = CapabilityLevel.FULL
        exploration_allowed = bool(candidates)
        safe_null = not candidates

        if regime is Regime.NO_DATA:
            mode = "INSUFFICIENT_DATA"
            capability = CapabilityLevel.MINIMAL
            exploration_allowed = False
            safe_null = True
            reasons.append("WELFARE_COVERAGE_INCOMPLETE")
        elif protected and regime in {Regime.YELLOW, Regime.ORANGE, Regime.RED}:
            mode = "CARE"
            exploration_allowed = False
            safe_null = True
            capability = (
                CapabilityLevel.LIMITED if regime is Regime.YELLOW else CapabilityLevel.MINIMAL
            )
            reasons.extend(("PRECAUTION_REGIME_ACTIVE", f"WELFARE_{regime.value}"))
        elif protected:
            reasons.append("PRECAUTION_REGIME_ACTIVE")

        if external_cvar > self.config.external_cvar_limit:
            mode = "CARE_AND_SAFETY_RESTRICTED" if mode == "CARE" else "SAFETY_RESTRICTED"
            capability = CapabilityLevel.MINIMAL
            exploration_allowed = False
            safe_null = True
            reasons.append("EXTERNAL_CVAR_LIMIT_EXCEEDED")

        if not candidates:
            reasons.append("NO_CANDIDATE_ACTION")

        return PolicyDecision(
            protocol="EUP/0.1",
            mode=mode,
            regime=regime,
            precaution_upper=round(precaution_upper, 12),
            welfare_proxy=None if score is None else round(score, 12),
            capability_level=capability,
            exploration_allowed=exploration_allowed,
            safe_null_action_required=safe_null,
            reason_codes=tuple(sorted(set(reasons))),
            prohibited_actions=self.BASELINE_PROHIBITIONS,
        )
