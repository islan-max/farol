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

## Decisão

- Modelo padrão: `qwen2.5-coder:1.5b` (rápido, 0,6 GB, cabe até no runner de repositório privado). O 3B não foi melhor. O 7B escreve melhor, mas custa 4,7 GB de RAM e de 15 a 37 s por nota (até 6 minutos com 10 comentários): serve para quem quiser, via `modelo:`.
- Desligada por padrão. Ligar: `with: ia: ollama` na Action ou `farol revisar --ia` na CLI (a CLI usa o Ollama que você já tem; não instala nada).
- **Custo.** Em repositório público o runner é grátis. Em repositório **privado**, baixar o Ollama e o modelo e gerar as notas consome minutos do plano (da ordem de 1 minuto a mais por execução com o 1,5B) num runner menor (2 vCPU e 7 GB, não medido).
- A nota nunca bloqueia: servidor fora do ar, tempo esgotado ou resposta estranha, e o comentário sai só com a lição. Duas falhas seguidas desligam a IA naquela execução; o orçamento total é de 4 minutos.
- Toda resposta é limpa antes de ir para o PR: sem HTML (não dá para forjar os marcadores do Farol), sem links, sem menção a pessoas, sem bloco de código, no máximo 420 caracteres.

## O que não foi medido

- Runner de repositório privado (2 vCPU, 7 GB).
- Qualidade em código de iniciante de verdade e em outras regras além das cinco medidas; só dá para confiar nas notas por amostragem.
- PC do mantenedor (9,8 GB de RAM, sem GPU): não instalei o Ollama lá, pois o runner responde à pergunta principal.
