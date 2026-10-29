# Fase 2: o que ficou fora do MVP e por quê

O MVP é o núcleo sem IA, a Action, a CLI e o site. Estes itens foram decididos **fora** de propósito, com a razão.

## IA local (Ollama)

A ideia: um modelo aberto pequeno (por exemplo Qwen2.5-Coder 1,5B) reescreve a explicação de uma lição para o trecho da pessoa e resume o PR. A IA nunca criaria um apontamento; só reformularia um que a ferramenta já achou.

Por que ficou de fora:

- **Pouco ganho agora.** A explicação de cada regra já é escrita à mão, revisada e testada. Um modelo de 1,5B reescrevendo isso alucina com facilidade e raramente melhora o texto.
- **Custo não é zero para todo mundo.** Rodar na Action só é grátis em repositório **público** (runner de 4 vCPU e 16 GB). Em repositório **privado**, baixar o modelo (cerca de 1 GB) e inferir consome os minutos do plano de quem usa, num runner menor.
- **Medição pendente.** Antes de depender dele é preciso medir tempo e memória no runner e em um PC modesto (o do mantenedor tem 9,8 GB de RAM e nenhuma GPU).

Se for feito: opcional e desligado por padrão, só no runner do próprio repositório ou no Ollama local de quem roda a CLI; prompt só com o apontamento já validado e o trecho; saída curta, sanitizada e marcada "gerada por IA local"; timeout com volta silenciosa ao texto da lição; um caso de teste de injeção de prompt vindo do código revisado.

## Resumo entre PRs

"O que você já domina e o que se repete." Precisa guardar histórico entre execuções sem servidor. Caminho mais barato: uma issue "Painel Farol" mantida pela Action, com a contagem de regras por pessoa em um comentário HTML. Não cabia no prazo e não é o núcleo do valor.

## Outras ideias

- Mais lições (hoje 12 de Python e 5 de JavaScript/TypeScript) e mais exemplos reais (hoje 5 lições têm exemplo). A ferramenta `scripts/buscar_exemplos.py` existe para isso.
- Publicar no PyPI (`uvx farol`), com nome reservado.
- Fixar as GitHub Actions de terceiros por SHA do commit, em vez de por tag.
- "Teste agora" para JavaScript/TypeScript no navegador, se houver um build de ESLint para o navegador que valha o peso.
- Recusar `--teto` negativo e outros ajustes finos de CLI.
