"""Gera o site estático em `_site/` a partir das lições (fonte única) e de `site/assets`.

Uso: python scripts/build_site.py   (depois de `npm ci` em site/ para copiar o WASM e as fontes)
"""

import html
import json
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from farol.comentarios import NIVEIS  # noqa: E402
from farol.exemplos import da_licao  # noqa: E402
from farol.licoes import Licao, todas  # noqa: E402

SAIDA = RAIZ / "_site"
ASSETS = RAIZ / "site" / "assets"
NODE = RAIZ / "site" / "node_modules"
URL = "https://islan-max.github.io/farol/"
REPO = "https://github.com/islan-max/farol"
BASE_404 = "/farol/"  # a página 404 é servida em qualquer caminho, então usa links absolutos

CSP = (
    "default-src 'none'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self'; "
    "img-src 'self'; font-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'"
)
DESCRICAO = (
    "O Farol revisa pull requests ensinando: cada comentário explica o que é, "
    "por que importa e como corrigir. Sem IA e sem chave de API."
)


def esc(texto: str) -> str:
    return html.escape(texto, quote=True)


def md(texto: str) -> str:
    """Só o que as lições usam: `código` e **negrito**. O resto é texto escapado."""
    t = esc(texto)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)


def bloco(codigo: str, rotulo: str) -> str:
    return f'<pre tabindex="0" aria-label="{esc(rotulo)}"><code>{esc(codigo)}</code></pre>'


def exemplo_html(ex, titulo_tag: str) -> str:
    return (
        f'<div class="cartao exemplo-real"><{titulo_tag}>Como projetos reais resolvem</{titulo_tag}>'
        f"<p>{md(ex.porque)}</p>{bloco(ex.trecho, 'Trecho de ' + ex.repo)}"
        f'<p><a href="{esc(ex.permalink)}">{esc(ex.repo)}</a> · licença {esc(ex.licenca)}</p></div>'
    )


def licao_html(lc: Licao, titulo_tag: str = "h2") -> str:
    docs = " · ".join(f'<a href="{esc(d["url"])}">{esc(d["titulo"])}</a>' for d in lc.docs)
    return (
        f'<p class="meta"><span class="nivel">nível {NIVEIS[lc.nivel]}</span>'
        f'<span class="nivel">regra <code>{esc(lc.codigo)}</code> do {esc(lc.ferramenta)}</span></p>'
        f"<p>{md(lc.o_que_e)}</p>"
        f"<{titulo_tag}>Por que importa</{titulo_tag}><p>{md(lc.por_que_importa)}</p>"
        f"<{titulo_tag}>Como corrigir</{titulo_tag}><p>{md(lc.como_corrigir)}</p>"
        f'<p class="suave">Antes:</p>{bloco(lc.antes, "Antes")}'
        f'<p class="suave">Depois:</p>{bloco(lc.depois, "Depois")}'
        + "".join(exemplo_html(ex, titulo_tag) for ex in da_licao(lc.exemplos))
        + (f"<p>Para ler mais: {docs}</p>" if docs else "")
    )


def pagina(
    arquivo: str,
    titulo: str,
    corpo: str,
    descricao: str = DESCRICAO,
    nivel: int = 0,
    ativo: str = "",
) -> None:
    pre = "../" * nivel
    abs_ = BASE_404 if arquivo == "404.html" else None
    ref = (lambda caminho: abs_ + caminho) if abs_ else (lambda caminho: pre + caminho)
    nav = [
        ("index.html", "Início"),
        ("teste.html", "Teste agora"),
        ("licoes/index.html", "Lições"),
        ("usar.html", "Como usar"),
    ]
    itens = "".join(
        f'<li><a href="{ref(h)}"{' aria-current="page"' if h == ativo else ""}>{n}</a></li>'
        for h, n in nav
    )
    url = URL + arquivo.removesuffix("index.html")
    doc = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<title>{esc(titulo)}</title>
