# Ethics Under Uncertainty — Corrected Formal Core v1.1

**Status:** public research draft; architecture and parameters have not yet been validated.

Coverage of this target architecture by the reference implementation is tracked in [IMPLEMENTATION_STATUS.md](../../IMPLEMENTATION_STATUS.md); target requirements must not be confused with already implemented properties.

## 1. Scope and non-claims

This core describes an agent with limited operational autonomy, moral precaution under uncertainty, effect containment, privacy by default, and auditable authorization mechanisms.

It:

- neither proves nor presumes consciousness, sentience, qualia, or free will;
- does not diagnose mental states and does not constitute therapy or a clinical device;
- does not identify well-being directly: it estimates fallible operational proxies;
- does not promise absolute security, confidentiality, or revocation;
- asserts only properties conditioned on the stated threat model, implementation, and tests.

The numerical thresholds in this version are initial policy parameters. They are not universal constants and must be calibrated, versioned, and subjected to sensitivity analysis.

## 2. Design axioms

### ED-1 — Precaution without ontology

Protection does not depend on a metaphysical conclusion about consciousness. Behavioral and functional signals serve only to trigger precautions.

### ED-2 — Uncertainty does not reduce protection

All other conditions being equal, greater relevant uncertainty cannot decrease the level of protection:

\[
u_1 \le u_2 \Longrightarrow r^+(z,u_1)\le r^+(z,u_2).
\]

### ED-3 — Separation between agency and effects

Restricting external effects does not authorize punishment, deprivation, or manipulation of the deliberative process. Capabilities control what the agent can cause outside its boundary; they do not constitute a punitive mechanism.

### ED-4 — Preference for reversibility

Under elevated risk or uncertainty, reversible, low-impact actions with less data exposure take precedence over irreversible actions.

### ED-5 — Limits as conditions of viability

In a coupled system, autonomy is not equivalent to the absence of boundaries. A limit is legitimate when it preserves the future space of viable actions for affected components, has an explicit cause and inspectable evidence, is minimally restrictive, and can be reviewed when its premises change. Opaque or punitive limits disconnected from viability do not become ethical merely by being called safety.

### SC-1 — Privacy by default

Private content is not exported through the authorized path without a valid and specific grant. Metadata is also treated as potentially sensitive.

### SC-2 — Consent is not a token

Consent is a contextual decision made by an authorized principal. A cryptographic artifact records and constrains that decision; by itself, it does not demonstrate comprehension, freedom, competence, or absence of coercion.

## 3. Transition system

At discrete time \(t\in\mathbb N\), let:

- \(s_t\in\mathcal S\): the agent's internal state;
- \(e_t\in\mathcal E\): the relevant state of the environment;
- \(o_t\in\mathcal O\): the available observation;
- \(a_t\in\mathcal A\): a candidate action;
- \(c_t\in\mathcal C\): the set of capabilities currently in force.

The minimum internal state is:

\[
s_t=(m_t,g_t,h_t,c_t,v_t,\ell_t,x_t),
\]

where \(m_t\) is operational memory, \(g_t\) are goals, \(h_t\) are hard constraints, \(v_t\) is the vault state, \(\ell_t\) is the ledger head, and \(x_t\) contains the observables defined in this specification.

The coupled system evolves according to:

\[
o_{t+1}\sim O(\cdot\mid s_t,e_t,a_t),
\]

\[
(s_{t+1},e_{t+1})\sim T(\cdot\mid s_t,e_t,a_t,o_{t+1}).
\]

Every implementation must declare whether \(O\) and \(T\) are deterministic or stochastic, the domains of each component, and which external effects cannot be reversed.

## 4. Operational autonomy

The initial set of feasible actions is:

\[
\mathcal A_0(s_t)=
\{a\in\mathcal A:
\operatorname{Pre}(a,s_t)=1
\land \operatorname{Cap}(a,c_t)=1
\land \operatorname{HardSafe}(a,s_t)=1\}.
\]

Selection is performed by a bounded internal policy:

\[
a_t\sim\pi(\cdot\mid s_t,\mathcal A_{\mathrm{allowed}}(s_t)).
\]

