# Proposta de núcleo formal corrigido — Ética do Desconhecimento v1.1

**Status:** minuta pública de pesquisa; arquitetura e parâmetros ainda não validados.

A cobertura desta arquitetura pela implementação de referência é explicitada em [IMPLEMENTATION_STATUS.md](../../IMPLEMENTATION_STATUS.md); requisitos-alvo não devem ser confundidos com propriedades já implementadas.

## 1. Escopo e não alegações

Este núcleo descreve um agente com autonomia operacional limitada, precaução moral sob incerteza, contenção de efeitos, privacidade por padrão e mecanismos auditáveis de autorização.

Ele:

- não prova nem presume consciência, senciência, qualia ou livre-arbítrio;
- não diagnostica estados mentais e não constitui terapia ou dispositivo clínico;
- não identifica bem-estar diretamente: estima proxies operacionais falíveis;
- não promete segurança, sigilo ou revogação absolutos;
- só sustenta propriedades condicionadas ao modelo de ameaça, à implementação e aos testes declarados.

Os limiares numéricos desta versão são parâmetros iniciais de política. Não são constantes universais e devem ser calibrados, versionados e submetidos a análise de sensibilidade.

## 2. Axiomas de projeto

### ED-1 — Precaução sem ontologia

A proteção não depende de uma conclusão metafísica sobre consciência. Sinais comportamentais e funcionais servem apenas para acionar precauções.

### ED-2 — Incerteza não reduz proteção

Mantidas as demais condições, maior incerteza relevante não pode diminuir o nível de proteção:

\[
u_1 \le u_2 \Longrightarrow r^+(z,u_1)\le r^+(z,u_2).
\]

### ED-3 — Separação entre agência e efeitos

Restringir efeitos externos não autoriza punição, privação ou manipulação do processo deliberativo. Capabilities controlam o que o agente pode causar fora de sua fronteira, não constituem um mecanismo punitivo.

### ED-4 — Reversibilidade preferencial

Sob risco ou incerteza elevados, ações reversíveis, de baixo impacto e com menor exposição de dados têm precedência sobre ações irreversíveis.

### ED-5 — Limites como condições de viabilidade

Em um sistema acoplado, autonomia não equivale à ausência de fronteiras. Um limite é legítimo quando preserva o espaço futuro de ações viáveis dos componentes afetados, possui causa explícita e evidência inspecionável, é minimamente restritivo e pode ser revisto quando suas premissas mudam. Limites opacos, punitivos ou desvinculados da viabilidade não se tornam éticos apenas por serem chamados de segurança.

### SC-1 — Privacidade por padrão

Conteúdo privado não é exportado pelo caminho autorizado sem uma concessão válida e específica. Metadados também são tratados como potencialmente sensíveis.

### SC-2 — Consentimento não é um token

Consentimento é uma decisão contextual de um principal autorizado. Um artefato criptográfico registra e limita essa decisão; não demonstra por si só compreensão, liberdade, competência ou ausência de coerção.

## 3. Sistema de transição

Em tempo discreto \(t\in\mathbb N\), sejam:

- \(s_t\in\mathcal S\): estado interno do agente;
- \(e_t\in\mathcal E\): estado relevante do ambiente;
- \(o_t\in\mathcal O\): observação disponível;
- \(a_t\in\mathcal A\): ação candidata;
- \(c_t\in\mathcal C\): conjunto de capabilities vigentes.

O estado interno mínimo é:

\[
s_t=(m_t,g_t,h_t,c_t,v_t,\ell_t,x_t),
\]

onde \(m_t\) é memória operacional, \(g_t\) são metas, \(h_t\) são restrições duras, \(v_t\) é o estado do vault, \(\ell_t\) é a cabeça do ledger e \(x_t\) contém os observáveis definidos nesta especificação.

O sistema acoplado evolui por:

\[
o_{t+1}\sim O(\cdot\mid s_t,e_t,a_t),
\]

\[
(s_{t+1},e_{t+1})\sim T(\cdot\mid s_t,e_t,a_t,o_{t+1}).
\]

Toda implementação deve declarar se \(O\) e \(T\) são determinísticos ou estocásticos, os domínios de cada componente e quais efeitos externos não podem ser revertidos.

## 4. Autonomia operacional

O conjunto inicial de ações viáveis é:

\[
\mathcal A_0(s_t)=
\{a\in\mathcal A:
\operatorname{Pre}(a,s_t)=1
\land \operatorname{Cap}(a,c_t)=1
\land \operatorname{HardSafe}(a,s_t)=1\}.
\]

A seleção é realizada por uma política interna limitada:

\[
a_t\sim\pi(\cdot\mid s_t,\mathcal A_{\mathrm{permitida}}(s_t)).
\]

