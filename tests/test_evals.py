from pathlib import Path

import pytest

from farol.analise.ruff import analisar

CASOS = sorted((Path(__file__).parent.parent / "evals" / "casos").glob("*.py"))


def esperado(fonte: str) -> set[str]:
    cabecalho = fonte.splitlines()[0]
    assert cabecalho.startswith("# farol-esperado:"), "falta o cabeçalho # farol-esperado:"
    valor = cabecalho.split(":", 1)[1].strip()
    return set() if valor == "nenhum" else set(valor.split(","))


def test_ha_casos_com_e_sem_problema():
    textos = [c.read_text(encoding="utf-8") for c in CASOS]
    assert sum(esperado(t) == set() for t in textos) >= 4  # casos limpos medem falso positivo
    assert sum(esperado(t) != set() for t in textos) >= 5


@pytest.mark.parametrize("caso", CASOS, ids=lambda c: c.stem)
def test_caso_da_avaliacao(caso):
    fonte = caso.read_text(encoding="utf-8")
    achados = {a.codigo for a in analisar(caso.name, fonte)}
    assert achados == esperado(fonte)