<meta name="description" content="{esc(descricao)}">
<link rel="canonical" href="{url}">
<link rel="icon" href="{ref("assets/logo.svg")}" type="image/svg+xml">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(descricao)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{URL}assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="{ref("assets/style.css")}">
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<header class="topo"><div class="contorno">
<a class="marca" href="{ref("index.html")}"><img src="{ref("assets/logo.svg")}" alt="" width="32" height="32">Farol</a>
<nav aria-label="Principal"><ul>{itens}</ul></nav>
</div></header>
<main id="conteudo" tabindex="-1"><div class="contorno">
{corpo}
</div></main>
<footer class="rodape"><div class="contorno">
<p>Farol é software livre (licença MIT). <a href="{REPO}">Código no GitHub</a> ·
<a href="{REPO}/issues">Relatar um problema</a>. Este site não usa cookies nem análise de acesso.</p>
</div></footer>
</body>
</html>
"""
    destino = SAIDA / arquivo
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(doc, encoding="utf-8", newline="\n")


def construir() -> None:
    SAIDA.mkdir(exist_ok=True)
    for filho in SAIDA.iterdir():  # esvazia sem apagar a pasta (um servidor local pode estar nela)
        shutil.rmtree(filho) if filho.is_dir() else filho.unlink()
    catalogo = sorted(todas().values(), key=lambda lc: (lc.ferramenta, lc.codigo))
    python = [lc for lc in catalogo if lc.ferramenta == "ruff"]
    javascript = [lc for lc in catalogo if lc.ferramenta == "eslint"]
    amostra = next(lc for lc in python if lc.codigo == "E722")

    # --- ativos ---
    shutil.copytree(ASSETS, SAIDA / "assets")
    fontes = SAIDA / "assets" / "fonts"
    fontes.mkdir(exist_ok=True)
    for pacote, prefixo, pesos in (
        ("inter", "inter", (400, 600)),
        ("jetbrains-mono", "jetbrains-mono", (400, 700)),
    ):
        for peso in pesos:
            origem = (
                NODE / "@fontsource" / pacote / "files" / f"{prefixo}-latin-{peso}-normal.woff2"
            )
            shutil.copy(origem, fontes / f"{prefixo}-{peso}.woff2")
    vendor = SAIDA / "assets" / "vendor" / "ruff"
    vendor.mkdir(parents=True)
    for nome in ("ruff_wasm.js", "ruff_wasm_bg.wasm", "LICENSE"):
        shutil.copy(NODE / "@astral-sh" / "ruff-wasm-web" / nome, vendor / nome)
    dados = {
        lc.codigo: {"html": f"<h3>{md(lc.titulo)}</h3>" + licao_html(lc, "h4")} for lc in python
    }
    (SAIDA / "licoes.json").write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")

    # --- páginas ---
    pagina(
        "index.html",
        "Farol: revisão de pull request que ensina",
        f"""<section class="heroi">
<h1>Revisão de PR que <span class="destaque">ensina</span>.</h1>
<p class="lead">O Farol comenta o seu pull request explicando cada ponto: o que é, por que importa e como corrigir.
Para quem está aprendendo e recebeu “LGTM” ou nada.</p>
<div class="acoes">
<a class="botao primario" href="teste.html">Teste agora com o seu código</a>
<a class="botao" href="usar.html">Instalar no seu repositório</a>
</div></section>
<h2>Como é um comentário do Farol</h2>
<article class="cartao"><p class="onde">Comentário no PR, na linha do <code>except:</code></p>
<h3>{md(amostra.titulo)}</h3>{licao_html(amostra, "h4")}</article>
<h2>Como funciona</h2>
<ol class="passos">
<li>Você abre o pull request.</li>
<li>O Farol olha <strong>só as linhas que você mudou</strong>, nunca o código antigo.</li>
<li>Cada regra vira uma lição, uma vez por arquivo, com no máximo 10 comentários por PR.</li>
</ol>
<h2>O que ele não faz</h2>
<div class="grade">
<div class="cartao"><h3>Não usa IA</h3><p>A análise vem do <a href="https://docs.astral.sh/ruff/">ruff</a> (Python) e do <a href="https://eslint.org/">ESLint</a> (JavaScript e TypeScript). Nada de resposta inventada: se o Farol aponta, a ferramenta apontou.</p></div>
<div class="cartao"><h3>Não executa seu código</h3><p>Ele só lê o texto do PR. Também recusa rodar em <code>pull_request_target</code>.</p></div>
<div class="cartao"><h3>Não pede chave nem conta</h3><p>Funciona com o token que o próprio GitHub Actions já dá. Grátis em repositório público.</p></div>
</div>
<h2>Lições escritas à mão e testadas</h2>
<p>Hoje são {len(python)} lições para Python e {len(javascript)} para JavaScript e TypeScript. Em cada uma,
o exemplo “antes” realmente dispara a regra e o “depois” não: isso é conferido por teste automático.</p>
<p><a href="licoes/index.html">Ver todas as lições</a></p>""",
        ativo="index.html",
    )

    cabecalho_teste = """<h1>Teste agora</h1>
