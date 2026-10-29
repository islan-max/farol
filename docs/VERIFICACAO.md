# Relatório de verificação

Instância do modelo do guia de desenvolvimento. Registra o que foi **observado**, não o que foi configurado.

## Identificação

- Projeto: Farol, revisão de pull request que ensina.
- Versão: release [v0.1.0](https://github.com/islan-max/farol/releases/tag/v0.1.0) (commit `a7b7002`) mais a documentação e os testes posteriores na `main` (PRs até o #41). Relatório revisado em 29/10/2026 depois de mais lições, IA local, Painel, medição em código real e Lighthouse.
- Ambientes e endereços testados: Windows 11 com Chrome (local), Ubuntu com Chromium (CI), `https://islan-max.github.io/farol/` (produção) e a Action rodando em PRs reais de `islan-max/farol`.
- Data e executor: 29/10/2026, o próprio agente de desenvolvimento (Claude), com o mantenedor Islan Max.
- Módulos consultados: S01 a S09, Q01, Q02, I01, V01, V02, V03, D01.
- Escopo: núcleo Python e JS/TS, CLI, Action, site e os dois opcionais (IA local e Painel do Farol, ambos desligados por padrão). O que continua fora: `docs/fase-2.md`.

## Evidências por controle

Estados: APROVADO, FALHOU, NÃO VERIFICADO, N/A. Criticidade: B = bloqueador, R = recomendado.

| ID | Crit. | Teste ou inspeção | Esperado | Observado | Estado | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| S01-01 | B | gitleaks no histórico completo, em todo PR e push | Nenhum segredo | Job `security` verde em todos os PRs (#2 a #41) | APROVADO | CI, job `security` |
| S01-02 | B | `git ls-files` por `.env`/chaves e `git grep` por padrões de token | Nada rastreado | Nada encontrado; só o `GITHUB_TOKEN` do Actions é usado, nunca gravado | APROVADO | Comandos rodados em 29/10 |
| S01-03 | B | Leitura de `permissions:` dos três workflows | Mínimo necessário | ci: `contents: read`; Farol: `contents: read` + `pull-requests: write`; Pages: `contents: read`, e `pages: write` + `id-token: write` só no job de deploy | APROVADO | `.github/workflows/*.yml` |
| S02 | — | Não há login, sessões nem papéis | — | — | N/A | O produto não tem autenticação; o único acesso é o token do workflow (S01-03) |
| S03 | — | Não há banco de dados | — | — | N/A | Sem armazenamento; nada a isolar |
| S04-01 | B | Caminho proibido: linha fora do diff não gera comentário; problema antigo não é comentado | Só linhas alteradas | Testes passam (`test_nao_comenta_linha_fora_do_diff`, `test_revisar_nao_comenta_problema_antigo`) | APROVADO | `pytest` (177 testes) |
| S04-02 | B | Nada do PR é executado: ruff e ESLint recebem o texto por entrada padrão; subprocessos com lista de argumentos (sem shell); `npm ci --ignore-scripts`; configuração do repositório revisado é ignorada | Só leitura | Inspeção do código e testes `test_regras_do_repositorio_revisado_sao_ignoradas` (ruff e ESLint) | APROVADO | `analise/ruff.py`, `analise/eslint.py` |
| S04-05 | B | Texto da IA vai para o comentário do PR: HTML, comentário HTML (forjar marcador), link, menção e bloco de código | Removidos ou descartados | Testes de `limpar` e de resposta estranha passam; o Ollama só é chamado em `127.0.0.1` | APROVADO | `tests/test_ia.py` |
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
| S09-04 | R | Actions de terceiros fixadas por SHA | Por SHA | Todas por SHA do commit, com a versão em comentário; um teste falha se alguma voltar a ficar por tag. O Ollama é baixado com versão fixa e sha256 conferido | APROVADO | PR #25, `tests/test_workflows.py`, `scripts/instalar_ollama.sh` |
| Q01-01 | B | Fluxo 1: Action em PR real no GitHub | Comentários por linha com a lição | PR #11 (Python): 9 comentários, `os` e `json` agrupados; PR #18 (TypeScript): 5 comentários; PR #36 (JavaScript, usando `islan-max/farol@v0` **de fora**, sem `uses: ./`): 2 comentários. Todos fechados sem merge (demonstrações) | APROVADO | `gh api repos/islan-max/farol/pulls/11/comments` |
| Q01-02 | B | Fluxo 2: CLI instalada do GitHub | Roda e aponta | `uvx --from git+https://github.com/islan-max/farol farol revisar` instalou e apontou o `import` sobrando | APROVADO | execução em 29/10 |
| Q01-03 | B | Fluxo 3: "Teste agora" no endereço final | Mesmas regras da Action | 10 apontamentos em 9 regras, foco no resultado, console sem erros | APROVADO | `https://islan-max.github.io/farol/teste.html` |
| Q01-04 | B | Links internos, 404 e navegação | Tudo existe; 404 responde | Teste varre todos os links; `/nao-existe` devolve 404 com a página própria | APROVADO | `a11y.test.mjs`, `curl` |
| Q01-05 | R | Celular e reflow | Sem rolagem horizontal a 320 e 640 px | Passa nas páginas principais (e no resultado do "Teste agora") | APROVADO (automático) / NÃO VERIFICADO (aparelho real) | `a11y.test.mjs` |
| Q02-01 | R | Peso e Lighthouse 13.6.0 (móvel, simulado) no endereço final | Leve; notas altas | Início 98 (desempenho) e 100 (acessibilidade, boas práticas e SEO), LCP 0,9 s, 96 KiB. "Teste agora" 98/100/100/100, 3,7 MiB por causa do WASM do ruff (só nessa página). Uma lição: 100/100/100/100 | APROVADO | Lighthouse rodado em 29/10 (`npx lighthouse`), `curl` com gzip |
| I01-01 | B | Deploy por workflow e conferência no endereço final | Site no ar e igual ao build | `Site` verde; páginas, `robots.txt`, `sitemap.xml`, `og.png` e o `.wasm` (tipo `application/wasm`) respondem 200 | APROVADO | execução do workflow + `curl` |
| I01-02 | R | Reversão ensaiada | Reverter um commit na `main` republica o site | Reimplantar uma tag foi **bloqueado** (o ambiente `github-pages` só aceita deploy da `main`, o que é desejável). O revert de um commit de documentação (#40) fez o endereço final voltar a mostrar `@main`; o PR #41 restaurou `@v0` e o endereço final foi conferido de novo | APROVADO | PRs #40 e #41, `curl` do site nas duas etapas |
| I01-03 | — | Domínio próprio | — | Usa `islan-max.github.io/farol` | N/A | sem DNS próprio |
| V01-01 | B | Idioma, título único, descrição, canonical e um só `h1` por página | Presentes | Teste passa nas 32 páginas do site | APROVADO | `a11y.test.mjs` |
| V02-01 | R | `robots.txt` e `sitemap.xml` | Existem e listam as páginas | 200 no endereço final | APROVADO | `curl` |
| V02-02 | R | Search Console | Opcional | Não configurado | NÃO VERIFICADO | depende da conta do mantenedor |
| V03-01 | R | Favicon, `og:image` (1200×630) e rodapé | Presentes | SVG de favicon e `og.png` no ar; rodapé com licença e repositório | APROVADO | `curl`, páginas |
| V03-02 | R | Prévia ao compartilhar em redes | Aparece | Não testada nas plataformas | NÃO VERIFICADO | — |
| D01 | — | Cookies, analytics, formulários, dados pessoais | Nenhum | Sem cookies, sem análise de acesso, sem formulário que envia dados; nenhuma requisição externa (teste) | N/A (ausência verificada) | `a11y.test.mjs` |

## Acessibilidade (requisito do projeto)

| ID | Teste | Observado | Estado |
| --- | --- | --- | --- |
| A11Y-01 | axe-core (WCAG 2.0 A/AA, 2.1 A/AA, 2.2 AA e boas práticas) em todas as páginas e no estado "com resultados", nos temas claro e escuro | 0 violações; 84 testes passam (Chrome local e Chromium na CI). Em uma rodada anterior, o tema claro falhou em contraste e foi corrigido | APROVADO |
| A11Y-02 | Teclado: primeiro Tab no link "Pular para o conteúdo"; foco visível em todo elemento focável (claro e escuro); revisar só com teclado leva o foco aos resultados; campo vazio avisa | Passa | APROVADO |
| A11Y-03 | Zoom 200%: sem rolagem horizontal a 640 px de largura (equivale a 200% de 1280) e a 320 px (400%) | Passa | APROVADO (equivalência automatizada) |
| A11Y-04 | Leitor de tela (NVDA/VoiceOver) lendo o "Teste agora" | Não executado. Há `aria-live`, `role="status"` e foco no título do resultado, mas sem ouvir | NÃO VERIFICADO |
| A11Y-05 | Navegação manual com zoom do navegador em aparelho real | Não executada | NÃO VERIFICADO |

Observação: ferramentas automáticas cobrem só parte dos problemas de acessibilidade; A11Y-04 e A11Y-05 continuam abertos.

## Qualidade das lições

| ID | Teste | Observado | Estado |
| --- | --- | --- | --- |
| L-01 | Em cada lição o `antes` dispara a regra e o `depois` não (ruff e ESLint; em `.js` e `.ts`) | 27 lições passam (17 de Python, 10 de JS/TS) | APROVADO |
| L-02 | Exemplos reais relidos no commit do permalink, com licença permissiva | 7 de 7 batem (`scripts/buscar_exemplos.py conferir`) | APROVADO |
| L-03 | Falso positivo no conjunto de avaliação (`evals/casos`) e em código real | 0 nos 7 casos limpos (18 casos). Em requests, flask, click, express e sindresorhus/is a medição achou 4 problemas reais, **corrigidos** ([avaliacao-em-codigo-real.md](avaliacao-em-codigo-real.md)); sobraram falsos positivos conhecidos para projetos estabelecidos (`F401` em módulos de compatibilidade, `== null`). Poucos projetos e amostra de 3 achados por regra | APROVADO (com limites registrados) |
| L-04 | Links de documentação | Todos os links das lições respondem 200 (conferido em 29/10, em duas rodadas) | APROVADO |

## Opcionais: IA local e Painel do Farol

| ID | Crit. | Teste | Observado | Estado |
| --- | --- | --- | --- | --- |
| IA-01 | B | A IA só acrescenta nota; não cria nem remove apontamentos | Teste compara os apontamentos antes e depois | APROVADO |
| IA-02 | B | Servidor fora do ar, tempo esgotado, JSON ruim, 500 e orçamento estourado | O comentário sai só com a lição; duas falhas seguidas desligam a IA | APROVADO |
| IA-03 | R | Roda no runner do GitHub (PR #31) com o Ollama v0.40.13 (sha256 conferido) e o Qwen2.5-Coder 1,5B | 3 notas em cerca de 1 minuto de job | APROVADO |
| IA-04 | R | Qualidade das notas do 1,5B em uso real | 1 de 3 boa; 1 com imprecisão; 1 enganosa antes de apertar o prompt e, depois, ainda com a primeira frase errada ([medicao-ia.md](medicao-ia.md)). Mitigações: desligada por padrão, nota rotulada "pode errar", lição escrita à mão ao lado | FALHOU (parcial; aceito por ser opcional e rotulado) |
| IA-05 | R | Runner de repositório privado (2 vCPU, 7 GB), modelo 7B em uso real, PC do mantenedor | Não medidos | NÃO VERIFICADO |
| PAINEL-01 | B | Painel no GitHub de verdade | A issue [#35](https://github.com/islan-max/farol/issues/35) foi criada pela Action no PR #34 | APROVADO |
| PAINEL-02 | B | Regras do resumo, limites, corpo corrompido, 403, fork e bot | 13 testes passam; fork e bot são pulados; erro do GitHub vira aviso e a revisão segue | APROVADO |
| PAINEL-03 | R | Dois PRs revisados ao mesmo tempo | O último a gravar vence (sem trava); documentado | NÃO VERIFICADO (limite aceito) |

## Itens não aplicáveis

Resumidos na tabela acima (S02, S03, S05, S08, I01-03, D01), cada um com a justificativa na coluna "Evidência".

## Pendências

| Controle | Impacto | O que falta | Próxima ação |
| --- | --- | --- | --- |
| A11Y-04 e A11Y-05 | Médio | Ouvir o "Teste agora" com leitor de tela e testar em aparelho real | Teste manual com NVDA e no celular (depende do mantenedor) |
| S04-04 | Baixo | PR de fork real | Abrir um PR de outra conta |
| IA-04 e IA-05 | Baixo (opcional) | Qualidade do 1,5B em uso real; 7B e runner privado nunca rodados em uso real | Medir o 7B e uma amostra maior de notas antes de recomendar a IA |
| PAINEL-03 | Baixo | Corrida entre dois PRs revisados juntos | Serializar com `concurrency` no workflow de quem usar |
| V02-02, V03-02 | Baixo | Search Console e prévia social | Opcional (depende da conta do mantenedor) |
| Publicação no PyPI | Baixo | Nome e token | Depende da conta do mantenedor |

## Parecer

- Estado: **PUBLICADO E VERIFICADO NO ESCOPO**, com as pendências acima (nenhuma bloqueadora) e uma ressalva explícita sobre a IA local.
- Bloqueadores: nenhum aberto. Todos os controles de criticidade B que se aplicam estão APROVADOS. Os dois abertos de acessibilidade (leitor de tela e aparelho real) significam que a acessibilidade foi comprovada por axe, Lighthouse, teclado e reflow automatizados, e **não** por uso com tecnologia assistiva.
- Ressalva sobre a IA local (IA-04): as notas do modelo pequeno **às vezes erram**, inclusive em uso real. Por isso a IA é opcional, vem desligada, a nota é rotulada e a lição escrita à mão aparece sempre. Não a recomendo ligada em um repositório de iniciantes sem antes medir o 7B.
- Limitações da verificação: executor único (sem revisão externa); os demos da Action foram feitos em PRs do próprio repositório; poucos projetos na medição em código real; o Pages não permite cabeçalhos HTTP próprios.
- Plano de recuperação: **ensaiado**. Reverter o commit na `main` republica o site (o ambiente `github-pages` só aceita deploy da `main`); a Action é usada pela tag `v0` ou `v0.1.0`, então quem fixar uma versão não é afetado por mudanças na `main`.
