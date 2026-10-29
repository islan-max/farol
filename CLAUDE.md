# Farol: instruções para agentes

Revisão de pull request que ensina. Documentação e interface em português do Brasil. Só soluções gratuitas; nenhuma API paga.

## Guia de desenvolvimento

Guia local do mantenedor: `Documents/Obsidian Vault/IA/guia-desenvolvimento-ia/README.md` (fora do repositório).
Leia o fluxo de trabalho e, antes de alterar uma funcionalidade, os módulos indicados pelos gatilhos do índice.
Registre contexto, decisões e resultados em `docs/CONTEXTO.md` e `docs/VERIFICACAO.md`, sem segredos ou dados pessoais.
Antes de publicar, percorra o checklist de publicação e justifique itens não aplicáveis.
Informe o que foi verificado, o que falhou e o que depende de acesso ou teste posterior.

## Regras do projeto

- Fluxo: issue, branch, PR, CI verde, merge squash. Nunca commit direto na `main`.
- Nada do PR revisado é executado: o Farol só lê texto. Sem `pull_request_target`.
- Comandos: `uv sync`, `uv run ruff check`, `uv run ruff format --check`, `uv run pytest`.
- Lições (`licoes/`) são a fonte única para CLI, Action e site; todo texto em pt-BR e sem inventar o que a ferramenta não disse.
