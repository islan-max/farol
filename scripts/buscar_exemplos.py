"""Ferramenta de curadoria (roda na máquina de quem mantém; não faz parte do produto).

Dois passos:
  1. `buscar --regra B006`: lista arquivos candidatos na busca de código do GitHub, em uma lista
     de projetos conhecidos. A busca acha arquivos que contêm as palavras, não exemplos bons:
     quem mantém lê cada candidato e escolhe.
  2. `adicionar ...`: grava em `src/farol/exemplos/curados.json` o trecho exato das linhas
     escolhidas, lido do commit (permalink fixo), com a licença do projeto. Recusa licença fora
     da lista e trechos longos. Depois, é só citar o id na lição (`exemplos = ["B006-1"]`).
  3. `conferir`: relê cada trecho no permalink e avisa se algum deixou de bater.

Precisa do `gh` logado. A busca de código tem limite de 10 chamadas por minuto.
"""

import argparse
import json
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

CURADOS = Path(__file__).resolve().parent.parent / "src" / "farol" / "exemplos" / "curados.json"
LICENCAS_OK = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "PSF-2.0", "Unlicense"}
MAX_LINHAS = 12
PROJETOS = (
    "psf/requests pallets/flask django/django pallets/click encode/httpx tiangolo/fastapi "
    "pytest-dev/pytest python-pillow/Pillow sqlalchemy/sqlalchemy pypa/pip"
).split()
# Palavras (a busca ignora pontuação) que aparecem perto do jeito certo de resolver cada regra.
CONSULTAS = {
    "E722": ["except TypeError ValueError"],
    "B006": ["is None headers", "if params is None"],
    "S110": ["contextlib suppress FileNotFoundError", "logger exception except OSError"],
    "S105": ["environ SECRET_KEY", "environ PASSWORD"],
    "S608": ["cursor execute WHERE %s params"],
}


def gh(*args: str) -> str:
    proc = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")  # noqa: S603, S607
    if proc.returncode != 0:
        sys.exit(f"gh falhou: {proc.stderr.strip()[:300]}")
    return proc.stdout


def buscar(regra: str) -> None:
    for consulta in CONSULTAS[regra]:
        escopo = " ".join(f"repo:{r}" for r in PROJETOS)
        q = urllib.parse.quote(f"{consulta} language:python {escopo}")
        dados = json.loads(gh("api", f"search/code?q={q}&per_page=8"))
        print(f"\n## {consulta!r}: {dados.get('total_count')} resultado(s)")
        for item in dados.get("items", []):
            print(f"- {item['repository']['full_name']} {item['path']}\n  {item['html_url']}")


def licenca(repo: str) -> str:
    return gh("api", f"repos/{repo}", "--jq", '.license.spdx_id // "NONE"').strip()


def adicionar(a: argparse.Namespace) -> None:
    ini, fim = (int(x) for x in a.linhas.split("-"))
    if fim - ini + 1 > MAX_LINHAS:
        sys.exit(f"trecho com {fim - ini + 1} linhas; o máximo é {MAX_LINHAS}")
    spdx = licenca(a.repo)
    if spdx not in LICENCAS_OK:
        sys.exit(f"licença {spdx} não está na lista permitida")
    caminho = urllib.parse.quote(a.caminho)
    texto = gh(
        "api",
        f"repos/{a.repo}/contents/{caminho}?ref={a.sha}",
        "-H",
        "Accept: application/vnd.github.raw",
    )
    trecho = "\n".join(texto.splitlines()[ini - 1 : fim])
    if not trecho.strip():
        sys.exit("trecho vazio: confira as linhas")
    dados = json.loads(CURADOS.read_text(encoding="utf-8")) if CURADOS.exists() else []
    novo_id = f"{a.regra}-{sum(d['regra'] == a.regra for d in dados) + 1}"
    dados.append(
        {
            "id": novo_id,
            "regra": a.regra,
            "repo": a.repo,
            "licenca": spdx,
            "permalink": f"https://github.com/{a.repo}/blob/{a.sha}/{a.caminho}#L{ini}-L{fim}",
            "trecho": trecho,
            "porque": a.porque,
        }
    )
    CURADOS.parent.mkdir(exist_ok=True)
    CURADOS.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"{novo_id} gravado:\n{trecho}")


def conferir() -> None:
    """Relê cada trecho no commit do permalink e compara com o que está gravado."""
    ruins = 0
    for ex in json.loads(CURADOS.read_text(encoding="utf-8")):
        m = re.match(
            r"https://github\.com/([^/]+/[^/]+)/blob/([0-9a-f]{40})/(.+)#L(\d+)-L(\d+)$",
            ex["permalink"],
        )
        repo, sha, caminho, ini, fim = m.groups()
        texto = gh(
            "api",
            f"repos/{repo}/contents/{urllib.parse.quote(caminho)}?ref={sha}",
            "-H",
            "Accept: application/vnd.github.raw",
        )
        atual = "\n".join(texto.splitlines()[int(ini) - 1 : int(fim)])
        ok = atual == ex["trecho"] and licenca(repo) == ex["licenca"]
        ruins += not ok
        print(("ok    " if ok else "DIFERE"), ex["id"], ex["permalink"])
    sys.exit(1 if ruins else 0)


def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("buscar")
    b.add_argument("--regra", required=True, choices=sorted(CONSULTAS))
    ad = sub.add_parser("adicionar")
    ad.add_argument("--regra", required=True)
    ad.add_argument("--repo", required=True, help="dono/nome")
    ad.add_argument("--caminho", required=True)
    ad.add_argument("--sha", required=True, help="commit completo (40 caracteres)")
    ad.add_argument("--linhas", required=True, help="ex.: 120-128")
    ad.add_argument(
        "--porque", required=True, help="uma frase: por que este trecho é um bom exemplo"
    )
    sub.add_parser("conferir")
    args = p.parse_args()
    if args.cmd == "buscar":
        buscar(args.regra)
    elif args.cmd == "adicionar":
        adicionar(args)
    else:
        conferir()


if __name__ == "__main__":
    main()
