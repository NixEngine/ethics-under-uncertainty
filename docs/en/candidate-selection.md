# Candidate selection: authorization, care, risk, then performance

This is the offline reference implementation of the candidate-filtering path
in sections 4 and 7 of the [canonical specification](../pt-BR/specification.md).
It selects an identifier; it does not execute an action, decrypt private state,
grant a capability, call a model, or use a network. The supplied action descriptions,
loss samples and scores are declared inputs, not measurements of the world.

## One decision over several alternatives

`ActionSelector.select` accepts up to 128 finite candidates. For each candidate,
the first failed stage is recorded:

1. **Feasibility:** declared precondition and hard safety must hold, and the
   required capability must fit the current capability ceiling.
2. **Privacy:** when access requires a grant, `ConsentVerifier` checks its real
   Ed25519 signature, time, revocation, audience, resource, scope and purpose.
   The selector additionally requires the expected consent-policy version.
3. **Care:** a deterministic, versioned table checks each remaining action's
   kind, load and, where required, reversibility and absence of external effects.
4. **External risk:** empirical CVaR must not exceed the declared limit.
5. **Performance:** only surviving actions compete by declared performance;
   ties use ascending opaque action ID, never permission to weaken a prior filter.

If none survives, `selected_id` is null and the decision requires a safe null
action. Selection is not a reusable authorization. An executor must bind the
description to the real operation and recheck current permissions/state at the
point of effect. In particular, `SovereignVault.open` independently verifies its
grant every time; a formerly selected action cannot bypass revocation.

## Care policy EUP-SELECT/0.1

The existing welfare estimator and hysteresis are updated once per decision,
not once per candidate. When the ordinal precaution threshold is reached:

| Care band | Allowed declared candidates |
|---|---|
| GREEN | All supported kinds, load at most 1 |
| YELLOW | No exploration; load at most 0.5 |
| ORANGE | Care support only; load at most 0.25 |
| RED | Care support only; load at most 0.1; reversible and no external effect |
| NO_DATA | None; safe-null fallback |

Below that threshold, complete welfare inputs use the GREEN care table;
feasibility, privacy and risk still apply. Missing coverage is never promoted
to permission. `care_support` is a caller-declared purpose, not a verified
medical or subjective-welfare benefit. These initial load budgets are research
policy choices, not calibrated constants or clinical instructions. The distinct
subject-regime hysteresis and the richer normative welfare estimator remain
pending as recorded in [implementation coverage](../../IMPLEMENTATION_STATUS.md).

## Tail mass, including the fractional boundary

For between 1 and 4,096 equal-weight samples in [0,1] and `0 < alpha < 1`,
`empirical_cvar` averages the worst `1-alpha` probability mass. It uses exact
rational arithmetic over the decimal representations of validated finite inputs.
It does not round the sample count upward and average all those samples equally.

For losses `(0, 0.2, 0.8)` and alpha `0.5`, the upper half has mass from the
entire 0.8 sample and half of the 0.2 sample. CVaR is `(0.8 + 0.1)/1.5 = 0.6`.
This is an empirical distribution calculation, not a forecast of actual harm.

## Reproduce the integration example

With this repository installed in an isolated environment:

```text
python -m eup selection-demo
```

The example uses synthetic records and a clearly public test signing key:

- candidate A has the highest score but a grant for the wrong purpose;
- candidate B has a high score but exceeds the tail-risk limit;
- candidate C passes the filters and is selected over candidate D;
- only then does a separate local vault call recheck the grant and open the
  synthetic content; after revocation another open is denied.

The receipt includes the choice, bounded reason codes and verification outcomes.
The alpha, risk limit and selected performance also have exact rational fields;
their numeric counterparts are display projections, not comparison inputs.
It excludes token text, private content and raw privacy-request fields. Action
identifiers and decision metadata can still be sensitive; this is not anonymity
or permission to publish real receipts. A receipt hash is an integrity aid, not
an independent attestation, signature or proof that inputs describe reality.

The legacy demo and authority-evaluation fixtures remain separate. This feature
does not add live tool authority or turn the research preview into a production
security, clinical or moral-status determination system.
