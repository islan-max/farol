# Usar o Farol como GitHub Action

O Farol comenta no seu pull request explicando cada ponto: o que é, por que importa, como corrigir. Não usa IA, não precisa de chave e não executa o código do PR.

## Instalar

Crie `.github/workflows/farol.yml` no repositório:

```yaml
name: Farol
on:
  pull_request:

permissions:
  contents: read
  pull-requests: write

jobs:
  farol:
    runs-on: ubuntu-latest
    steps:
      - uses: islan-max/farol@main
```

Não precisa de `actions/checkout`: o Farol lê os arquivos do PR pela API do GitHub.

Opções (`with:`):

| Opção | Padrão | Para que serve |
| --- | --- | --- |
| `teto` | `10` | Máximo de comentários por linha em um PR. O que passar disso vai agrupado, por regra, no corpo da review. |
| `token` | `github.token` | Só mude se souber por quê. |

## O que ele faz

- Olha **só as linhas alteradas** no PR. Problema que já existia antes não vira comentário.
- Comenta cada regra **uma vez por arquivo**. Se `except:` aparece em cinco lugares, o comentário lista os outros quatro.
- Em um novo commit no mesmo PR, **não repete** uma regra já explicada naquele arquivo.
- Se não achar nada, **não comenta**; o resultado fica no resumo do job.
- Arquivos gerados, `lockfile`s, binários e linguagens ainda não suportadas aparecem em "Não revisados".
- Em arquivos de teste (`tests/`, `test_*.py`, `*_test.py`, `conftest.py`), as regras `S105`, `S110`, `S113` e `S608` não valem: senha de mentira e `except: pass` são normais ali.
- Em JavaScript/TypeScript, parâmetros de função não usados não são apontados, e nomes começando com `_` valem como "não usado de propósito".

## Linguagens

Python (ruff) e JavaScript/TypeScript (ESLint com typescript-eslint: `.js`, `.jsx`, `.mjs`, `.cjs`, `.ts`, `.tsx`). O Node.js já vem nos runners do GitHub; o Farol instala o ESLint fixado uma vez por execução, sem rodar scripts de instalação. As regras são as do Farol; a configuração do ESLint do seu repositório é ignorada.

## Permissões e segurança

- Precisa de `pull-requests: write` para comentar e `contents: read` para ler. Nada além disso.
- Só roda no evento `pull_request`. O Farol **recusa** `pull_request_target`, que daria permissão de escrita a código vindo de fora.
- PR de **fork**: o GitHub dá ao workflow um token só de leitura. Nesse caso o Farol não tenta comentar; escreve o resultado no resumo do job e em anotações no diff.
- Repositório **privado**: funciona, mas o tempo do job conta nos minutos gratuitos do seu plano.

## Quando algo dá errado

- **Nenhum comentário apareceu**: veja o resumo do job. Se disser "nenhum apontamento", está tudo bem.
- **Erro 403 ao comentar**: o workflow não tem `pull-requests: write`, ou o PR veio de um fork.
- **Erro 422**: alguma linha apontada não está no diff; o Farol cai para o resumo do job.
