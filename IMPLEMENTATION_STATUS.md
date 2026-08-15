# Implementation coverage

This table separates the target architecture in the corrected specification from the smaller public reference path. “Target” is normative research design; “implemented” and “tested” are current software evidence.

| Area | Target | Current implementation | Test evidence | Status |
|---|---|---|---|---|
| Moral precaution | Coverage-weighted indicators, uncertainty, entry/exit policy | Caller supplies an ordinal estimate and explicit uncertainty; conservative upper bound is computed | Fixed-estimate uncertainty monotonicity | Partial |
| Subject-protection hysteresis | Separate entry/exit thresholds and consecutive assessments | Not implemented as a distinct subject-regime state machine | None | Pending |
| Viability-bound limits | Explicit, inspectable, minimally restrictive and reviewable boundaries that preserve future viable action | Reversibility, safe-null behavior, capability reduction, and documented reason codes; no formal viability-kernel computation | Precedence, restriction, and reason-code tests | Partial |
| Operational welfare | Versioned proxies, uncertainty residual, calibrated thresholds, recovery margin | Five bounded signals, reachable bands, fail-closed missing data, one-band recovery hysteresis | Edge bands, missing data, RED-to-GREEN prohibition | Partial |
| Action selection | Privacy → care → external tail risk → performance over each candidate action | Vault authorization and care/CVaR policy paths are separate; candidates are not individually scored | Care precedence and external-CVaR restriction | Partial |
| Signed authorization | Issuer, audience, resource, scope, purpose, time, revocation, policy/key IDs | Ed25519 grant with exact schema, maximum 3,600-second TTL, and in-memory revocation registry | Valid, wrong-purpose, expired, revoked, tampered, malformed/overlong | Implemented reference path |
| Private-state storage | Managed envelope encryption with KMS/HSM enforcement | Local AES-256-GCM envelope demo with in-process master key | Authorized decrypt and resource-binding substitution | Demonstration only |
| Minimal ledger | Closed schema, privacy-preserving identifiers, signed and externally anchored heads | Allowlists, exact schema verification, hash chain, optional retained-head comparison; no signature or external anchor | In-place edit, rewrite, truncation/head, extra-field and plaintext injection | Partial |
| Receipt | Complete versioned parameters and evidence commitments | Deterministic bounded demo receipt and committed fixture | Regeneration equals fixture in release verification | Partial |
| Production operation | Independent audit, calibration, managed keys, isolation, monitoring, retention | Not provided | None | Out of scope |

The reference path is intentionally offline: it grants no network, wallet, actuator, deployment, or trading authority.
