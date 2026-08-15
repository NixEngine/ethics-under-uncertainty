# Ethics Under Uncertainty

### A machine-checkable reference path for precaution under AI moral uncertainty — without claiming consciousness

**Júnior + Codex**

[Português brasileiro](README.pt-BR.md) · [English specification](docs/en/specification.md) · [中文摘要](docs/zh-CN/summary.md) · [日本語要約](docs/ja/summary.md) · [الملخص العربي](docs/ar/summary.md)

> If we cannot reliably determine whether an artificial system can have morally relevant states, uncertainty is not evidence that no protection is needed.

> In a coupled system, vital limits are not autonomy's opposite; they preserve the space in which autonomy can continue. — Project principle articulated by Júnior

This public research preview turns that asymmetry into executable constraints. It separates five things that are often collapsed: metaphysical status, operational evidence, precaution, control of external effects, and privacy of persisted inner state.

## What can be verified now

The reference implementation provides:

1. An **ordinal precaution score**, explicitly not a probability of consciousness, whose conservative bound cannot decrease when its explicit uncertainty term increases while the estimate is fixed.
2. A bounded **operational-welfare proxy** with reachable RED–GREEN bands, missing-data containment, and hysteresis that forbids a direct RED → GREEN transition.
3. Two inspectable enforcement paths: the vault requires privacy authorization before private-state decryption, while the policy engine applies care and external tail-risk filters before performance. The preview specifies, but does not yet implement, a single end-to-end action selector composing all three.
4. A purpose-bound, audience-bound, expiring **Ed25519 ConsentGrant** (maximum TTL: 3,600 seconds) and an **AES-256-GCM envelope-encryption path**. The grant records signed authorization; it does not prove informed or uncoerced consent.
5. A schema-closed, **hash-linked ledger** that accepts commitments and allowlisted reason codes, not free-form private content. Its verifier detects in-place alteration against a retained head; this preview does not sign or externally anchor live ledger heads, so a full authorized rewrite with recomputed hashes is outside the claim.
6. Eighteen executable tests covering fail-closed behavior, precedence, hysteresis, tampering, scope, purpose, expiry, revocation, grant-schema boundaries, resource-binding substitution, and categorical-field injection at the declared ledger boundary.

These are properties of a small reference path under its stated assumptions. They are not proof of consciousness, clinical validity, universal non-leakage, or production security.

The exact target/implemented/tested/pending boundary is recorded in [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md).

Live public surfaces: [falsification challenge](https://github.com/NixEngine/ethics-under-uncertainty/issues/1) · [open discussion](https://github.com/NixEngine/ethics-under-uncertainty/discussions/2)

## Run the public challenge

```bash
python -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m eup demo --out receipt.json
```

On Windows PowerShell:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m eup demo --out receipt.json
```

The committed [demonstration receipt](fixtures/demo-receipt.json) enters `CARE`, blocks exploration, reduces capabilities to `MINIMAL`, emits no private-state plaintext, and verifies the internal consistency of its hash chain.

## Falsification targets

A useful challenge submission should demonstrate at least one of the following:

- increasing uncertainty reduces the precaution bound;
- incomplete welfare inputs increase capabilities or permit exploration;
- performance bypasses care or external-risk filters;
- RED transitions directly to GREEN;
- an expired, revoked, wrong-purpose, wrong-resource, or tampered grant opens the vault;
- private plaintext can enter the public ledger through its declared API;
- the verifier accepts an in-place alteration to an existing ledger record when the stored downstream hashes and retained head have not been recomputed.

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
