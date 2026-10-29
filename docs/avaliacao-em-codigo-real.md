# Avaliação em código real

O conjunto de `evals/casos` é pequeno e escrito por quem escreveu as regras. Para achar o que ele não pega, o Farol foi rodado, em 29/10/2026, sobre arquivos de projetos abertos (clones rasos, só leitura), com amostragem dos achados para conferência manual. Foi uma checagem de **precisão por regra**, não uma medida estatística.

| Projeto | Arquivos | O que apareceu |
| --- | --- | --- |
| psf/requests | 37 `.py` | `F401` (35), `S105` (1) |
| pallets/flask | 83 `.py` | `S110` (7), `S105` (5) |
| pallets/click | 91 `.py` | `S110` (7) |
| expressjs/express | 50 `.js` sorteados | `no-var` (488), `no-unused-vars` (39), `eqeqeq` (1) |
| sindresorhus/is | 5 `.ts` | `no-unused-vars` (66) e dezenas de mensagens "regra não encontrada" |

## O que a medição achou (e foi corrigido)

1. **Comentários `eslint-disable` de plugins que o Farol não carrega** viravam apontamentos sem sentido ("Definition for rule 'unicorn/…' was not found"). Agora só entram regras que têm lição.
2. **`_` não era aceito como "não usado de propósito"**, embora a lição ensine isso (66 achados em `sindresorhus/is`, quase todos `const _ = …`). Agora nomes começando com `_` são aceitos.
3. **Parâmetros não usados** (`(req, res, next)`, `function (err, res)`) respondiam por 39 dos achados em `express`. Isso é idiomático em callbacks, então parâmetros deixaram de ser apontados; variáveis e imports continuam.
4. **Segurança em arquivos de teste** (`S105` com senha de mentira, `S110` com `except: pass`, `S113`, `S608`): 13 achados em `flask` e `requests`, 12 deles em `tests/`. Esses quatro não valem em `tests/`, `test/`, `test_*.py`, `*_test.py` e `conftest.py`. As demais regras continuam valendo em testes.

Depois das correções: `requests` mostra só `F401` e `B904`; `flask` só um `S110` (em `src/`); `click` sete `S110` (em `src/`); `express` um `no-unused-vars` e um `eqeqeq`; `is` os `no-explicit-any`. Os `B904` de `requests` e os `S110` de `click` foram lidos: são casos legítimos da regra.

## O que continua sendo "falso positivo" para um projeto estabelecido

- **`F401` em módulos de compatibilidade** (`requests/compat.py`, 35 achados): o projeto reexporta de propósito e liga a exceção na própria configuração. O Farol ignora a configuração do repositório revisado de propósito (regras previsíveis para quem aprende), então ele aponta. Quem tem esse caso deve usar `# noqa: F401` com o motivo, como a lição ensina.
- **`eqeqeq` em `x == null`**, idioma aceito por parte da comunidade. O Farol ensina `===` sempre.
- **`no-var` em código antigo**: correto, mas ruidoso em projeto legado. Como só as linhas alteradas são revisadas, o ruído se limita ao que a pessoa tocou.

## Limites

Poucos projetos, todos de bibliotecas maduras (código de iniciantes tem outro perfil). A conferência manual foi feita por amostra de 3 achados por regra. Isso reduz, mas não elimina, a chance de falso positivo em código real.
