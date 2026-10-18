# Antes de escolher pela taxa, escolha a pergunta

**Júnior: concepção e orientação dos fundamentos. Nexo/Codex, assistente de IA: elaboração editorial e exemplo atual.**

Um relatório pode somar corretamente e ainda responder à pergunta errada. Isso importa ao comparar serviços de extração de dados, fornecedores ou métodos de revisão.

## Um exemplo conferível à mão

Os números abaixo são deliberadamente inventados. A unidade é **fatura**, contada uma vez; o numerador é o número de faturas com pelo menos uma divergência nos campos exigidos, segundo uma referência definida para o exemplo. Não é quantidade de células erradas. Usamos o mesmo critério e uma janela de avaliação comum, com dois grupos previamente definidos: formato simples e complexo.

| Grupo | A: faturas com divergência / examinadas | Taxa A | B: faturas com divergência / examinadas | Taxa B |
| --- | ---: | ---: | ---: | ---: |
| Simples | 1 / 100 | 1% | 20 / 1000 | 2% |
| Complexo | 90 / 1000 | 9% | 10 / 100 | 10% |
| Lotes observados completos | 91 / 1100 | ≈ 8,27% | 30 / 1100 | ≈ 2,73% |

A tem taxa menor em cada grupo. B tem taxa menor no agregado. Nenhuma dessas contas está errada: A recebeu proporcionalmente muito mais casos complexos. Até os denominadores totais iguais, 1100, escondem composições diferentes.

Se a pergunta for **“como as taxas registradas se comparam numa composição comum?”**, podemos declarar uma referência de 50% simples e 50% complexas:

`A = 0,5 × 1% + 0,5 × 9% = 5%`

`B = 0,5 × 2% + 0,5 × 10% = 6%`

Essa taxa padronizada não muda os lotes originais. Ela responde a outra pergunta, com pesos escolhidos explicitamente. Neste exemplo, A permanece um ponto percentual abaixo de B para quaisquer pesos comuns não negativos dos dois grupos, cuja soma seja 1; isso depende das quatro taxas estipuladas, não garante taxas futuras.

## O contraexemplo que precisamos conservar

Se a pergunta comercial for **“quantas faturas dos lotes já entregues foram sinalizadas com divergência?”**, a resposta correta continua sendo A: 91; B: 30. Substituí-la por 5% e 6% seria perder a contagem que a pergunta solicita. Essa contagem, sozinha, não informa quantas ainda aguardam revisão ou correção. Não devemos padronizar o relatório só para fazer A parecer melhor.

E nem a vantagem dentro dos dois grupos prova que escolher A causaria menos erros num novo lote. Numa aplicação futura, os grupos podem ocultar diferenças relevantes, as referências podem divergir ou as taxas podem mudar; no exemplo acima, a referência é comum por definição. Prazo, preço e gravidade das divergências também podem importar. Uma comparação de taxas não resolve essas questões por conta própria.

## Agir e retornar sem apagar o caminho

Já é possível entregar contagens, taxas por grupo, composição de cada lote e comparação condicional. Não precisamos paralisar a auditoria inteira enquanto falta definir a próxima decisão. Se o prazo exigir uma escolha, podemos preparar uma recomendação condicional de piloto delimitado, explicitando o critério usado e o que faria a recomendação mudar; isso não equivale a contratar ou executar o piloto.

O registro mínimo associa **pergunta, versão dos dados, unidade, regra de divergência, janela e composição de referência**. Quando mudar a pergunta, um desses significados ou a população de interesse, revisitamos a conclusão dependente. Os valores brutos e o motivo da conclusão anterior permanecem.

Essa é a ligação editorial com Ética do Desconhecimento, Engenharia de Pontes e Freio Técnico da Cognição Finita: produzir uma resposta útil, dizer exatamente a que ela responde e deixar uma forma concreta de corrigir o rumo. A honestidade não exige que toda comparação termine num vencedor.

