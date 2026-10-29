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

## Erros comuns

- `Erro: fatal: not a git repository`: rode dentro de um repositório git ou use `--diff`.
- Arquivo com acento ou espaço no nome ficou de fora: limitação conhecida do leitor de `git diff` (registrada no código).
