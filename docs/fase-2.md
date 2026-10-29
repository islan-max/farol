# Fase 2: o que ficou fora do MVP

O MVP é o núcleo sem IA, a Action, a CLI e o site. Estes itens foram decididos **fora** de propósito, com a razão.

## IA local (Ollama): feita depois do MVP

Medida e implementada como **opcional, desligada por padrão**. O que foi medido, o que deu errado na primeira rodada e as decisões estão em [medicao-ia.md](medicao-ia.md).

## Resumo entre PRs: ainda não feito

"O que você já domina e o que se repete." Precisa guardar histórico entre execuções sem servidor. Caminho mais barato: uma issue "Painel Farol" mantida pela Action, com a contagem de regras por pessoa em um comentário HTML.

## Outras ideias

- Mais lições (hoje 12 de Python e 5 de JavaScript/TypeScript) e mais exemplos reais (hoje 5 lições têm exemplo). A ferramenta `scripts/buscar_exemplos.py` existe para isso.
- Publicar no PyPI (`uvx farol`), com nome reservado.
- Fixar as GitHub Actions de terceiros por SHA do commit, em vez de por tag.
- "Teste agora" para JavaScript/TypeScript no navegador, se houver um build de ESLint para o navegador que valha o peso.
- Recusar `--teto` negativo e outros ajustes finos de CLI.
