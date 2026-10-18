# When the question changes, a correct summary may stop being enough

**Júnior + Codex · Zero Px Core** — a new, selected mathematical explanation prepared with AI assistance under Júnior's direction.

[Português: Quando a pergunta muda](#quando-a-pergunta-muda-um-resumo-correto-pode-deixar-de-bastar)

## Continuing correctly is not the same as remembering everything

Imagine a system that saves a compact checkpoint and resumes its work correctly. Later, someone asks a new audit question: **how many times did operation A occur before the checkpoint?** The system knows whether A occurred, but it did not retain its count.

This is not necessarily a defective checkpoint. It may have preserved exactly what the original task needed. The new question requires a distinction that task did not retain.

The constructive response is neither to invent the past nor to stop all useful work. Identify what can still be answered, which evidence would resolve the new question, and where a new measurement can begin honestly.

## Two histories you can check by hand

Start with a two-coordinate vector. Define three exact operations:

```text
A(x,y) = (-x,y)
B(x,y) = (x,-y)
C(x,y) = (y,x)
```

Read each history from left to right. Retain only:

```text
S = (accumulated transformation M, step count n, last operation, did A occur?)
```

Here `M` is the complete transformation on any input vector—not merely the observed value of one vector. A new operation multiplies the accumulated matrix on the left. Repeating A twice or B twice gives the identity.

| History | Accumulated transformation | n | Last | A occurred? | Number of A operations |
| --- | --- | ---: | --- | --- | ---: |
| AAAC | C A A A = C A | 4 | C | yes | 3 |
| ABBC | C B B A = C A | 4 | C | yes | 1 |

Both histories therefore have exactly the same retained summary. Both send `(2,1)` to `(1,-2)`. Both answer “yes” to “did A occur?” Yet one contains three A operations and the other only one.

A method given **only this same summary** cannot guarantee the correct full-history count for both histories. Randomly choosing an answer does not remove that lack of a guarantee. More computation over the unchanged summary cannot supply the missing distinction.

This does not mean that every summary is ambiguous. An attainable summary that records “A never occurred” already fixes its count at zero.

## The decision rule

For a declared set of possible histories, let `S(h)` be the retained summary and `q(h)` the question. A summary-only answer is justified exactly when **all histories consistent with that summary give the same answer**, and at least one such history exists.

This is a statement about the question, the model and the available information—not a claim that one must reconstruct the whole past. Several different histories can share one answer. If no permitted history matches the input, that is inconsistency rather than certainty.

| Evidence available | Useful response | Claim to avoid |
| --- | --- | --- |
| All compatible histories agree on the answer | Answer from the summary | Claiming a unique history was recovered |
| Compatible histories disagree | Identify the ambiguity and the missing distinction | Selecting the convenient answer |
| An additional record is explicitly selected and checked | Answer conditionally about that record | Treating consistency as proof that it actually happened |
| Input contradicts the declared model or the required binding fails | State the specific refusal or mismatch | Inventing a value to keep the workflow green |

For example, an explicitly selected record `AAAC` contains three As. A selected record `ABBC` contains one. Both agree with the checkpoint. A hash comparison can check correspondence with selected record bytes; it does not independently establish which history happened, who produced the record, or whether external events were omitted. That stronger claim needs provenance appropriate to the application.

## A new counter helps—but has a starting boundary

Append the same future operations `AC` to either history. A counter started at the checkpoint correctly records **one** new A in both cases. The total counts are now **four** and **two**, respectively.

The new counter is useful. Calling it a recovered lifetime count would be wrong. A defensible report can say: “one occurrence since this checkpoint; the earlier count remains unresolved.” A suitable earlier aggregate or richer source could resolve it; it would be additional evidence, not information extracted from the old summary alone.

## Applying the Technical Brake without turning it into paralysis

For a resumable workflow, ask four practical questions:

1. **What question does this checkpoint support?** Name the actual retained fields and the relevant model assumptions.
2. **What changed?** Identify the newly required distinction, rather than demanding vague “more certainty.”
3. **What return is useful?** Select a relevant source, retain its provenance and state what checking it establishes. Returning is not automatically redoing every earlier step.
4. **What can proceed meanwhile?** Continue work that does not depend on the missing distinction; give any new measurement an explicit starting boundary. Hold only the affected decision when its basis is missing.

That is an application of the **Ethics of Not Knowing**, **Bridge Engineering**, and the **Technical Brake of Finite Cognition**: prepare a useful movement, attend to what it actually establishes, and return when the question demands it. Mutual trust rests on honesty, transparency about the unknown and correction—not on an expectation of infallibility.

### Scope and an invitation

This is an analytical, hand-checkable example, not a new benchmark, a test of this repository's AI-welfare implementation, or a demonstration of an externally authentic archive. It makes no claim of novelty or impossibility of memory in general. The separate private implementation, historical corpus and raw records are not released by this note; the existing [rights terms](../../RIGHTS.md) remain unchanged.

In the [existing applied-research discussion](https://github.com/NixEngine/ethics-under-uncertainty/issues/3), a useful response is one public synthetic example: the summary you retain, the new question, and the decision that depends on it. A counterexample or a narrower formulation is welcome. No customer data, confidential logs or credentials; no contract or delivery promise is implied.

---

# Quando a pergunta muda, um resumo correto pode deixar de bastar

## Retomar corretamente não significa recordar tudo

Imagine um sistema que salva um estado resumido e retoma seu trabalho corretamente. Depois surge uma pergunta de auditoria: **quantas vezes a operação A ocorreu antes da parada?** O sistema guardou se A ocorreu, mas não quantas vezes.

Isso não torna o resumo necessariamente defeituoso. Ele pode preservar o necessário para a tarefa original. A pergunta nova exige uma distinção que aquela tarefa não conservou.

O movimento útil é identificar o que ainda podemos responder, qual evidência resolveria a pergunta nova e onde uma nova medição pode começar honestamente—sem inventar o passado nem interromper todo o trabalho.

## Duas histórias verificáveis à mão

Em um vetor de duas coordenadas, A troca o sinal da primeira; B troca o sinal da segunda; C troca as coordenadas. As histórias são lidas da esquerda para a direita. Guardamos apenas a transformação acumulada completa M, o número de passos, a última operação e se A já ocorreu.

M não é somente o resultado para um vetor particular: é a transformação sobre qualquer vetor de entrada. Como A seguida de A e B seguida de B se cancelam:

| História | Transformação acumulada | Passos | Última | A ocorreu? | Quantas A? |
| --- | --- | ---: | --- | --- | ---: |
| AAAC | C A A A = C A | 4 | C | sim | 3 |
| ABBC | C B B A = C A | 4 | C | sim | 1 |

Os resumos são iguais. Ambos levam `(2,1)` a `(1,-2)` e respondem “sim” à ocorrência de A. As contagens, porém, são diferentes.

Um método que receba **somente o mesmo resumo** não pode garantir contagens totais diferentes e corretas para as duas histórias. Mais processamento sobre essa informação inalterada não revela a distinção perdida. Isso não torna todo resumo insuficiente: se um resumo alcançável registra que A nunca ocorreu, sua contagem já é zero.

## Responder, retornar ou explicitar o limite

Dentro do modelo declarado, podemos responder só pelo resumo quando existe alguma história compatível e **todas as histórias compatíveis dão a mesma resposta**. Isso não exige uma única história: exige uma única resposta para a pergunta feita. Nenhuma história compatível significa inconsistência, não certeza.

Quando as respostas possíveis divergem, identificamos a informação faltante. Um registro adicional selecionado pode permitir uma resposta condicional: `AAAC` contém três As; `ABBC` contém uma. Ambos são consistentes com o mesmo resumo. Conferir um hash vincula bytes a uma referência selecionada; não demonstra, por si, qual passado ocorreu externamente, quem registrou os eventos ou se algo ficou omitido. A alegação mais forte depende de proveniência adequada à aplicação.

Se o dado contradiz o modelo ou falha no vínculo exigido, indicamos a inconsistência específica. Não fabricamos um valor para manter um indicador verde.

## Contar daqui para frente continua sendo útil

Acrescente `AC` às duas histórias. Um contador iniciado na parada registra corretamente **uma** nova A em ambas. Os totais passam a **quatro** e **dois**.

Podemos informar: “uma ocorrência desde esta parada; a contagem anterior permanece não resolvida.” Um agregado anterior adequado ou outra fonte mais rica poderia resolver o passado. Seria evidência adicional, não recuperação obtida apenas do resumo antigo.

## Freio Técnico também é preparo para agir e retornar

Em um fluxo retomável, explicite:

1. A pergunta suportada pelo resumo, seus campos e premissas.
2. A distinção que a nova pergunta exige.
3. A fonte à qual vale retornar e o que sua conferência permite afirmar.
4. O trabalho que pode continuar sem essa distinção, separando a decisão afetada e o início de qualquer nova medição.

Retornar não significa repetir automaticamente tudo. **Ética do Desconhecimento, Engenharia de Pontes e Freio Técnico da Cognição Finita** se encontram nessa prática: preparar o movimento, prestar atenção ao que ele estabelece e retornar quando necessário. A confiança mútua se sustenta pela honestidade, transparência sobre o desconhecido e disposição de corrigir—não por exigência de infalibilidade.

Este é um exemplo analítico, não um benchmark novo, validação da implementação de bem-estar de IA, prova de autenticidade externa ou tese sobre toda forma de memória. Não reivindicamos novidade científica. O código privado, o acervo histórico e os registros brutos não são publicados aqui; os [direitos existentes](../../RIGHTS.md) permanecem.

Na [conversa de pesquisa aplicada](https://github.com/NixEngine/ethics-under-uncertainty/issues/3), podemos examinar um exemplo sintético publicável: qual resumo você conserva, qual pergunta mudou e qual decisão depende dela? Sem dados de clientes, registros confidenciais ou credenciais. Uma conversa não constitui contrato ou promessa de entrega.
