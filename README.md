# Farol

Revisão de pull request que **ensina**. Quem está aprendendo abre um PR e recebe "LGTM" ou nada; o lint aponta o erro e não explica. O Farol comenta cada ponto dizendo **o que é**, **por que importa** e **como corrigir**, e mostra como projetos reais resolvem o mesmo caso.

> Em construção. Já existem o núcleo para Python (12 lições), a CLI e a GitHub Action; JavaScript/TypeScript e o site chegam nos próximos PRs.

## Como vai funcionar

- **GitHub Action** (principal): comenta no PR, grátis em repositório público.
- **CLI**: `farol revisar` sobre um diff local.
- **Site**: cole um trecho de Python e veja as lições, tudo no navegador.

Não usa IA nem API paga. A análise vem de ferramentas abertas (ruff, eslint) e cada apontamento vira uma lição escrita à mão em português do Brasil.

## Usar a GitHub Action

```yaml
# .github/workflows/farol.yml
on: pull_request
permissions: { contents: read, pull-requests: write }
jobs:
  farol:
    runs-on: ubuntu-latest
    steps:
      - uses: islan-max/farol@main
```

Detalhes, limites e segurança em [docs/usar-action.md](docs/usar-action.md).

## Usar a CLI

Dentro de um repositório git, com suas alterações feitas:

```bash
uvx --from git+https://github.com/islan-max/farol farol revisar            # o que mudou desde o último commit
uvx --from git+https://github.com/islan-max/farol farol revisar --base main # tudo desde que a branch saiu de main
uvx --from git+https://github.com/islan-max/farol farol explicar E722       # uma lição, sem diff
```

O Farol só olha as **linhas que você alterou**, junta ocorrências da mesma regra em um comentário e mostra no máximo 10 por vez (`--teto`). `--json` dá a saída para outros programas.

## Desenvolvimento

```bash
uv sync
uv run ruff check
uv run pytest
```

Licença MIT.