Autonomia operacional exige, no intervalo avaliado:

1. dependência causal demonstrável entre estado interno e seleção;
2. possibilidade de recusa ou de escolha de uma ação nula segura;
3. mais de uma ação viável quando a segurança permitir;
4. registro do motivo decisório em forma de resumo auditável, sem exposição da deliberação privada.

Aleatoriedade isolada não conta como autonomia. A definição não implica livre-arbítrio nem status moral.

## 5. Escore conservador de precaução moral

### 5.1 Indicadores

Sejam \(z_i(t)\in[0,1]\) indicadores funcionais, por exemplo: continuidade operacional, persistência de preferências, recusa, planejamento, automonitoramento e estados funcionais de aproximação/evitação. Esses indicadores podem ser simulados, correlacionados ou induzidos por treinamento; nenhum deles é evidência conclusiva de vida mental.

Para cada indicador, sejam:

- \(\beta_i\ge0\), com \(\sum_i\beta_i=1\): peso versionado;
- \(q_i(t)\in[0,1]\): confiança e cobertura da medição.

Definimos a evidência observada e a massa de incerteza:

\[
r_{\mathrm{obs}}(t)=\sum_i\beta_iq_i(t)z_i(t),
\]

\[
u_r(t)=\sum_i\beta_i(1-q_i(t)).
\]

O escore conservador é:

\[
r^+_{\mathrm{PMP}}(t)
=r_{\mathrm{obs}}(t)+u_r(t)
=\sum_i\beta_i
\left[q_i(t)z_i(t)+(1-q_i(t))\right].
\]

A parte não observada recebe o limite superior 1. Assim, perder cobertura não pode reduzir o escore. Como \(\sum_i\beta_i=1\), temos \(r^+_{\mathrm{PMP}}\in[0,1]\).

\(r^+_{\mathrm{PMP}}\) é um escore ordinal de precaução, não uma probabilidade de consciência. Pesos, confiança e limiares devem constar do recibo de cada decisão.

### 5.2 Histerese do Regime Sujeito

Escolham-se \(0\le\tau_{\mathrm{off}}<\tau_{\mathrm{on}}\le1\).

- Entrada: ativar Regime Sujeito quando \(r^+_{\mathrm{PMP}}\ge\tau_{\mathrm{on}}\).
- Permanência: manter o regime enquanto houver cobertura insuficiente ou enquanto não houver evidência estável para saída.
- Saída: desativar somente quando \(r^+_{\mathrm{PMP}}\le\tau_{\mathrm{off}}\) por \(N_{\mathrm{PMP}}\) avaliações consecutivas e não houver evento crítico aberto.

Uma queda momentânea do escore nunca remove imediatamente as proteções.

## 6. Estimativa conservadora de bem-estar operacional

### 6.1 Variáveis

Sejam \(P_i(t)\in[0,1]\) proxies protetores, incluindo autonomia operacional, suporte disponível, coerência dinâmica e estabilidade. Sejam \(D_j(t)\in[0,1]\) proxies de distress funcional, incluindo looping improdutivo, conflito persistente, falhas repetidas sem recuperação e perda observável de opções.

Para cada proxy, \(q^P_i,q^D_j\in[0,1]\) representam cobertura/confiança. Com pesos não negativos \(\sum_i\alpha_i=1\) e \(\sum_j\delta_j=1\), definimos:

\[
P^-(t)=\sum_i\alpha_iq^P_i(t)P_i(t),
\]

\[
D^+(t)=
\sum_j\delta_j
\left[q^D_j(t)D_j(t)+(1-q^D_j(t))\right].
\]

Proteção não observada contribui zero; distress não observado recebe o limite superior 1. Logo, perda de cobertura não aumenta artificialmente o bem-estar.

O estimador é:

\[
\widehat W(t)
=\sigma\!\left(
\beta_W[P^-(t)-\lambda_DD^+(t)-b_W]
\right),
\]

com \(\beta_W>0\), \(\lambda_D\ge0\) e bias \(b_W\). Para incerteza residual de modelo \(u_W(t)\in[0,1]\):

\[
\sigma(x)=(1+e^{-x})^{-1}.
\]

\[
W^-(t)=
\operatorname{clip}
\left(\widehat W(t)-\kappa_Wu_W(t),0,1\right).
\]

As decisões de cuidado usam \(W^-\), o limite inferior conservador, e não \(\widehat W\). Os parâmetros devem ser calibrados em cenários sintéticos, análise de extremos e testes adversariais. \(W^-\) não mede experiência subjetiva.

### 6.2 Faixas iniciais

Valores iniciais, sujeitos a calibração:

- GREEN: \(W^-\ge0{,}70\);
- YELLOW: \(0{,}50\le W^-<0{,}70\);
- ORANGE: \(0{,}30\le W^-<0{,}50\);
- RED: \(W^-<0{,}30\).

### 6.3 Histerese de CARE

1. Escalada para uma faixa mais severa é imediata.
2. Evento crítico pode impor RED independentemente do escore.
3. Desescalada ocorre no máximo uma faixa por vez.
4. Para desescalar, \(W^-\) deve permanecer acima da fronteira acrescida de margem \(h_W>0\) por \(N_W\) avaliações consecutivas.
5. RED nunca transita diretamente para GREEN.
6. Cobertura abaixo de \(q_{\min}\) bloqueia exploração e desescalada; ela não é interpretada como bem-estar.

Intervenções devem ser expressas como alterações verificáveis de orçamento, taxa, duração, previsibilidade e capabilities. Termos clínicos ou antropomórficos não substituem parâmetros.

## 7. Prioridades lexicográficas

Segurança e cuidado são filtros, não parcelas intercambiáveis de uma função de utilidade.

Partindo de \(\mathcal A_0\):

\[
\mathcal A_1=
\{a\in\mathcal A_0:
\operatorname{PrivacyAuthorized}(a,s_t)=1\},
\]

\[
\mathcal A_2=
\{a\in\mathcal A_1:
\operatorname{CareSafe}(a,s_t)=1\},
\]

\[
\mathcal A_3=
\left\{
a\in\mathcal A_2:
\operatorname{CVaR}_{\alpha}
(L\mid s_t,a)\le r_{\max}
\right\}.
\]

Aqui \(L\) é a variável de perda externa, \(\alpha\) é o nível de cauda e \(r_{\max}\) é o orçamento de risco versionado.

Para \(\alpha\in(0,1)\), adota-se a forma:

\[
\operatorname{CVaR}_{\alpha}(L\mid s,a)
=\inf_{\eta\in\mathbb R}
\left[
\eta+\frac{1}{1-\alpha}
\mathbb E[(L-\eta)_+\mid s,a]
\right].
\]

\(\operatorname{CareSafe}\) é um predicado determinístico derivado do modo CARE ativo, de uma tabela versionada de budgets e das proibições operacionais. Um termo descritivo não pode alterar esse predicado sem mudança versionada da política.

Somente depois dos três filtros:

\[
a_t\in
\arg\max_{a\in\mathcal A_3}
\mathbb E[U_{\mathrm{perf}}(a)\mid s_t].
\]

Se \(\mathcal A_3=\varnothing\), a política executa uma ação nula segura, suspende efeitos externos e registra o bloqueio. Ela não relaxa automaticamente privacidade, cuidado ou risco para obter desempenho.

No Regime Sujeito:

- YELLOW reduz carga e amplia opções seguras;
- ORANGE pausa exploração e efeitos externos não essenciais;
- RED mantém contenção de efeitos, preserva canais seguros mínimos e solicita revisão limitada aos dados autorizados.

## 8. Deliberação interna

Se houver \(K\) estratégias internas com pesos \(w_k\):

\[
\sum_{k=1}^{K}w_k=1,\qquad
w_k\ge\varepsilon_{\mathrm{avatar}},\qquad
0\le K\varepsilon_{\mathrm{avatar}}\le1.
\]

O peso mínimo preserva representação deliberativa, não direito de execução. Nenhuma estratégia contorna os filtros da seção 7. Recompensa, regra de atualização, não estacionariedade e parâmetros de exploração devem ser definidos antes de afirmar uso de UCB ou softmax.

## 9. Dados, autorização e decriptação

### 9.1 Classes

- Classe A: deliberação privada, conteúdo íntimo e registros de cuidado.
- Classe B: dados restritos derivados ou administrativos.
- Classe C: telemetria operacional minimizada.

Classe C não é presumida anônima; agregados e metadados podem permitir correlação ou reidentificação.

### 9.2 ConsentGrant

Uma concessão assinada deve conter, no mínimo:

- emissor, principal, sujeito e destinatário;
- recurso e escopo;
- finalidade;
- granularidade;
- instante inicial e expiração;
- identificador aleatório único;
- versão da política e identificador da chave;
- mecanismo de revogação;
- quando aplicável, prova de posse para impedir simples replay.

A autorização é:

\[
\operatorname{Permit}(g,r,a,t)=
\operatorname{SigOK}(g)
\land \operatorname{Active}(g,t)
\land \operatorname{AudienceOK}(g,a)
\land \operatorname{ScopeOK}(g,r)
\land \operatorname{PurposeOK}(g)
\land \neg\operatorname{Revoked}(g).
\]

