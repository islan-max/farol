"""Gera os SVGs animados do README (banner e demonstração da CLI), nos temas escuro e claro.

Cores do GitHub (Primer) para a moldura e o texto; o âmbar do feixe é a identidade do Farol.
São dois arquivos por imagem, escolhidos no README com <picture>, porque o GitHub segue o tema do
site e não deixa colocar <style> no README. Respeita prefers-reduced-motion.

Uso: python scripts/gerar_assets.py
"""

from html import escape
from pathlib import Path

SAIDA = Path(__file__).resolve().parent.parent / "docs" / "assets"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"

TEMAS = {
    "dark": {
        "fundo": "#0d1117",
        "canvas": "#161b22",
        "borda": "#30363d",
        "texto": "#e6edf3",
        "suave": "#8b949e",
        "azul": "#2f81f7",
        "verde": "#3fb950",
        "ambar": "#e3b341",
        "feixe": "#e3b341",
        "feixe_op": "0.30",
        "vermelho": "#f85149",
        "torre": "#c9d1d9",
        "pilula": "#21262d",
        "lampada": "#e3b341",
    },
    "light": {
        "fundo": "#ffffff",
        "canvas": "#f6f8fa",
        "borda": "#d0d7de",
        "texto": "#1f2328",
        "suave": "#59636e",
        "azul": "#0969da",
        "verde": "#1a7f37",
        "ambar": "#9a6700",
        "feixe": "#d4a72c",
        "feixe_op": "0.38",
        "vermelho": "#cf222e",
        "torre": "#57606a",
        "pilula": "#ffffff",
        "lampada": "#bf8700",
    },
}


def banner(c: dict) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="330" viewBox="0 0 1200 330" role="img" aria-labelledby="t d">
<title id="t">Farol</title>
<desc id="d">Um farol com o feixe de luz varrendo a tela e o texto: Farol, revisão de pull request que ensina.</desc>
<defs>
  <linearGradient id="feixe" x1="0" x2="1" y1="0" y2="0">
    <stop offset="0" stop-color="{c["feixe"]}" stop-opacity="{c["feixe_op"]}"/>
    <stop offset="1" stop-color="{c["feixe"]}" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="brilho">
    <stop offset="0" stop-color="{c["feixe"]}" stop-opacity="0.55"/>
    <stop offset="1" stop-color="{c["feixe"]}" stop-opacity="0"/>
  </radialGradient>
