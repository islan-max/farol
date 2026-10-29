# Fase 2: o que foi adiado e o que continua fora

O MVP é o núcleo sem IA, a Action, a CLI e o site. Itens que o MVP deixou de fora de propósito. Os dois maiores foram feitos depois; o que sobra está no fim.

## IA local (Ollama): feita depois do MVP

Medida e implementada como **opcional, desligada por padrão**. O que foi medido, o que deu errado na primeira rodada e as decisões estão em [medicao-ia.md](medicao-ia.md).

## Resumo entre PRs: feito depois do MVP

Implementado como a issue "Painel do Farol" (opcional, `painel: on`). Veja [usar-action.md](usar-action.md).

## O que continua fora

- Mais lições (hoje 17 de Python e 10 de JavaScript/TypeScript) e mais exemplos reais (hoje 7 lições têm exemplo). A ferramenta `scripts/buscar_exemplos.py` existe para isso; a lição de `S113` ficou sem exemplo porque nenhum trecho achado era bom.
- Publicar no PyPI (`uvx farol`): precisa do nome reservado e de um token, que são do mantenedor.
- Medir o modelo de 7B e uma amostra maior de notas da IA em uso real, e o runner de repositório privado.
- "Teste agora" para JavaScript/TypeScript no navegador: não verifiquei se existe um build de ESLint para o navegador que valha o peso.
- Serializar a gravação do Painel quando dois PRs são revisados ao mesmo tempo.
- Recusar `--teto` negativo e outros ajustes finos da CLI.
