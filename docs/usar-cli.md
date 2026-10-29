# Usar o Farol na linha de comando

## Instalar e rodar

Precisa do [uv](https://docs.astral.sh/uv/) e de um repositório git. Para revisar JavaScript e TypeScript, também do Node.js 20 ou mais novo.

```bash
uvx --from git+https://github.com/islan-max/farol farol revisar
```

Ou instale uma vez: `uv tool install git+https://github.com/islan-max/farol` e use `farol revisar`.

## Comandos

| Comando | O que faz |
| --- | --- |
| `farol revisar` | Revisa as linhas que você alterou desde o último commit (`git diff HEAD`). |
| `farol revisar --base main` | Revisa tudo que mudou desde o ponto onde sua branch saiu de `main`. |
| `farol revisar --diff mudancas.diff` | Lê um diff pronto (`-` lê da entrada padrão). Os arquivos precisam existir na pasta atual. |
| `farol revisar --json` | Saída para outros programas. |
| `farol revisar --teto 5` | No máximo 5 comentários (padrão 10). |
| `farol revisar --ia` | Acrescenta uma nota de IA local (precisa do [Ollama](https://ollama.com) rodando e do modelo: `ollama pull qwen2.5-coder:1.5b`). Sem ele, avisa e segue sem IA. `--modelo` e `--ollama` ajustam. |
| `farol explicar E722` | Mostra a lição de uma regra (`eqeqeq`, `no-var` etc.), sem precisar de diff. |

## O que ele considera

- **Só as linhas alteradas.** Problema que já existia antes não aparece.
- **Uma vez por regra.** Se `except:` aparece em cinco lugares, vem um comentário com os outros quatro listados.
- **Teto.** Passando do limite, o resto aparece agrupado por regra. Lições de segurança passam na frente.
- Arquivos gerados, `lockfile`s, binários e linguagens não suportadas aparecem em "Não revisados", com o motivo.
- As regras são as do Farol: a configuração de `ruff` ou `eslint` do seu repositório é ignorada de propósito.

## JavaScript e TypeScript

Na primeira vez o Farol instala o ESLint fixado (cerca de 100 pacotes, com `npm ci --ignore-scripts`) em `~/.cache/farol`. Sem Node.js, os arquivos `.js`/`.ts` aparecem em "Não revisados" dizendo que falta o Node.

## Imagem de container

Sem `uv` nem Node.js, use a imagem publicada no GitHub Packages. Ela traz Python, Node.js, `git` e o ESLint já instalado (fixado, sem baixar a cada execução) e roda como usuário sem privilégios (uid 10001).

```bash
docker run --rm -v "$PWD:/repo" ghcr.io/islan-max/farol revisar --base main
docker run --rm ghcr.io/islan-max/farol explicar E722
```

Tags: `0.1.1` (versão exata), `0.1`, `v0` (mais nova 0.x) e `latest`. Para travar uma versão, use a exata. O diretório montado em `/repo` precisa ser um repositório git; a imagem só **lê** os arquivos. Receita em [`Dockerfile`](../Dockerfile); a CI constrói a imagem e roda um teste de fumaça (Python e JavaScript) antes de publicar.

## Erros comuns

- `Erro: fatal: not a git repository`: rode dentro de um repositório git ou use `--diff`.
- Arquivo com acento ou espaço no nome ficou de fora: limitação conhecida do leitor de `git diff` (registrada no código).