<p class="texto">Cole um trecho de Python. A análise roda <strong>aqui, no seu navegador</strong>: o código não é enviado a ninguém.
Num PR de verdade o Farol olha só as linhas alteradas; aqui ele olha o trecho inteiro.</p>
<div class="texto">
<label class="rotulo" for="codigo">Seu código Python</label>
<textarea id="codigo" spellcheck="false" autocomplete="off" autocapitalize="off" placeholder="def somar(a, b):&#10;    return a + b"></textarea>
<div class="acoes">
<button type="button" class="botao primario" id="revisar">Revisar</button>
<button type="button" class="botao" id="exemplo">Carregar um exemplo</button>
</div>
<p id="status" class="status" role="status"></p>
</div>
<div id="resultado" aria-live="polite"></div>
<script type="module" src="assets/teste.js"></script>"""
    pagina(
        "teste.html",
        "Teste agora | Farol",
        cabecalho_teste,
        "Cole um trecho de Python e veja as lições do Farol, tudo no navegador.",
        ativo="teste.html",
    )

    por_nivel = ""
    for nome, grupo_linguagem in (("Python", python), ("JavaScript e TypeScript", javascript)):
        por_nivel += f"<h2>{nome}</h2>"
        for chave, rotulo in NIVEIS.items():
            grupo = [lc for lc in grupo_linguagem if lc.nivel == chave]
            if grupo:
                linhas = "".join(
                    f'<li><a href="{esc(lc.codigo)}.html"><span class="codigo-regra">{esc(lc.codigo)}</span>'
                    f'<span class="titulo-licao">{md(lc.titulo)}</span></a></li>'
                    for lc in grupo
                )
                por_nivel += f'<h3>Nível {rotulo}</h3><ul class="lista-licoes">{linhas}</ul>'
    pagina(
        "licoes/index.html",
        "Lições | Farol",
        f'<h1>Lições</h1><p class="texto">{len(python) + len(javascript)} lições, cada uma com o erro, o motivo e a correção.</p>{por_nivel}',
        "Catálogo das lições do Farol para Python, JavaScript e TypeScript, por nível.",
        nivel=1,
        ativo="licoes/index.html",
    )
    for lc in python + javascript:
        pagina(
            f"licoes/{lc.codigo}.html",
            f"{lc.titulo} ({lc.codigo}) | Farol",
            f'<p><a href="index.html">← Todas as lições</a></p><h1>{md(lc.titulo)}</h1><div class="texto">{licao_html(lc)}</div>',
            lc.o_que_e.replace("`", "")[:160],
            nivel=1,
            ativo="licoes/index.html",
        )

    pagina(
        "usar.html",
        "Como usar | Farol",
        USAR,
        "Instale o Farol como GitHub Action ou use a linha de comando.",
        ativo="usar.html",
    )
    pagina(
        "404.html",
        "Página não encontrada | Farol",
        f'<h1>Página não encontrada</h1><p>O endereço não existe. <a href="{BASE_404}">Voltar ao início</a>.</p>',
    )

    paginas = ["", "teste.html", "usar.html", "licoes/"] + [
        f"licoes/{lc.codigo}.html" for lc in python + javascript
    ]
    (SAIDA / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{URL}{p}</loc></url>\n" for p in paginas)
        + "</urlset>\n",
        encoding="utf-8",
        newline="\n",
    )
    (SAIDA / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {URL}sitemap.xml\n", encoding="utf-8", newline="\n"
    )
    print(f"Site gerado em {SAIDA} ({len(python) + len(javascript)} lições).")


USAR = f"""<h1>Como usar</h1>
<div class="texto">
<h2>GitHub Action</h2>
<p>Crie <code>.github/workflows/farol.yml</code> no repositório:</p>
<pre tabindex="0" aria-label="Workflow do GitHub Actions"><code>name: Farol
on:
  pull_request:

permissions:
  contents: read
  pull-requests: write

jobs:
  farol:
    runs-on: ubuntu-latest
    steps:
      - uses: islan-max/farol@main</code></pre>
<p>Não precisa de <code>actions/checkout</code>. O Farol comenta só nas linhas alteradas, uma vez por regra e por arquivo,
com no máximo 10 comentários (opção <code>teto</code>). Sem apontamentos, ele não comenta.</p>
<h3>Segurança e limites</h3>
<ul class="lista">
<li>Só roda em <code>pull_request</code>; recusa <code>pull_request_target</code>.</li>
<li>PR vindo de fork: o GitHub dá só leitura, então o resultado vai para o resumo do job.</li>
<li>Repositório privado funciona, mas o tempo do job consome os minutos gratuitos do seu plano.</li>
</ul>
<h2>Linha de comando</h2>
<pre tabindex="0" aria-label="Comandos da CLI"><code>uvx --from git+{REPO} farol revisar
uvx --from git+{REPO} farol revisar --base main
uvx --from git+{REPO} farol explicar E722</code></pre>
<p>Precisa do <a href="https://docs.astral.sh/uv/">uv</a> e de um repositório git. <code>--json</code> dá a saída para outros programas.</p>
<h2>Linguagens</h2>
<p>Python (ruff) e JavaScript/TypeScript (ESLint com typescript-eslint). Arquivos <code>.js</code>, <code>.jsx</code>,
<code>.mjs</code>, <code>.cjs</code>, <code>.ts</code> e <code>.tsx</code> são revisados na Action e na linha de comando, que precisam
do Node.js (já vem nos runners do GitHub). O “Teste agora” do site roda só Python.</p>
<p>Mais detalhes na <a href="{REPO}/tree/main/docs">documentação do repositório</a>.</p>
</div>"""


if __name__ == "__main__":
    construir()
