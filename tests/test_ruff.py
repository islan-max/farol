from farol.analise.ruff import analisar

FONTE = """import os


def f(a, b=[]):
    try:
        pass
    except:
        pass
"""


def codigos(achados):
    return [a.codigo for a in achados]


def test_sem_filtro_devolve_tudo_ordenado_por_linha():
    achados = analisar("a.py", FONTE)
    assert codigos(achados) == ["F401", "B006", "E722"]
    assert [a.line for a in achados] == sorted(a.line for a in achados)


def test_filtro_mantem_so_linhas_alteradas():
    achados = analisar("a.py", FONTE, linhas={4, 7})
    assert codigos(achados) == ["B006", "E722"]  # o import da linha 1 não foi alterado


def test_linha_fora_do_diff_nao_gera_achado():
    assert analisar("a.py", FONTE, linhas={5}) == []


def test_achado_traz_caminho_ferramenta_e_url():
    (achado,) = analisar("pasta/a.py", FONTE, linhas={1})
    assert (achado.path, achado.ferramenta, achado.codigo) == ("pasta/a.py", "ruff", "F401")
    assert achado.url.startswith("https://docs.astral.sh/ruff/rules/")


def test_erro_de_sintaxe_vem_sem_codigo():
    (achado,) = analisar("a.py", "def f(:\n    pass\n")
    assert achado.codigo is None


def test_regras_do_repositorio_revisado_sao_ignoradas(tmp_path, monkeypatch):
    (tmp_path / "ruff.toml").write_text('[lint]\nselect = ["ALL"]\nignore = ["E722"]\n')
    monkeypatch.chdir(tmp_path)
    assert "E722" in codigos(analisar("a.py", FONTE))
