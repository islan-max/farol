"""Mantém a tabela de lições do README em dia com o catálogo (`src/farol/licoes`).

Uso: python scripts/atualizar_readme.py          (reescreve o trecho entre os marcadores)
     python scripts/atualizar_readme.py --conferir   (sai com erro se o README estiver defasado)
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from farol.comentarios import NIVEIS  # noqa: E402
from farol.licoes import todas  # noqa: E402

INICIO, FIM = "<!-- licoes:inicio -->", "<!-- licoes:fim -->"
SITE = "https://islan-max.github.io/farol/licoes"


def tabela(ferramenta: str) -> str:
    linhas = ["| Regra | Lição | Nível | Exemplo real |", "| --- | --- | --- | :---: |"]
    for lc in sorted(
        (v for v in todas().values() if v.ferramenta == ferramenta), key=lambda v: v.codigo
    ):
        titulo = lc.titulo.replace("|", "\\|")
        exemplo = "✔" if lc.exemplos else ""
        link = f"[`{lc.codigo}`]({SITE}/{lc.codigo}.html)"
        linhas.append(f"| {link} | {titulo} | {NIVEIS[lc.nivel]} | {exemplo} |")
    return "\n".join(linhas)


def bloco() -> str:
    py = sum(v.ferramenta == "ruff" for v in todas().values())
    js = sum(v.ferramenta == "eslint" for v in todas().values())
    return "\n".join(
        [
            INICIO,
            "<details>",
            f"<summary><b>Python</b> · {py} lições (ruff)</summary>",
            "",
            tabela("ruff"),
            "",
            "</details>",
            "",
            "<details>",
            f"<summary><b>JavaScript e TypeScript</b> · {js} lições (ESLint)</summary>",
            "",
            tabela("eslint"),
            "",
            "</details>",
            FIM,
        ]
    )


def main() -> int:
    readme = RAIZ / "README.md"
    texto = readme.read_text(encoding="utf-8")
    i, j = texto.index(INICIO), texto.index(FIM) + len(FIM)
    novo = texto[:i] + bloco() + texto[j:]
    total = len(todas())
    novo = re.sub(r"(li%C3%A7%C3%B5es-)\d+(-)", rf"\g<1>{total}\g<2>", novo)
    novo = re.sub(r'alt="\d+ lições"', f'alt="{total} lições"', novo)
    if "--conferir" in sys.argv:
        if novo != texto:
            print("README defasado: rode python scripts/atualizar_readme.py", file=sys.stderr)
            return 1
        return 0
    readme.write_text(novo, encoding="utf-8", newline="\n")
    print("Tabela de lições atualizada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
