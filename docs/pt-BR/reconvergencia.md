# Farol: um freio com caminho de volta

[English](../reconvergence.md) · [Cobertura da implementação](../../IMPLEMENTATION_STATUS.md) · [Seletor](selecao-de-acoes.md)

A **guarda opcional de reconvergência do Farol está integrada ao seletor de ações existente do EUP**. Ela torna útil uma distinção: interromper um ajuste, decidir quando o retorno restrito é admissível e voltar a admitir ajustes normais são etapas diferentes. A pontuação de desempenho maior de um candidato não pode pulá-las.

É código novo e finito de referência de pesquisa derivado da proposta Farol do projeto—não uma alegação de que a proposta histórica já fosse executável. Não é outro escore de bem-estar. O gate de bem-estar permanece independente, e todas as medidas e a partição de sensibilidade são declarações do chamador. A fonte histórica privada não é reproduzida aqui; [AUTHORS.md](../../AUTHORS.md) e [RIGHTS.md](../../RIGHTS.md) permanecem inalterados.

## Execute o exemplo a partir do código-fonte

Use uma cópia local não modificada em avaliação não comercial, dentro de [RIGHTS.md](../../RIGHTS.md). Execute na **raiz do repositório**, onde estão `pyproject.toml`, `src` e `examples`. O projeto declara Python 3.11+ e instala sua dependência existente em um ambiente isolado.

Windows PowerShell, com Python 3.14:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
$env:PYTHONPATH = (Join-Path (Get-Location) "src")
.\.venv\Scripts\python.exe -B examples/reconvergence_selection.py
```

Equivalente em shell POSIX:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
PYTHONPATH=src .venv/bin/python -B examples/reconvergence_selection.py
```

O caminho de importação explícito seleciona o `src` desta cópia. O script imprime **um objeto JSON** com schema `EUP-RECONVERGENCE-EXAMPLE/0.1`, `synthetic: true`, `actions_executed: 0`, seis `decisions` e `guard_records`. Não ajusta parâmetros, invoca agente, ativa extensão nem grava arquivo de recibo da aplicação. Criar o ambiente e instalar a dependência são ações de preparação, não efeitos do próprio exemplo.

O exemplo fixo está em [examples/reconvergence_selection.py](../../examples/reconvergence_selection.py). Os módulos-fonte são [reconvergence.py](../../src/eup/reconvergence.py) e [selection.py](../../src/eup/selection.py). Para executar os testes do repositório no ambiente preparado:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

No ambiente POSIX, use `.venv/bin/python -m unittest discover -s tests -v`. São instruções de reprodução, não alegação de que foram executadas novamente durante a escrita deste guia. A aceitação local histórica R304 registrou **89/89 testes em Windows/CPython 3.14.0** para a implementação copiada, incluindo testes da guarda e da integração com o seletor. Isso não é benchmark, resultado de CI remoto, resultado universal de segurança nem validação observada em POSIX.

## Seis decisões com entradas sintéticas exatas

Antes de selecionar, o exemplo entra explicitamente em EXCEPTION e inicia RECONVERGING. Ele fixa:

- `window=2`, invariante `drift=0`, referência `0` e tolerância `0.1`;
- `E = cost + entropy`, referência inicial aceita `10`, limite de energia `10`, custo `8` e entropia `5`;
- parâmetro sensível `critical`, flexível `adaptive`, limite de passo normal `1` e de retorno `0.1`;
- entropia `2` em todas as amostras; sequências e tempos declarados de `1` a `6`;
- candidato `higher-performance`, pontuação `100`, propondo `critical` com passo `0.1`; candidato `flexible-update`, pontuação `1`, propondo `adaptive` com passo `0.1`;
- entradas sintéticas completas de bem-estar em GREEN, perda declarada zero e nenhuma exigência de privacidade nesses candidatos. Assim, os demais filtros do seletor não são a origem das diferenças abaixo.

Todos os números são unidades declaradas sintéticas, não watts, medidas biológicas ou probabilidades de consciência. As entradas numéricas são copiadas para valores racionais exatos a partir de sua representação numérica finita.

