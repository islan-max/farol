# Política de segurança

## Versões com suporte

| Versão | Suporte |
| --- | --- |
| `v0` (tag móvel) e a última `0.x` | Correções de segurança |
| Versões anteriores | Atualize para a última |

## Como relatar uma vulnerabilidade

**Não abra uma issue pública.** Use o relato privado do GitHub:

**[Relatar uma vulnerabilidade](https://github.com/islan-max/farol/security/advisories/new)**

Inclua o que viu, como reproduzir (de preferência com um PR ou trecho de código mínimo) e o impacto que imagina. Respondo o mais rápido que puder. Se confirmado, corrijo, publico um aviso e dou o crédito a quem relatou, se quiser.

## O que o Farol promete (e como foi verificado)

O Farol lê texto de pull requests de terceiros, então estas garantias importam:

- **Nunca executa o código revisado.** Ele manda o texto por entrada padrão para o ruff e o ESLint, sem shell, e instala o ESLint com `npm ci --ignore-scripts`.
- **Só roda em `pull_request`.** Recusa `pull_request_target`, que daria escrita a código de fora.
- **Permissões mínimas:** `contents: read` e `pull-requests: write` (e `issues: write` só se o painel for ligado).
- **Em PR de fork** o token é só de leitura, então o Farol não tenta comentar e escreve o resultado no resumo do job.
- **O texto da IA local é limpo** antes de ir para o PR: sem HTML (não dá para forjar os marcadores), sem link, sem menção e sem bloco de código.
- **Sem segredo no git**, com `gitleaks` em todo PR; Actions de terceiros fixadas por SHA; `pip-audit`, `npm audit` e CodeQL no CI.

As evidências e o que **não** foi verificado estão em [docs/VERIFICACAO.md](docs/VERIFICACAO.md).

## Fora do escopo

Problemas nas ferramentas que o Farol usa (ruff, ESLint, Ollama) devem ser relatados aos projetos delas. Notas erradas da IA local são um limite conhecido e documentado em [docs/medicao-ia.md](docs/medicao-ia.md); relate-as como issue comum.
