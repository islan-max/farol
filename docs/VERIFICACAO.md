# Relatório de verificação

Instância do modelo do guia de desenvolvimento. Registra o que foi **observado**, não o que foi configurado.

## Identificação

- Projeto: Farol, revisão de pull request que ensina.
- Versão: `main` no commit `c6520e7` (CI verde: [execução](https://github.com/islan-max/farol/actions/runs/40875885590); deploy do site: [execução](https://github.com/islan-max/farol/actions/runs/40875885712)). Este relatório entra em um PR seguinte.
- Ambientes e endereços testados: Windows 11 com Chrome (local), Ubuntu com Chromium (CI), `https://islan-max.github.io/farol/` (produção) e a Action rodando em PRs reais de `islan-max/farol`.
- Data e executor: 29/10/2026, o próprio agente de desenvolvimento (Claude), com o mantenedor Islan Max.
- Módulos consultados: S01 a S09, Q01, Q02, I01, V01, V02, V03, D01.
- Escopo: MVP (núcleo Python e JS/TS, CLI, Action, site). Fora do escopo: IA local e resumo entre PRs (`docs/fase-2.md`).

## Evidências por controle

Estados: APROVADO, FALHOU, NÃO VERIFICADO, N/A. Criticidade: B = bloqueador, R = recomendado.

| ID | Crit. | Teste ou inspeção | Esperado | Observado | Estado | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| S01-01 | B | gitleaks no histórico completo, em todo PR e push | Nenhum segredo | Job `security` verde em todos os PRs (#2 a #20) | APROVADO | CI, job `security` |
| S01-02 | B | `git ls-files` por `.env`/chaves e `git grep` por padrões de token | Nada rastreado | Nada encontrado; só o `GITHUB_TOKEN` do Actions é usado, nunca gravado | APROVADO | Comandos rodados em 29/10 |
| S01-03 | B | Leitura de `permissions:` dos três workflows | Mínimo necessário | ci: `contents: read`; Farol: `contents: read` + `pull-requests: write`; Pages: `contents: read`, e `pages: write` + `id-token: write` só no job de deploy | APROVADO | `.github/workflows/*.yml` |
| S02 | — | Não há login, sessões nem papéis | — | — | N/A | O produto não tem autenticação; o único acesso é o token do workflow (S01-03) |
| S03 | — | Não há banco de dados | — | — | N/A | Sem armazenamento; nada a isolar |
| S04-01 | B | Caminho proibido: linha fora do diff não gera comentário; problema antigo não é comentado | Só linhas alteradas | Testes passam (`test_nao_comenta_linha_fora_do_diff`, `test_revisar_nao_comenta_problema_antigo`) | APROVADO | `pytest` (mais de 100 testes) |
| S04-02 | B | Nada do PR é executado: ruff e ESLint recebem o texto por entrada padrão; subprocessos com lista de argumentos (sem shell); `npm ci --ignore-scripts`; configuração do repositório revisado é ignorada | Só leitura | Inspeção do código e testes `test_regras_do_repositorio_revisado_sao_ignoradas` (ruff e ESLint) | APROVADO | `analise/ruff.py`, `analise/eslint.py` |
| S04-03 | B | `main()` da Action em `pull_request_target`, `push` e sem evento | Recusa (código 2) | Recusa nos três | APROVADO | `test_main_so_roda_em_pull_request` |
| S04-04 | B | PR de fork: token só leitura | Nunca tenta comentar; escreve o resumo | Teste com API falsa passa. **Não testado em PR de fork real** (precisa de segunda conta) | APROVADO (teste) / NÃO VERIFICADO (fork real) | `test_pr_de_fork_so_escreve_o_resumo...` |
| S05 | — | Não há upload nem download de arquivos de usuários | — | — | N/A | O "Teste agora" lê texto colado, na própria página |
| S06-01 | B | Token e dados em logs e respostas | Nenhum token impresso; nada armazenado | `GITHUB_TOKEN` só vai no cabeçalho de `github.py`; `grep` de `print(...token...)` vazio; o site não guarda nada | APROVADO | Inspeção + `grep` |
| S07-01 | B | `curl http://` e API do Pages | Redireciona para HTTPS; HTTPS forçado | `301` e `https_enforced: true` | APROVADO | `gh api repos/islan-max/farol/pages` |
| S07-02 | R | Cabeçalhos HTTP de segurança | Configuráveis | O GitHub Pages não permite cabeçalhos próprios (HSTS, X-Frame-Options). A CSP foi posta por `<meta>` (sem `frame-ancestors`); o site funciona com ela ativa e sem erros no console | NÃO VERIFICADO (limite da plataforma) | Site estático sem sessão nem ação sensível; limitação aceita |
| S07-03 | B | Cookies e armazenamento do navegador | Nenhum | `document.cookie` vazio e `localStorage`/`sessionStorage` com 0 itens após usar o "Teste agora" | APROVADO | `a11y.test.mjs`, teste de privacidade |
| S08 | — | Não há endpoint público próprio | — | A Action faz poucas chamadas à API (3 de leitura + 1 por arquivo, no máximo 40; cerca de 45 chamadas no total), bem abaixo do limite do token | N/A | `action.py` |
| S09-01 | B | `pip-audit` (uv.lock) e `npm audit` (site e ESLint) no CI | Sem achado alto | Verde em todos os PRs | APROVADO | CI, job `security` e `site` |
| S09-02 | R | Versões fixadas; Dependabot | Lockfiles e pins | `uv.lock`, dois `package-lock.json`, ruff `==0.17.3` igual ao WASM, `.github/dependabot.yml` | APROVADO | arquivos |
| S09-03 | B | Scripts e recursos externos no site | Nenhum de terceiros | WASM, fontes e script saem do próprio site; nenhuma requisição externa | APROVADO | teste de privacidade |
| S09-04 | R | Actions de terceiros fixadas por SHA | Por SHA | Fixadas por tag (`@v7` etc.) | NÃO VERIFICADO (pendência) | `docs/fase-2.md` |
| Q01-01 | B | Fluxo 1: Action em PR real no GitHub | Comentários por linha com a lição | PR #11 (Python): 9 comentários, `os` e `json` agrupados; PR #18 (TypeScript): 5 comentários. Ambos fechados sem merge (demonstrações) | APROVADO | `gh api repos/islan-max/farol/pulls/11/comments` |
| Q01-02 | B | Fluxo 2: CLI instalada do GitHub | Roda e aponta | `uvx --from git+https://github.com/islan-max/farol farol revisar` instalou e apontou o `import` sobrando | APROVADO | execução em 29/10 |
| Q01-03 | B | Fluxo 3: "Teste agora" no endereço final | Mesmas regras da Action | 10 apontamentos em 9 regras, foco no resultado, console sem erros | APROVADO | `https://islan-max.github.io/farol/teste.html` |
| Q01-04 | B | Links internos, 404 e navegação | Tudo existe; 404 responde | Teste varre todos os links; `/nao-existe` devolve 404 com a página própria | APROVADO | `a11y.test.mjs`, `curl` |
| Q01-05 | R | Celular e reflow | Sem rolagem horizontal a 320 e 640 px | Passa nas páginas principais (e no resultado do "Teste agora") | APROVADO (automático) / NÃO VERIFICADO (aparelho real) | `a11y.test.mjs` |
| Q02-01 | R | Peso das páginas no ar (com gzip) | Leve; WASM só quando usado | Início ≈ 97 KB com as 4 fontes; WASM do ruff ≈ 3,6 MB, só em "Teste agora" (≈ 1 s aqui). **Lighthouse/PageSpeed não rodou** | APROVADO (medição de peso) / NÃO VERIFICADO (Lighthouse) | `curl` com `Accept-Encoding: gzip` |
| I01-01 | B | Deploy por workflow e conferência no endereço final | Site no ar e igual ao build | `Site` verde; páginas, `robots.txt`, `sitemap.xml`, `og.png` e o `.wasm` (tipo `application/wasm`) respondem 200 | APROVADO | execução do workflow + `curl` |
| I01-02 | R | Reversão | Reverter o commit e republicar | Não ensaiada | NÃO VERIFICADO | pendência |
| I01-03 | — | Domínio próprio | — | Usa `islan-max.github.io/farol` | N/A | sem DNS próprio |
| V01-01 | B | Idioma, título único, descrição, canonical e um só `h1` por página | Presentes | Teste passa nas 22 páginas do site | APROVADO | `a11y.test.mjs` |
| V02-01 | R | `robots.txt` e `sitemap.xml` | Existem e listam as páginas | 200 no endereço final | APROVADO | `curl` |
| V02-02 | R | Search Console | Opcional | Não configurado | NÃO VERIFICADO | depende da conta do mantenedor |
| V03-01 | R | Favicon, `og:image` (1200×630) e rodapé | Presentes | SVG de favicon e `og.png` no ar; rodapé com licença e repositório | APROVADO | `curl`, páginas |
| V03-02 | R | Prévia ao compartilhar em redes | Aparece | Não testada nas plataformas | NÃO VERIFICADO | — |
| D01 | — | Cookies, analytics, formulários, dados pessoais | Nenhum | Sem cookies, sem análise de acesso, sem formulário que envia dados; nenhuma requisição externa (teste) | N/A (ausência verificada) | `a11y.test.mjs` |

## Acessibilidade (requisito do projeto)

| ID | Teste | Observado | Estado |
| --- | --- | --- | --- |
| A11Y-01 | axe-core (WCAG 2.0 A/AA, 2.1 A/AA, 2.2 AA e boas práticas) em todas as páginas e no estado "com resultados", nos temas claro e escuro | 0 violações; 64 testes passam (Chrome local e Chromium na CI). Em uma rodada anterior, o tema claro falhou em contraste e foi corrigido | APROVADO |
| A11Y-02 | Teclado: primeiro Tab no link "Pular para o conteúdo"; foco visível em todo elemento focável (claro e escuro); revisar só com teclado leva o foco aos resultados; campo vazio avisa | Passa | APROVADO |
| A11Y-03 | Zoom 200%: sem rolagem horizontal a 640 px de largura (equivale a 200% de 1280) e a 320 px (400%) | Passa | APROVADO (equivalência automatizada) |
| A11Y-04 | Leitor de tela (NVDA/VoiceOver) lendo o "Teste agora" | Não executado. Há `aria-live`, `role="status"` e foco no título do resultado, mas sem ouvir | NÃO VERIFICADO |
| A11Y-05 | Navegação manual com zoom do navegador em aparelho real | Não executada | NÃO VERIFICADO |

Observação: ferramentas automáticas cobrem só parte dos problemas de acessibilidade; A11Y-04 e A11Y-05 continuam abertos.

## Qualidade das lições

| ID | Teste | Observado | Estado |
| --- | --- | --- | --- |
| L-01 | Em cada lição o `antes` dispara a regra e o `depois` não (ruff e ESLint; em `.js` e `.ts`) | 17 lições passam | APROVADO |
| L-02 | Exemplos reais relidos no commit do permalink, com licença permissiva | 5 de 5 batem (`scripts/buscar_exemplos.py conferir`) | APROVADO |
| L-03 | Falso positivo no conjunto de avaliação (`evals/casos`) | 0 nos 5 casos limpos. O conjunto é pequeno (14 casos): não prova ausência de falso positivo em código real | APROVADO (no conjunto) |
| L-04 | Links de documentação | Os 29 links respondem 200 (conferido em 29/10) | APROVADO |

## Itens não aplicáveis

Resumidos na tabela acima (S02, S03, S05, S08, I01-03, D01), cada um com a justificativa na coluna "Evidência".

## Pendências

| Controle | Impacto | O que falta | Próxima ação |
| --- | --- | --- | --- |
| A11Y-04 e A11Y-05 | Médio | Ouvir o "Teste agora" com leitor de tela e testar em aparelho real | Teste manual com NVDA e no celular |
| S04-04 | Baixo | PR de fork real | Abrir um PR de outra conta |
| S09-04 | Baixo | Fixar Actions por SHA | Fase 2 |
| I01-02 | Baixo | Ensaiar a reversão | Reverter um commit de teste e ver o Pages |
| Q02-01 | Baixo | Lighthouse/PageSpeed | Rodar no endereço final |
| V02-02, V03-02 | Baixo | Search Console e prévia social | Opcional |

## Parecer

- Estado: **PUBLICADO E VERIFICADO NO ESCOPO**, com as pendências acima (nenhuma bloqueadora).
- Bloqueadores: nenhum aberto. Todos os controles de criticidade B que se aplicam estão APROVADOS; os dois abertos de acessibilidade (leitor de tela e aparelho real) não impedem o uso, mas significam que a acessibilidade foi comprovada por axe, teclado e reflow automatizados, e **não** por uso com tecnologia assistiva.
- Limitações da verificação: executor único (sem revisão externa); os demos da Action foram feitos em PRs do próprio repositório; o conjunto de avaliação tem 14 casos; o Pages não permite cabeçalhos HTTP próprios.
- Plano de recuperação: reverter o commit na `main` e deixar o workflow `Site` republicar; a Action é usada por tag/branch, então quem fixar uma versão não é afetado.
