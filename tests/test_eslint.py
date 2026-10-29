import shutil

import pytest

from farol.analise import FerramentaIndisponivel, analisar
from farol.analise import eslint as modulo
from farol.licoes import todas

pytestmark = pytest.mark.skipif(not shutil.which("node"), reason="precisa do Node.js")
JS = [lc for (f, _), lc in todas().items() if f == "eslint"]


def codigos(achados):
    return [a.codigo for a in achados]


def test_ha_pelo_menos_cinco_licoes_de_javascript():
    assert len(JS) >= 10


@pytest.mark.parametrize("lc", JS, ids=lambda lc: lc.codigo)
def test_antes_dispara_a_regra_e_depois_nao(lc):
    arquivo = f"x.{lc.extensao or 'js'}"
    assert lc.codigo in codigos(analisar(arquivo, lc.antes)), "o 'antes' não dispara a regra"
    assert lc.codigo not in codigos(analisar(arquivo, lc.depois)), "o 'depois' ainda dispara"


@pytest.mark.parametrize("lc", JS, ids=lambda lc: lc.codigo)
def test_o_mesmo_vale_para_typescript(lc):
    assert lc.codigo in codigos(analisar("x.ts", lc.antes))
    assert lc.codigo not in codigos(analisar("x.ts", lc.depois))


FONTE = "var a = 1;\nconst b: number = a;\nif (b == 2) {\n  console.log(b);\n}\n"


def test_typescript_com_anotacoes_de_tipo_e_lido_e_filtrado_por_linha():
    todos = analisar("src/a.ts", FONTE)
    assert codigos(todos) == ["no-var", "eqeqeq"]
    assert [a.line for a in todos] == [1, 3]
    assert codigos(analisar("src/a.ts", FONTE, linhas={3})) == ["eqeqeq"]


def test_jsx_e_tsx_sao_lidos():
    assert codigos(analisar("a.jsx", "export const A = () => <p>{1 == 1}</p>;\n")) == ["eqeqeq"]
    assert codigos(analisar("a.tsx", "export const A = (): JSX.Element => <p>{1 == 1}</p>;\n")) == [
        "eqeqeq"
    ]


def test_regras_do_repositorio_revisado_sao_ignoradas(tmp_path, monkeypatch):
    (tmp_path / "eslint.config.mjs").write_text("export default [{ rules: { eqeqeq: 'off' } }];\n")
    monkeypatch.chdir(tmp_path)
    assert codigos(analisar("a.js", "if (1 == 1) {}\n")) == ["eqeqeq", "no-empty"]


def test_erro_de_sintaxe_vem_sem_codigo_e_uma_vez_so():
    (achado,) = analisar("a.js", "function (:\n")
    assert achado.codigo is None and achado.ferramenta == "eslint"


def test_achado_tem_ferramenta_e_url():
    (achado,) = analisar("a.js", "if (1 == 1) { console.log(1); }\n")
    assert (achado.ferramenta, achado.codigo) == ("eslint", "eqeqeq")
    assert achado.url == "https://eslint.org/docs/latest/rules/eqeqeq"


def test_sem_node_o_arquivo_vira_nao_revisado_com_motivo(tmp_path, monkeypatch):
    monkeypatch.setenv("FAROL_CACHE", str(tmp_path))  # cache vazio: força a instalação
    monkeypatch.setattr(modulo.shutil, "which", lambda _nome: None)
    with pytest.raises(FerramentaIndisponivel, match="Node.js"):
        analisar("a.js", "var a = 1;\n")


def test_no_explicit_any_so_vale_para_typescript_e_aponta_para_a_doc_certa():
    fonte = "export function f(x: any) {\n  return x;\n}\n"
    (achado,) = analisar("a.ts", fonte)
    assert achado.codigo == "no-explicit-any"
    assert achado.url == "https://typescript-eslint.io/rules/no-explicit-any/"
    assert analisar("a.js", "export function f(x) {\n  return x;\n}\n") == []


def test_mudar_a_configuracao_muda_a_pasta_de_cache(tmp_path, monkeypatch):
    for nome in modulo.ARQUIVOS:
        (tmp_path / nome).write_text("v1")
    monkeypatch.setattr(modulo, "FONTE", tmp_path)
    antes = modulo._cache()
    (tmp_path / "farol.config.mjs").write_text("v2")
    assert modulo._cache() != antes


def test_comentario_eslint_disable_de_plugin_que_o_farol_nao_tem_nao_vira_achado():
    fonte = "// eslint-disable-next-line unicorn/prefer-spread\nexport const a = [].concat([1]);\n"
    assert analisar("a.js", fonte) == []


def test_underscore_e_parametros_nao_usados_nao_sao_apontados():
    fonte = (
        "export function f(a, _b, c) {\n  const [_x, y] = a;\n  return y;\n}\n"
        "export const g = (req, res, next) => res;\n"
    )
    assert analisar("a.js", fonte) == []
    assert codigos(analisar("a.js", "export function f() {\n  const sobra = 1;\n}\n")) == [
        "no-unused-vars"
    ]
