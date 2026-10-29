"""Roda o ruff sobre o texto de um arquivo Python e devolve só o que está nas linhas alteradas."""

import json
import subprocess
import sys

from farol.achados import Achado
from farol.licoes import codigos

TIMEOUT_S = 30
# Senha de mentira, `except: pass` e chamada sem timeout são normais em teste: não aponta lá.
EM_TESTES = ["S105", "S110", "S113", "S608"]
PADROES_DE_TESTE = ["**/tests/**", "**/test/**", "**/test_*.py", "**/*_test.py", "**/conftest.py"]
_ITENS = ", ".join(f'"{padrao}" = {json.dumps(EM_TESTES)}' for padrao in PADROES_DE_TESTE)
IGNORAR_EM_TESTES = f"lint.per-file-ignores = {{{_ITENS}}}"


def analisar(path: str, source: str, linhas: set[int] | None = None) -> list[Achado]:
    """`linhas` limita o resultado às linhas alteradas; None mantém tudo (uso na CLI e no site)."""
    select = ",".join(codigos("ruff"))
    cmd = [
        sys.executable,
        "-m",
        "ruff",
        "check",
        "--isolated",  # ignora a configuração do repositório revisado: o Farol decide as regras
        "--config",
        IGNORAR_EM_TESTES,
        "--select",
        select,
        "--output-format",
        "json",
        "--stdin-filename",
        path,
        "-",
    ]
    proc = subprocess.run(  # noqa: S603 - comando fixo; o texto do PR vai só pela entrada padrão
        cmd, input=source, capture_output=True, text=True, encoding="utf-8", timeout=TIMEOUT_S
    )
    if proc.returncode not in (0, 1):  # 0 = limpo, 1 = achados; outro = falha do ruff
        raise RuntimeError(f"ruff falhou ({proc.returncode}): {proc.stderr.strip()[:300]}")
    achados = []
    for d in json.loads(proc.stdout or "[]"):
        line = d["location"]["row"]
        if linhas is None or line in linhas:
            codigo = None if d["code"] in (None, "invalid-syntax") else d["code"]
            achados.append(Achado(path, line, "ruff", codigo, d["message"], d.get("url")))
    # Um erro de sintaxe costuma gerar vários em cascata; o primeiro é o que ajuda.
    sintaxe = [a for a in achados if a.codigo is None][:1]
    achados = [a for a in achados if a.codigo is not None] + sintaxe
    return sorted(achados, key=lambda a: (a.line, a.codigo or ""))
