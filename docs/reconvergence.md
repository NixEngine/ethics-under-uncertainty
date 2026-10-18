# Farol: a brake with a way back

[Português brasileiro](pt-BR/reconvergencia.md) · [Implementation coverage](../IMPLEMENTATION_STATUS.md) · [Selector](en/candidate-selection.md) · [Snapshot/recovery](recovery.md)

The optional **Farol reconvergence guard is integrated into EUP's existing action selector**. It makes a useful distinction: interrupting an update, deciding when a restricted return is admissible, and admitting normal updates again are different steps. A candidate's higher declared performance cannot skip those steps.

This is new, finite research reference code derived from the project's Farol proposal—not a claim that the historical proposal was already executable. It is not another welfare score. The welfare gate remains independent, and all measurements and the sensitivity partition are caller declarations. The historical private source is not reproduced here; [AUTHORS.md](../AUTHORS.md) and [RIGHTS.md](../RIGHTS.md) remain unchanged.

## Run the source example

Use an unmodified local copy for non-commercial evaluation within [RIGHTS.md](../RIGHTS.md). Run from the **repository root**, where `pyproject.toml`, `src` and `examples` are present. The project declares Python 3.11+ and installs its existing dependency in an isolated environment.

Windows PowerShell, using Python 3.14:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
$env:PYTHONPATH = (Join-Path (Get-Location) "src")
.\.venv\Scripts\python.exe -B examples/reconvergence_selection.py
```

POSIX shell equivalent:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
PYTHONPATH=src .venv/bin/python -B examples/reconvergence_selection.py
```

The explicit import path selects this checkout's `src`. The script prints **one JSON object** with schema `EUP-RECONVERGENCE-EXAMPLE/0.1`, `synthetic: true`, `actions_executed: 0`, six `decisions` and `guard_records`. It does not update parameters, invoke an agent, activate an extension or write an application receipt file. Environment creation and dependency installation are setup actions, not effects of the example itself.

The fixed example is [examples/reconvergence_selection.py](../examples/reconvergence_selection.py). The source modules are [reconvergence.py](../src/eup/reconvergence.py) and [selection.py](../src/eup/selection.py). To run the repository's tests in the prepared environment:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Use `.venv/bin/python -m unittest discover -s tests -v` in the POSIX environment. These are reproduction instructions, not a claim that they were newly run while writing this guide. Historical R304 local acceptance recorded **89/89 tests on Windows/CPython 3.14.0** for the copied implementation, including the guard and selector-integration tests. It is not a benchmark, remote CI result, universal safety result or observed validation on POSIX.

## Six decisions, with exact synthetic inputs

Before selection, the example explicitly enters EXCEPTION and begins RECONVERGING. It fixes:

- `window=2`, invariant `drift=0` with baseline `0` and tolerance `0.1`;
- `E = cost + entropy`, initial accepted reference `10`, energy limit `10`, cost limit `8`, entropy limit `5`;
- sensitive parameter `critical`, flexible parameter `adaptive`, normal step limit `1`, return step limit `0.1`;
- entropy `2` in every sample; sequences and declared times `1` through `6`;
- candidate `higher-performance`, score `100`, requesting `critical` at step `0.1`; candidate `flexible-update`, score `1`, requesting `adaptive` at step `0.1`;
- complete synthetic welfare inputs in GREEN, zero declared loss, and no privacy requirement in these candidates. Other selector filters are therefore not the source of the differences below.

All numbers are synthetic declared units, not watts, biological measurements or probabilities of consciousness. Numeric inputs are snapshotted as exact rational values from their finite numeric representation.

