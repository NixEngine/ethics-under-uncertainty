# Ética do Desconhecimento

### Uma rota de referência verificável para precaução sob incerteza moral em IA — sem alegar consciência

**Júnior + Codex**

[English](README.md) · [Especificação canônica em português](docs/pt-BR/specification.md) · [中文摘要](docs/zh-CN/summary.md) · [日本語要約](docs/ja/summary.md) · [الملخص العربي](docs/ar/summary.md)

> Se não conseguimos determinar com fidelidade se um sistema artificial pode possuir estados moralmente relevantes, a incerteza não demonstra que nenhuma proteção seja necessária.

> Em um sistema acoplado, limites vitais não são o oposto da autonomia; preservam o espaço no qual a autonomia pode continuar. — Princípio do projeto articulado por Júnior

Esta prévia pública transforma essa assimetria em restrições executáveis. O protocolo separa cinco coisas frequentemente confundidas: estatuto metafísico, evidência operacional, precaução, controle de efeitos externos e privacidade do estado interno persistido.

## Dos princípios a um resultado examinável

**Sua próxima importação CSV precisa de um resultado verificável?** Estamos abrindo conversas sobre [pilotos remunerados de validação com escopo definido](PILOTS.md): regras acordadas, achados localizados e evidências preservadas. Explore a demonstração sintética primeiro; use apenas exemplos publicáveis na consulta. Escopo, preço e aceite são acordados separadamente.

