"""Roda o ESLint (com typescript-eslint) sobre o texto de um arquivo JavaScript ou TypeScript.

As dependências ficam fixadas em `farol/eslint/package-lock.json` e são instaladas uma vez, com
`npm ci --ignore-scripts`, em uma pasta de cache. Precisa de Node.js 20+ e npm; sem eles o
arquivo vai para "não revisados" com o motivo. O código revisado nunca é executado: só lido.
"""

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

from farol.achados import Achado

FONTE = Path(__file__).resolve().parent.parent / "eslint"
TIMEOUT_S = 60
EXTENSOES = (".js", ".mjs", ".cjs", ".jsx", ".ts", ".mts", ".cts", ".tsx")
# O plugin do TypeScript troca a regra base; para quem aprende é a mesma lição.
NOMES = {"@typescript-eslint/no-unused-vars": "no-unused-vars"}


class FerramentaIndisponivel(RuntimeError):
    """Node.js ou npm ausente, ou a instalação do ESLint falhou."""


def _cache() -> Path:
    base = Path(os.environ.get("FAROL_CACHE") or Path.home() / ".cache" / "farol")
    chave = hashlib.sha256((FONTE / "package-lock.json").read_bytes()).hexdigest()[:12]
    return base / f"eslint-{chave}"


def preparar() -> Path:
    destino = _cache()
    if (destino / "node_modules" / "eslint").exists():
        return destino
    if not (shutil.which("node") and shutil.which("npm")):
        raise FerramentaIndisponivel("JavaScript e TypeScript precisam do Node.js 20 ou mais novo")
    destino.mkdir(parents=True, exist_ok=True)
    for nome in ("package.json", "package-lock.json", "farol.config.mjs"):
        shutil.copy(FONTE / nome, destino / nome)
    proc = subprocess.run(  # noqa: S603 - comando fixo, sem entrada de fora
        [shutil.which("npm"), "ci", "--ignore-scripts", "--no-audit", "--no-fund"],
        cwd=destino, capture_output=True, text=True, encoding="utf-8", timeout=300, check=False,
    )  # fmt: skip
    if proc.returncode != 0:
        shutil.rmtree(destino / "node_modules", ignore_errors=True)
        raise FerramentaIndisponivel(f"não consegui instalar o ESLint: {proc.stderr.strip()[:200]}")
    return destino


def analisar(path: str, source: str, linhas: set[int] | None = None) -> list[Achado]:
    raiz = preparar()
    proc = subprocess.run(  # noqa: S603 - comando fixo; o texto do PR vai só pela entrada padrão
        [
            shutil.which("node"),
            str(raiz / "node_modules" / "eslint" / "bin" / "eslint.js"),
            "--no-config-lookup",
            "-c", "farol.config.mjs",
            "--stdin", "--stdin-filename", path,
            "-f", "json",
        ],
        cwd=raiz, input=source, capture_output=True, text=True, encoding="utf-8",
        timeout=TIMEOUT_S, check=False,
    )  # fmt: skip
    if proc.returncode not in (0, 1):  # 0 = limpo, 1 = achados; 2 = falha do ESLint
        raise RuntimeError(f"eslint falhou ({proc.returncode}): {proc.stderr.strip()[:300]}")
    achados: list[Achado] = []
    for msg in json.loads(proc.stdout)[0]["messages"]:
        if msg.get("fatal") or not msg.get("ruleId"):
            codigo, url = None, None
        else:
            codigo = NOMES.get(msg["ruleId"], msg["ruleId"])
            url = f"https://eslint.org/docs/latest/rules/{codigo}"
        if linhas is None or msg["line"] in linhas:
            achados.append(Achado(path, msg["line"], "eslint", codigo, msg["message"], url))
    # Erro de sintaxe: só o primeiro; os seguintes costumam ser cascata.
    sintaxe = [a for a in achados if a.codigo is None][:1]
    achados = [a for a in achados if a.codigo is not None] + sintaxe
    return sorted(achados, key=lambda a: (a.line, a.codigo or ""))
