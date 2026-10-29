# IA local: o que foi medido e o que foi decidido

A IA é **opcional e fica desligada por padrão**. Ela só escreve uma nota curta, "No seu código", ligando a lição ao trecho da pessoa. Ela nunca cria nem remove um apontamento: a regra vem do ruff ou do ESLint e a lição é escrita à mão.

## Como foi medido

Em 29/10/2026, num runner `ubuntu-latest` do GitHub (4 vCPU, 16 GB de RAM, sem GPU), com o Ollama v0.40.13 e o modelo Qwen2.5-Coder em três tamanhos. Cinco apontamentos de exemplo (`except:` sem tipo, valor padrão mutável, SQL montado com texto, `eval`, variável não usada), cada um com a lição, a mensagem exata da ferramenta e o trecho no prompt. Temperatura 0,1, no máximo 140 tokens. Os dois workflows de medição estão no PR descartável [#23](https://github.com/islan-max/farol/pull/23).

| | Qwen2.5-Coder 1,5B | 3B | 7B |
| --- | --- | --- | --- |
| Download do modelo no runner | 13 s (941 MB) | 15 s | 25 s |
| Memória a mais com o modelo carregado | 0,6 GB | 2,0 GB | 4,7 GB |
| Velocidade de geração | 16 a 40 tokens/s | 8 tokens/s | 3,7 tokens/s |
| Tempo por nota | 2 a 9 s | 7 a 14 s | 16 a 37 s |
| Qualidade nas 5 notas | 5 corretas; uma frase mal formada ("segurança e segurança") | 5 corretas, mas português quebrado em 2 ("Isso usar `except Exception:`") | 5 corretas e as mais específicas (a de variável não usada sugeriu devolver `total`) |

Fora o modelo: baixar e extrair o Ollama leva cerca de 15 s e ocupa 2,4 GB no disco do runner (o pacote tem 1,5 GB).

## O que a primeira rodada mostrou (e por isso o prompt tem a mensagem da ferramenta)

Na primeira rodada o prompt só trazia a explicação geral. O 1,5B **errou 2 de 5**: disse que a variável `frete` "não estava declarada" (o problema era `total` nunca usado) e inventou um efeito para o valor padrão mutável ("todas as tarefas anteriores serão marcadas"). Com a **mensagem exata da ferramenta** e os três campos da lição no prompt, os erros sumiram. Moral: a IA pequena só presta quando a resposta é ancorada em fatos que o Farol já tem. Mesmo assim ela pode errar, por isso toda nota vem rotulada.

## Rodada real no GitHub (PR de demonstração [#31](https://github.com/islan-max/farol/pull/31))

A Action rodou com `ia: ollama` sobre três apontamentos (`B006`, `F841`, `E722`), com o 1,5B. O download do Ollama e do modelo e a geração das 3 notas cabem em cerca de 1 minuto de job. A **qualidade foi mista**, e vale ser dito:

| Apontamento | Primeira versão do prompt | Depois de exigir que siga o "Como corrigir" |
| --- | --- | --- |
| `B006` (lista como padrão) | Correta, mas repete a lição | Correta e mais específica (cita o parâmetro `feitas`) |
| `F841` (variável não usada) | Imprecisa: diz que `total` "é criada e usada", mas sugere `return total` | Igual |
| `E722` (`except:` sem tipo) | **Enganosa**: mandava capturar `KeyboardInterrupt` e `SystemExit`, o contrário da lição | Segue a lição ("nomeie o erro que você espera"), mas a primeira frase ainda afirma que o erro "é KeyboardInterrupt ou SystemExit" |

Ou seja: o 1,5B acertou bem as cinco notas da medição controlada, mas em uso real errou parte. O rótulo "pode errar" e a lição escrita à mão ao lado de cada nota existem por isso. Quem quiser notas melhores deve usar o 7B (`modelo: qwen2.5-coder:7b`), a um custo de 15 a 37 s por nota; **não medi o 7B nessa rodada real**.

## Amostra maior: 48 notas, 1,5B contra 7B (PR descartável [#44](https://github.com/islan-max/farol/pull/44))

Pedido do mantenedor depois da rodada pequena. O código real do Farol (`farol.ia`) gerou uma nota para cada um dos **48 apontamentos** formados pelo `antes` das 27 lições e pelos achados dos casos de avaliação com problema, com os dois modelos, no mesmo runner (4 vCPU, 16 GB). A saída completa, com a classificação de cada nota, está em [medicao-ia-notas.md](medicao-ia-notas.md).

| | 1,5B | 7B |
| --- | --- | --- |
| Notas boas | **39 de 48** (81%) | **46 de 48** (96%) |
| Imprecisas (acertam o essencial, afirmam algo falso ou confuso) | 7 | 1 |
| Enganosas (diagnóstico errado ou contradiz a lição) | 1 | 1 |
| Descartadas pela limpeza | 1 | 0 |
| Tempo por nota (média, máximo) | 3,9 s, 7,2 s | 17,4 s, 29,2 s |
| Memória usada no runner com o modelo carregado (total, incluindo o sistema) | 2,4 GB | 6,4 GB |

O que cada um errou:

- **1,5B, enganosa:** num `try` que só tocava em `item.valor`, afirmou que o erro ignorado era `FileNotFoundError` ("quando o arquivo não é encontrado"). Não havia arquivo nenhum; inventou um fato.
- **1,5B, imprecisas:** no `var`, disse que `total` "continua existindo fora do `for`" (era o `i`); no `except:`, que o código "não está tratando `KeyboardInterrupt`" (é o contrário: captura); no `raise` sem `from`, confundiu qual erro era capturado e qual era levantado (duas vezes); numa variável não usada, sugeriu "calcular o total sem o frete"; duas vezes inventou detalhes do código em `l` e na f-string.
- **7B, enganosa:** disse que um código com `f"..."` sem campo "está correto" e "não há necessidade de nenhuma mudança", contradizendo o apontamento.
- **7B, imprecisa:** num `not item in vistos`, afirmou "está correto, mas a ferramenta apontou uma melhor prática" (o resultado é mesmo igual, mas a frase confunde quem aprende).
- O 7B foi melhor onde importa para ensinar: acertou a correção de `F841` (devolver `total` em vez de `sum(precos)`) e escolheu o erro certo no `except` (`ValueError` para uma conversão).

**Limites desta medição, para não superestimar o resultado:** a classificação é minha, feita por quem também escreveu as lições, e não por uma segunda pessoa; os casos são os mesmos em que as lições se apoiam, então tendem a ser mais fáceis que código de iniciante de verdade; 48 notas por modelo é pouco; uma única execução (a geração tem temperatura 0,1, mas não é determinística); e **o runner de repositório privado (2 vCPU, 7 GB) não foi medido**: o 7B usou 6,4 GB no total, então provavelmente não cabe ali.

## Decisão

- Modelo padrão: `qwen2.5-coder:1.5b` (rápido, 0,6 GB a mais de RAM, cabe até no runner de repositório privado). O 3B não foi melhor. **Quem quer notas mais confiáveis deve usar o 7B** (`modelo: qwen2.5-coder:7b`): na amostra de 48, 96% de notas boas contra 81%, a um custo de cerca de 17 s por nota e de um download de alguns GB (não medi o tamanho no disco do runner). O orçamento de 4 minutos por execução cobre cerca de 14 notas com o 7B; o que passar disso sai só com a lição, sem a nota. Só em repositório público e com runner de 16 GB: em runner de 7 GB o 7B provavelmente não cabe (não medido).
- Desligada por padrão. Ligar: `with: ia: ollama` na Action ou `farol revisar --ia` na CLI (a CLI usa o Ollama que você já tem; não instala nada).
- **Custo.** Em repositório público o runner é grátis. Em repositório **privado**, baixar o Ollama e o modelo e gerar as notas consome minutos do plano (da ordem de 1 minuto a mais por execução com o 1,5B) num runner menor (2 vCPU e 7 GB, não medido).
- A nota nunca bloqueia: servidor fora do ar, tempo esgotado ou resposta estranha, e o comentário sai só com a lição. Duas falhas seguidas desligam a IA naquela execução; o orçamento total é de 4 minutos.
- Toda resposta é limpa antes de ir para o PR: sem HTML (não dá para forjar os marcadores do Farol), sem links, sem menção a pessoas, sem bloco de código, no máximo 420 caracteres.

## O que não foi medido

- Runner de repositório privado (2 vCPU, 7 GB), para os dois modelos.
- Qualidade em código de iniciante de verdade (os 48 casos são os da própria suíte) e avaliação por uma segunda pessoa; só dá para confiar nas notas por amostragem.
- PC do mantenedor (9,8 GB de RAM, sem GPU): não instalei o Ollama lá, pois o runner responde à pergunta principal.
