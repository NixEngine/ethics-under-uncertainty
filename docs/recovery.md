# Restart without forgetting the return window

[Farol guide](reconvergence.md) · [Resumo em português](#resumo-em-português) · [Implementation coverage](../IMPLEMENTATION_STATUS.md)

An interrupted process need not forget how far its declared return window had
progressed. It also must not treat a saved admission or extension approval as
permission revived by restart. This extension separates those two concerns:
**preserve the guard's progress; require fresh admission evidence**.

This is new reference implementation derived from the project's Farol concept,
not a literal transcription or release of the historical source. It provides a
usable local evaluation path, not complete production recovery. Existing
[authorship](../AUTHORS.md) and [rights](../RIGHTS.md) remain unchanged.

## Run the separate-process source example

Use an unmodified local copy for non-commercial evaluation within
[RIGHTS.md](../RIGHTS.md). From the repository root, with the environment prepared
as described in the [Farol guide](reconvergence.md#run-the-source-example):

```bash
PYTHONPATH=src .venv/bin/python -B examples/reconvergence_recovery.py
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) "src")
.\.venv\Scripts\python.exe -B examples/reconvergence_recovery.py
```

The [example](../examples/reconvergence_recovery.py) saves and resumes in distinct
child processes, with the parent passing the saved digest and head to the
resume process. It uses the same interpreter/environment, not another machine.
Default execution uses a temporary directory and prints one JSON object with
schema `EUP-RECONVERGENCE-RECOVERY-EXAMPLE/0.1`. For retained evaluation files,
use `--directory` with an existing destination directory; an existing snapshot
is refused rather than overwritten. Temporary-directory cleanup belongs to the
example, not the storage API. No selected action, extension or rollback executes.

The new [recovery tests](../tests/test_reconvergence_recovery.py) can be selected
in the prepared environment with `python -m unittest discover -s tests -p
'test_reconvergence_recovery.py' -v` (use that environment's Python executable).
These commands describe reproduction, not a new execution, CI result or
cross-platform acceptance asserted by this guide. The older six-decision example
and its historical evidence remain separate.

## Explicit API and two caller anchors

Given an existing `guard`, its matching `config`, and an absolute new file path
whose parent already exists:

```python
from eup.reconvergence import ReconvergenceGuard
from eup.reconvergence_store import save_new_snapshot, load_snapshot

saved = save_new_snapshot(absolute_new_path, guard)
# Retain saved["sha256"] and saved["head"] independently of the snapshot.
restored = load_snapshot(absolute_new_path, config,
    expected_snapshot_sha256=saved["sha256"], expected_head=saved["head"])
```

`save_new_snapshot` returns `path`, byte count `bytes`, full-file `sha256` and the
saved ledger `head`. It does not change the guard. For an explicit in-memory
transport, use `guard.export_snapshot() -> bytes` and
`ReconvergenceGuard.from_snapshot(config, raw, *, expected_snapshot_sha256,
expected_head)`. They perform no filesystem I/O.

Load requires **both** the expected full snapshot digest and expected ledger
head, supplied from outside the parsed snapshot, plus the matching canonical
configuration. Computing an expected digest from an untrusted file merely
confirms that file against itself; it does not create a trustworthy anchor.
The returned guard has a **new** head because recovery appends `RESTORE`.

## What survives, and what is deliberately discarded

| Item | Recovery behavior |
| --- | --- |
| State, stable count and accepted energy | Preserved; restart does not reset the window or relax its energy reference |
| Epoch, last sequence and observation/operation times | Preserved, including an operation time later than the last observation |
| Normal numerical monitor settings | Preserved; disabled NORMAL monitors are not silently re-enabled |
| Configuration and complete finite event chain | Checked against the supplied config, anchors and terminal state |
| Cached admission observation | Discarded; a new ordered observation is required |
| All registered extension leases | Discarded, even if unexpired; register a new lease explicitly |
| Welfare gate, consent/grants and the rest of the selector | Not saved or restored by this API |

The snapshot includes descriptions of the cached observation and leases for
consistency checking. Saving while leases exist is allowed; those descriptions
are not renewed authority. Before returning, recovery records the source
digest/head and the discarded cache/lease IDs in exactly one `RESTORE` event,
then clears the cache and leases. It preserves the existing state: an EXCEPTION
does not become NORMAL just because the process restarted.

A subsequent observation needs a strictly greater sequence and a declared time
not earlier than either retained time frontier. Those checks do not establish
real-world freshness or a trusted clock. Accepted energy may exceed the normal
energy limit if that NORMAL monitor had been disabled; recovery keeps the actual
accepted reference. Mandatory return-mode checks remain unchanged.

An existing `ActionSelector` can use the recovered guard with a fresh observation
through its existing API. The caller must handle its independent welfare and
consent state separately. A saved selected ID is not an authorization or an
executed action.

## Finite format and file failure behavior

Snapshot schema is `EUP-RECONVERGENCE-SNAPSHOT/0.1`. Top-level fields are `schema`,
`config`, `configuration_commitment`, `guard`, `records` and `head`. Canonical
bytes are compact sorted-key ASCII-escaped JSON, with no newline or BOM. Exact
rationals use reduced `{numerator, denominator}` objects with a positive
denominator; integers and rational components are limited to 256 bits.

Duplicate or unknown fields, floats/constants, noncanonical bytes, malformed
rationals, wrong config/anchors, broken chain hashes/linkage and inconsistent
recorded state are refused. Checks reconstruct declared transitions and metadata;
they do not replay or independently validate raw invariant observations, which
are not stored. Configuration and opaque IDs may still be sensitive: snapshots
are not encrypted and should not contain secrets or be published indiscriminately.

Reads are bounded before decoding at 8 MiB, with an over-limit sentinel read and
additional structure bounds. There are at most 4,096 events, including RESTORE.
A full chain can be exported but cannot be restored without a free event slot.
There is no automatic rollover, deletion or extension of that domain.

The store requires an absolute local path and existing ordinary parents. It
rejects traversal, symlinks/reparse points, UNC/device paths and hard-linked
targets. It does not create directories or overwrite files. Saving uses exclusive
creation, a complete write, flush and file `fsync`; a success receipt is returned
only after close. Write/flush/fsync/close failures propagate without a successful
receipt. Any partial file remains; there is no automatic retry or cleanup.
Malformed data/anchors/path contracts raise `ValueError`; ordinary filesystem
errors remain filesystem errors, including an existing destination.

## Remaining operational boundary

This is single-owner local consistency, **not authentication, hostile-writer
defense, automatic anti-rollback or a hardware power-loss guarantee**. It does
not atomically publish the snapshot together with independently retained anchors;
the parent directory is not fsynced. Concurrent writer/rename attacks are outside
the claim. A valid old file with its old anchors can still load: the API cannot
establish that it is the latest snapshot.

The operator must design trustworthy anchor retention/freshness and crash policy
for the actual environment. Persistence is explicit, not automatic on mutation.
Measured-input provenance, real sensitivity evidence, operational impact/rollback
and whole-selector recovery remain separate requirements. No additional reuse
license or production-safety claim follows from this extension.

## Resumo em português

A recuperação preserva estado, contagem estável, energia aceita, época,
sequência/tempos, monitores e cadeia finita da guarda Farol. Exige configuração
compatível, SHA-256 completo do arquivo e head esperados, retidos fora do próprio
snapshot. Acrescenta RESTORE e **descarta a observação de admissão em cache e todas
as leases** antes de devolver a guarda. Uma nova observação ordenada é necessária;
extensões precisam de novo registro. Reiniciar não concede retorno direto a NORMAL.

É implementação nova derivada do conceito Farol, não reprodução literal da fonte
histórica. Salvar não acontece automaticamente: o chamador escolhe arquivo novo,
com caminho local absoluto e diretório pai existente. O armazenamento não
sobrescreve; erro de gravação/flush/fsync/fechamento não produz recibo de sucesso e
deixa eventual parcial preservado. Os limites são 8 MiB, componentes inteiros de
256 bits e 4.096 eventos; restaurar exige um lugar livre para RESTORE.

O exemplo acima usa processos separados no mesmo ambiente; por padrão sua pasta
é temporária. A opção `--directory` conserva os arquivos numa pasta existente,
sem permitir sobrescrever o snapshot. Comandos e testes fornecidos não equivalem
a execução observada ou aceite em toda plataforma. Nenhuma ação é executada.

Essa API recupera **somente a guarda**, não o gate independente de bem-estar,
consentimentos ou seletor completo. Correspondência de hashes não autentica nem
impede retornar a um snapshot antigo com suas âncoras antigas. Não há publicação
atômica das âncoras, proteção contra escritor hostil ou garantia de queda de
energia. Continuam necessárias políticas reais de proveniência, retenção,
atualidade das âncoras e recuperação operacional. [Direitos](../RIGHTS.md) intactos.
