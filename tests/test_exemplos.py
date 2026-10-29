import re

import pytest

from farol.comentarios import corpo_licao
from farol.exemplos import todos
from farol.licoes import todas

PERMISSIVAS = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "PSF-2.0", "Unlicense"}
PERMALINK = re.compile(r"^https://github\.com/[\w.-]+/[\w.-]+/blob/[0-9a-f]{40}/\S+#L(\d+)-L(\d+)$")


@pytest.mark.parametrize("ex", todos().values(), ids=lambda e: e.id)
def test_exemplo_e_citavel(ex):
    m = PERMALINK.match(ex.permalink)
    assert m, "o permalink precisa apontar para um commit fixo (40 hex) e um intervalo de linhas"
    ini, fim = int(m.group(1)), int(m.group(2))
    assert len(ex.trecho.splitlines()) == fim - ini + 1 <= 12
    assert ex.permalink.startswith(f"https://github.com/{ex.repo}/blob/")
    assert ex.licenca in PERMISSIVAS
    assert ex.porque.strip().endswith(".")


def test_toda_licao_aponta_para_exemplo_que_existe_e_da_mesma_regra():
    for lc in todas().values():
        for id_ in lc.exemplos:
            assert id_ in todos(), f"{lc.codigo} cita {id_}, que não existe"
            assert todos()[id_].regra == lc.codigo


def test_lico_com_exemplo_mostra_a_secao_e_sem_exemplo_nao_inventa():
    com = next(lc for lc in todas().values() if lc.codigo == "B006")
    sem = next(lc for lc in todas().values() if lc.codigo == "E741")
    assert "Como projetos reais resolvem" in corpo_licao(com)
    assert "licença BSD-3-Clause" in corpo_licao(com)
    assert "Como projetos reais resolvem" not in corpo_licao(sem)
