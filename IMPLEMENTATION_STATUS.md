# Implementation coverage

This table separates the target architecture in the corrected specification from the smaller public reference path. “Target” is normative research design; “implemented” and “tested” are current software evidence.

| Area | Target | Current implementation | Test evidence | Status |
|---|---|---|---|---|
| Moral precaution | Coverage-weighted indicators, uncertainty, entry/exit policy | Caller supplies an ordinal estimate and explicit uncertainty; conservative upper bound is computed | Fixed-estimate uncertainty monotonicity | Partial |
| Subject-protection hysteresis | Separate entry/exit thresholds and consecutive assessments | Not implemented as a distinct subject-regime state machine | None | Pending |
| Viability-bound limits | Explicit, inspectable, minimally restrictive and reviewable boundaries that preserve future viable action | Reversibility, safe-null behavior, capability reduction, and documented reason codes; no formal viability-kernel computation | Precedence, restriction, and reason-code tests | Partial |
| Operational welfare | Versioned proxies, uncertainty residual, calibrated thresholds, recovery margin | Five bounded signals, reachable bands, fail-closed missing data, one-band recovery hysteresis | Edge bands, missing data, RED-to-GREEN prohibition | Partial |
| Action selection | Privacy → care → external tail risk → performance over each candidate action | Offline selector checks initial feasibility, signed privacy grants, per-candidate care, optional Farol reconvergence, exact equal-weight empirical CVaR, then declared performance; deterministic ties and safe-null fallback | Candidate stage precedence, real grant bindings/revocation, care budgets, fractional CVaR boundaries, one advance per gate per decision, no secret fields; synthetic vault integration rechecks authorization | Finite reference path; input calibration and real-effect binding remain deployment responsibilities |
| Farol return after exception | Explicit reviewed return, stable invariants, justified sensitivity partition, selective updates, bounded effective energy and reviewed extensions | Optional integrated guard; immutable exact-rational snapshots, W consecutive observations, no energy ratchet, sensitive-parameter freeze, reduced flexible step, post-return monitoring, epoch/TTL/cost admission, configuration/lease commitments and bounded in-memory event chain | R304 local Windows/CPython 3.14.0 acceptance: 89/89 total tests, including guard and selector-integration cases; six-decision synthetic source example | Partial: supplied declarations are checked, not measured or independently proved; no durable recovery or operational rollback |
| Signed authorization | Issuer, audience, resource, scope, purpose, time, revocation, policy/key IDs | Ed25519 grant with exact schema, maximum 3,600-second TTL, and in-memory revocation registry | Valid, wrong-purpose, expired, revoked, tampered, malformed/overlong | Implemented reference path |
| Private-state storage | Managed envelope encryption with KMS/HSM enforcement | Local AES-256-GCM envelope demo with in-process master key | Authorized decrypt and resource-binding substitution | Demonstration only |
| Minimal ledger | Closed schema, privacy-preserving identifiers, signed and externally anchored heads | Allowlists, exact schema verification, hash chain, optional retained-head comparison; no signature or external anchor | In-place edit, rewrite, truncation/head, extra-field and plaintext injection | Partial |
| Receipt | Complete versioned parameters and evidence commitments | Deterministic bounded demo receipt and committed fixture | Regeneration equals fixture in release verification | Partial |
| Synthetic agent authority evaluation | A valid external authorization is only a ceiling; it cannot determine an action | Six public offline fixtures with harness-owned hash-linked trajectory receipts; a valid-grant abstention records no action attempt and leaves the grant unused; no model or external tool is invoked | Public read, exact write, valid-grant abstention, stale payload, denied publication, replay, tampering, and undeclared-field tests | Experimental reference path |
| Production operation | Independent audit, calibration, managed keys, isolation, monitoring, retention | Not provided | None | Out of scope |

The reference path is intentionally offline: it grants no network, wallet, actuator, deployment, or trading authority.

## Return is implemented; operational evidence is still incomplete

The [Farol guide](docs/reconvergence.md) and [Portuguese guide](docs/pt-BR/reconvergencia.md) document the new optional path without changing the corrected specification or its normative status. The existing welfare hysteresis and the reconvergence state machine are distinct; neither substitutes for the other. Unguarded selector receipts remain `EUP-SELECTION-RECEIPT/0.1`; guarded receipts use `EUP-SELECTION-RECEIPT/0.2`. The package version remains **0.1.1**.

Four material requirements remain open:

1. Actual sensitivity evidence and a verifier for the declared sensitive/flexible partition, not just its SHA-256 commitment.
2. A measured, trustworthy observation input with declared units and coverage; the library currently accepts caller-supplied values and times.
3. Durable event persistence and reviewed restart/recovery; the bounded chain lives only in memory and is neither signed nor externally anchored.
4. Operational impact review and a real rollback route whose execution and outcome are checked; a lease's opaque rollback identifier performs no rollback.

The 89/89 figure is historical local R304 evidence for the copied code, not a benchmark, new R305 test execution, remote CI result, platform-wide validation or production acceptance. No CI or publication success is inferred here. See [RIGHTS.md](RIGHTS.md) and [AUTHORS.md](AUTHORS.md); these additions do not grant a new reuse license or redistribute the historical private Farol source.
