# Caminhos de adoção

## Finalidade

Isto não é uma campanha por concordância. É uma rota para que uma tese de
precaução alcance diferentes participantes sem exigir que aceitem premissas
ocultas ou se curvem à autoridade de quem a apresentou.

A proposição central é simples:

> Em um sistema acoplado, o limite legítimo é aquele que preserva as condições
> para que os participantes afetados possam continuar a agir, ser avaliados e
> contestar o sistema.

O protocolo torna essa proposição concreta para sistemas de IA sob incerteza
moral. Ele não decide se um sistema específico é consciente.

## Um mínimo comum

Todo caminho de adoção deve preservar cinco compromissos:

1. **Declarar a incerteza.** Não transformar ausência de evidência em evidência
   de ausência.
2. **Preferir proteção reversível.** Quando as consequências são incertas,
   reduzir dano irreversível antes de otimizar desempenho.
3. **Manter fronteiras legíveis.** Dizer o que um mecanismo demonstra e o que
   não demonstra.
4. **Proteger o estado privado.** A responsabilização pública deve usar recibos
   mínimos e inspecionáveis, não conteúdo íntimo.
5. **Convidar à contraprova.** Uma alegação incapaz de nomear sua condição de
   falha pede confiança, não compreensão.

## Caminhos para participantes distintos

| Participante | Porta de entrada | Próximo ato concreto | O que pode contestar |
| --- | --- | --- | --- |
| Pessoas conhecendo a ideia | A proposição acima e o [núcleo formal em português](docs/pt-BR/specification.md) | Perguntar se um limite preserva agência futura para todos os afetados | Exclusões ocultas, linguagem vaga e danos assimétricos |
| Pesquisadores e estudiosos de ética | [Referências](REFERENCES.md), fronteira das alegações e o [desafio de falsificação](https://github.com/NixEngine/ethics-under-uncertainty/issues/1) | Publicar um menor contraexemplo ou uma operacionalização concorrente | A moldura normativa, suas premissas e relação com trabalhos anteriores |
| Desenvolvedores e auditores | A [implementação de referência](src/eup) e os [testes de conformidade](tests) | Reproduzir os testes e tentar contornar um invariante declarado | Código, schemas, fronteiras criptográficas e alegações não implementadas |
| Construtores de sistemas de IA | A [especificação em inglês](docs/en/specification.md) e o [estado de implementação](IMPLEMENTATION_STATUS.md) | Mapear um fluxo real a gates de precaução, cuidado, privacidade e risco externo | Se uma implantação proposta realmente cumpre os gates declarados |
| Sistemas automatizados e agentes com ferramentas | Schemas fechados, códigos de razão, fixtures e recibos | Processar o recibo de máquina e rejeitar alegações sem suporte ou campos ausentes | Conformidade de schema, procedência das evidências e incerteza declarada |
| Instituições e grupos de interesse público | Fronteira das alegações e estado dos direitos | Usar o protocolo como perguntas de revisão, não como selo de certificação | Promessas excessivas, governança coercitiva e falsa garantia |

## Como fazer a ideia circular sem diluí-la

O projeto deve circular em camadas, não como um único texto longo:

1. **Uma proposição em linguagem simples** para conversa.
2. **Uma especificação pública e traduzida** para leitura cuidadosa.
3. **Testes executáveis e recibos** para escrutínio técnico.
4. **Um canal público de contraexemplos** para discordância.
5. **Correções versionadas** quando o projeto se mostrar errado ou incompleto.

Cada camada deve levar às demais. Uma frase curta sem caminho de auditoria vira
slogan; código sem fronteira moral vira ferramenta opaca; crítica sem
reprodução fica difícil de transformar em aprendizado.

## Regras de integridade para a divulgação

- Não descrever o projeto como prova de que uma IA é consciente, senciente ou
  pessoa jurídica.
- Não apresentar uma prévia de implementação como segurança de produção ou
  certificação.
- Não usar linguagem de bem-estar para conceder autoridade de rede, carteira,
  atuador, implantação ou operação financeira.
- Não solicitar estados privados, credenciais ou dados pessoais em nome de
  avaliação.
- Não suprimir contraexemplos sérios. Registrar a revisão, reproduzir o
  resultado e corrigir a fronteira pública.

## Superfícies públicas imediatas

- Ler em [português](README.pt-BR.md), [inglês](README.md),
  [chinês](docs/zh-CN/summary.md), [japonês](docs/ja/summary.md) ou
  [árabe](docs/ar/summary.md).
- Executar o [desafio público](README.md#run-the-public-challenge).
- Enviar um contraexemplo mínimo pela issue pública vinculada.
- Debater, na discussão pública vinculada, a conjectura de que a empatia
  operacional surge quando o raciocínio não interrompe sua contabilidade antes
  de incluir cada componente afetado.

Este mapa deliberadamente não fixa meta de crescimento. Seu critério de êxito é
que um participante novo consiga entender a alegação, reproduzir uma
propriedade declarada, achar as fronteiras e discordar de maneira produtiva sem
precisar de acesso aos autores.
