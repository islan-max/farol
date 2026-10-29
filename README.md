# Farol

**Revisão de pull request que ensina.** Quem está aprendendo abre um PR e recebe "LGTM" ou nada; o lint aponta o erro e não explica. O Farol comenta cada ponto dizendo **o que é**, **por que importa** e **como corrigir**, e, em algumas lições, mostra **como projetos reais resolvem o mesmo caso**.

[Site e "Teste agora"](https://islan-max.github.io/farol/) · [Como usar a Action](docs/usar-action.md) · [Como usar a CLI](docs/usar-cli.md) · [Lições](https://islan-max.github.io/farol/licoes/)

Não usa IA, não precisa de chave e não executa o seu código. A análise vem de ferramentas abertas (ruff para Python; ESLint com typescript-eslint para JavaScript e TypeScript) e cada apontamento vira uma lição escrita à mão, em português do Brasil, com nível (iniciante a intermediário) e link para a documentação.

## Um comentário do Farol

> **Farol · `except:` sem tipo captura erro demais** · `E722` · nível iniciante
>
> Um `except:` sem nome de exceção captura **qualquer** erro, inclusive os que você nunca quis tratar, como o Ctrl+C.
>
> **Por que importa.** Quando algo dá errado por um motivo inesperado, o programa segue em silêncio e você perde a pista do problema. […]
>
> **Como corrigir.** Nomeie o erro que você espera tratar. […]
>
> **Como projetos reais resolvem.** Captura só `TypeError` e `ValueError`, os dois erros que `int()` pode levantar aqui. ([django/django](https://github.com/django/django/blob/817df1c4d6d38f416460d7d9354d7deab9d35139/django/contrib/gis/gdal/srs.py#L211-L214), BSD-3-Clause)

## Usar

**GitHub Action** (o caminho principal; grátis em repositório público):

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

**Linha de comando** (precisa do [uv](https://docs.astral.sh/uv/) e de um repositório git):

```bash
uvx --from git+https://github.com/islan-max/farol farol revisar
uvx --from git+https://github.com/islan-max/farol farol explicar E722
```

**No navegador:** cole um trecho de Python em [Teste agora](https://islan-max.github.io/farol/teste.html). A análise roda na sua máquina (ruff em WebAssembly); o código não é enviado a ninguém.

## O que ele faz (e não faz)

- Olha **só as linhas que você alterou**. Problema que já existia não vira comentário.
- Comenta cada regra **uma vez** por arquivo, com no máximo **10 comentários** por PR; o resto vai agrupado. Segurança vem primeiro.
- As regras são as do Farol; a configuração de lint do seu repositório é ignorada de propósito.
- Hoje: **17 lições de Python** e **10 de JavaScript/TypeScript**; 6 delas têm exemplo real de projeto aberto, com link para o commit e licença.
- Código sem lição escrita não é apontado. Se uma ferramenta acha algo que o Farol ainda não explica, ele não inventa explicação.
- Fora do MVP, de propósito: IA local e resumo entre PRs. Veja [docs/fase-2.md](docs/fase-2.md).

## Segurança e privacidade

Só roda em `pull_request` (recusa `pull_request_target`), com permissões mínimas, lê o texto do PR pela API e nunca o executa. O site não usa cookies, análise de acesso nem recursos de terceiros. Detalhes e evidências em [docs/VERIFICACAO.md](docs/VERIFICACAO.md).

## Contribuir

As lições são o produto: [docs/escrever-licao.md](docs/escrever-licao.md) explica o formato, o tom e os testes. O fluxo é issue, branch, PR e CI verde.

```bash
uv sync
uv run ruff check && uv run ruff format --check
uv run pytest                      # precisa de Node.js para os testes de JavaScript/TypeScript
cd site && npm ci && cd ..         # site e testes de acessibilidade
uv run python scripts/build_site.py
npm run --prefix site test:a11y    # use FAROL_BROWSER=chrome para usar o Chrome instalado
```

Contexto e decisões do projeto: [docs/CONTEXTO.md](docs/CONTEXTO.md).

## Licença

MIT.
