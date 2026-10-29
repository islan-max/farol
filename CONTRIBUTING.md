# Como contribuir com o Farol

Obrigado por querer ajudar. O Farol existe para ensinar, então **a contribuição mais valiosa é uma boa lição**, seguida de um exemplo real bem escolhido e de um falso positivo bem descrito.

## Por onde começar

| Quero... | Vá para |
| --- | --- |
| Escrever uma lição nova | [docs/escrever-licao.md](docs/escrever-licao.md) e as issues com o rótulo [`lição`](https://github.com/islan-max/farol/labels/li%C3%A7%C3%A3o) |
| Achar um exemplo real para uma lição | O rótulo [`exemplo real`](https://github.com/islan-max/farol/labels/exemplo%20real) e `scripts/buscar_exemplos.py` |
| Relatar um comentário errado ou ruidoso | [Nova issue](https://github.com/islan-max/farol/issues/new/choose), "Falso positivo ou comentário errado" |
| Tirar uma dúvida ou propor uma ideia | [Discussões](https://github.com/islan-max/farol/discussions) |
| Algo fácil para a primeira vez | [`good first issue`](https://github.com/islan-max/farol/labels/good%20first%20issue) |

## Preparar o ambiente

Precisa de Python 3.12, [uv](https://docs.astral.sh/uv/) e Node.js 20 ou mais novo.

```bash
uv sync
uv run ruff check && uv run ruff format --check
uv run pytest
```

Para o site e a acessibilidade:

```bash
cd site && npm ci && cd ..
uv run python scripts/build_site.py
npm run --prefix site test:a11y       # no Windows, FAROL_BROWSER=chrome usa o Chrome instalado
```

## Fluxo de trabalho

1. **Abra uma issue** (ou comente em uma existente) dizendo o que pretende fazer.
2. Crie uma branch a partir da `main`. Nunca se faz commit direto na `main`.
3. Faça uma mudança com conteúdo real: **sem PR vazio nem só cosmético**.
4. Rode os comandos acima. A CI roda `pytest`, `ruff`, `gitleaks`, `pip-audit`, `npm audit`, CodeQL e os testes de acessibilidade.
5. Abra o PR. No corpo, use `Closes #NUMERO` (em inglês, para o GitHub fechar a issue sozinho).
6. O merge é *squash*.

## O que um PR de lição precisa

- O `antes` dispara a regra na ferramenta e o `depois` não (os testes conferem).
- Texto em português do Brasil, direto e acolhedor, sem sermão e sem afirmar o que a ferramenta não disse.
- Link da documentação oficial que responde 200.
- Se houver exemplo real: trecho de até 12 linhas, permalink de commit, licença permissiva e uma frase dizendo por que ele resolve o caso. Use `scripts/buscar_exemplos.py`; ele grava o trecho exato lido do commit.
- Um caso em `evals/casos/` com o problema e outro limpo, para vigiar falso positivo.
- Rode `python scripts/atualizar_readme.py` para atualizar a tabela de lições do README (a CI confere).

## Regras do projeto

- **Só soluções gratuitas.** Nada de API paga nem de serviço que exija cartão.
- **Nunca executar o código revisado.** O Farol só lê texto.
- **Acessibilidade é requisito**, não detalhe: o site passa no axe (WCAG 2.2 AA) nos temas claro e escuro.
- **Sem segredo no git.** O `gitleaks` roda em todo PR.
- Seja honesto sobre o que não verificou, como em [docs/VERIFICACAO.md](docs/VERIFICACAO.md).

## Conduta e segurança

Participando, você concorda com o [código de conduta](CODE_OF_CONDUCT.md). Para vulnerabilidades, siga a [política de segurança](SECURITY.md) e **não** abra uma issue pública.
