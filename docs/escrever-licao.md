# Como escrever uma lição

As lições são o produto. Cada uma é um arquivo TOML em `src/farol/licoes/python/` (ruff) ou `src/farol/licoes/javascript/` (ESLint). O nome do arquivo é o código da regra. A CLI, a Action e o site leem os mesmos arquivos.

```toml
codigo = "E722"            # código da regra, igual ao que a ferramenta emite
ferramenta = "ruff"        # ou "eslint"
linguagem = "python"       # só em javascript: "javascript" (bloco de código)
categoria = "seguranca"    # opcional: passa na frente quando o teto de comentários aperta
titulo = "..."
nivel = "iniciante"        # iniciante, intermediario ou avancado
o_que_e = """..."""
por_que_importa = """..."""
como_corrigir = """..."""
antes = '''código que dispara a regra'''
depois = '''o mesmo código corrigido'''
exemplos = ["E722-1"]      # ids em src/farol/exemplos/curados.json; pode ser []

[[docs]]
titulo = "Regra E722 no ruff"
url = "https://docs.astral.sh/ruff/rules/bare-except/"
```

## Tom

Colega técnico direto e acolhedor. "Isso é comum no começo" vale; sermão não. Frases curtas. Diga o erro, o motivo real (o que quebra) e o conserto. Não afirme o que a ferramenta não disse.

## O que os testes exigem

- O `antes` **dispara** a regra na ferramenta e o `depois` **não** (`tests/test_licoes.py`, `tests/test_eslint.py`). Por isso os dois são código completo e válido.
- Nível válido, link `https://` e `antes` diferente de `depois`.
- Exemplos citados existem e são da mesma regra.

## Exemplos reais

```bash
uv run python scripts/buscar_exemplos.py buscar --regra B006      # candidatos (precisa do gh logado)
uv run python scripts/buscar_exemplos.py adicionar --regra B006 --repo dono/projeto \
  --caminho caminho/arquivo.py --sha <commit de 40 caracteres> --linhas 10-14 \
  --porque "Uma frase: por que este trecho resolve o caso."
uv run python scripts/buscar_exemplos.py conferir                 # relê todos no GitHub
```

Nem toda lição precisa de exemplo: quando o jeito certo é apenas **não cometer o erro** (chave repetida, código depois do `return`, `f` sem campo), um trecho de projeto real não ensina nada, e a lição sai sem a seção. Na hora de escolher, procure o jeito certo em uso de verdade, e não o erro; documentação oficial também vale (o exemplo de `S113` vem da documentação do requests).

Leia o arquivo candidato e escolha você mesmo: a busca acha arquivos que contêm as palavras, não bons exemplos. O trecho tem até 12 linhas, vem de um commit fixo (permalink) e de um projeto com licença permissiva (MIT, Apache-2.0, BSD, ISC, PSF, Unlicense). Se não achar um exemplo bom, deixe `exemplos = []`: a lição sai sem a seção.

## Regra nova

1. Adicione o código à lista de regras (ruff: automático, pela pasta; ESLint: também em `src/farol/eslint/farol.config.mjs`).
2. Escreva a lição e rode `uv run pytest`.
3. Abra um caso em `evals/casos/` (com e sem o problema) para vigiar falso positivo.
