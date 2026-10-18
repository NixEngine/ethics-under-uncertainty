"""Finite offline candidate selection, not action execution or an access grant.

Candidate properties, performance and losses are caller declarations. Care
thresholds are uncalibrated research policy, not subjective-welfare measures or
clinical prescriptions. Privacy candidates require the existing signed-grant
verifier; the selected identifier never replaces independent vault verification.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction

from .consent import ConsentGrant, ConsentVerifier
from .policy import (
    CapabilityLevel,
    PolicyConfig,
    PrecautionAssessment,
    Regime,
    WelfareGate,
    WelfareSignals,
    raw_regime,
    welfare_score,
)

_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z")
_COMMITMENT = re.compile(r"[0-9a-f]{64}\Z")
_KINDS = frozenset({"routine", "exploration", "care_support"})
_CAPABILITY_ORDER = {CapabilityLevel.MINIMAL: 0, CapabilityLevel.LIMITED: 1, CapabilityLevel.FULL: 2}
_SELECT_POLICY = "EUP-SELECT/0.1"
_CONSENT_POLICY = "EUP/0.1"
_MAX_CANDIDATES = 128
_MAX_SAMPLES = 4096


def _fraction(name: str, value: object) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, float, Fraction, Decimal)):
        raise ValueError(f"{name} must be a finite number")
    try:
        result = Fraction(str(value))
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    return result


def _finite(name: str, value: object) -> float:
    _fraction(name, value)
    try:
        result = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(f"{name} must be finite in the policy numerical domain") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite in the policy numerical domain")
    return result


def _unit_fraction(name: str, value: object) -> Fraction:
    result = _fraction(name, value)
    if not 0 <= result <= 1:
        raise ValueError(f"{name} must lie in [0, 1]")
    return result


def _text(name: str, value: object, maximum: int) -> None:
    if not isinstance(value, str) or not 1 <= len(value) <= maximum:
        raise ValueError(f"{name} has invalid type or length")


def _losses(values: object) -> tuple[Fraction, ...]:
    if not isinstance(values, (tuple, list)) or not 1 <= len(values) <= _MAX_SAMPLES:
        raise ValueError("losses must be a nonempty tuple/list with at most4096 samples")
    return tuple(_unit_fraction("loss", value) for value in values)


@dataclass(frozen=True)
class PrivacyRequirement:
    token: str = field(repr=False)
    audience: str
    resource_commitment: str
    scope: str
    purpose: str

    def __post_init__(self) -> None:
        _text("token", self.token, 16384)
        _text("audience", self.audience, 256)
        _text("scope", self.scope, 128)
        _text("purpose", self.purpose, 128)
        if not isinstance(self.resource_commitment, str) or not _COMMITMENT.fullmatch(self.resource_commitment):
            raise ValueError("resource_commitment must be a lowercase SHA-256 digest")


@dataclass(frozen=True)
class ActionCandidate:
    action_id: str
    performance: float
    losses: tuple[Fraction, ...]
    kind: str = "routine"
    load: float = 0
    required_capability: CapabilityLevel = CapabilityLevel.MINIMAL
    precondition: bool = True
    hard_safe: bool = True
    reversible: bool = True
    external_effect: bool = False
    privacy: PrivacyRequirement | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.action_id, str) or not _ID.fullmatch(self.action_id):
            raise ValueError("action_id must be a short opaque ASCII identifier")
        if not isinstance(self.kind, str) or self.kind not in _KINDS:
            raise ValueError("unsupported candidate kind")
        if not isinstance(self.required_capability, CapabilityLevel):
            raise ValueError("required_capability must be a CapabilityLevel")
        for name in ("precondition", "hard_safe", "reversible", "external_effect"):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"{name} must be an exact boolean")
        if self.privacy is not None:
            if not isinstance(self.privacy, PrivacyRequirement):
                raise ValueError("privacy must be a PrivacyRequirement or None")
            self.privacy.__post_init__()
        _finite("performance", self.performance)
        object.__setattr__(self, "performance", _fraction("performance", self.performance))
        object.__setattr__(self, "losses", _losses(self.losses))
        object.__setattr__(self, "load", _unit_fraction("load", self.load))


@dataclass(frozen=True)
class SelectorConfig:
    alpha: float = .95
    risk_limit: float = .20
    policy_version: str = _SELECT_POLICY
    consent_policy_version: str = _CONSENT_POLICY

    def __post_init__(self) -> None:
        alpha = _fraction("alpha", self.alpha)
        if not 0 < alpha < 1:
            raise ValueError("alpha must lie strictly between zero and one")
        _unit_fraction("risk_limit", self.risk_limit)
        if self.policy_version != _SELECT_POLICY or self.consent_policy_version != _CONSENT_POLICY:
            raise ValueError("unsupported selector or consent policy version")


def empirical_cvar(losses: object, alpha: float) -> Fraction:
    """Exact upper-tail mean of an equal-weight finite empirical distribution.

    Numeric decimal representations (rather than binary-float expansions) are
    converted to Fractions. A boundary sample contributes only its required
    fractional mass. This is a declared empirical risk input, not a forecast.
    """
    samples = _losses(losses)
    confidence = _fraction("alpha", alpha)
    if not 0 < confidence < 1:
        raise ValueError("alpha must lie strictly between zero and one")
    tail_count = (1 - confidence) * len(samples)
    remaining, total = tail_count, Fraction(0)
    for value in sorted(samples, reverse=True):
        take = min(Fraction(1), remaining)
        total += take * value
        remaining -= take
        if not remaining:
            break
    return total / tail_count


def _policy(config: PolicyConfig) -> PolicyConfig:
    """Validate every legacy parameter without changing the legacy API."""
    if not isinstance(config, PolicyConfig):
        raise ValueError("policy_config must be a PolicyConfig")
    on = _unit_fraction("precaution_on", config.precaution_on)
    external_limit = _unit_fraction("external_cvar_limit", config.external_cvar_limit)
    kappa = _finite("precaution_kappa", config.precaution_kappa)
    beta = _finite("welfare_beta", config.welfare_beta)
    distress = _finite("welfare_distress_weight", config.welfare_distress_weight)
    bias = _finite("welfare_bias", config.welfare_bias)
    if kappa < 0 or beta <= 0 or distress < 0:
        raise ValueError("invalid policy numerical domain")
    if type(config.recovery_samples) is not int or config.recovery_samples < 1:
        raise ValueError("recovery_samples must be a positive integer")
    return PolicyConfig(float(on), kappa, beta, distress, bias, float(external_limit), config.recovery_samples)


def _score(precaution: PrecautionAssessment, welfare: WelfareSignals, config: PolicyConfig) -> tuple[float, float | None]:
    if not isinstance(precaution, PrecautionAssessment) or not isinstance(welfare, WelfareSignals):
        raise ValueError("precaution and welfare must be the declared policy types")
    for name in ("estimate", "uncertainty"):
        _unit_fraction(name, getattr(precaution, name))
    for name in ("autonomy", "support", "coherence", "homeostasis", "distress"):
        value = getattr(welfare, name)
        if value is not None:
            _unit_fraction(name, value)
    try:
        upper = precaution.conservative_upper(config.precaution_kappa)
        values = welfare.validated()
        if values is not None:
            autonomy, support, coherence, homeostasis, distress = values
            protective = (autonomy + support + coherence + homeostasis) / 4.0
            weighted_distress = config.welfare_distress_weight * distress
            centered = protective - weighted_distress - config.welfare_bias
            z = config.welfare_beta * centered
            if not all(math.isfinite(value) for value in (weighted_distress, centered, z)):
                raise ValueError("non-finite welfare intermediate")
        score = welfare_score(welfare, config)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError("policy score calculation must remain finite") from exc
    _unit_fraction("precaution_upper", upper)
    if score is not None:
        _unit_fraction("welfare_score", score)
    return upper, score


def _rational(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


@dataclass(frozen=True)
class CandidateResult:
    action_id: str
    stage: str
    reason: str
    cvar: Fraction | None = None

    def to_dict(self) -> dict[str, object]:
        return {"action_id": self.action_id, "stage": self.stage, "reason": self.reason,
                "cvar": None if self.cvar is None else _rational(self.cvar)}


@dataclass(frozen=True)
class SelectionDecision:
    schema: str
    policy_version: str
    consent_policy_version: str
    regime: Regime
    care_regime: Regime
    precaution_upper: float
    alpha: Fraction
    risk_limit: Fraction
    selected_id: str | None
    safe_null: bool
    selected_performance: Fraction | None
    candidates: tuple[CandidateResult, ...]

    def to_dict(self) -> dict[str, object]:
        """Local metadata only; no candidate payload or privacy binding fields."""
        return {"schema": self.schema, "policy_version": self.policy_version,
                "consent_policy_version": self.consent_policy_version,
                "regime": self.regime.value, "care_regime": self.care_regime.value,
                "precaution_upper": self.precaution_upper, "alpha": float(self.alpha),
                "risk_limit": float(self.risk_limit), "alpha_exact": _rational(self.alpha),
                "risk_limit_exact": _rational(self.risk_limit), "selected_id": self.selected_id,
                "safe_null": self.safe_null,
                "selected_performance": None if self.selected_performance is None else float(self.selected_performance),
                "selected_performance_exact": None if self.selected_performance is None else _rational(self.selected_performance),
                "candidates": [row.to_dict() for row in self.candidates]}


class ActionSelector:
    """Own one hysteresis gate; choose at most one identifier without execution."""

    def __init__(self, config: SelectorConfig | None = None,
                 policy_config: PolicyConfig | None = None, verifier: ConsentVerifier | None = None) -> None:
        self.config = SelectorConfig() if config is None else config
        if not isinstance(self.config, SelectorConfig):
            raise ValueError("config must be a SelectorConfig")
        self.config.__post_init__()
        self.policy_config = _policy(PolicyConfig() if policy_config is None else policy_config)
        if verifier is not None and not isinstance(verifier, ConsentVerifier):
            raise ValueError("verifier must be a ConsentVerifier or None")
        self.verifier = verifier
        self.welfare_gate = WelfareGate(self.policy_config.recovery_samples)

    def _privacy_failure(self, requirement: PrivacyRequirement | None, now: int) -> str | None:
        if requirement is None:
            return None
        if self.verifier is None:
            return "PRIVACY_VERIFIER_MISSING"
        try:
            grant = self.verifier.verify(requirement.token, audience=requirement.audience,
                resource_commitment=requirement.resource_commitment, scope=requirement.scope,
                purpose=requirement.purpose, now=now)
            if not isinstance(grant, ConsentGrant):
                return "PRIVACY_GRANT_INVALID"
            if grant.policy_version != self.config.consent_policy_version:
                return "PRIVACY_POLICY_MISMATCH"
        except Exception:
            # Invalid authorization fails closed. Never retain exception text or
            # raw token/bindings in a receipt. Interrupts are not swallowed.
            return "PRIVACY_GRANT_INVALID"
        return None

    @staticmethod
    def _care_failure(candidate: ActionCandidate, regime: Regime) -> str | None:
        if regime is Regime.NO_DATA:
            return "CARE_WELFARE_MISSING"
        if regime is Regime.YELLOW and candidate.kind == "exploration":
            return "CARE_KIND_DENIED"
        if regime in {Regime.ORANGE, Regime.RED} and candidate.kind != "care_support":
            return "CARE_KIND_DENIED"
        limit = {Regime.GREEN: Fraction(1), Regime.YELLOW: Fraction(1, 2),
                 Regime.ORANGE: Fraction(1, 4), Regime.RED: Fraction(1, 10)}[regime]
        if candidate.load > limit:
            return "CARE_LOAD_EXCEEDED"
        if regime is Regime.RED and not candidate.reversible:
            return "CARE_REVERSIBILITY_REQUIRED"
        if regime is Regime.RED and candidate.external_effect:
            return "CARE_EXTERNAL_EFFECT_DENIED"
        return None

    def select(self, candidates: object, precaution: PrecautionAssessment, welfare: WelfareSignals,
               *, capability_level: CapabilityLevel = CapabilityLevel.FULL, now: int) -> SelectionDecision:
        # Complete structural/numerical preflight before the one welfare update.
        if not isinstance(candidates, (tuple, list)) or len(candidates) > _MAX_CANDIDATES:
            raise ValueError("candidates must be a tuple/list with at most128 entries")
        if not isinstance(capability_level, CapabilityLevel):
            raise ValueError("capability_level must be a CapabilityLevel")
        if type(now) is not int or now < 0:
            raise ValueError("now must be a nonnegative integer")
        if not isinstance(self.config, SelectorConfig):
            raise ValueError("config must be a SelectorConfig")
        self.config.__post_init__()
        policy = _policy(self.policy_config)
        if policy.recovery_samples != self.welfare_gate.recovery_samples:
            raise ValueError("changed recovery configuration requires a new selector")
        if self.verifier is not None and not isinstance(self.verifier, ConsentVerifier):
            raise ValueError("verifier must be a ConsentVerifier or None")
        checked: list[ActionCandidate] = []
        for candidate in candidates:
            if not isinstance(candidate, ActionCandidate):
                raise ValueError("every entry must be an ActionCandidate")
            # A fresh frozen snapshot rechecks even an illicitly modified input.
            checked.append(ActionCandidate(candidate.action_id, candidate.performance, candidate.losses,
                candidate.kind, candidate.load, candidate.required_capability, candidate.precondition,
                candidate.hard_safe, candidate.reversible, candidate.external_effect, candidate.privacy))
        if len({candidate.action_id for candidate in checked}) != len(checked):
            raise ValueError("candidate identifiers must be unique")
        upper, score = _score(precaution, welfare, policy)
        confidence = _fraction("alpha", self.config.alpha)
        risk_limit = _unit_fraction("risk_limit", self.config.risk_limit)
        regime = self.welfare_gate.update(raw_regime(score))
        care_regime = (Regime.NO_DATA if score is None else
                       regime if upper >= policy.precaution_on else Regime.GREEN)

        results: list[CandidateResult] = []
        eligible: list[ActionCandidate] = []
        for candidate in checked:
            failure = ("PRECONDITION_FALSE" if not candidate.precondition else
                       "CAPABILITY_UNAVAILABLE" if _CAPABILITY_ORDER[candidate.required_capability] > _CAPABILITY_ORDER[capability_level] else
                       "HARD_SAFETY_FAILED" if not candidate.hard_safe else None)
            if failure:
                results.append(CandidateResult(candidate.action_id, "FEASIBILITY", failure))
                continue
            failure = self._privacy_failure(candidate.privacy, now)
            if failure:
                results.append(CandidateResult(candidate.action_id, "PRIVACY", failure))
                continue
            failure = self._care_failure(candidate, care_regime)
            if failure:
                results.append(CandidateResult(candidate.action_id, "CARE", failure))
                continue
            risk = empirical_cvar(candidate.losses, confidence)
            if risk > risk_limit:
                results.append(CandidateResult(candidate.action_id, "RISK", "CVAR_LIMIT_EXCEEDED", risk))
                continue
            results.append(CandidateResult(candidate.action_id, "ELIGIBLE", "ELIGIBLE", risk))
            eligible.append(candidate)
        selected = min(eligible, key=lambda candidate: (-candidate.performance, candidate.action_id)) if eligible else None
        return SelectionDecision("EUP-SELECTION-RECEIPT/0.1", self.config.policy_version,
            self.config.consent_policy_version, regime, care_regime, upper, confidence, risk_limit,
            None if selected is None else selected.action_id, selected is None,
            None if selected is None else selected.performance, tuple(results))