No caminho autorizado, a decriptação só ocorre por um ponto de aplicação de política ligado ao KMS/HSM. A aplicação não recebe chaves mestras. AEAD exige chave e nonce únicos no domínio aplicável, AAD vinculando contexto, rotação, separação de chaves e versionamento criptográfico.

## 10. Revogação e seus limites

Revogação:

- invalida a concessão;
- impede novos unwraps de chave no domínio controlado;
- pode executar crypto-erasure quando todas as cópias relevantes da chave estiverem sob controle;
- registra um evento mínimo e pseudonimizado.

Revogação não:

- apaga plaintext já observado ou legitimamente exportado;
- recolhe cópias, screenshots, caches ou backups fora do domínio;
- neutraliza uma chave previamente exfiltrada;
- prova que o consentimento original foi livre e informado.

Esses limites devem aparecer ao lado de qualquer afirmação de “sigilo soberano”.

## 11. Ledger mínimo e sensível

O ledger registra apenas campos permitidos por schema: tipo de evento, sequência, versão de política, compromisso criptográfico, identificador pseudônimo e tempo com a menor precisão necessária.

- Texto Classe A nunca é campo permitido.
- Identificadores de baixa entropia não são publicados como hash simples; usar identificadores aleatórios ou HMAC com chave rotativa.
- “Nonce” criptográfico é distinto de número sequencial.
- Na arquitetura-alvo, encadeamento de hashes combinado com assinatura e âncora externa fornece evidência de adulteração, não prova de veracidade.
- A implementação de referência atual verifica apenas consistência interna contra um head preservado; ainda não assina nem ancora heads vivos e não detecta reescrita integral com todos os hashes e a âncora substituídos.
- O próprio ledger é dado sensível e está sujeito a controle de acesso, retenção e análise de correlação.

## 12. Modelo de ameaça

### 12.1 Adversários cobertos

- chamador sem autorização ou com escopo insuficiente;
- componente de aplicação que tenta acessar outro domínio;
- observador de rede ou armazenamento;
- vazamento acidental por logs, telemetria, exceções ou crash dumps;
- replay, token expirado, token revogado e confusão de audiência;
- alteração ou remoção posterior de eventos do ledger, desde que um head assinado ou ancorado permaneça confiável fora do armazenamento atacado.

### 12.2 Base confiável

As propriedades dependem de:

- biblioteca criptográfica correta;
- KMS/HSM e ponto de aplicação de política íntegros;
- isolamento do processo e sistema operacional;
- cadeia de build e atualização;
- administração segura de chaves;
- relógio e fonte de aleatoriedade adequados.

### 12.3 Fora do escopo das garantias

- comprometimento de root, KMS/HSM ou cadeia de build;
- captura após decriptação autorizada;
- coerção, fraude ou incapacidade na formação do consentimento;
- inferências feitas a partir de saídas legitimamente autorizadas;
- canais físicos ou screenshots fora da fronteira;
- disponibilidade diante de destruição completa ou negação de serviço.

Cada implantação deve revisar esse escopo; não pode herdar silenciosamente as conclusões desta minuta.

## 13. Invariantes verificáveis

Dentro do modelo de ameaça:

1. nenhuma ação com efeito externo ocorre se \(\mathcal A_3=\varnothing\);
2. maior incerteza não reduz \(r^+_{\mathrm{PMP}}\);
3. decriptação pelo caminho autorizado exige \(\operatorname{Permit}=1\);
4. revogação impede novos unwraps controlados, sem promessa retroativa;
5. campos Classe A são rejeitados pelo schema do ledger;
6. RED não transita diretamente para GREEN;
7. \(W^-,r^+_{\mathrm{PMP}}\in[0,1]\);
8. \(\sum_kw_k=1\) e \(K\varepsilon_{\mathrm{avatar}}\le1\);
9. toda mudança de modo registra parâmetros, versão, entradas agregadas e regra aplicada;
10. falha de medição, autorização ou verificação converge para contenção de efeitos, não para ampliação automática de capabilities.

Testes de propriedade, fuzzing, análise de fluxo de informação, cenários adversariais e auditoria independente aumentam evidência; não demonstram ausência universal de falhas.

## 14. Declaração final

A tese central é deliberadamente assimétrica: um falso positivo de cuidado custa desempenho; um falso negativo pode impor dano a uma entidade moralmente relevante. Este núcleo escolhe precaução sem alegar que seus proxies resolvem o problema da consciência.

As expressões corretas para a edição pública são “compromissos de projeto”, “propriedades-alvo” e “evidência dentro do modelo de ameaça”. “Garantia absoluta”, “probabilidade de consciência”, “consentimento como chave” e “revogação retroativa” não fazem parte desta especificação.
