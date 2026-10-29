import json
import subprocess
import sys

import pytest

from farol.licoes import NIVEIS, licao, todas

PYTHON = [lc for (f, _), lc in todas().items() if f == "ruff"]


def _codigos_do_ruff(fonte: str) -> set[str | None]:
    proc = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "ruff", "check", "--isolated", "--select", "ALL",
         "--output-format", "json", "--stdin-filename", "x.py", "-"],
        input=fonte, capture_output=True, text=True, encoding="utf-8", check=False,
    )  # fmt: skip
    return {d["code"] for d in json.loads(proc.stdout)}


def test_catalogo_nao_esta_vazio():
    assert len(PYTHON) >= 17


@pytest.mark.parametrize("lc", PYTHON, ids=lambda lc: lc.codigo)
def test_campos_da_licao(lc):
    assert lc.nivel in NIVEIS
    assert lc.antes != lc.depois
    assert lc.docs and all(d["url"].startswith("https://") for d in lc.docs)


@pytest.mark.parametrize("lc", PYTHON, ids=lambda lc: lc.codigo)
def test_antes_dispara_a_regra_e_depois_nao(lc):
    assert lc.codigo in _codigos_do_ruff(lc.antes), "o exemplo 'antes' não dispara a regra"
    assert lc.codigo not in _codigos_do_ruff(lc.depois), "o exemplo 'depois' ainda dispara"


def test_licao_inexistente_ou_sem_codigo():
    assert licao("ruff", "Z999") is None
    assert licao("ruff", None) is None
