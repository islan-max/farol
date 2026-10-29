# Farol

Revisão de pull request que **ensina**. Quem está aprendendo abre um PR e recebe "LGTM" ou nada; o lint aponta o erro e não explica. O Farol comenta cada ponto dizendo **o que é**, **por que importa** e **como corrigir**, e mostra como projetos reais resolvem o mesmo caso.

> Em construção. O núcleo (Python), a CLI, a GitHub Action e o site chegam nos próximos PRs.

## Como vai funcionar

- **GitHub Action** (principal): comenta no PR, grátis em repositório público.
- **CLI**: `farol revisar` sobre um diff local.
- **Site**: cole um trecho de Python e veja as lições, tudo no navegador.

Não usa IA nem API paga. A análise vem de ferramentas abertas (ruff, eslint) e cada apontamento vira uma lição escrita à mão em português do Brasil.

## Desenvolvimento

```bash
uv sync
uv run ruff check
uv run pytest
```

Licença MIT.