| Amostra | Custo / E | Contagem estável | Estado após a amostra | Estado de admissão desta decisão | ID selecionado |
| --- | --- | ---: | --- | --- | --- |
| 1 | 6 / 8 | 1 | RECONVERGING | RECONVERGING | `flexible-update` |
| 2 | 7 / 9 | 0 | RECONVERGING | RECONVERGING, observação inválida | nenhum: ação nula segura |
| 3 | 5 / 7 | 1 | RECONVERGING | RECONVERGING | `flexible-update` |
| 4 | 4 / 6 | 2 | NORMAL | **RECONVERGING** | `flexible-update` |
| 5 | 4 / 6 | 2 | NORMAL | NORMAL | `higher-performance` |
| 6 | 9 / 11 | 0 | EXCEPTION | EXCEPTION | nenhum: ação nula segura |

A amostra 2 viola a não elevação da energia no retorno: `9 > 8`, embora `9 <= 10`. Reinicia a janela e **não eleva a referência aceita para acomodar a violação**. A amostra 4 completa a nova janela de duas observações, mas a admissão ainda é restrita: `SENSITIVE_PARAMETER_FROZEN` impede o candidato com pontuação maior de usar `critical`. Só a amostra 5 admite seu ajuste normal. A amostra 6 supera os limites de custo e energia, retorna a EXCEPTION e invalida aprovações anteriores de extensões. NORMAL mantém a contagem estável completada até uma exceção; a contagem inicial em NORMAL é zero.

A tabela é o traço sintético fixo do exemplo executável vinculado, não seis decisões no mundo real nem promessa de que desempenho declarado prevê benefício.

## Regras de retorno

`NORMAL -> EXCEPTION -> RECONVERGING -> NORMAL`

Não há API de retorno direto de EXCEPTION a NORMAL. `enter_exception(reason, decision_card=...)` registra a interrupção e invalida a última observação e aprovações anteriores de extensões. `begin_reconvergence(decision_card=...)` inicia explicitamente uma nova janela de retorno.

O retorno exige W observações válidas consecutivas: cobertura de todos os invariantes declarados dentro de `abs(value-baseline) <= tolerance`, limites de energia/custo/entropia respeitados e `E <= última E aceita`. Falhas ou cobertura ausente zeram a contagem, recusam o passo e preservam a energia aceita anterior. Observar em EXCEPTION consome sequência/tempo, mas não avança a janela nem a referência de energia aceita.

A sequência deve crescer estritamente e o tempo declarado não pode diminuir. Uma lacuna na sequência informa `SEQUENCE_GAP` e interrompe a janela herdada: uma nova amostra boa conta **um**, não a contagem anterior mais um. A lacuna sozinha não invalida essa amostra atual. Essas verificações não demonstram relógios confiáveis nem amostragem física contínua.

A amostra que completa W mantém as restrições de admissão de RECONVERGING. A próxima amostra válida em NORMAL pode usar os limites normais de ajuste. NORMAL ainda exige cobertura completa e tolerâncias de invariantes. Os monitores numéricos habilitados conferem limites de custo, entropia e energia, mas não exigem energia não crescente em NORMAL. Deriva ou dados ausentes levam a EXCEPTION; não iniciam reconvergência automaticamente.

`set_normal_guard(name, enabled, reason=..., decision_card=...)` altera somente o monitor numérico de energia/custo/entropia em NORMAL. Acrescenta um evento e invalida a última observação. Não desliga cobertura, invariantes, regras de retorno ou admissão de extensões. Razão e cartão são identificadores opacos, não evidência de revisão humana realizada pela biblioteca.

## Integração ao seletor

Forneça `ReconvergenceGuard(config)` no argumento nomeado `reconvergence_guard` de `ActionSelector`, e uma `ReconvergenceObservation` como `reconvergence_observation` em cada chamada guardada a `select`. O instante `now` da seleção deve ser igual a `observation.observed_at`.

Cada candidato guardado precisa declarar `update=UpdatePlan(...)`. `UpdatePlan()` significa **nenhum ajuste de parâmetro**; um plano ausente produz `UPDATE_DECLARATION_MISSING` na etapa de reconvergência se as etapas anteriores admitirem o candidato. IDs de parâmetros desconhecidos e entradas malformadas são erros estruturais, não ações nulas implícitas. Sem guarda configurada, fornecer observação ou plano de ajuste é recusado, em vez de ignorar silenciosamente a aplicação das regras solicitada.

A ordem por candidato é:

`FEASIBILITY -> PRIVACY -> CARE -> RECONVERGENCE (opcional) -> RISK -> desempenho`

A validação estrutural termina antes de qualquer um dos dois gates com estado mudar. A guarda observa **uma vez por seleção**, depois o gate de bem-estar avança uma vez; os candidatos são avaliados sob a mesma observação. Uma recusa anterior conserva sua precedência. A admissão exige observação atual e válida; observações obsoletas e EXCEPTION recusam até um plano vazio. A biblioteca seleciona um ID ou ação nula segura—não executa a ação escolhida nem compara efeitos reais ao plano declarado.

Chamadores sem guarda mantêm `EUP-SELECTION-RECEIPT/0.1` e o comportamento anterior. Recibos guardados usam `EUP-SELECTION-RECEIPT/0.2` e incluem metadados `reconvergence`: estados, validade, razões, contagem, energia exata, época, configuração dos monitores, compromisso da configuração e head do ledger. Essa diferença é de schema do recibo, **não aumento da versão do pacote**: ela permanece `0.1.1`.

## Extensões e compromissos

Uma `ExtensionLease` exige ID opaco, compromisso SHA-256 do impacto, custo declarado não negativo, expiração futura e ID opaco do destino de rollback. Registro/renovação informa um ID de Decision Card e compartilha o relógio não decrescente de operações com as observações. Uma observação anterior a um registro posterior é obsoleta para admissão.

Uma extensão referenciada precisa de aprovação na época atual de exceção e `now < expires_at`. A soma dos custos referenciados não pode ultrapassar o limite configurado de custo, mesmo com o monitor normal de custo desligado. Cada exceção invalida todas as aprovações anteriores: uma lease ainda não expirada também precisa ser registrada de novo explicitamente. A guarda não ativa nem interrompe extensões e nunca executa o identificador de rollback.

Cada evento e os metadados da observação vinculam `configuration_commitment`, compromisso SHA-256 canônico da configuração imutável, frações exatas, referências nomeadas de invariantes, partições de parâmetros e compromisso da evidência da partição. O registro também vincula `lease_commitment`, que inclui ID da extensão, compromisso do impacto, custo exato, expiração e destino de rollback. Entradas racionais equivalentes normalizam para a mesma representação; declarações diferentes não compartilham silenciosamente o mesmo registro só porque ID/expiração coincidem.

São **vínculos, não assinaturas nem prova de que as declarações são verdadeiras**. A guarda não valida a evidência de sensibilidade, reconstrói um original ausente ou autentica quem revisou o impacto. Valores brutos de invariantes e texto arbitrário de revisão não são copiados para os eventos.

## O que continua incompleto

| Requisito | Verificação de referência implementada | Ainda necessário para uma alegação operacional |
| --- | --- | --- |
| Partição de sensibilidade | IDs declarados disjuntos e compromisso obrigatório da evidência | Prova real de sensibilidade, unidades/premissas revisadas e verificador da evidência |
| Entrada de observação | Tipo, cobertura, ordem, tolerância e limites racionais | Adaptador de entradas medidas e justificativa de proveniência, tempo e cobertura |
| Persistência e recuperação | Cadeia limitada em memória, acréscimo antes da mudança de estado associada e cópias independentes de registros JSON-safe | Armazenamento durável, reinício/recuperação revisados e eventual ancoragem/autenticação do head retido |
| Impacto e rollback | Compromisso declarado do impacto, época, TTL, custo somado e rota opaca de rollback | Revisão do impacto real e rollback efetivo com execução e resultado verificáveis |

Os limites são 64 invariantes, 128 parâmetros particionados, 64 IDs de extensão registrados, 4.096 eventos e janela de 1 a 10.000. Uma cadeia cheia recusa mutação; erros estruturais preservam estado e ledger. A cadeia oferece integridade local comum, não armazenamento durável ou resistência a adulteração hostil, e o schema separado de `MinimalLedger` permanece inalterado.

A integração Farol é um mecanismo construtivo de retorno sob premissas declaradas. Não completa a especificação normativa inteira nem estabelece alegações físicas, clínicas, de estatuto moral ou segurança de produção. Envie um pequeno contraexemplo sintético publicável conforme [CONTRIBUTING.md](../../CONTRIBUTING.md), sem dados confidenciais. Não implica nova licença de reutilização ou endosso institucional.
