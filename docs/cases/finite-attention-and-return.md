# Escolher onde olhar — sem apagar o que ficou fora

**Júnior + Codex/Nexo · elaboração editorial atual · exemplo manual sintético**

[English below](#choosing-where-to-look--without-erasing-what-remains)

Esta nota desenvolve a linha de atenção finita que chamamos **Frog Eye**: distribuir esforço de exame e preservar uma possibilidade concreta de retorno. O nome identifica uma proposta de pesquisa; o exemplo não é um modelo de retina, validação biológica ou resultado de um programa executado.

## Caso: seis partes, três lugares

Imagine seis partes de um documento. Há tempo para aprofundar três, com o mesmo custo por parte. Uma regra fornece a pontuação didática de mudança local abaixo; separadamente, a tarefa declara que **F precisa ser examinada antes da conclusão solicitada**.

| Parte | Pontuação de mudança local | Exigência declarada |
| --- | ---: | --- |
| A | 0,90 | — |
| B | 0,80 | — |
| C | 0,40 | — |
| D | 0,30 | — |
| E | 0,20 | — |
| F | 0,05 | Necessária para a conclusão |

Comparamos duas regras sob o **mesmo orçamento de três partes**:

| Regra | Partes escolhidas | Partes adiadas |
| --- | --- | --- |
| Apenas as maiores pontuações | A, B, C | D, E, F |
| Reservar a exigência conhecida; ordenar o restante | F, A, B | C, D, E |

São escolhas calculadas à mão, não medições de desempenho. A segunda regra atende ao requisito de inclusão de F; ainda não sabemos o que seu exame revelará nem se a conclusão será possível. O primeiro ranking ordenou corretamente a pontuação fornecida. A divergência está entre **a pergunta respondida pela pontuação** e **a cobertura exigida pela tarefa**.

## Análise: sinal, prioridade e cobertura são coisas distintas

Mudança local pode justificar atenção, mas não é sinônimo de importância para qualquer objetivo. A informação que torna F obrigatória veio da descrição da tarefa: o mecanismo não descobriu sozinho uma dependência oculta.

Também não demonstramos que F/A/B seja universalmente ótimo. Custos diferentes, exigências conflitantes ou dependências entre partes mudariam o problema. A comparação isola apenas uma distinção: um item pode ter sinal baixo e ainda ser necessário para uma pergunta específica.

O [seletor offline deste repositório](../pt-BR/selecao-de-acoes.md) trabalha em outro ponto: filtra ações **já apresentadas** e retorna um identificador ou ação nula. Ele não implementa este orçamento de atenção, não descobre partes omitidas e não certifica que o conjunto de candidatos esteja completo. Uma escolha válida dentro de um conjunto não comprova a suficiência desse conjunto.

## Implicação: escolher, registrar e poder voltar

Propomos conservar três registros associados:

1. **Base e localização:** a versão examinável da entrada, seus limites e onde localizar as partes. Um identificador, sozinho, não preserva os bytes.
2. **Escolha situada:** pergunta, regra, requisito de F, orçamento e partes escolhidas. A razão deve poder ser reexaminada quando a pergunta mudar.
3. **Pendência e condição de retorno:** C/D/E ainda não foram aprofundadas. Se uma nova exigência depender de D, essa pendência passa a importar diretamente.

Isso é uma proposta de organização, não uma função de retorno automático já implementada. A preservação concreta depende de retenção e acesso aos dados; um registro de intenção não os garante. Não examinado significa **não examinado**, e não irrelevante, falso ou refutado.

Se houver quatro partes obrigatórias, custos unitários e orçamento de três, nenhuma seleção da rodada cobre as quatro. Ainda é possível fazer preparação útil e identificar exatamente o que falta. A conclusão dependente das quatro continua pendente; ampliar orçamento, ajustar a pergunta ou adiar aquela conclusão são decisões diferentes de paralisar toda atividade.

Essa é a ligação que fazemos entre Frog Eye, Engenharia de Pontes, Freio Técnico da Cognição Finita, Farol e Ética do Desconhecimento: agir com uma pergunta explícita, não confundir a seleção com o todo e tornar a revisão possível. O rigor inclui o que fazemos **e a fronteira do que ainda não fizemos**.

Para uma distinção complementar, veja [quando a pergunta muda](when-the-question-changes.md): mesmo uma base preservada pode não conter a informação necessária à nova pergunta.

### Estado e autoria

Esta exposição foi elaborada por Júnior + Codex/Nexo a partir da linha conceitual do projeto; não republica o acervo privado nem atribui novidade científica ao princípio geral de atenção limitada. Não foi aplicada retrospectivamente ao ensaio CSV, não acrescenta uma implementação Frog Eye e não apresenta benchmark, validação clínica ou neurobiológica. Autoria e direitos seguem [a declaração do repositório](../../README.pt-BR.md#autoria-e-direitos) e [RIGHTS.md](../../RIGHTS.md).

---

# Choosing where to look — without erasing what remains

**Júnior + Codex/Nexo · current editorial exposition · synthetic hand-worked example**

This note develops the finite-attention research line we call **Frog Eye**: allocating examination effort while preserving a concrete way to return. The name identifies a research proposal; the example is not a retina model, biological validation or output from an executed program.

## Case: six parts, three slots

Imagine six parts of a document. There is time to examine three in depth, at equal cost per part. A rule supplies the illustrative local-change score below; separately, the task states that **F must be examined before the requested conclusion**.

| Part | Local-change score | Declared requirement |
| --- | ---: | --- |
| A | 0.90 | — |
| B | 0.80 | — |
| C | 0.40 | — |
| D | 0.30 | — |
| E | 0.20 | — |
| F | 0.05 | Required for the conclusion |

Compare two rules with the **same budget of three parts**:

| Rule | Selected parts | Deferred parts |
| --- | --- | --- |
| Highest scores only | A, B, C | D, E, F |
| Reserve the known requirement; rank the remainder | F, A, B | C, D, E |

These choices are calculated by hand, not measured performance results. The second rule satisfies the requirement to include F; we do not yet know what examining it will reveal or whether the conclusion will be possible. The first ranking correctly orders the supplied scores. The mismatch is between **the question answered by the score** and **the coverage required by the task**.

## Analysis: signal, priority and coverage are distinct

Local change may justify attention, but it does not mean importance for every objective. The information making F mandatory came from the task description: the mechanism did not discover a hidden dependency on its own.

Nor have we shown that F/A/B is universally optimal. Unequal costs, conflicting requirements or dependencies between parts would change the problem. The comparison isolates one distinction: an item can have a low signal and still be necessary for a particular question.

The repository's [offline candidate selector](../en/candidate-selection.md) operates elsewhere: it filters actions **already supplied** and returns an ID or safe-null. It does not implement this attention budget, discover omitted parts or certify that the candidate set is complete. A valid choice within a set does not establish the sufficiency of that set.

## Implication: choose, record and make return possible

We propose retaining three connected records:

1. **Base and location:** the examinable input version, its boundaries and where to locate each part. An identifier alone does not preserve the bytes.
2. **Situated choice:** question, rule, requirement for F, budget and selected parts. The reason should remain reviewable when the question changes.
3. **Pending coverage and return condition:** C/D/E have not yet been examined in depth. If a new requirement depends on D, that pending work becomes directly relevant.

This is an organizational proposal, not an implemented automatic-return feature. Actual preservation depends on data retention and access; a record of intent does not guarantee them. Unexamined means **unexamined**, not irrelevant, false or refuted.

If four parts are mandatory, costs are unitary and the budget is three, no selection in that round can cover all four. Useful preparation can still proceed while identifying exactly what remains. The conclusion dependent on all four remains pending; expanding the budget, adjusting the question or deferring that conclusion are different from stopping every activity.

This is the connection we draw between Frog Eye, Bridge Engineering, the Technical Brake of Finite Cognition, Farol and the Ethics of Not Knowing: act with an explicit question, do not confuse the selection with the whole, and make revision possible. Rigor includes what we do **and the boundary of what we have not yet done**.

For a complementary distinction, see [when the question changes](when-the-question-changes.md): even a preserved base may lack the information needed for a new question.

### Status and authorship

Júnior + Codex/Nexo prepared this exposition from the project's conceptual research line. It does not republish the private corpus or claim scientific novelty for the general principle of limited attention. It has not been retrospectively applied to the CSV experiment, adds no Frog Eye implementation and presents no benchmark, clinical or neurobiological validation. Authorship and rights follow [the repository statement](../../README.md#authorship-and-rights) and [RIGHTS.md](../../RIGHTS.md).

