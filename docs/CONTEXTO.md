# Contexto do projeto

Instância do modelo de contexto do guia. Sem segredos.

## Produto e ambientes

- Nome, objetivo e responsável: **Farol**, revisão de pull request que ensina (o que é, por que importa, como corrigir, como projetos reais resolvem). Responsável: Islan Max (islan-max).
- Tipo: ferramenta de linha de comando + GitHub Action + site estático.
- Público e dispositivos: qualquer pessoa aprendendo a programar; site em celular e desktop.
- Fluxos essenciais: (1) a Action comenta em um PR com lições; (2) `farol revisar` na linha de comando; (3) colar Python em "Teste agora" no site e ver as lições.
- Público, privado e administrativo: tudo público; não há área privada, login nem administração.
- Domínios e ambientes: repositório `github.com/islan-max/farol`; site em `islan-max.github.io/farol` (GitHub Pages). Sem domínio próprio.
- Escopo autorizado: construir e publicar o MVP até 01/11/2026.

## Implementação real

- Repositório e instruções locais: este repositório; `CLAUDE.md`.
- Runtime: Python 3.12 e uv; ruff 0.17.3 fixado (o WASM do site é da mesma versão). JS/TS: ESLint 10 com typescript-eslint 8 (versões fixadas em `src/farol/eslint/package-lock.json`, instalado em cache com `npm ci --ignore-scripts`; precisa do Node.js 20+). Site em HTML/CSS/JS puro, gerado por `scripts/build_site.py`; testes de acessibilidade com Playwright e axe em `site/`.
- Comandos: `uv sync`, `uv run ruff check`, `uv run ruff format --check`, `uv run pytest`.
- Autenticação, papéis, banco, armazenamento de arquivos: nenhum.
- Hospedagem e publicação: GitHub Pages por workflow; Action distribuída pelo próprio repositório.
- Serviços externos: GitHub (API de PR com o `GITHUB_TOKEN` do workflow). Nada mais.
- Variáveis sensíveis: apenas `GITHUB_TOKEN` fornecido pelo GitHub Actions; nenhum valor no repositório.

## Dados e operação

- Dados coletados: nenhum. O site não usa cookies nem analytics; o "Teste agora" roda no navegador e não envia o código.
- Indexação: páginas públicas indexáveis (sitemap e robots).
- Custo, tráfego e disponibilidade: gratuito (repositório público, Actions e Pages gratuitos). Em repositório privado a Action consome minutos da cota do usuário.
- Reversão: reverter o commit na `main` e republicar o Pages.
- Fora do MVP: IA local e resumo entre PRs (ver `docs/fase-2.md`).
- Identidade: base de editor sóbrio com acentos âmbar (`#ffc857`) e verde-água; Inter e JetBrains Mono servidas pelo próprio site; tema escuro padrão e claro pelo sistema.

## Seleção de módulos

| Módulo | Aplicável? | Motivo |
| --- | --- | --- |
| S01 | Sim | Git público, `GITHUB_TOKEN`, gitleaks no CI |
| S04 | Sim | Diff e texto do PR são entrada não confiável; nada é executado |
| S07 | Sim | Site no Pages (HTTPS, sem cookies; CSP via meta) |
| S09 | Sim | Dependências fixadas, auditoria no CI, WASM do ruff copiado de versão fixa |
| Q01, Q02, I01 | Sim | Avaliados em qualquer site |
| V01, V02, V03 | Sim | Site público com sitemap, favicon e prévia social |
| D01 | N/A (verificado) | Sem cookies, analytics nem requisição externa; confirmado por teste automático |
| S02, S03, S05, S08 | N/A | Sem login, banco, upload nem endpoint próprio |
| S06 | Sim (restrito) | Token do workflow nunca é impresso; nada é armazenado |

## Decisões

| Decisão | Justificativa | Data |
| --- | --- | --- |
| Núcleo sem IA; IA local e resumo entre PRs na fase 2 | Prazo de 4 dias; IA pequena agrega pouco e custa minutos em repositório privado | 29/10/2026 |
| Exemplos reais curados à mão (script offline para achar candidatos) | Busca ao vivo é não determinística, limitada a 10/min e sem licença conferida | 29/10/2026 |
| JS e TS com `typescript-eslint` | O parser padrão do ESLint não lê TypeScript | 29/10/2026 |
| Teto de 10 comentários inline por PR e deduplicação por regra | Evitar ruído que ninguém lê | 29/10/2026 |
| Ruff e ESLint do Farol, não os do repositório revisado | Regras e lições precisam ser previsíveis e testáveis; a configuração de fora mudaria o resultado | 29/10/2026 |
| Campo `categoria` na lição para a prioridade de segurança | O prefixo do código não serve entre ferramentas | 29/10/2026 |
| Site sem cookies, análise de acesso, CDN ou fontes externas | Privacidade e CSP simples; tudo sai do próprio endereço | 29/10/2026 |
