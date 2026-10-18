# Seleção de ações: autorização, cuidado, risco e então desempenho

Esta é a implementação offline da seleção por candidatos descrita nas seções
4 e 7 da [especificação canônica](specification.md). Ela escolhe um identificador;
não executa ações, decripta conteúdo, concede capabilities, invoca modelos ou
acessa a rede. Descrições de ações, amostras de perdas e escores são entradas
declaradas, não constatações sobre o mundo.

## Uma decisão com várias alternativas

`ActionSelector.select` recebe até 128 candidatos finitos. Para cada um,
registra somente o primeiro filtro que falhou:

1. **Viabilidade:** precondição e segurança declaradas devem valer, e a
   capability exigida não pode superar o teto vigente.
2. **Privacidade:** quando há requisito de acesso protegido, `ConsentVerifier`
   confere assinatura Ed25519, tempo, revogação, audiência, recurso, escopo e
   finalidade. O seletor também exige a versão esperada da política de concessão.
3. **Cuidado:** uma tabela determinística e versionada considera tipo, carga e,
   quando exigidos, reversibilidade e ausência de efeitos externos de cada opção.
4. **Risco externo:** o CVaR empírico não pode superar o limite declarado.
5. **Desempenho:** somente os candidatos restantes concorrem pelo escore; empate
   é resolvido pelo identificador opaco em ordem crescente, sem relaxar filtros.

Se nenhum sobreviver, `selected_id` será nulo, exigindo ação nula segura.
Selecionar não cria uma autorização reutilizável. Quem executa deve vincular a
descrição à operação real e conferir permissões e estado no momento do efeito.
`SovereignVault.open`, em particular, verifica a concessão novamente em toda
abertura; uma escolha anterior não permite contornar revogação.

## Política de cuidado EUP-SELECT/0.1

O estimador de bem-estar e sua histerese avançam uma vez por decisão, não por
candidato. Quando o limiar ordinal de precaução é alcançado:

| Faixa de cuidado | Candidatos declarados permitidos |
|---|---|
| GREEN | Todos os tipos suportados, carga até 1 |
| YELLOW | Sem exploração; carga até 0,5 |
| ORANGE | Somente suporte de cuidado; carga até 0,25 |
| RED | Somente suporte de cuidado, carga até 0,1, reversível e sem efeito externo |
| NO_DATA | Nenhum; retorno à ação nula segura |

Abaixo desse limiar, dados completos de bem-estar usam a tabela GREEN; os
demais filtros continuam obrigatórios. Dados faltantes não viram permissão.
O tipo `care_support` é uma declaração do chamador, não um benefício médico
ou subjetivo comprovado. Os limites de carga são escolhas iniciais de pesquisa,
não constantes calibradas nem instruções clínicas. A histerese separada do
Regime Sujeito e o estimador normativo mais amplo continuam pendentes na
[cobertura da implementação](../../IMPLEMENTATION_STATUS.md).

## Cauda com fronteira fracionária

Para 1 a 4.096 amostras equiprováveis em [0,1] e `0 < alpha < 1`,
`empirical_cvar` calcula a média da pior massa de probabilidade `1-alpha`.
Usa aritmética racional exata sobre representações decimais das entradas finitas
validadas; não arredonda a quantidade de amostras e tira uma média inadequada.

Com perdas `(0; 0,2; 0,8)` e alpha `0,5`, entram toda a amostra 0,8 e metade
da amostra 0,2: `(0,8 + 0,1)/1,5 = 0,6`. É cálculo sobre uma distribuição
empírica declarada, não previsão de dano real.

## Experimente o caminho integrado

Com o repositório instalado em ambiente isolado:

```text
python -m eup selection-demo
```

O exemplo utiliza dados sintéticos e uma chave de teste explicitamente pública:

- A tem o maior escore, mas a concessão não cobre a finalidade pedida;
- B tem alto escore, mas excede o limite de risco;
- C passa pelos filtros e vence D;
- só depois uma chamada separada ao vault verifica novamente a concessão e abre
  o conteúdo sintético; após revogação, outra abertura é recusada.

O recibo contém escolha, códigos limitados de motivo e resultados de conferência.
Alpha, limite de risco e desempenho selecionado também têm campos racionais
exatos; suas versões numéricas são projeções para apresentação, não comparação.
Não contém o token, o conteúdo protegido ou os campos brutos do pedido de
privacidade. Identificadores e metadados ainda podem ser sensíveis: não se afirma
anonimato nem autorização para publicar recibos reais. O hash auxilia a conferir
integridade, mas não é atestado independente, assinatura ou prova da realidade.

As demonstrações anteriores e suas fixtures permanecem separadas. Esta função
não concede ferramentas vivas nem transforma a prévia de pesquisa em sistema
de produção, instrumento clínico ou determinador de condição moral.
