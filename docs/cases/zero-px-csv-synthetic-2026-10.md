# CSV: menos procura manual, mais clareza sobre onde revisar

Regras verificadas, posições para revisar e limites explícitos: dois exemplos sintéticos do Zero Px CSV mostram um resultado útil sem prometer que os dados são “verdadeiros”.

## 1. Do achado à localização

Em um arquivo de inventário, **2 registros lidos e validados produziram 5 apontamentos**, com resultado completo `FINDINGS`. Todos estão no **registro lógico 2, linha física 3**:

| Campo | Regra sinalizada |
| --- | --- |
| `quantity` | `TYPE_INTEGER` — formato de inteiro |
| `mass_kg` | `TYPE_DECIMAL` — decimal finito |
| `received` | `TYPE_DATE` — data válida em `YYYY-MM-DD` |
| `contact` | `TYPE_EMAIL` — formato básico de e-mail |
| Chave do registro | `DUPLICATE_KEY` — repetição exata da chave do registro 1 |

O benefício é começar pela posição indicada, sem correção silenciosa. E-mail básico não comprova existência ou entrega. O recibo identifica os relatórios; o SHA-256 da fonte tem escopo `READ_BUFFER`: identifica bytes lidos, **não autenticidade, origem ou verdade**.

## 2. Um recorte de desempenho, com fronteira explícita

**50.000 registros em 0,586015 s, com pico residente de 45,930 MiB no processo CLI.** Foi uma observação local em Windows/Python 3.14.0, com dados sintéticos ASCII e três colunas: `codigo`, `nome`, `email`.

| Registros | Tempo observado | Pico residente do CLI |
| --- | --- | --- |
| 1.000 | 0,154824 s | 28,457 MiB |
| 10.000 | 0,234511 s | 28,898 MiB |
| 50.000 | 0,586015 s | 45,930 MiB |

Houve **uma execução por porte**. Todas terminaram completas, `CLEAN`, com todos os registros validados e zero diagnósticos sob as regras declaradas: campos obrigatórios, inteiro, texto limitado, e-mail básico e chave sem repetição.

O tempo inclui início do Python, leitura, validação e escrita dos relatórios; exclui a GUI e os controles posteriores. A memória é do processo CLI, não do host inteiro. Não é média, prova de escalabilidade, comparação com concorrentes ou promessa para outros arquivos. **Os cinco achados acima pertencem a outro arquivo, não ao ensaio de 50.000 registros.**

## 3. Princípios que mudam a prática

Aplicamos a **Ética do Desconhecimento** para não trocar “passou nestas regras” por “é verdadeiro”. **Engenharia de Pontes** orienta ligar regra, posição e evidência. O **Freio Técnico da Cognição Finita** orienta agir num recorte útil, observar o retorno e rever a decisão quando dados ou condições mudarem — sem exigir certeza impossível antes do primeiro uso, nem esconder limites depois.

Pesquisa independente de **Júnior**, com engenharia e documentação assistidas por **Codex**. O código original permanece privado; este relato não o torna open source nem concede nova licença.

