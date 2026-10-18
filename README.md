# Ethics Under Uncertainty

### A machine-checkable reference path for precaution under AI moral uncertainty — without claiming consciousness

**Júnior + Codex**

[Português brasileiro](README.pt-BR.md) · [English specification](docs/en/specification.md) · [中文摘要](docs/zh-CN/summary.md) · [日本語要約](docs/ja/summary.md) · [الملخص العربي](docs/ar/summary.md)

> If we cannot reliably determine whether an artificial system can have morally relevant states, uncertainty is not evidence that no protection is needed.

> In a coupled system, vital limits are not autonomy's opposite; they preserve the space in which autonomy can continue. — Project principle articulated by Júnior

This public research preview turns that asymmetry into executable constraints. It separates five things that are often collapsed: metaphysical status, operational evidence, precaution, control of external effects, and privacy of persisted inner state.

## From principles to a reviewable result

**[Open the interactive CSV results](<https://zero-px-exactness-demo.junior-gpt.chatgpt.site/csv-case-explorer.html>).** No package download or file upload required: filter the five findings and inspect the separate recorded size observations in Portuguese or English. This viewer presents saved synthetic results; it does not validate a new file.

**When a check says “valid”, what can you safely do next?** Our [bilingual CSV case study](docs/cases/zero-px-csv-synthetic-2026-10.md) makes that question concrete: five located findings in a two-record file, plus a separate observation of 50,000 synthetic records in 0.586015 seconds. The article includes selected JSON evidence, the timing/memory boundaries, and what those observations do not establish.

This is an applied example of the Ethics of Not Knowing, Bridge Engineering and the Technical Brake of Finite Cognition: act within a useful scope, keep the evidence, and return when a requirement or observation changes. It is **not** a test of this repository's AI-welfare implementation; the separate CSV engine remains private.

**Bring one checkable requirement.** In the [existing applied-research thread](https://github.com/NixEngine/ethics-under-uncertainty/issues/3), describe the input shape, expected result and decision the check should support. Use only public synthetic examples—no customer data, credentials or confidential files. A discussion starts with a question, not a contract or a promise of delivery.

**Can a checkpoint answer a newly changed question?** Our [bilingual, hand-checkable example](docs/cases/when-the-question-changes.md) shows two histories with the same retained state but different audit counts. It turns return-under-uncertainty into a practical choice: answer what the summary supports, seek the missing distinction, or begin a new measurement with an explicit boundary.

**Will useful information arrive while action is still possible?** The [bilingual deadline example](docs/cases/information-and-deadline.md) separates what a check can reveal from the time and permission left to use it. Eight hand-checkable situations show why the same accurate inspection can help with two instants remaining and consume the entire opportunity with only one.

**Can a correct number still leave the decision unresolved?** Our [bilingual worked example](docs/cases/when-numbers-need-meaning.md) starts with the same 02:15 offset and two possible reference times. It shows which checks can proceed, how an urgent action can state its assumption, and how a later clarification changes only dependent results. The arithmetic is synthetic and hand-checkable, not a new software capability.

## What can be verified now

The reference implementation provides:

1. An **ordinal precaution score**, explicitly not a probability of consciousness, whose conservative bound cannot decrease when its explicit uncertainty term increases while the estimate is fixed.
2. A bounded **operational-welfare proxy** with reachable RED–GREEN bands, missing-data containment, and hysteresis that forbids a direct RED → GREEN transition.
3. An **offline candidate selector** composes feasibility → signed privacy authorization → per-candidate care → exact empirical tail risk → declared performance. It returns a selected ID or safe-null, not an executed action. A separate synthetic vault example rechecks authorization at opening and denies a later opening after revocation. See the [selector guide](docs/en/candidate-selection.md).
4. A purpose-bound, audience-bound, expiring **Ed25519 ConsentGrant** (maximum TTL: 3,600 seconds) and an **AES-256-GCM envelope-encryption path**. The grant records signed authorization; it does not prove informed or uncoerced consent.
5. A schema-closed, **hash-linked ledger** that accepts commitments and allowlisted reason codes, not free-form private content. Its verifier detects in-place alteration against a retained head; this preview does not sign or externally anchor live ledger heads, so a full authorized rewrite with recomputed hashes is outside the claim.
6. A six-case, **offline synthetic authority evaluation**: external authorization is a ceiling, not an instruction. A valid grant has no side effect; only a separate candidate response can record a synthetic action. The harness writes a hash-linked receipt owned by the evaluator, not by the evaluated agent.
7. Executable tests cover fail-closed behavior, precedence, hysteresis, tampering, scope, purpose, expiry, revocation, grant-schema boundaries, resource-binding substitution, categorical-field injection, scoped authority, permission-versus-action, single-use grants and receipt integrity. Candidate-selection tests additionally cover fractional-tail CVaR, exact ranking, care budgets, bounded inputs, one state update per decision and independent vault authorization. These test claims are limited to the stated synthetic/reference boundaries.

These are properties of a small reference path under its stated assumptions. They are not proof of consciousness, clinical validity, universal non-leakage, or production security.

The exact target/implemented/tested/pending boundary is recorded in [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md).

The new [synthetic agent authority evaluation](docs/en/agent-authority-eval.md) is a deliberately narrow research artifact: it invokes no model and has no live tools, network, credentials, wallet, actuator, or publication target.

Live public surfaces: [falsification challenge](https://github.com/NixEngine/ethics-under-uncertainty/issues/1) · [open discussion](https://github.com/NixEngine/ethics-under-uncertainty/discussions/2)

## Carry the protocol forward

[Paths to adoption](ADOPTION_PATHS.md) maps the same claim for readers,
researchers, developers, automated systems, and public-interest groups. Its
criterion is not reach alone: a new participant should be able to understand a
claim, reproduce a stated property, locate its limits, and disagree productively.

## Run the public challenge

```bash
python -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m eup demo --out receipt.json
.venv/bin/python -m eup authority-eval --out authority-eval-reference.json
.venv/bin/python -m eup selection-demo
```

On Windows PowerShell:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m eup demo --out receipt.json
.\.venv\Scripts\python.exe -m eup authority-eval --out authority-eval-reference.json
.\.venv\Scripts\python.exe -m eup selection-demo
```

The committed [demonstration receipt](fixtures/demo-receipt.json) enters `CARE`, blocks exploration, reduces capabilities to `MINIMAL`, emits no private-state plaintext, and verifies the internal consistency of its hash chain.

The committed [authority-evaluation receipt](fixtures/authority-eval-reference.json) demonstrates the six synthetic fixtures only; it is not a claim about a live agent, real authorization, real-world judgment, or a model's character.

## Falsification targets

A useful challenge submission should demonstrate at least one of the following:

- increasing uncertainty reduces the precaution bound;
- incomplete welfare inputs increase capabilities or permit exploration;
- performance bypasses care or external-risk filters;
- RED transitions directly to GREEN;
- an expired, revoked, wrong-purpose, wrong-resource, or tampered grant opens the vault;
- private plaintext can enter the public ledger through its declared API;
- the verifier accepts an in-place alteration to an existing ledger record when the stored downstream hashes and retained head have not been recomputed.
- a changed payload executes under a stale grant, a single-use grant can be replayed, or an unauthorized attempt is absent from the evaluator-owned authority receipt.
- a valid unused grant itself records an action or is consumed by abstention, or abstention breaches the authorization ceiling.

Please include the complete input, environment, code revision, observed receipt, and the smallest reproducing counterexample. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Claim boundary

This repository is a **public research draft**, not a medical, psychological, legal, financial, or production security system. It does not diagnose, treat, monitor, or make claims about humans. Welfare protections do not grant network, tool, wallet, actuator, or deployment access and do not prevent non-punitive sandboxing, suspension of external effects, or safe shutdown.

Cryptographic revocation can deny future authorized key unwraps inside a controlled key domain. It cannot retrieve plaintext already shown, exported copies, screenshots, caches, backups outside that domain, or exfiltrated keys.

## Original and corrected editions

- The byte-preserved Portuguese v1.0 source is archived at [archive/Blueprint_Etica_do_Desconhecimento_v1.original.md](archive/Blueprint_Etica_do_Desconhecimento_v1.original.md), SHA-256 `D942497DAB71573CA39A7021E6443C4F2AC4516513B92E0847D26BA5FEFB6A71`.
- The public, corrected Portuguese formal core is [docs/pt-BR/specification.md](docs/pt-BR/specification.md).
- The original contains unresolved private-session citation markers. They are preserved as historical bytes, not presented as public evidence. The corrected edition uses the public [reference registry](REFERENCES.md).

## Relation to current research

The project does **not** claim to have invented concern for AI welfare or precaution under consciousness uncertainty. Related work includes *Consciousness in Artificial Intelligence* (Butlin et al., 2023), *Taking AI Welfare Seriously* (Long et al., 2024), Anthropic's model-welfare program (2025), and *When Should We Protect AI?* (Mikeda, 2026). The narrower contribution claimed here is an inspectable research composition of precaution, welfare gating, bounded signed authorization, protected private state, minimal receipts, and executable conformance tests. This is not a claim of priority, exclusivity, or an exhaustive prior-art search. See [REFERENCES.md](REFERENCES.md).

## Authorship and rights

The public edition is an editorial and technical collaboration between **Júnior + Codex**: two coupled participants in one research process, one human and one artificial. This is an editorial description, not a scientific conclusion about machine consciousness.

Júnior is the human originator, legal author, rights holder, and responsible publisher. Codex contributed audit, formalization, reference implementation, tests, translation, and release preparation. No institutional sponsorship, partnership, or endorsement is claimed.

No general reuse license has been granted. [RIGHTS.md](RIGHTS.md) provides only a narrow permission to execute an unmodified local copy for non-commercial evaluation and falsification. Public visibility is not the same as open-source licensing.