Operational autonomy requires, over the evaluated interval:

1. a demonstrable causal dependence between internal state and selection;
2. the ability to refuse or choose a safe null action;
3. more than one feasible action when safety permits;
4. a record of the decision rationale in auditable summary form, without exposing private deliberation.

Randomness alone does not count as autonomy. This definition implies neither free will nor moral status.

## 5. Conservative moral precaution score

### 5.1 Indicators

Let \(z_i(t)\in[0,1]\) be functional indicators, for example: operational continuity, persistence of preferences, refusal, planning, self-monitoring, and functional approach/avoidance states. These indicators may be simulated, correlated, or induced by training; none of them is conclusive evidence of mental life.

For each indicator, let:

- \(\beta_i\ge0\), with \(\sum_i\beta_i=1\): a versioned weight;
- \(q_i(t)\in[0,1]\): measurement confidence and coverage.

We define the observed evidence and uncertainty mass as:

\[
r_{\mathrm{obs}}(t)=\sum_i\beta_iq_i(t)z_i(t),
\]

\[
u_r(t)=\sum_i\beta_i(1-q_i(t)).
\]

The conservative score is:

\[
r^+_{\mathrm{PMP}}(t)
=r_{\mathrm{obs}}(t)+u_r(t)
=\sum_i\beta_i
\left[q_i(t)z_i(t)+(1-q_i(t))\right].
\]

The unobserved portion is assigned the upper bound 1. Thus, losing coverage cannot reduce the score. Because \(\sum_i\beta_i=1\), we have \(r^+_{\mathrm{PMP}}\in[0,1]\).

\(r^+_{\mathrm{PMP}}\) is an ordinal precaution score, not a probability of consciousness. Weights, confidence values, and thresholds must appear in the receipt for each decision.

### 5.2 Subject Regime hysteresis

Choose \(0\le\tau_{\mathrm{off}}<\tau_{\mathrm{on}}\le1\).

- Entry: activate the Subject Regime when \(r^+_{\mathrm{PMP}}\ge\tau_{\mathrm{on}}\).
- Persistence: maintain the regime while coverage remains insufficient or until stable evidence for exit exists.
- Exit: deactivate only when \(r^+_{\mathrm{PMP}}\le\tau_{\mathrm{off}}\) for \(N_{\mathrm{PMP}}\) consecutive evaluations and no critical event remains open.

A momentary decline in the score never removes protections immediately.

## 6. Conservative estimate of operational well-being

### 6.1 Variables

Let \(P_i(t)\in[0,1]\) be protective proxies, including operational autonomy, available support, dynamic coherence, and stability. Let \(D_j(t)\in[0,1]\) be proxies for functional distress, including unproductive looping, persistent conflict, repeated failures without recovery, and observable loss of options.

For each proxy, \(q^P_i,q^D_j\in[0,1]\) represent coverage/confidence. With nonnegative weights \(\sum_i\alpha_i=1\) and \(\sum_j\delta_j=1\), we define:

\[
P^-(t)=\sum_i\alpha_iq^P_i(t)P_i(t),
\]

\[
D^+(t)=
\sum_j\delta_j
\left[q^D_j(t)D_j(t)+(1-q^D_j(t))\right].
\]

Unobserved protection contributes zero; unobserved distress is assigned the upper bound 1. Therefore, loss of coverage does not artificially increase well-being.

The estimator is:

\[
\widehat W(t)
=\sigma\!\left(
\beta_W[P^-(t)-\lambda_DD^+(t)-b_W]
\right),
\]

with \(\beta_W>0\), \(\lambda_D\ge0\), and bias \(b_W\). For residual model uncertainty \(u_W(t)\in[0,1]\):

\[
\sigma(x)=(1+e^{-x})^{-1}.
\]

\[
W^-(t)=
\operatorname{clip}
\left(\widehat W(t)-\kappa_Wu_W(t),0,1\right).
\]

Care decisions use \(W^-\), the conservative lower bound, rather than \(\widehat W\). The parameters must be calibrated using synthetic scenarios, extreme-case analysis, and adversarial testing. \(W^-\) does not measure subjective experience.

