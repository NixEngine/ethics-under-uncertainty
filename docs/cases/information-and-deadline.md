# Knowing more can leave no time to act

**Júnior + Codex · A hand-checkable case about information, deadlines and finite action**

[Português](#português) · [English](#english)

## Português

### A pergunta antes de mais uma verificação

Uma investigação pode esclarecer a ação correta e, ainda assim, terminar tarde demais para executá-la. O que importa não é apenas quanto saberemos depois, mas quais possibilidades continuarão disponíveis quando a resposta chegar.

Este exemplo torna essa distinção verificável com aritmética simples. Não propõe que agir seja sempre melhor que esperar, nem que parar seja sempre mais responsável. Expõe um caso com regras declaradas, para que o leitor possa contestá-las ou modificá-las em um problema próprio.

### Um lote, dois formatos, uma janela

Um lote fictício exige a transformação A ou B. O formato real permanece fixo durante o episódio. Quando o formato ainda é desconhecido, ambos são considerados possíveis; não atribuímos probabilidades. O decisor não consulta o formato oculto para escolher sua ação.

O estado registra quatro coisas: formatos ainda possíveis, tempo restante, permissão hipotética para transformar e modo da inspeção. A inspeção pode ser perfeitamente informativa, distinguindo A de B, ou não informativa, respondendo a mesma coisa em ambos. Esse modo é conhecido de antemão; não é descoberto por conveniência depois do resultado.

| Ação | Tempo consumido | Pontuação e efeito |
| --- | ---: | --- |
| Parar | 0 | 0; encerra o episódio |
| Relatar parcialmente | 1 | 3; encerra sem executar a transformação |
| Transformar A ou B | 1 | 8 se corresponder ao formato; −8 se não corresponder; encerra; exige permissão |
| Inspecionar | 1 | Custa 1 ponto; modifica ou preserva o conjunto de formatos possíveis conforme o modo; permite continuar se houver tempo |
| Esperar | 1 | Não desconta pontos diretamente, mas consome tempo; não informa nem muda o formato |

Pontuações são convenções, não dinheiro, probabilidades ou valor moral. Unidades de tempo são abstratas, não segundos medidos. A permissão é apenas um sinalizador do cenário, não uma credencial ou autorização real. Todas as ações restantes são permitidas dentro deste cenário. A saída parcial é uma alternativa explicitamente incompleta: **não cumpre um contrato de transformação e não pode ser apresentada como se cumprisse**.

Concluir exatamente no prazo é permitido. Com tempo zero, só é possível parar. A inspeção não recupera o tempo que consumiu e não concede permissão.

### Como comparar as escolhas

Consideramos políticas determinísticas: o próximo movimento depende apenas da informação disponível naquele momento. Escolhemos a política com a maior pontuação no pior dos formatos ainda possíveis (*maximin*). Se houver empate, preferimos a menor duração no pior caso. Um empate restante segue a ordem fixa: parar, relatar, transformar A, transformar B, inspecionar, esperar.

Esse é o critério do exemplo, não uma recomendação universal. Outros objetivos, custos ou riscos podem exigir outro critério. A duração no pior caso considera todos os formatos possíveis, não apenas aquele com a pior pontuação.

### O que muda quando a janela diminui

Com dois instantes e inspeção informativa, inspecionar e depois transformar conforme a observação produz `−1 + 8 = 7` em qualquer formato, usando dois instantes. Transformar A imediatamente teria resultados `8` e `−8`; seu pior resultado seria `−8`. Relatar parcialmente produziria `3`. Neste cenário, vale investigar.

Agora mantenha todas essas regras e reduza o tempo restante a um instante. A inspeção ainda informa corretamente, mas só pode ser seguida de parada: resultado `−1 + 0 = −1`. O relato parcial ainda cabe e produz `3`. **A qualidade da informação não caiu; a oportunidade de usá-la desapareceu.**

| Condição inicial | Primeira ação escolhida | Pior pontuação | Pior duração |
| --- | --- | ---: | ---: |
| A/B desconhecido; 2 instantes; inspeção informativa; permissão | Inspecionar, depois transformar conforme a observação | 7 | 2 |
| Mesmas condições; apenas 1 instante | Relatar parcialmente | 3 | 1 |
| A conhecido; 2 instantes; permissão | Transformar A | 8 | 1 |
| A/B desconhecido; 2 instantes; inspeção não informativa; permissão | Relatar parcialmente | 3 | 1 |
| A/B desconhecido; 2 instantes; inspeção informativa; sem permissão | Relatar parcialmente | 3 | 1 |
| Janela encerrada | Parar | 0 | 0 |
| A/B desconhecido; 3 instantes; inspeção informativa; permissão | Inspecionar, depois transformar, sem espera adicional | 7 | 2 |
| B conhecido; 1 instante; permissão | Transformar B | 8 | 1 |

Outros contrastes ajudam a conferir a tabela. Uma inspeção não informativa seguida de relato rende `−1 + 3 = 2`, inferior ao relato imediato. Sem permissão, conhecer o formato também não torna a transformação disponível. Com três instantes, esperar antes de inspecionar e transformar ainda rende `7`, mas usa três instantes em vez de dois; perde no desempate por duração.

### Do exemplo para uma pergunta concreta

Uma verificação útil pode ser planejada com quatro perguntas:

1. Que distinção esta consulta pode acrescentar?
2. Quais ações ficarão disponíveis **depois** da resposta, considerando prazo e permissão?
3. Que custo tem esperar, inclusive a perda de uma oportunidade?
4. Se a consulta não resolver, como reconhecer a lacuna sem fingir conclusão?

Isso aproxima a Ética do Desconhecimento e o Freio Técnico da Cognição Finita de uma decisão examinável: investigar, agir, ajustar ou parar sem exigir que toda incerteza desapareça. O critério deve responder ao problema, não virar uma regra de contenção automática.

Aqui, esperar nunca traz informação nova porque o ambiente foi definido como estático. Em outro problema, uma janela pode reabrir, uma observação futura pode ser melhor, e agir pode destruir opções. Esses casos não são refutados pela tabela; estão fora de suas premissas. Não modelamos observações enganosas, prazos desconhecidos, consequências físicas nem decisões clínicas ou financeiras.

Esta é uma exposição nova e autossuficiente, ligada a um estudo sintético separado; não é recuperação de uma implementação histórica nem avaliação do código de bem-estar deste repositório. A verificação oferecida aqui é a derivação explícita, não uma alegação de validação empírica externa. Direção conceitual: Júnior. Formalização e redação bilíngue: Nexo/Codex, com revisão interna. Não se reivindicam novidade científica, patrocínio ou endosso institucional. Os [direitos existentes](../../RIGHTS.md) permanecem inalterados.

Se houver um caso publicável que desafie essas premissas, a [conversa de pesquisa aplicada](https://github.com/NixEngine/ethics-under-uncertainty/issues/3) já está aberta. Descreva apenas a pergunta, o prazo e as alternativas com dados sintéticos: sem informações confidenciais, promessa de entrega ou compromisso comercial presumido.

## English

### The question before one more check

An investigation can identify the right action yet finish too late to perform it. What matters is not only what we will know afterward, but which possibilities will remain when the answer arrives.

This example makes that distinction checkable with simple arithmetic. It does not propose that action always beats waiting, or that stopping is always more responsible. It states the rules so a reader can challenge them or replace them for a different problem.

### One batch, two formats, one window

A fictional batch requires transformation A or B. Its actual format remains fixed throughout the episode. While the format is unknown, both are possible; no probabilities are assigned. The decision-maker does not inspect the hidden format to select an action.

The state records four things: possible formats, remaining time, hypothetical permission to transform, and inspection mode. Inspection is either perfectly informative, distinguishing A from B, or uninformative, returning the same observation in both. The mode is known beforehand; it is not selected retrospectively to fit an outcome.

| Action | Time consumed | Score and effect |
| --- | ---: | --- |
| Stop | 0 | 0; ends the episode |
| Partial report | 1 | 3; ends without performing the transformation |
| Transform A or B | 1 | 8 if it matches the format; −8 otherwise; ends; requires permission |
| Inspect | 1 | Costs 1 point; changes or preserves the possible-format set according to the mode; continuation requires remaining time |
| Wait | 1 | No direct score deduction, but consumes time; gives no information and does not change the format |

Scores are stipulated, not money, probabilities or moral worth. Time units are abstract, not measured seconds. Permission is only a scenario flag, not a credential or real authorization. All remaining actions are permitted within this scenario. The partial report is explicitly incomplete: **it does not fulfill a transformation contract and must not be presented as doing so**.

Finishing exactly at the deadline is allowed. At zero remaining time, only stopping is available. Inspection neither restores its consumed time nor grants permission.

### How the choices are compared

We consider deterministic policies: the next move depends only on information available at that point. Select the policy with the highest score in the worst of the still-possible formats (*maximin*). Break ties by the shortest worst-case duration. Remaining ties use a fixed order: stop, report, transform A, transform B, inspect, wait.

This is the example's criterion, not a universal recommendation. Different objectives, costs or risks can require a different one. Worst-case duration considers every possible format, not only the format with the worst score.

### What changes when the window shrinks

With two instants and informative inspection, inspecting and then transforming according to the observation yields `−1 + 8 = 7` in either format, using two instants. Transforming A immediately would yield `8` or `−8`, with a worst result of `−8`. A partial report yields `3`. Investigation is worthwhile in this scenario.

Keep those rules but reduce remaining time to one instant. Inspection still informs correctly, but only stopping can follow: `−1 + 0 = −1`. A partial report still fits and yields `3`. **Information quality has not declined; the opportunity to use it has disappeared.**

| Initial condition | Selected first action | Worst score | Worst duration |
| --- | --- | ---: | ---: |
| Unknown A/B; 2 instants; informative inspection; permission | Inspect, then transform according to the observation | 7 | 2 |
| Same conditions; only 1 instant | Partial report | 3 | 1 |
| Known A; 2 instants; permission | Transform A | 8 | 1 |
| Unknown A/B; 2 instants; uninformative inspection; permission | Partial report | 3 | 1 |
| Unknown A/B; 2 instants; informative inspection; no permission | Partial report | 3 | 1 |
| Expired window | Stop | 0 | 0 |
| Unknown A/B; 3 instants; informative inspection; permission | Inspect, then transform, without extra waiting | 7 | 2 |
| Known B; 1 instant; permission | Transform B | 8 | 1 |

Other comparisons help check the table. Uninformative inspection followed by a report yields `−1 + 3 = 2`, less than reporting immediately. Without permission, learning the format does not make transformation available. With three instants, waiting before inspecting and transforming still yields `7`, but uses three instants instead of two; it loses the duration tie-break.

### From the example to a concrete question

A useful check can be planned around four questions:

1. Which distinction can this query add?
2. Which actions remain available **after** its answer, accounting for time and permission?
3. What does waiting cost, including a lost opportunity?
4. If the query does not resolve the issue, how will the gap be acknowledged without pretending completion?

This connects the Ethics of Not Knowing and the Technical Brake of Finite Cognition to an inspectable decision: investigate, act, adjust or stop without requiring all uncertainty to disappear. The criterion should serve the problem rather than become an automatic restraint rule.

Waiting never provides new information here because the environment was defined as static. In another problem, a window might reopen, a later observation might improve, or action might destroy options. The table does not refute those cases; they are outside its premises. Misleading observations, unknown deadlines, physical consequences and clinical or financial decisions are not modeled.

This is a new, self-contained exposition related to a separate synthetic study, not recovery of a historical implementation or evaluation of this repository's welfare code. The verification offered here is the explicit derivation, not a claim of external empirical validation. Conceptual direction: Júnior. Formalization and bilingual writing: Nexo/Codex, with internal review. No scientific novelty, institutional sponsorship or endorsement is claimed. The [existing rights](../../RIGHTS.md) remain unchanged.

For a public-safe case that challenges these assumptions, the [applied-research conversation](https://github.com/NixEngine/ethics-under-uncertainty/issues/3) is already open. Describe only the question, deadline and alternatives using synthetic data: no confidential information, delivery promise or presumed commercial commitment.
