Closes #

## O que muda e por quê

<!-- Uma ou duas frases. O PR precisa ter conteúdo real: sem PR vazio nem só cosmético. -->

## Como conferi

- [ ] `uv run ruff check && uv run ruff format --check`
- [ ] `uv run pytest`
- [ ] Se mexi no site: `uv run python scripts/build_site.py` e `npm run --prefix site test:a11y`
- [ ] Se mexi em lições: o `antes` dispara a regra, o `depois` não, os links respondem e rodei `python scripts/atualizar_readme.py`
- [ ] Sem segredo no código

## O que não verifiquei

<!-- Seja honesto: o que ficou sem teste ou depende de outra pessoa. -->