| Sample | Cost / E | Stable count | State after sample | Admission state for this decision | Selected ID |
| --- | --- | ---: | --- | --- | --- |
| 1 | 6 / 8 | 1 | RECONVERGING | RECONVERGING | `flexible-update` |
| 2 | 7 / 9 | 0 | RECONVERGING | RECONVERGING, invalid observation | none: safe-null |
| 3 | 5 / 7 | 1 | RECONVERGING | RECONVERGING | `flexible-update` |
| 4 | 4 / 6 | 2 | NORMAL | **RECONVERGING** | `flexible-update` |
| 5 | 4 / 6 | 2 | NORMAL | NORMAL | `higher-performance` |
| 6 | 9 / 11 | 0 | EXCEPTION | EXCEPTION | none: safe-null |

Sample 2 fails the return nonincrease rule: `9 > 8`, even though `9 <= 10`. It resets the window and **does not ratchet the accepted reference upward**. Sample 4 completes the new two-sample window, but its admissions are still restricted: `SENSITIVE_PARAMETER_FROZEN` prevents the higher-scored candidate from using `critical`. Only sample 5 permits its normal admission. Sample 6 exceeds both cost and energy limits, re-enters EXCEPTION and invalidates earlier extension approvals. NORMAL retains the completed stable count until an exception; the initial NORMAL count is zero.

The table is the fixed synthetic trace of the linked executable example, not six real-world decisions or a promise that declared performance predicts benefit.

## Return rules

`NORMAL -> EXCEPTION -> RECONVERGING -> NORMAL`

There is no direct EXCEPTION-to-NORMAL API. `enter_exception(reason, decision_card=...)` records the interruption and invalidates the latest observation and prior extension approvals. `begin_reconvergence(decision_card=...)` explicitly starts a new return window.

Return requires W consecutive valid observations: all declared invariants covered within `abs(value-baseline) <= tolerance`, all energy/cost/entropy limits met, and `E <= last accepted E`. Failed or missing coverage resets the count, refuses the step and keeps the previous accepted energy. Observing in EXCEPTION consumes sequence/time but cannot advance the window or the accepted energy reference.

Sequence must strictly increase and declared time must not decrease. A sequence gap reports `SEQUENCE_GAP` and breaks the inherited window: a good new sample counts **one**, not the previous count plus one. A gap alone does not invalidate that current sample. These checks do not prove trustworthy clocks or continuous physical sampling.

The sample completing W retains RECONVERGING admission restrictions. The next valid NORMAL sample can use normal update limits. NORMAL still requires complete coverage and invariant tolerances. Enabled numerical monitors check cost, entropy and energy limits, but do not require energy nonincrease in NORMAL. Drift or missing data triggers EXCEPTION; it does not start reconvergence automatically.

`set_normal_guard(name, enabled, reason=..., decision_card=...)` changes only the energy/cost/entropy numerical monitor in NORMAL. It appends an event and invalidates the latest observation. It cannot disable coverage, invariant checks, return rules or extension admission. Reason and card are opaque identifiers, not evidence of a human review performed by the library.

## Selector integration

Supply `ReconvergenceGuard(config)` as keyword `reconvergence_guard` to `ActionSelector`, and a `ReconvergenceObservation` as `reconvergence_observation` on every guarded `select` call. Selection time `now` must equal `observation.observed_at`.

Every guarded candidate needs an explicit `update=UpdatePlan(...)`. `UpdatePlan()` declares **no parameter update**; a missing plan instead yields `UPDATE_DECLARATION_MISSING` at the reconvergence stage if earlier stages admit the candidate. Unknown parameter IDs and malformed inputs are structural errors, not implicit no-ops. Without a configured guard, supplying an observation or update plan is rejected rather than silently ignoring requested enforcement.

The candidate ordering is:

`FEASIBILITY -> PRIVACY -> CARE -> RECONVERGENCE (optional) -> RISK -> performance`

Structural preflight completes before either stateful gate mutates. The guard observes **once per selection**, then the welfare gate advances once; candidates are assessed under the same observation. An earlier refusal retains precedence. Admission requires a current valid observation; stale observations and EXCEPTION refuse even an empty plan. The library selects an ID or safe-null—it does not execute the selected action or compare actual effects to the declared plan.