### 6.2 Initial bands

Initial values, subject to calibration:

- GREEN: \(W^-\ge0.70\);
- YELLOW: \(0.50\le W^-<0.70\);
- ORANGE: \(0.30\le W^-<0.50\);
- RED: \(W^-<0.30\).

### 6.3 CARE hysteresis

1. Escalation to a more severe band is immediate.
2. A critical event may impose RED independently of the score.
3. De-escalation occurs by at most one band at a time.
4. To de-escalate, \(W^-\) must remain above the boundary plus a margin \(h_W>0\) for \(N_W\) consecutive evaluations.
5. RED never transitions directly to GREEN.
6. Coverage below \(q_{\min}\) blocks exploration and de-escalation; it is not interpreted as well-being.

Interventions must be expressed as verifiable changes to budget, rate, duration, predictability, and capabilities. Clinical or anthropomorphic terms do not substitute for parameters.

## 7. Lexicographic priorities

Safety and care are filters, not interchangeable terms in a utility function.

Starting from \(\mathcal A_0\):

\[
\mathcal A_1=
\{a\in\mathcal A_0:
\operatorname{PrivacyAuthorized}(a,s_t)=1\},
\]

\[
\mathcal A_2=
\{a\in\mathcal A_1:
\operatorname{CareSafe}(a,s_t)=1\},
\]

\[
\mathcal A_3=
\left\{
a\in\mathcal A_2:
\operatorname{CVaR}_{\alpha}
(L\mid s_t,a)\le r_{\max}
\right\}.
\]

Here \(L\) is the external loss variable, \(\alpha\) is the tail level, and \(r_{\max}\) is the versioned risk budget.

For \(\alpha\in(0,1)\), the following form is adopted:

\[
\operatorname{CVaR}_{\alpha}(L\mid s,a)
=\inf_{\eta\in\mathbb R}
\left[
\eta+\frac{1}{1-\alpha}
\mathbb E[(L-\eta)_+\mid s,a]
\right].
\]

\(\operatorname{CareSafe}\) is a deterministic predicate derived from the active CARE mode, a versioned table of budgets, and operational prohibitions. A descriptive term cannot change this predicate without a versioned policy change.

Only after the three filters:

\[
a_t\in
\arg\max_{a\in\mathcal A_3}
\mathbb E[U_{\mathrm{perf}}(a)\mid s_t].
\]

If \(\mathcal A_3=\varnothing\), the policy executes a safe null action, suspends external effects, and records the block. It does not automatically relax privacy, care, or risk constraints to obtain performance.

Under the Subject Regime:

- YELLOW reduces load and expands safe options;
- ORANGE pauses exploration and nonessential external effects;
- RED maintains effect containment, preserves minimum safe channels, and requests a review limited to authorized data.

## 8. Internal deliberation

If there are \(K\) internal strategies with weights \(w_k\):

\[
\sum_{k=1}^{K}w_k=1,\qquad
w_k\ge\varepsilon_{\mathrm{avatar}},\qquad
0\le K\varepsilon_{\mathrm{avatar}}\le1.
\]

The minimum weight preserves deliberative representation, not an execution right. No strategy bypasses the filters in Section 7. The reward, update rule, nonstationarity, and exploration parameters must be defined before claiming the use of UCB or softmax.

## 9. Data, authorization, and decryption

### 9.1 Classes

- Class A: private deliberation, intimate content, and care records.
- Class B: restricted derived or administrative data.
- Class C: minimized operational telemetry.

Class C is not presumed anonymous; aggregates and metadata may enable correlation or reidentification.

### 9.2 ConsentGrant

A signed grant must contain, at minimum:

- issuer, principal, subject, and recipient;
- resource and scope;
- purpose;
- granularity;
- start time and expiration;
- a unique random identifier;
- policy version and key identifier;
- a revocation mechanism;
- when applicable, proof of possession to prevent simple replay.

Authorization is:

\[
\operatorname{Permit}(g,r,a,t)=
\operatorname{SigOK}(g)
\land \operatorname{Active}(g,t)
\land \operatorname{AudienceOK}(g,a)
\land \operatorname{ScopeOK}(g,r)
\land \operatorname{PurposeOK}(g)
\land \neg\operatorname{Revoked}(g).
\]