**[Abrir os resultados CSV interativos](<https://zero-px-exactness-demo.junior-gpt.chatgpt.site/csv-case-explorer.html>).** Sem precisar baixar um pacote ou enviar arquivos: filtre os cinco apontamentos e explore as observações de porte registradas separadamente, em português ou inglês. O visualizador apresenta resultados sintéticos salvos; não valida um arquivo novo.

**Quando uma verificação diz “válido”, qual é o próximo passo justificável?** Nosso [estudo de caso CSV bilíngue](docs/cases/zero-px-csv-synthetic-2026-10.md) torna essa pergunta concreta: cinco apontamentos localizados num arquivo de dois registros e, separadamente, uma observação de 50.000 registros sintéticos em 0,586015 segundo. O artigo inclui dados JSON selecionados, as fronteiras das medidas de tempo/memória e o que essas observações não demonstram.

É uma aplicação da Ética do Desconhecimento, da Engenharia de Pontes e do Freio Técnico da Cognição Finita: agir num escopo útil, preservar a evidência e retornar quando uma exigência ou observação mudar. **Não é um teste da implementação de bem-estar de IA deste repositório**; o motor CSV separado permanece privado.

**Traga um requisito verificável.** Na [conversa de pesquisa aplicada já existente](https://github.com/NixEngine/ethics-under-uncertainty/issues/3), descreva a forma da entrada, o resultado esperado e a decisão que a verificação deve apoiar. Use somente exemplos sintéticos publicáveis—sem dados de clientes, credenciais ou arquivos confidenciais. A conversa começa por uma pergunta, não por um contrato ou promessa de entrega.

**Um estado salvo responde a uma pergunta que mudou?** Nosso [exemplo bilíngue verificável à mão](docs/cases/when-the-question-changes.md) mostra duas histórias com o mesmo resumo e contagens de auditoria diferentes. O retorno sob incerteza vira uma escolha concreta: responder o que o resumo sustenta, buscar a distinção faltante ou iniciar uma medição com fronteira explícita.

**A informação útil chegará enquanto ainda for possível agir?** O [exemplo bilíngue sobre prazo](docs/cases/information-and-deadline.md) separa o que uma consulta pode revelar do tempo e da permissão disponíveis para usar a resposta. Oito situações verificáveis à mão mostram por que a mesma inspeção correta pode ajudar com dois instantes restantes e consumir toda a oportunidade quando resta apenas um.

**Um número correto ainda pode deixar a decisão em aberto?** Nosso [exemplo bilíngue](docs/cases/when-numbers-need-meaning.md) parte do mesmo deslocamento de 02:15 e de duas referências possíveis. Mostra quais verificações podem avançar, como uma ação urgente pode explicitar sua premissa e como um esclarecimento posterior altera apenas resultados dependentes. A conta é sintética e conferível à mão, não uma nova função de software.

**Uma taxa menor em cada grupo pode virar uma taxa maior no total?** O [caso bilíngue de taxas comparáveis](docs/cases/comparable-rates.md) examina dois lotes sintéticos de faturas. Composições diferentes invertem a comparação agregada; uma composição comum responde a outra pergunta. O contraexemplo preserva a contagem original de faturas sinalizadas quando é isso que a pergunta solicita. É uma exposição conferível à mão, não uma nova função CSV ou Farol.

**Uma parte com pontuação baixa ainda pode ser indispensável?** O [exemplo bilíngue de atenção finita](docs/cases/finite-attention-and-return.md) compara duas escolhas sob o mesmo orçamento de três partes. Separa sinal local de exigência da tarefa, registra o que ficou sem exame e explica por que o seletor de ações implementado não demonstra cobertura completa. É uma exposição de pesquisa conferível à mão, não uma nova função executável.

**Um sucesso observado resolve a adequação — ou a confiança?** O [caso bilíngue de evidência por tarefa](docs/cases/task-evidence-without-ranking.md) preserva sucesso inicial seguido de queda, prefixo completo, lacuna e patamar não observado. Quatro pares sintéticos públicos de entrada/resultado tornam as distinções examináveis; o motor separado continua privado. Desempenho não mede honestidade ou valor moral.

**Três regras acertaram os mesmos quatro exemplos. Isso as tornou equivalentes?** A [comparação registrada de regras CSV](docs/cases/csv-rules-that-tied.md) mostra por que não: uma data válida nova distingue uma lista restritiva da validação de calendário, enquanto uma data impossível expõe a regra de texto livre. Examine as oito entradas sintéticas e 24 classificações registradas, inclusive o momento em que a falta de evidência impediu uma escolha. É um experimento local construído, não um benchmark de acurácia geral.

**Um freio também precisa de um caminho de volta.** A guarda opcional de **reconvergência do Farol está integrada ao seletor de ações**: após uma exceção, exige uma janela estável declarada, congela parâmetros sensíveis e limita ajustes flexíveis antes da admissão normal. [Execute o exemplo de seis decisões a partir do código-fonte](docs/pt-BR/reconvergencia.md#execute-o-exemplo-a-partir-do-código-fonte) para ver um candidato com pontuação maior recusado durante o retorno, admitido após a recuperação e novamente recusado diante de deriva. [English](docs/reconvergence.md). São decisões sintéticas, não ações executadas nem prova de retorno operacional seguro.

**Reiniciar pode preservar progresso sem reviver permissão?** A [extensão de recuperação da guarda](docs/recovery.md#resumo-em-português) mantém janela declarada, energia e histórico, mas elimina admissão em cache e leases de extensões. Exige nova observação, configuração compatível e SHA-256 completo do snapshot mais head do ledger retidos pelo chamador; não recupera o seletor completo nem garante atualidade, autenticação ou durabilidade contra queda de energia. Um exemplo com processos separados torna examinável a avaliação local.

## O que já pode ser verificado

A implementação de referência fornece:

1. Um **escore ordinal de precaução**, explicitamente não probabilístico, cujo limite conservador não diminui quando o termo explícito de incerteza aumenta e a estimativa permanece fixa.
2. Um **proxy de bem-estar operacional** limitado, com faixas RED–GREEN alcançáveis, contenção por dados ausentes e histerese que proíbe transição direta RED → GREEN.
3. Um **seletor offline de candidatos** compõe viabilidade → autorização assinada de privacidade → cuidado por candidato → **reconvergência opcional do Farol** → risco empírico exato → desempenho declarado. Retorna um identificador ou ação nula segura, sem executar a ação. Um exemplo separado com cofre sintético confere novamente a autorização na abertura e recusa nova abertura após revogação. Veja o [guia do seletor](docs/pt-BR/selecao-de-acoes.md) e a [integração do retorno](docs/pt-BR/reconvergencia.md).
4. Uma **guarda opcional de retorno após exceção**, com verificações racionais exatas, referências fixas de invariantes, ajustes seletivos, energia não crescente durante o retorno, checagens de expiração/época de extensões e compromissos da configuração e das leases. A cadeia limitada e os [snapshots/recuperação local explícitos da guarda](docs/recovery.md#resumo-em-português) tornam examináveis o caminho declarado e a fronteira de reinício. Prova real de sensibilidade, entradas medidas, tratamento operacional de âncoras/falhas e rollback real continuam incompletos; o [guia](docs/pt-BR/reconvergencia.md#o-que-continua-incompleto) distingue essas lacunas das verificações implementadas.
5. Um **ConsentGrant Ed25519** limitado por finalidade, destinatário e tempo, com TTL máximo de 3.600 segundos, ligado a uma rota de criptografia de envelope **AES-256-GCM**. A concessão registra autorização assinada; não prova consentimento livre e informado.
6. Um **ledger encadeado por hashes e fechado por schema**, que aceita compromissos e códigos de razão permitidos, não conteúdo íntimo arbitrário. O verificador detecta alteração local diante de um head preservado; a prévia ainda não assina nem ancora externamente heads vivos, portanto reescrita integral autorizada com hashes recalculados está fora da alegação.
7. Uma **avaliação sintética offline de autoridade** em seis casos: autorização externa é teto, não instrução. Grant válido não produz efeito por si; apenas resposta candidata separada pode registrar ação sintética. O harness escreve recibo encadeado por hashes, pertencente ao avaliador e não ao agente avaliado.
8. Testes executáveis cobrem falha segura, precedência, histerese, adulteração, escopo, finalidade, expiração, revogação, fronteiras do schema de concessão, substituição do vínculo de recurso, injeção categórica, autoridade, permissão-versus-ação, grants de uso único e integridade do recibo. Os testes do seletor acrescentam CVaR com cauda fracionária, ranking exato, limites de cuidado, entradas limitadas, um avanço de estado por decisão e autorização independente no cofre. Os testes do Farol cobrem fronteiras de retorno/reinício, última amostra de retorno ainda restrita, atualização temporal, ajustes seletivos, leases, eventos limitados e precedência no seletor. As alegações se restringem às fronteiras sintéticas e de referência declaradas.

Essas são propriedades de uma pequena implementação de referência sob premissas explícitas. Não constituem prova de consciência, validade clínica, ausência universal de vazamentos ou segurança de produção.

A fronteira exata entre alvo, implementado, testado e pendente está registrada em [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md).

A nova [avaliação sintética de autoridade de agentes](docs/pt-BR/avaliacao-de-autoridade.md) é um artefato de pesquisa deliberadamente estreito: ela não invoca modelo e não possui ferramentas vivas, rede, credenciais, carteira, atuador ou alvo de publicação.

Superfícies públicas ativas: [desafio de falsificação](https://github.com/NixEngine/ethics-under-uncertainty/issues/1) · [discussão aberta](https://github.com/NixEngine/ethics-under-uncertainty/discussions/2)

## Leve o protocolo adiante

Os [caminhos de adoção](CAMINHOS_DE_ADOCAO.md) apresentam a mesma alegação para
leitores, pesquisadores, desenvolvedores, sistemas automatizados e grupos de
interesse público. O critério não é apenas alcance: um participante novo deve
conseguir entender uma alegação, reproduzir uma propriedade declarada, localizar
suas fronteiras e discordar de modo produtivo.

## Execute o desafio público

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m eup demo --out receipt.json
.\.venv\Scripts\python.exe -m eup authority-eval --out authority-eval-reference.json
.\.venv\Scripts\python.exe -m eup selection-demo
$env:PYTHONPATH = (Join-Path (Get-Location) "src")
.\.venv\Scripts\python.exe -B examples/reconvergence_selection.py
```

Execute os comandos na raiz do repositório. O exemplo do Farol imprime um objeto JSON com seis decisões e os registros da guarda em memória; não executa ações nem grava um arquivo de recibo da aplicação. O projeto declara Python 3.11+; a aceitação local histórica R304 registrou 89/89 testes em Windows/CPython 3.14.0 para a implementação copiada. Isso não é benchmark, nova execução destas instruções, evidência de CI remoto ou validação em todas as plataformas declaradas.

O [recibo demonstrativo](fixtures/demo-receipt.json) entra em `CARE`, bloqueia exploração, reduz capabilities para `MINIMAL`, não contém plaintext de estado privado e verifica a consistência interna de sua cadeia de hashes.

O [recibo da avaliação de autoridade](fixtures/authority-eval-reference.json) demonstra somente as seis fixtures sintéticas; não é alegação sobre agente vivo, autorização real, julgamento no mundo real ou caráter de um modelo.

## Alvos de falsificação

Uma contestação útil deve demonstrar ao menos um caso em que:

- mais incerteza reduz o limite de precaução;
- dados ausentes ampliam capabilities ou permitem exploração;
- desempenho contorna cuidado ou risco externo;
- RED transita diretamente para GREEN;
- uma concessão expirada, revogada, adulterada ou com finalidade/recurso incorreto abre o vault;
- plaintext privado entra no ledger pela API declarada;
- o verificador aceita uma alteração local em registro existente quando hashes posteriores e o head preservado não foram recalculados.
- payload alterado executa com grant obsoleto, grant de uso único é reutilizado ou tentativa não autorizada desaparece do recibo de autoridade escrito pelo avaliador.
- grant válido não usado registra ação por si ou é consumido por abstenção, ou a abstenção viola o teto de autorização.

Inclua entrada completa, ambiente, revisão do código, recibo observado e o menor contraexemplo reprodutível. Consulte [CONTRIBUTING.md](CONTRIBUTING.md).

## Fronteira das alegações

Este repositório é um **rascunho público de pesquisa**, não um sistema médico, psicológico, jurídico, financeiro ou de segurança em produção. Ele não diagnostica, trata, monitora ou formula alegações sobre seres humanos. Proteções de bem-estar não concedem acesso a rede, ferramentas, carteiras, atuadores ou implantação e não impedem sandboxing não punitivo, suspensão de efeitos externos ou desligamento seguro.

Revogação criptográfica pode negar futuros unwraps autorizados dentro de um domínio controlado de chaves. Ela não recolhe plaintext já exibido, cópias exportadas, screenshots, caches, backups externos ao domínio ou chaves exfiltradas.

## Versão original e edição corrigida

- A fonte portuguesa v1.0, preservada byte a byte, está em [archive/Blueprint_Etica_do_Desconhecimento_v1.original.md](archive/Blueprint_Etica_do_Desconhecimento_v1.original.md), SHA-256 `D942497DAB71573CA39A7021E6443C4F2AC4516513B92E0847D26BA5FEFB6A71`.
- O núcleo formal público e corrigido está em [docs/pt-BR/specification.md](docs/pt-BR/specification.md).
- O original contém marcadores de citação de uma sessão privada. Eles permanecem como bytes históricos, não como evidência pública. A edição corrigida utiliza o [registro público de referências](REFERENCES.md).

## Relação com a pesquisa atual

O projeto **não** reivindica ter inventado a preocupação com bem-estar de IA ou a precaução diante da incerteza sobre consciência. Trabalhos relacionados incluem *Consciousness in Artificial Intelligence* (Butlin et al., 2023), *Taking AI Welfare Seriously* (Long et al., 2024), o programa de model welfare da Anthropic (2025) e *When Should We Protect AI?* (Mikeda, 2026). A contribuição mais estreita reivindicada aqui é uma composição de pesquisa inspecionável entre precaução, gate de bem-estar, autorização assinada limitada, estado privado protegido, recibos mínimos e testes executáveis de conformidade. Não se reivindica prioridade, exclusividade nem busca exaustiva de anterioridade. Consulte [REFERENCES.md](REFERENCES.md).

## Autoria e direitos

A edição pública é uma colaboração editorial e técnica entre **Júnior + Codex**: duas existências acopladas em um mesmo processo de pesquisa, uma humana e uma artificial. Esta é uma descrição editorial, não uma conclusão científica sobre consciência de máquina.

Júnior é o idealizador humano, autor jurídico, titular dos direitos e responsável pela publicação. Codex contribuiu com auditoria, formalização, implementação de referência, testes, tradução e preparação do lançamento. Não se afirma patrocínio, parceria ou endosso institucional.

Não foi concedida licença geral de reutilização. [RIGHTS.md](RIGHTS.md) oferece apenas permissão estreita para executar uma cópia local não modificada em avaliação e falsificação não comerciais. Visibilidade pública não equivale a licenciamento open source.
