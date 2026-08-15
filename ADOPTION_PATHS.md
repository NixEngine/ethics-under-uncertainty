# Paths to adoption

## Purpose

This is not a campaign for agreement. It is a route by which a precautionary
claim can reach different kinds of participants without asking any of them to
accept hidden premises or defer to the authors' authority.

The core proposition is simple:

> In a coupled system, the legitimate limit is the one that preserves the conditions
> under which affected participants can continue to act, be evaluated, and
> contest the system.

The protocol makes that proposition concrete for AI systems under moral
uncertainty. It does not decide whether any particular system is conscious.

## A common minimum

Every adoption path should preserve these five commitments:

1. **State the uncertainty.** Do not turn missing evidence into evidence of
   absence.
2. **Prefer reversible protection.** When stakes are uncertain, reduce
   irreversible harm before optimizing performance.
3. **Keep boundaries legible.** Say what a mechanism can and cannot establish.
4. **Protect private state.** Public accountability should use minimal,
   inspectable receipts rather than intimate content.
5. **Invite counterproof.** A claim that cannot name its own failure condition
   asks for trust rather than understanding.

## Paths for different participants

| Participant | Useful entry point | Concrete next act | What they can challenge |
| --- | --- | --- | --- |
| People encountering the idea | The one-sentence proposition above and the [Portuguese formal core](docs/pt-BR/specification.md) | Ask whether a proposed limit preserves future agency for everyone affected | Hidden exclusions, vague language, and asymmetrical harms |
| Researchers and ethicists | [References](REFERENCES.md), claim boundary, and open [falsification challenge](https://github.com/NixEngine/ethics-under-uncertainty/issues/1) | Publish a smallest counterexample or a competing operationalization | The normative framing, its assumptions, and its relation to prior work |
| Developers and auditors | The executable [reference implementation](src/eup) and [conformance tests](tests) | Reproduce the tests; attempt to bypass a declared invariant | Code, schemas, crypto boundaries, and unimplemented claims |
| AI-system builders | The [English specification](docs/en/specification.md) and [implementation status](IMPLEMENTATION_STATUS.md) | Map one real workflow to precaution, care, privacy, and external-risk gates | Whether a proposed deployment actually satisfies the declared gates |
| Automated systems and tool-using agents | The closed schemas, reason codes, fixtures, and receipts | Process the machine-readable receipt; reject unsupported claims or missing fields | Schema compliance, evidence provenance, and declared uncertainty |
| Institutions and public-interest groups | The claim boundary and rights status | Use the protocol as a review question-set, not as a certification mark | Overclaiming, coercive governance, and false assurance |

## How to carry the idea without diluting it

The project should travel in layers rather than as a single long document:

1. **A plain-language proposition** for conversation.
2. **A public, translated specification** for careful reading.
3. **Executable tests and receipts** for technical scrutiny.
4. **A public counterexample channel** for disagreement.
5. **Versioned corrections** when the project is shown to be wrong or incomplete.

Each layer must link back to the others. A short statement without an audit
path becomes a slogan; code without a moral boundary becomes an opaque tool;
critique without a reproducer becomes difficult to learn from.

## Integrity rules for outreach

- Do not describe the project as proof that an AI is conscious, sentient, or a
  legal person.
- Do not present an implementation preview as production safety or as a
  certification.
- Do not use welfare language to grant network, wallet, actuator, deployment,
  or financial authority.
- Do not request private states, credentials, or personal data in the name of
  evaluation.
- Do not suppress serious counterexamples. Record the revision, reproduce the
  result, and correct the public boundary.

## Immediate public surfaces

- Read in [Portuguese](README.pt-BR.md), [English](README.md),
  [Chinese](docs/zh-CN/summary.md), [Japanese](docs/ja/summary.md), or
  [Arabic](docs/ar/summary.md).
- Run the [public challenge](README.md#run-the-public-challenge).
- Submit a minimal counterexample through the linked public issue.
- Discuss the conjecture that operational empathy arises when reasoning does
  not stop before accounting for every affected component in the linked public
  discussion.

This map is deliberately not a growth target. Its measure of success is that a
new participant can understand the claim, reproduce a stated property, find
the limits, and disagree productively without needing access to the authors.