</defs>
<style>
  .titulo {{ font: 700 92px {MONO}; fill: {c["texto"]}; }}
  .sub {{ font: 400 30px {SANS}; fill: {c["texto"]}; }}
  .chip {{ font: 500 18px {SANS}; fill: {c["suave"]}; }}
  .seta {{ font: 400 20px {SANS}; fill: {c["suave"]}; }}
  @keyframes pulso {{ 0%, 100% {{ opacity: .5; }} 50% {{ opacity: 1; }} }}
  @keyframes entra {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: none; }} }}
  .lampada {{ animation: pulso 3.2s ease-in-out infinite; }}
  .a1 {{ animation: entra .9s .1s both; }}
  .a2 {{ animation: entra .9s .35s both; }}
  .a3 {{ animation: entra .9s .6s both; }}
  .a4 {{ animation: entra .9s .85s both; }}
  .a5 {{ animation: entra .9s 1.1s both; }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>

<g>
  <animateTransform attributeName="transform" type="rotate" values="-7 170 124;7 170 124;-7 170 124" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1" keyTimes="0;.5;1"/>
  <polygon points="170,124 1120,24 1120,224" fill="url(#feixe)"/>
</g>
<g>
  <animateTransform attributeName="transform" type="rotate" values="7 170 124;-7 170 124;7 170 124" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1" keyTimes="0;.5;1"/>
  <polygon points="170,124 -300,60 -300,188" fill="url(#feixe)" opacity=".6"/>
</g>

<circle class="lampada" cx="170" cy="124" r="62" fill="url(#brilho)"/>
<g transform="translate(42 40) scale(4)">
  <path d="M26 28 L38 28 L42 58 L22 58 Z" fill="{c["torre"]}"/>
  <path d="M25 40 L39 40 L40 47 L24 47 Z" fill="{c["verde"]}"/>
  <rect x="14" y="58" width="36" height="4" rx="2" fill="{c["verde"]}"/>
  <path d="M23 14 L32 6 L41 14 Z" fill="{c["azul"]}"/>
  <rect x="25" y="14" width="14" height="14" rx="2" fill="{c["lampada"]}"/>
</g>

<text class="titulo a1" x="340" y="150">Farol</text>
<text class="sub a2" x="344" y="205">Revisão de pull request que <tspan font-weight="700" fill="{c["ambar"]}">ensina</tspan>.</text>

<g class="a3"><rect x="344" y="236" width="118" height="40" rx="20" fill="{c["pilula"]}" stroke="{c["borda"]}"/><text class="chip" x="403" y="262" text-anchor="middle">o que é</text></g>
<text class="seta a3" x="476" y="263">→</text>
<g class="a4"><rect x="506" y="236" width="170" height="40" rx="20" fill="{c["pilula"]}" stroke="{c["borda"]}"/><text class="chip" x="591" y="262" text-anchor="middle">por que importa</text></g>
<text class="seta a4" x="690" y="263">→</text>
<g class="a5"><rect x="720" y="236" width="150" height="40" rx="20" fill="{c["pilula"]}" stroke="{c["verde"]}"/><text class="chip" x="795" y="262" text-anchor="middle" style="fill: {c["verde"]}">como corrigir</text></g>
</svg>
"""


# (rótulo, tempo em segundos em que aparece)
def demo(c: dict) -> str:
    total = 16.0
    largura_cmd = 27 * 9.0  # 27 caracteres a ~9 px
    linhas = [
        # (y, tempo, [(x, classe, texto, ancora)])
        (126, 2.6, [(30, "suave", "3 apontamentos nas linhas alteradas.", "start")]),
        (166, 3.2, [(30, "suave", "── app.py:5", "start")]),
        (
            192,
            3.5,
            [
                (30, "vermelho", "S105", "start"),
                (88, "texto", "Senha escrita direto no código", "start"),
                (930, "suave", "iniciante", "end"),
            ],
        ),
        (
            214,
            3.9,
            [
                (
                    88,
                    "suave",
                    "Tudo que está no código vai para o Git, inclusive o histórico.",
                    "start",
                )
            ],
        ),
        (
            236,
            4.4,
            [(88, "verde", '✔ Leia de os.environ["DB_PASSWORD"] e tire do repositório.', "start")],
        ),
        (276, 5.6, [(30, "suave", "── app.py:9", "start")]),
        (
            302,
            5.9,
            [
                (30, "ambar", "E722", "start"),
                (88, "texto", "`except:` sem tipo captura erro demais", "start"),
                (930, "suave", "iniciante", "end"),
            ],
        ),
        (
            324,
            6.3,
            [(88, "suave", "Captura até o Ctrl+C e esconde o problema de verdade.", "start")],
        ),
        (346, 6.8, [(88, "verde", "✔ Nomeie o erro que você espera tratar.", "start")]),
        (386, 8.0, [(30, "suave", "── app.py:14", "start")]),
        (
            412,
            8.3,
            [
                (30, "azul", "B006", "start"),
                (88, "texto", "Valor padrão mutável em argumento de função", "start"),
                (930, "suave", "intermediário", "end"),
            ],
        ),
        (
            434,
            8.7,
            [
                (
                    88,
                    "suave",
                    "A lista é criada uma única vez e compartilhada entre chamadas.",
                    "start",
                )
            ],
        ),
        (
            456,
            9.2,
            [(88, "verde", "✔ Use None como padrão e crie a lista dentro da função.", "start")],
        ),
        (
            498,
            10.4,
            [(30, "suave", "Uma lição por regra, só nas linhas que você alterou.", "start")],
        ),
    ]
    cores = {
        "texto": c["texto"],
        "suave": c["suave"],
        "verde": c["verde"],
        "vermelho": c["vermelho"],
        "ambar": c["ambar"],
        "azul": c["azul"],
    }

    css = []
    for i, (_, t0, _) in enumerate(linhas):
        a, b, f1, f2 = t0 / total, (t0 + 0.35) / total, 0.93, 0.97
        css.append(
            f"@keyframes l{i} {{ 0%, {a * 100:.2f}% {{ opacity: 0; }} {b * 100:.2f}%, {f1 * 100:.0f}% {{ opacity: 1; }} "
            f"{f2 * 100:.0f}%, 100% {{ opacity: 0; }} }} .l{i} {{ animation: l{i} {total}s infinite; }}"
        )
    fim = 0.93
    css.append(
        f"@keyframes digita {{ 0%, 3% {{ width: 0; }} 15% {{ width: {largura_cmd}px; }} {fim * 100:.0f}% {{ width: {largura_cmd}px; }} "
        f"{(fim + 0.04) * 100:.0f}%, 100% {{ width: 0; }} }} #clip rect {{ animation: digita {total}s steps(27, end) infinite; }}"
    )
    css.append(
        "@keyframes cursor { 0%, 49% { opacity: 1; } 50%, 100% { opacity: 0; } } .cursor { animation: cursor 1s steps(1) infinite; }"
    )

    corpo = []
    for i, (y, _, partes) in enumerate(linhas):
        textos = "".join(
            f'<text x="{x}" y="{y}" fill="{cores[cl]}" text-anchor="{anc}">{escape(txt)}</text>'
            for x, cl, txt, anc in partes
        )
        corpo.append(f'<g class="l{i}">{textos}</g>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540" role="img" aria-labelledby="t d">
<title id="t">Farol na linha de comando</title>
<desc id="d">Um terminal onde o comando farol revisar --base main é digitado e mostra três apontamentos, cada um com o que é, por que importa e como corrigir.</desc>
<style>
  text {{ font: 400 15px {MONO}; }}
  .barra {{ font: 500 13px {SANS}; fill: {c["suave"]}; }}
  {" ".join(css)}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} g[class^="l"] {{ opacity: 1; }} #clip rect {{ width: {largura_cmd}px; }} }}
</style>
<defs><clipPath id="clip"><rect x="30" y="64" width="0" height="32"/></clipPath></defs>
<rect x="0.5" y="0.5" width="959" height="539" rx="12" fill="{c["canvas"]}" stroke="{c["borda"]}"/>
<path d="M0.5 40.5 H959.5" stroke="{c["borda"]}"/>
<circle cx="24" cy="21" r="6" fill="{c["vermelho"]}"/><circle cx="46" cy="21" r="6" fill="{c["ambar"]}"/><circle cx="68" cy="21" r="6" fill="{c["verde"]}"/>
<text class="barra" x="480" y="26" text-anchor="middle" style="font-family: {SANS}">~/meu-projeto · farol</text>
<g clip-path="url(#clip)"><text x="30" y="86" fill="{c["texto"]}"><tspan fill="{c["verde"]}">$</tspan> farol revisar --base main</text></g>
<rect class="cursor" x="{30 + largura_cmd + 10}" y="72" width="9" height="18" fill="{c["texto"]}"/>
{chr(10).join(corpo)}
</svg>
"""


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    for nome, tema in TEMAS.items():
        (SAIDA / f"banner-{nome}.svg").write_text(banner(tema), encoding="utf-8", newline="\n")
        (SAIDA / f"demo-{nome}.svg").write_text(demo(tema), encoding="utf-8", newline="\n")
    print(f"SVGs em {SAIDA}")


if __name__ == "__main__":
    main()