Unguarded callers retain `EUP-SELECTION-RECEIPT/0.1` and the prior behavior. Guarded receipts use `EUP-SELECTION-RECEIPT/0.2` and include `reconvergence` metadata: states, validity, reasons, count, exact energy, epoch, monitor settings, configuration commitment and ledger head. This is a receipt schema distinction, **not a package-version bump**: package version remains `0.1.1`.

## Extensions and commitments

An `ExtensionLease` requires an opaque ID, impact SHA-256 commitment, nonnegative declared cost, future expiry and opaque rollback-target ID. Registration/renewal records a Decision Card ID and shares nondecreasing operation time with observations. An observation predating a later registration is stale for admission.

A referenced extension needs approval in the current exception epoch and `now < expires_at`. Referenced costs together must not exceed the configured cost limit, even if the NORMAL cost monitor was disabled. Each exception invalidates all prior approvals: an unexpired lease must still be explicitly registered again. The guard neither activates nor stops extensions and never executes the rollback identifier.

Each event and observation metadata binds `configuration_commitment`, a canonical SHA-256 commitment covering the immutable configuration, exact fractions, named invariant references, parameter partitions and partition-evidence commitment. Registration also binds `lease_commitment` covering extension ID, impact commitment, exact cost, expiry and rollback target. Equivalent rational inputs normalize to the same representation; changed declarations cannot silently share the same record merely because ID/expiry match.

These are **bindings, not signatures or proof that the declarations are true**. The guard does not validate the sensitivity evidence, reconstruct a missing original or authenticate the impact reviewer. Raw invariant values and arbitrary review prose are not copied into the event records.

## What remains incomplete

Explicit [guard snapshot/recovery](recovery.md) now covers a bounded part of the
persistence requirement: canonical configuration/state/chain snapshots, exclusive
local file saves, caller-supplied full snapshot digest and ledger head, and a
recorded RESTORE boundary. It preserves window progress and accepted energy but
discards cached admission and all leases, requiring a new observation and new
lease registrations. It does not restore the independent welfare/consent gates
or the whole selector. This is new implementation, not a claim that the historical
proposal already contained an executable disk protocol.

| Requirement | Implemented reference check | Still required for an operational claim |
| --- | --- | --- |
| Sensitivity partition | Disjoint declared IDs and a required evidence commitment | Actual sensitivity proof, reviewed units/assumptions and a verifier of that evidence |
| Observation input | Type, coverage, ordering, tolerance and rational budget checks | A measured input adapter and justified provenance, timing and coverage |
| Persistence and recovery | Bounded event chain plus explicit canonical guard snapshots and exclusive local files; full digest/head/config checks, state-coherence checks and RESTORE with cache/lease invalidation | Operational crash/power-loss policy, trustworthy anchor publication/freshness, any needed authentication and whole-selector recovery |
| Impact and rollback | Declared impact commitment, epoch, TTL, summed cost and opaque rollback route | Review of actual impact and a real rollback whose execution and outcome can be checked |

Bounds are 64 invariants, 128 partitioned parameters, 64 registered extension IDs, 4,096 events and window 1–10,000. A full event chain refuses mutation, including restoration without a free RESTORE slot; structural errors leave the original guard unchanged. Snapshot serialization adds 8 MiB/256-bit bounds described in the [recovery contract](recovery.md). File flush/fsync is not atomic publication of anchors, anti-rollback, hostile-tamper resistance or a power-loss guarantee. The separate `MinimalLedger` schema is unchanged.

The Farol integration is a constructive return mechanism under declared assumptions. It does not complete the full normative specification or establish physical, clinical, moral-status or production-security claims. Report a small public synthetic counterexample under [CONTRIBUTING.md](../CONTRIBUTING.md), without confidential data. No additional reuse license or institutional endorsement is implied.