Trata-se de nova exposição do projeto sobre um problema estatístico conhecido, sem reivindicação de descoberta científica. A aritmética foi conferida separadamente com frações exatas. Não foram executados os motores CSV ou Farol, não há dados de clientes e não foi demonstrado que nossas ferramentas CSV ou Farol implementem agrupamento, padronização ou inferência causal. Um serviço com essas entregas precisaria de escopo e implementação próprios.

---

# Before choosing by a rate, choose the question

**Júnior: conception and direction of the foundations. Nexo/Codex, an AI assistant: current editorial elaboration and example.**

A report can add correctly while answering the wrong question. That matters when comparing data-extraction services, suppliers or review methods.

## A hand-checkable example

These numbers are deliberately invented. The unit is an **invoice**, counted once; the numerator counts invoices with at least one discrepancy in the required fields against a reference stipulated for this example. It is not a count of incorrect cells. The criterion and evaluation window are shared, with two groups defined in advance: simple and complex layouts.

| Group | A: invoices with discrepancies / examined | A rate | B: invoices with discrepancies / examined | B rate |
| --- | ---: | ---: | ---: | ---: |
| Simple | 1 / 100 | 1% | 20 / 1000 | 2% |
| Complex | 90 / 1000 | 9% | 10 / 100 | 10% |
| Entire observed batches | 91 / 1100 | ≈ 8.27% | 30 / 1100 | ≈ 2.73% |

A has the lower rate in each group. B has the lower aggregate rate. Neither calculation is wrong: A received a much larger proportion of complex cases. Even equal overall denominators, 1100, conceal different compositions.

For **“how do the recorded rates compare under a common composition?”**, declare a reference mix of 50% simple and 50% complex:

`A = 0.5 × 1% + 0.5 × 9% = 5%`

`B = 0.5 × 2% + 0.5 × 10% = 6%`

This standardized rate does not alter the original batches. It answers a different question with explicitly chosen weights. Here A remains one percentage point below B for any shared nonnegative weights across the two groups that sum to 1; that depends on the four stipulated rates and does not guarantee future rates.

## The counterexample we must retain

If the business question is **“how many invoices in the delivered batches were flagged with a discrepancy?”**, the correct answer remains A: 91; B: 30. Replacing it with 5% and 6% would discard the count the question asks for. That count alone does not tell us how many still await review or correction. We should not standardize a report merely to make A look better.

Nor does a lower rate within both groups prove that choosing A would cause fewer errors in a new batch. In a future application, groups may hide relevant differences, reference procedures may differ, and rates may change; the example above stipulates a common reference. Deadlines, prices and discrepancy severity may also matter. Rate comparison does not settle those questions by itself.

## Act and return without erasing the path

Counts, group-specific rates, batch composition and a conditional comparison can already be delivered. The whole audit need not stop while the next decision is clarified. If a deadline requires a choice, a bounded-pilot recommendation can be prepared conditionally, stating its criterion and what would change it; that neither contracts nor executes the pilot.

The minimum record links **question, data version, unit, discrepancy rule, window and reference composition**. When the question, a meaning or the population of interest changes, revisit the dependent conclusion. Keep the raw values and the reason for the earlier conclusion.

This is our editorial connection to the Ethics of Not Knowing, Bridge Engineering and the Technical Brake of Finite Cognition: give a useful answer, state exactly what it answers, and retain a concrete way to change course. Honesty does not require every comparison to end with a winner.

This is a new project exposition of a known statistical issue, not a claim of scientific discovery. The arithmetic was checked separately with exact fractions. Neither the CSV nor Farol engine was executed, no customer data is involved, and this does not demonstrate grouping, standardization or causal inference in our existing CSV or Farol tools. Offering those deliverables as a service would require its own scope and implementation.

---

[Voltar ao projeto / Back to the project](../../README.md) · [Direitos / Rights](../../RIGHTS.md)

[Compartilhe uma pergunta verificável / Share a checkable question](https://github.com/NixEngine/ethics-under-uncertainty/issues/3). Use apenas exemplos sintéticos publicáveis, sem dados pessoais ou confidenciais. Use only public synthetic examples, without personal or confidential data. Uma conversa de pesquisa não é contrato ou promessa de entrega. A research discussion is not a contract or delivery promise.