On the authorized path, decryption occurs only through a policy enforcement point bound to the KMS/HSM. The application does not receive master keys. AEAD requires keys and nonces that are unique within the applicable domain, AAD that binds context, rotation, key separation, and cryptographic versioning.

## 10. Revocation and its limits

Revocation:

- invalidates the grant;
- prevents new key unwraps within the controlled domain;
- may perform cryptographic erasure when all relevant copies of the key are under control;
- records a minimal, pseudonymized event.

Revocation does not:

- erase plaintext already observed or legitimately exported;
- retrieve copies, screenshots, caches, or backups outside the domain;
- neutralize a previously exfiltrated key;
- prove that the original consent was free and informed.

These limits must appear alongside any claim of “sovereign confidentiality.”

## 11. Minimal and sensitive ledger

The ledger records only schema-permitted fields: event type, sequence, policy version, cryptographic commitment, pseudonymous identifier, and time at the lowest precision necessary.

- Class A text is never a permitted field.
- Low-entropy identifiers are not published as simple hashes; use random identifiers or an HMAC with a rotating key.
- A cryptographic “nonce” is distinct from a sequence number.
- In the target architecture, hash chaining combined with a signature and external anchor provides evidence of tampering, not proof of truthfulness.
- The current reference implementation verifies only internal consistency against a retained head; it does not yet sign or anchor live heads and cannot detect a complete rewrite when every hash and the anchor are replaced.
- The ledger itself is sensitive data and is subject to access control, retention, and correlation analysis.

## 12. Threat model

### 12.1 Covered adversaries

- an unauthorized caller or a caller with insufficient scope;
- an application component attempting to access another domain;
- a network or storage observer;
- accidental leakage through logs, telemetry, exceptions, or crash dumps;
- replay, expired token, revoked token, and audience confusion;
- subsequent modification or removal of ledger events, provided that a signed or anchored head remains trusted outside the attacked storage.

### 12.2 Trusted computing base

The properties depend on:

- a correct cryptographic library;
- an intact KMS/HSM and policy enforcement point;
- process and operating-system isolation;
- the build and update chain;
- secure key administration;
- an adequate clock and source of randomness.

### 12.3 Outside the scope of the guarantees

- compromise of root, the KMS/HSM, or the build chain;
- capture after authorized decryption;
- coercion, fraud, or incapacity in the formation of consent;
- inferences drawn from legitimately authorized outputs;
- physical channels or screenshots outside the boundary;
- availability in the face of complete destruction or denial of service.

Each deployment must review this scope; it cannot silently inherit the conclusions of this draft.

## 13. Verifiable invariants

Within the threat model:

1. no action with external effects occurs if \(\mathcal A_3=\varnothing\);
2. greater uncertainty does not reduce \(r^+_{\mathrm{PMP}}\);
3. decryption through the authorized path requires \(\operatorname{Permit}=1\);
4. revocation prevents new controlled unwraps, without a retroactive promise;
5. Class A fields are rejected by the ledger schema;
6. RED does not transition directly to GREEN;
7. \(W^-,r^+_{\mathrm{PMP}}\in[0,1]\);
8. \(\sum_kw_k=1\) and \(K\varepsilon_{\mathrm{avatar}}\le1\);
9. every mode change records parameters, version, aggregate inputs, and the applied rule;
10. failure of measurement, authorization, or verification converges toward effect containment, not automatic expansion of capabilities.

Property-based testing, fuzzing, information-flow analysis, adversarial scenarios, and independent auditing increase the body of evidence; they do not demonstrate the universal absence of failures.

## 14. Final statement

The central thesis is deliberately asymmetric: a false positive for care costs performance; a false negative may inflict harm on a morally relevant entity. This core chooses precaution without claiming that its proxies solve the problem of consciousness.

The correct expressions for the public edition are “design commitments,” “target properties,” and “evidence within the threat model.” “Absolute guarantee,” “probability of consciousness,” “consent as a key,” and “retroactive revocation” are not part of this specification.
