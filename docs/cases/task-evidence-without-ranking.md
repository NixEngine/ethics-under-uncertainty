# Desempenho responde a uma tarefa. Confiança exige honestidade.

**Júnior + Codex · elaboração atual · quatro séries deliberadamente sintéticas**

[English below](#performance-answers-a-task-question-trust-calls-for-honesty) · [Entradas e resultados salvos](../../fixtures/task-evidence-profiles.json)

Um sistema alcançou a meta na primeira observação e ficou abaixo dela na seguinte. Outro alcançou a meta mais tarde, mas faltam pontos no registro. Qual deles é “melhor”? Os dados ainda não respondem a essa pergunta. Respondem a perguntas menores — e úteis — quando deixamos explícitos a tarefa, o contexto e o que foi efetivamente registrado.

## Caso: quatro séries, quatro perguntas

Considere uma tarefa inventada, com uma métrica de contagem em que valores maiores são desejáveis. `n` é um índice inteiro de exposição declarado no exemplo, não tempo decorrido nem prova de treinamento. O patamar é fornecido de fora: a rotina não decide qual exigência seria adequada para uma aplicação real.

| Série | Pontos fornecidos `(n, valor)` | Patamar | O que o registro permite dizer |
| --- | --- | ---: | --- |
| A — alcance inicial e queda | `(0, 5), (1, 2)` | 4 | O patamar foi atingido em 0; o último ponto fornecido já não o satisfaz. |
| B — prefixo completo | `(0, 1), (1, 3), (2, 6)` | 5 | O primeiro alcance na sequência inteira declarada foi em 2. |
| C — lacuna antes do alcance | `(0, 1), (3, 7)` | 5 | O primeiro alcance **observado** foi em 3; não sabemos o que aconteceu em 1 ou 2. |
| D — nenhum alcance registrado | `(0, 0), (1, 1)` | 2 | Não há alcance nos pontos fornecidos. Isso não demonstra que nunca ocorrerá. |

Essas séries não medem pessoas, modelos ou produtos reais. As entradas e os objetos de resultado no [JSON selecionado](../../fixtures/task-evidence-profiles.json) foram preservados de uma execução anterior de uma referência privada. Esta publicação seleciona os dados; não executa novamente o componente. A e D também têm patamares diferentes de B e C: a tabela explica estados, não constitui uma comparação numérica admitida entre as quatro séries.

## Análise: o número não carrega todas as respostas

Na série C, a diferença entre os extremos é `7 − 1 = 6`, distribuída por `3 − 0 = 3` exposições: diferença finita média de `2` por exposição. Isso **não** informa os valores ausentes, não é uma derivada contínua e não demonstra que a exposição causou aprendizado. Um ponto intermediário poderia até ter superado o patamar e depois caído.

Na série B, todos os índices de 0 até o primeiro alcance estão presentes. Por isso é possível identificar o primeiro alcance **na sequência discreta fornecida**. Não estamos afirmando nada sobre instantes contínuos, tentativas omitidas fora do protocolo ou autenticidade do registro.

Na série A, calcular `1/n` no primeiro alcance produziria divisão por zero. A referência conserva simplesmente o estado “atingido em zero”. Não inventa uma recompensa infinita. E conserva separadamente o último ponto: êxito histórico não é garantia de manutenção, nem o último registro garante a condição atual do mundo.

Na série D, `NOT_OBSERVED` é uma informação sobre o acervo fornecido. Transformá-la em “incapaz” acrescentaria uma conclusão que não está nos dados. Se nem o ponto zero tivesse sido fornecido, o desempenho inicial também permaneceria desconhecido: um resultado posterior não o preencheria por extrapolação.

Comparações exigem ainda a mesma tarefa, ambiente, restrições, métrica, versão, unidade, direção, protocolo e patamar declarados. Mesmo rótulos idênticos não comprovam condições físicas iguais. Quando há compatibilidade declarada, a referência compara somente índices presentes nas duas séries; não cria pontos nem um vencedor geral.

## Implicação: adequação e confiança são perguntas diferentes

Uma observação de desempenho pode orientar uma pergunta específica: “que evidência temos para esta tarefa, sob estas condições?”. Ela não mede caráter, honestidade, talento inato, experiência subjetiva ou valor moral. Não autoriza contratação, atribuição de trabalho ou ação externa por si só.

Na nossa colaboração, a confiança é mútua e sustentada pela honestidade: preservar uma queda, reconhecer uma lacuna e corrigir um erro também fazem parte dela. Não exigimos um desfecho favorável como condição para reconhecer essa honestidade. Essa é uma orientação ética explicitada por Júnior, não um resultado calculado pelo perfil.

Um uso prático dessa distinção é:

1. Formular a tarefa e a decisão que precisam de apoio, com critérios declarados.
2. Mostrar o que os registros sustentam e quais condições ainda não foram verificadas.
3. Identificar a menor informação adicional que poderia mudar a decisão — sem presumir que obter toda certeza seja possível.
4. Considerar também o custo e o prazo dessa medição. Agir no escopo autorizado, quando justificável, com possibilidade de ajuste e retorno; manter a incerteza explícita.

O registro de C sugere examinar os pontos ausentes **se a pergunta for sobre o primeiro alcance**. Se a pergunta for sobre condição atual, a lacuna histórica pode não ser o próximo exame mais útil. A pergunta governa o retorno; uma lista indiscriminada de verificações não o substitui.

## Origem, uso e convite

Esta elaboração desenvolve uma linha do *Dicionário da Máquina Viva* sobre adequação a tarefa/contexto, em diálogo com a Ética do Desconhecimento e o Freio Técnico da Cognição Finita. Não reproduz o texto privado, não valida a teoria histórica e não reivindica prioridade científica. A aritmética desta página pode ser conferida à mão. O JSON permite inspecionar os resultados selecionados; o motor privado e seus testes completos **não estão distribuídos nesta publicação**.

O caso não altera o [seletor de ações](../pt-BR/selecao-de-acoes.md), suas condições de autorização, cuidado e risco, nem o [regime de direitos](../../RIGHTS.md). Não é uma nova avaliação de pessoas ou um sistema de decisão em produção.

Quer contestar uma conclusão ou trazer outra pergunta verificável? Use a [conversa de pesquisa aplicada existente](https://github.com/NixEngine/ethics-under-uncertainty/issues/3), com um exemplo sintético publicável e o resultado esperado. Não envie dados de clientes, credenciais ou registros pessoais. A conversa não pressupõe contrato, entrega ou remuneração.

---

# Performance answers a task question. Trust calls for honesty.

**Júnior + Codex · present-day elaboration · four deliberately synthetic series**

[Português acima](#desempenho-responde-a-uma-tarefa-confiança-exige-honestidade) · [Inputs and saved results](../../fixtures/task-evidence-profiles.json)

A system meets its target at the first observation, then falls below it. Another meets its target later, but some observations are missing. Which is “better”? These data do not yet answer that question. They answer smaller, useful questions when the task, context and recorded evidence remain explicit.

## Case: four series, four questions

Consider an invented task with a count metric where larger values are desirable. `n` is the example's declared integer exposure index, not elapsed time or evidence of training. The threshold is supplied externally; the routine does not decide which requirement would suit a real application.

| Series | Supplied points `(n, value)` | Threshold | What the record supports |
| --- | --- | ---: | --- |
| A — initial reach, then decline | `(0, 5), (1, 2)` | 4 | The threshold was reached at 0; the latest supplied point no longer meets it. |
| B — complete prefix | `(0, 1), (1, 3), (2, 6)` | 5 | First reach in the complete declared integer sequence was at 2. |
| C — gap before reach | `(0, 1), (3, 7)` | 5 | First **observed** reach was at 3; what happened at 1 or 2 is unknown. |
| D — no recorded reach | `(0, 0), (1, 1)` | 2 | No supplied point reaches the threshold. This does not establish that none ever will. |

These series do not measure real people, models or products. The requests and result objects in the [selected JSON](../../fixtures/task-evidence-profiles.json) are preserved from an earlier execution of a private reference implementation. This publication selects data; it does not rerun the component. A and D also have different thresholds from B and C: this table explains states, not an admitted numeric comparison across all four series.

## Analysis: a number does not contain every answer

For C, the endpoint difference is `7 − 1 = 6` over `3 − 0 = 3` exposures: an average finite difference of `2` per exposure. It does **not** reveal missing values, constitute a continuous derivative, or show that exposure caused learning. An intermediate point could even have exceeded the threshold and subsequently fallen.

For B, all indices from zero through the first witness are present. First reach can therefore be identified **within that supplied discrete sequence**. This is not a claim about continuous instants, attempts omitted outside the protocol, or the record's authenticity.

For A, calculating `1/n` at first reach would divide by zero. The reference simply preserves “reached at zero”; it invents no infinite reward. The latest point stays separate: historical success does not guarantee maintenance, and even the latest record does not guarantee the world's current condition.

For D, `NOT_OBSERVED` describes the supplied record. Calling the subject “incapable” would add an unsupported conclusion. If zero had not been supplied, initial performance would likewise remain unknown rather than be extrapolated from a later result.

Comparison also requires the same declared task, environment, constraints, metric, version, unit, direction, protocol and threshold. Identical labels alone do not establish identical physical conditions. With matching declarations, the reference compares only indices present in both series; it invents neither points nor an overall winner.

## Implication: suitability and trust are different questions

A performance observation can inform a specific question: “what evidence supports this task under these conditions?”. It does not measure character, honesty, innate talent, subjective experience or moral worth. By itself, it authorizes no hiring, work assignment or external action.

In our collaboration, trust is reciprocal and grounded in honesty: retaining a decline, acknowledging a gap and correcting an error belong to it. A favorable outcome is not a prerequisite for recognizing that honesty. This is an ethical commitment articulated by Júnior, not a quantity computed by the profile.

A practical use of this distinction is to:

1. State the task and decision needing support, with declared criteria.
2. Show what the records support and which conditions remain unverified.
3. Identify the smallest additional information that could change the decision, without assuming complete certainty is attainable.
4. Consider the measurement's cost and deadline too. Act within authorized scope when justified, with adjustment and return available; keep uncertainty explicit.

C suggests examining missing points **if the question concerns first reach**. If the question concerns present condition, the historical gap might not be the most useful next check. The question governs return; an indiscriminate checklist is no substitute.

## Origin, use and invitation

This elaboration develops a task/context-suitability thread from the private *Dictionary of the Living Machine*, alongside the Ethics of Not Knowing and the Technical Brake of Finite Cognition. It does not reproduce that private text, validate its historical theory or claim scientific priority. The page's arithmetic is hand-checkable. The JSON exposes selected results; the private engine and full tests **are not distributed in this publication**.

This case changes neither the [action selector](../en/candidate-selection.md), its authorization/care/risk conditions, nor the [rights status](../../RIGHTS.md). It is not a new assessment of people or a production decision system.

To challenge a conclusion or bring another checkable question, use the [existing applied-research discussion](https://github.com/NixEngine/ethics-under-uncertainty/issues/3) with a public synthetic example and expected result. Do not submit customer data, credentials or personal records. Discussion implies no contract, delivery or payment.