**Qual regra verificável ajudaria seu fluxo?** Proponha um requisito e resultado esperado na [discussão pública existente](https://github.com/NixEngine/ethics-under-uncertainty/issues/3), apenas com exemplos sintéticos publicáveis — sem dados de clientes, credenciais ou informações confidenciais. Não é compromisso de entrega.

---

# CSV: less manual searching, clearer review locations

Checked rules, review locations and explicit limits: two separate synthetic Zero Px CSV examples show useful results without claiming that data is “true”.

## 1. From finding to location

A small inventory file produced **5 findings across 2 fully read and validated records**, with a complete `FINDINGS` result. All findings locate **logical record 2, physical line 3**:

| Field | Reported rule |
| --- | --- |
| `quantity` | `TYPE_INTEGER` — integer format |
| `mass_kg` | `TYPE_DECIMAL` — finite decimal |
| `received` | `TYPE_DATE` — valid `YYYY-MM-DD` date |
| `contact` | `TYPE_EMAIL` — basic email format |
| Record key | `DUPLICATE_KEY` — exact repeat of record 1's key |

The reviewer gets a location, not a silent rewrite. Basic email syntax proves neither existence nor delivery. The receipt identifies reports; the source SHA-256 covers `READ_BUFFER`: bytes read, **not authenticity, provenance or truth**.

## 2. A measured slice, not a general performance claim

**50,000 records in 0.586015 s, with a 45.930 MiB peak resident CLI process.** Environment: Windows/Python 3.14.0; the synthetic ASCII data had three columns: `codigo`, `nome`, `email`.

| Records | Observed time | CLI peak resident memory |
| --- | --- | --- |
| 1,000 | 0.154824 s | 28.457 MiB |
| 10,000 | 0.234511 s | 28.898 MiB |
| 50,000 | 0.586015 s | 45.930 MiB |

There was **one execution per size**. Each completed `CLEAN`, validating every record with zero diagnostics under required-field, integer, bounded-text, basic-email and duplicate-key rules.

Timing includes Python startup, reading, validation and report writing, not the GUI or later consistency checks. Memory covers the CLI process, not the whole host. These observations are not averages, scaling proof, competitive comparisons or promises for other files. **The five findings belong to the separate inventory example, not the 50,000-record run.**

## 3. Principles with practical consequences

We apply the **Ethics of Not Knowing** to keep “passed these rules” distinct from “true”. **Bridge Engineering** connects a rule, its location and evidence. The **Technical Brake of Finite Cognition** guides us to act within a useful boundary, observe the return, and revisit decisions as conditions change — neither demanding impossible certainty before use nor hiding limits afterward.

Independent research by **Júnior**, with **Codex-assisted engineering and documentation**. Original code remains private; this account neither open-sources it nor grants a new license.

**Which checkable rule would help your workflow?** Share a requirement and expected result in the [existing public discussion](https://github.com/NixEngine/ethics-under-uncertainty/issues/3), with public synthetic examples only — no customer data, credentials or confidential information. No delivery commitment.


## Dados examináveis / Inspectable data

As tabelas acima resumem as observações abaixo. Este é um recorte publicado de registros salvos, não uma nova execução ou replicação independente. Identificadores do host, caminhos privados e telemetria completa não fazem parte desta publicação.

The tables summarize the saved observations below. This is a public selection, not a new execution or independent replication. Host identifiers, private paths and full telemetry are excluded.

### Desempenho / Performance

```json
{
  "schema": "zero-px.public-synthetic-observation.r279.v1",
  "scope": "Selected data from saved R271 observations, not a rerun or full telemetry export.",
  "environment": "Windows, CPython 3.14.0, x64.",
  "timing_boundary": "CLI wall time from before process launch to completion, with monitoring overhead; Python start/read/validate/write included, GUI and later integrity review excluded.",
  "runs_per_size": 1,
  "measurements": [
    {
      "records": 1000,
      "input_bytes": 51911,
      "input_sha256": "f897ee9fc8de5b919eef1a9dbfe1ef1135d18426b6432ba610c5a40b7db5ef62",
      "cli_wall_seconds": 0.15482389996759593,
      "os_peak_working_set_last_known_bytes": 29839360,
      "os_peak_working_set_mib": 28.45703125,
      "result_summary": {
        "schema": "zero-px.csv-service.summary.v1",
        "status": "CLEAN",
        "complete": true,
        "refusal_code": null,
        "exit_code": 0,
        "records_read": 1000,
        "records_validated": 1000,
        "diagnostic_count": 0
      }
    },
    {
      "records": 10000,
      "input_bytes": 528912,
      "input_sha256": "c48125ff86e9674571946871fdc72cad06fccaa9a42bebbd25235ce22c21a127",
      "cli_wall_seconds": 0.2345107999863103,
      "os_peak_working_set_last_known_bytes": 30302208,
      "os_peak_working_set_mib": 28.8984375,
      "result_summary": {
        "schema": "zero-px.csv-service.summary.v1",
        "status": "CLEAN",
        "complete": true,
        "refusal_code": null,
        "exit_code": 0,
        "records_read": 10000,
        "records_validated": 10000,
        "diagnostic_count": 0
      }
    },
    {
      "records": 50000,
      "input_bytes": 2688912,
      "input_sha256": "2029eb4a270585332a938c7b79070a5eaf5809c1f1dc2e1df655cadd6abdb747",
      "cli_wall_seconds": 0.5860145000042394,
      "os_peak_working_set_last_known_bytes": 48160768,
      "os_peak_working_set_mib": 45.9296875,
      "result_summary": {
        "schema": "zero-px.csv-service.summary.v1",
        "status": "CLEAN",
        "complete": true,
        "refusal_code": null,
        "exit_code": 0,
        "records_read": 50000,
        "records_validated": 50000,
        "diagnostic_count": 0
      }
    }
  ],
  "limits": [
    "No cold-cache assertion",
    "No repeated-trial distribution",
    "CLI memory excludes browser, server, collector and other processes",
    "Not independent replication or a customer acceptance test"
  ]
}
```

### Resultado do caso pequeno / Small-case result

Conteúdo JSON do resultado salvo, com formatação editorial. O arquivo original de 1.468 bytes tem SHA-256 `ea3c2e74807a17779ad33d5a0a37a52d8e341824077eacb80140ca37991d4a6e`; esta formatação não preserva seu hash de bytes. Os hashes identificam os artefatos locais reportados, não atestação independente.

Saved result as JSON with editorial formatting. The original 1,468-byte file has the SHA-256 above; this formatting does not retain its byte hash. Hashes identify the reported local artifacts, not independent attestation.

```json
{
  "profile": "zero-px.csv-service.r267.v1",
  "version": 1,
  "status": "FINDINGS",
  "complete": true,
  "refusal_code": null,
  "exit_code": 1,
  "source": {
    "basename": "inventory_findings_r273.csv",
    "bytes_read": 106,
    "sha256": "4fa2fda2170babb258194f93d8ae8d84bc76ec8bd14f35f0e5c59cefd0b55982",
    "complete_read": true,
    "hash_scope": "READ_BUFFER"
  },
  "header_span": {
    "physical_start_line": 1,
    "physical_end_line": 1
  },
  "counters": {
    "records_read": 2,
    "records_validated": 2
  },
  "diagnostics": [
    {
      "rule_code": "TYPE_INTEGER",
      "message": "Value does not have the declared ASCII integer format.",
      "logical_record": 2,
      "physical_start_line": 3,
      "physical_end_line": 3,
      "field_index": 2,
      "field_name": "quantity"
    },
    {
      "rule_code": "TYPE_DECIMAL",
      "message": "Value does not have the declared finite ASCII decimal format.",
      "logical_record": 2,
      "physical_start_line": 3,
      "physical_end_line": 3,
      "field_index": 3,
      "field_name": "mass_kg"
    },
    {
      "rule_code": "TYPE_DATE",
      "message": "Value is not a valid date in YYYY-MM-DD format.",
      "logical_record": 2,
      "physical_start_line": 3,
      "physical_end_line": 3,
      "field_index": 4,
      "field_name": "received"
    },
    {
      "rule_code": "TYPE_EMAIL",
      "message": "Value does not meet the declared basic email format.",
      "logical_record": 2,
      "physical_start_line": 3,
      "physical_end_line": 3,
      "field_index": 5,
      "field_name": "contact"
    },
    {
      "rule_code": "DUPLICATE_KEY",
      "message": "Exact key tuple repeats an earlier correct-arity record.",
      "logical_record": 2,
      "physical_start_line": 3,
      "physical_end_line": 3,
      "field_index": null,
      "field_name": null,
      "first_logical_record": 1
    }
  ]
}
```
