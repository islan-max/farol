import pytest

from farol.action import (
    anotacoes,
    executar,
    marca_regra,
    marca_revisao,
    regras_ja_comentadas,
)
from farol.github import GitHubError

SHA = "a" * 40
FONTE = "import os\n\n\ndef f(a, b=[]):\n    return a\n"  # F401 (linha 1) e B006 (linha 4)


def patch_novo(n_linhas: int) -> str:
    return f"@@ -0,0 +1,{n_linhas} @@\n" + "".join("+x\n" for _ in range(n_linhas))


class ApiFalsa:
    """Responde no lugar do GitHub e guarda o que o Farol tentou enviar."""

    repo = "dono/repo"

    def __init__(self, arquivos, textos, reviews=(), comentarios=(), erro_ao_enviar=None):
        self.arquivos, self.textos = arquivos, textos
        self.reviews, self.comentarios = list(reviews), list(comentarios)
        self.erro_ao_enviar, self.enviados = erro_ao_enviar, []

    def paginar(self, caminho):
        if caminho.endswith("/reviews"):
            return self.reviews
        if caminho.endswith("/comments"):
            return self.comentarios
        return self.arquivos

    def texto_do_arquivo(self, repo, caminho, ref):
        assert ref == SHA
        return self.textos[caminho]

    def enviar(self, caminho, corpo):
        if self.erro_ao_enviar:
            raise self.erro_ao_enviar
        self.enviados.append((caminho, corpo))
        return {}


def evento(repo_cabeca="dono/repo"):
    return {"pull_request": {"number": 7, "head": {"sha": SHA, "repo": {"full_name": repo_cabeca}}}}


def arquivo_py(nome="a.py", linhas=5):
    return {"filename": nome, "status": "added", "patch": patch_novo(linhas)}


def test_comenta_as_linhas_alteradas_com_a_licao(tmp_path):
    api = ApiFalsa([arquivo_py()], {"a.py": FONTE})
    assert executar(api, evento(), None) == 0
    ((caminho, corpo),) = api.enviados
    assert caminho == "/repos/dono/repo/pulls/7/reviews"
    assert corpo["commit_id"] == SHA and corpo["event"] == "COMMENT"
    assert {(c["path"], c["line"], c["side"]) for c in corpo["comments"]} == {
        ("a.py", 1, "RIGHT"),
        ("a.py", 4, "RIGHT"),
    }
    assert marca_revisao(SHA) in corpo["body"]
    assert all("Por que importa" in c["body"] for c in corpo["comments"])


def test_nao_comenta_linha_fora_do_diff():
    api = ApiFalsa(
        [{**arquivo_py(), "patch": "@@ -4,0 +4,1 @@\n+def f(a, b=[]):"}], {"a.py": FONTE}
    )
    executar(api, evento(), None)
    (_, corpo) = api.enviados[0]
    assert [c["line"] for c in corpo["comments"]] == [4]  # o import da linha 1 ficou de fora


def test_mesmo_commit_nao_e_revisado_duas_vezes():
    api = ApiFalsa([arquivo_py()], {"a.py": FONTE}, reviews=[{"body": marca_revisao(SHA)}])
    executar(api, evento(), None)
    assert api.enviados == []


def test_regra_ja_comentada_no_arquivo_nao_repete_em_commit_novo():
    from farol.achados import Achado

    antigo = Achado("a.py", 4, "ruff", "B006", "m")
    api = ApiFalsa(
        [arquivo_py()], {"a.py": FONTE}, comentarios=[{"body": "x\n" + marca_regra(antigo)}]
    )
    executar(api, evento(), None)
    (_, corpo) = api.enviados[0]
    assert [c["line"] for c in corpo["comments"]] == [1]  # só o F401; o B006 já foi explicado


def test_sem_apontamentos_nao_comenta(tmp_path):
    api = ApiFalsa([arquivo_py("b.py", 1)], {"b.py": "x = 1\n"})
    resumo = tmp_path / "resumo.md"
    executar(api, evento(), str(resumo))
    assert api.enviados == []
    assert "Nenhum apontamento" in resumo.read_text(encoding="utf-8")


def test_pr_de_fork_so_escreve_o_resumo_e_nunca_tenta_comentar(tmp_path, capsys):
    api = ApiFalsa([arquivo_py()], {"a.py": FONTE})
    resumo = tmp_path / "resumo.md"
    executar(api, evento("outra-pessoa/repo"), str(resumo))
    assert api.enviados == []
    assert "Valor padrão mutável" in resumo.read_text(encoding="utf-8")
    assert "::notice file=a.py,line=4" in capsys.readouterr().out


@pytest.mark.parametrize("status", [403, 422])
def test_se_o_github_recusa_os_comentarios_cai_para_o_resumo(tmp_path, status):
    api = ApiFalsa([arquivo_py()], {"a.py": FONTE}, erro_ao_enviar=GitHubError(status, "recusado"))
    resumo = tmp_path / "resumo.md"
    assert executar(api, evento(), str(resumo)) == 0
    assert "apontamento(s)" in resumo.read_text(encoding="utf-8")


def test_erro_inesperado_da_api_nao_e_engolido():
    api = ApiFalsa([arquivo_py()], {"a.py": FONTE}, erro_ao_enviar=GitHubError(500, "falhou"))
    with pytest.raises(GitHubError):
        executar(api, evento(), None)


def test_arquivo_ilegivel_ou_de_outra_linguagem_vai_para_nao_revisados():
    api = ApiFalsa([arquivo_py(), arquivo_py("x.rb", 1)], {"a.py": FONTE, "x.rb": "puts 1"})
    executar(api, evento(), None)
    (_, corpo) = api.enviados[0]
    assert "`x.rb`: linguagem ainda não suportada" in corpo["body"]


def test_teto_de_comentarios_vale_na_action():
    fonte = "import os\nimport sys\n\ndef f(a, b=[]):\n    l = 1\n    return f'x'\n"
    api = ApiFalsa([arquivo_py(linhas=6)], {"a.py": fonte})
    executar(api, evento(), None, teto=2)
    (_, corpo) = api.enviados[0]
    assert len(corpo["comments"]) == 2
    assert "ficaram só aqui" in corpo["body"]


def test_marcas_sao_lidas_de_volta():
    from farol.achados import Achado

    a = Achado("src/x y.py", 1, "ruff", None, "m")
    assert regras_ja_comentadas([{"body": marca_regra(a)}, {"body": None}]) == {
        ("sintaxe", marca_regra(a).split(":")[-1].removesuffix(" -->"))
    }


def test_anotacoes_escapam_quebra_de_linha_e_porcentagem():
    from farol.achados import Achado
    from farol.revisao import montar

    saida = anotacoes(montar([Achado("a.py", 1, "ruff", None, "100%\nruim")]))
    assert saida == ["::notice file=a.py,line=1,title=Erro de sintaxe::100%25%0Aruim"]


@pytest.mark.parametrize("evento", ["pull_request_target", "push", ""])
def test_main_so_roda_em_pull_request(monkeypatch, capsys, evento):
    from farol.action import main

    monkeypatch.setenv("GITHUB_EVENT_NAME", evento)
    assert main() == 2
    assert "pull_request" in capsys.readouterr().err
