# CSV rules that tied at 4/4

Júnior + Codex · Current authored case based on saved executions. / Caso autoral atual baseado em execuções registradas.

## Português — Quatro acertos não revelavam duas regras inadequadas

Executamos o validador CSV privado **24 vezes: oito arquivos sintéticos, três regras fixas**. O contrato pretendido exigia identificador inteiro obrigatório e único, data válida `YYYY-MM-DD` e status permitido. O oráculo de aceite/rejeição e os casos foram fixados antes das execuções.

A exigia calendário válido **e** uma das duas datas enumeradas; B exigia calendário ISO válido; C exigia apenas texto não vazio na data. As demais regras eram comuns. A e C foram contrastes deliberados, não defeitos descobertos em dados de cliente.

| Configuração | Lote 0 | Lote 1 | Desacordo com o contrato pretendido |
| --- | --- | --- | --- |
| A · Datas enumeradas | 4/4 | 3/4 | Rejeitou a data válida `2028-06-12` |
| B · Calendário ISO | 4/4 | 4/4 | Nenhum nos quatro casos do lote 1 |
| C · Apenas texto | 4/4 | 3/4 | Aceitou a data impossível `2028-06-31` |

**O motor cumpriu as regras recebidas.** A falsa rejeição de A veio de `ENUM`; C não exigia validade de calendário. Cumprir uma configuração não demonstra que ela representa a necessidade. `CLEAN` tampouco substitui o contrato.

A nota contou classificações corretas entre quatro arquivos, não quantos ficaram CLEAN. Falso aceite e falsa rejeição perderam um ponto cada; seus custos reais não são necessariamente iguais. Risco e cuidado usaram hipóteses artificiais neutras, não estimativas derivadas dessas notas.

### A recomendação mudou; o histórico não

Após **12** classificações, os três 4/4 empataram: A foi recomendada pela ordem dos identificadores, sem evidência de superioridade. Após **20**, faltava a observação do lote 1 de C. No modo que exigia todas as opções, o adaptador retornou `EVIDENCE_INSUFFICIENT`, sem chamar o seletor nem atualizar o controle de cuidado. Após **24**, a cobertura estava completa e B foi recomendada. Os registros anteriores, incluindo os dois 4→3, foram preservados.

`n=0/1` identifica composições diferentes, não tempo ou treinamento. Não houve aprendizagem automática, alteração das regras ou execução da opção recomendada. Este recorte deliberado não é benchmark representativo nem estimativa de acurácia geral.

As **24 verificações dos mesmos resultados** retornaram `MATCHED_UNAUTHENTICATED`: correspondência de bytes, não autenticação ou mais 24 amostras. A [projeção JSON](../../fixtures/csv-rule-comparison.json) contém oito CSVs, três objetos de regras, 24 resultados, seis escores e três seleções. Não são os recibos completos nem uma reprodução independente; o motor privado não é distribuído.

Como leitura aplicada da Ética do Desconhecimento e do Freio Técnico da Cognição Finita: agir e ajustar com informação delimitada, preservar o que falta e retornar a uma decisão sem reescrever seu passado. Confiança se sustenta em honestidade, transparência e correção — não numa nota.

## English — Four correct answers did not expose two unsuitable rules

We ran the private CSV validator **24 times: eight synthetic files, three fixed rule configurations**. The intended contract required a nonempty integer identifier, uniqueness, a valid `YYYY-MM-DD` date, and an allowed status. Acceptance expectations and cases were fixed before execution.

A required a valid calendar date **and** a two-date allowlist; B required a valid ISO calendar date; C required only nonempty text in the date field. Other rules were shared. A and C were deliberate contrasts, not defects discovered in customer data.

| Configuration | Batch 0 | Batch 1 | Mismatch with the intended contract |
| --- | --- | --- | --- |
| A · Enumerated dates | 4/4 | 3/4 | Rejected valid `2028-06-12` |
| B · ISO calendar | 4/4 | 4/4 | None in batch 1's four cases |
| C · Text only | 4/4 | 3/4 | Accepted impossible `2028-06-31` |

**The engine followed the supplied rules.** A's false rejection came from `ENUM`; C did not require calendar validity. Compliance with a configuration does not establish that it expresses the intended need. CLEAN is not a substitute for that contract.

The score counted correct classifications out of four files, not CLEAN outputs. False acceptance and false rejection each lost one point; their real costs need not be equal. Risk and care used artificial neutral assumptions, not estimates inferred from these scores.

### The recommendation changed; history did not

After **12** classifications, all three scored 4/4: A was recommended by identifier tie-break, not demonstrated superiority. After **20**, C's batch-1 observation was missing. In the mode requiring all options, the adapter returned `EVIDENCE_INSUFFICIENT`, without calling the selector or updating the care gate. After **24**, coverage was complete and B was recommended. Earlier records, including both 4→3 changes, remained intact.

`n=0/1` labels different case compositions, not time or training. No automatic learning, rule change or execution of the recommended option occurred. This designed comparison is neither a representative benchmark nor a general accuracy estimate.

The **24 corresponding receipt checks** returned `MATCHED_UNAUTHENTICATED`: byte correspondence, not authentication or 24 additional samples. The [JSON projection](../../fixtures/csv-rule-comparison.json) contains eight CSV texts, three rule objects, 24 results, six scores and three selections. It is not the full native receipts or independent replication; the private engine is not distributed.

As an applied reading of the Ethics of Not Knowing and the Technical Brake of Finite Cognition: act and revise within stated information, retain unknowns, and revisit a decision without rewriting its past. Trust rests on honesty, transparency and correction, not a score.

---

[Existing discussion / Discussão existente](https://github.com/NixEngine/ethics-under-uncertainty/issues/3): bring a public synthetic requirement or counterexample; do not post customer or private data. [Repository rights / Direitos](../../RIGHTS.md) remain unchanged; no additional engine license is granted here.
