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
      - uses: islan-max/farol@v0
```

Não precisa de `actions/checkout`: o Farol lê os arquivos do PR pela API do GitHub.

Opções (`with:`):

| Opção | Padrão | Para que serve |
| --- | --- | --- |
| `teto` | `10` | Máximo de comentários por linha em um PR. O que passar disso vai agrupado, por regra, no corpo da review. |
| `ia` | `off` | `ollama` liga uma nota extra de IA local em cada comentário. Veja abaixo. |
| `modelo` | `qwen2.5-coder:1.5b` | Modelo do Ollama usado com `ia: ollama`. |
| `painel` | `off` | `on` mantém a issue "Painel do Farol" (precisa de `issues: write`). Veja abaixo. |
| `token` | `github.token` | Só mude se souber por quê. |

## O que ele faz

- Olha **só as linhas alteradas** no PR. Problema que já existia antes não vira comentário.
- Comenta cada regra **uma vez por arquivo**. Se `except:` aparece em cinco lugares, o comentário lista os outros quatro.
- Em um novo commit no mesmo PR, **não repete** uma regra já explicada naquele arquivo.
- Se não achar nada, **não comenta**; o resultado fica no resumo do job.
- Arquivos gerados, `lockfile`s, binários e linguagens ainda não suportadas aparecem em "Não revisados".
- Em arquivos de teste (`tests/`, `test_*.py`, `*_test.py`, `conftest.py`), as regras `S105`, `S110`, `S113` e `S608` não valem: senha de mentira e `except: pass` são normais ali.
- Em JavaScript/TypeScript, parâmetros de função não usados não são apontados, e nomes começando com `_` valem como "não usado de propósito".

## IA local (opcional)

```yaml
      - uses: islan-max/farol@v0
        with:
          ia: ollama
```

O runner baixa o Ollama (conferido por sha256) e o modelo (cerca de 1 GB) e o Farol acrescenta, em cada comentário, uma nota **No seu código**, rotulada "IA local, pode errar". A IA nunca cria nem tira apontamentos, e se algo falhar o comentário sai só com a lição. Em repositório público é grátis; em **privado** consome minutos do seu plano. Medições, escolha de modelo e limites em [medicao-ia.md](medicao-ia.md).

## Painel do Farol: o que se repete entre PRs (opcional)

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write          # só para o painel

    steps:
      - uses: islan-max/farol@v0
        with:
          painel: "on"
```

A Action mantém **uma issue** "Painel do Farol" (rótulo `farol`) com, para cada pessoa, o que **se repete** (regras que apareceram em 2 ou mais PRs), o que **apareceu agora** e o que **já parece dominado** (apareceu antes e não está nos 2 PRs mais recentes, com 3 ou mais PRs revisados). O resumo da pessoa também entra no corpo da review ("Seu progresso neste repositório"), quando já há histórico.

- O histórico fica em um comentário HTML no corpo da issue e guarda só o **login** (já público no PR), o **número do PR** e os **códigos das regras**. Até 30 PRs por pessoa e 50 pessoas. É regravado a cada PR revisado; dois PRs revisados no mesmo segundo podem sobrescrever um ao outro (o último vence).
- Não roda para PR de fork nem de bot. Sem a permissão `issues: write`, o painel é pulado com um aviso e a revisão segue normal.
- Para zerar, apague a issue ou edite o corpo.

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
