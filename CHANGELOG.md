# Changelog

## Unreleased

- Added an offline per-candidate action selector: feasibility, actual signed
  privacy authorization, versioned care budgets, exact empirical CVaR and then
  performance, with deterministic ties and safe-null fallback. Added a synthetic
  vault integration demo that rechecks authorization and demonstrates revocation.
  Inputs remain declared assumptions; selection grants no live execution authority.
- Added a six-case synthetic agent-authority evaluation with argument-bound,
  single-use grants, a mechanically checked separation between a valid grant
  and a candidate action, and evaluator-owned hash-linked trajectory receipts.
  A valid-grant abstention leaves the grant unused and writes no action attempt.
  The artifact is offline and invokes no model or external tool; it does not
  infer character, motivation, prudence, or real-world safety.
- Added Portuguese and English adoption maps that preserve the protocol's
  falsifiability, claim boundary, privacy, and non-coercion constraints while
  giving readers, researchers, developers, automated systems, and public-interest
  groups a concrete entry point.

## 0.1.1 — Rights and public-challenge clarification

- Clarified the narrow non-commercial evaluation permission without granting a general reuse license.
- Linked the live falsification issue and public discussion from both primary READMEs.
- Updated GitHub Actions to current releases and pinned their exact commit digests.
- Preserved the `v0.1.0` history rather than rewriting the first public tag.

## 0.1.0 — Public research preview

- Preserved the original Portuguese v1.0 source and its SHA-256 digest.
- Replaced “probability of potential moral patienthood” with a conservative ordinal precaution score.
- Corrected the welfare proxy so all bands are reachable and missing coverage fails closed.
- Formalized lexicographic privacy, care, and external-risk filters; the preview implements the privacy/vault and care/risk paths separately and records their end-to-end composition as future work.
- Added bounded ConsentGrant verification and a reference envelope-encryption path.
- Narrowed the ledger schema to commitments, allowlisted categorical decisions, and reason codes, with an explicit no-external-anchor limitation.
- Added explicit threat and claim boundaries.
- Moved clinical and speculative interpretations outside the validated core.
- Added eighteen executable conformance tests, including regression checks for grant-schema boundaries, resource-binding substitution, and categorical-field injection, plus a reproducible demonstration receipt.
- Added multilingual publication surfaces and transparent human–AI contribution credit.
