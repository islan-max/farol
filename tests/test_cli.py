import json
import subprocess

import pytest

from farol.cli import main
from farol.diffs import split_git_diff


def test_main_sem_comando_mostra_ajuda(capsys):
    assert main([]) == 0
    assert "revisar" in capsys.readouterr().out


def test_explicar_mostra_a_licao(capsys):
    assert main(["explicar", "e722"]) == 0
    saida = capsys.readouterr().out
    assert "Por que importa" in saida and "except ValueError" in saida


def test_explicar_codigo_desconhecido_lista_os_disponiveis(capsys):
    assert main(["explicar", "Z999"]) == 2
    assert "E722" in capsys.readouterr().err


GIT_DIFF = """diff --git a/a.py b/a.py
index 1..2 100644
--- a/a.py
+++ b/a.py
@@ -1,2 +1,4 @@
 import os
+try:
+    pass
+except:
     print(os.name)
diff --git a/velho.py b/velho.py
deleted file mode 100644
--- a/velho.py
+++ /dev/null
@@ -1 +0,0 @@
-x = 1
"""


def test_split_git_diff_ignora_removidos_e_separa_os_patches():
    (item,) = split_git_diff(GIT_DIFF)
    assert item["filename"] == "a.py" and item["patch"].startswith("@@ -1,2 +1,4 @@")


@pytest.fixture
def repo(tmp_path, monkeypatch):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)  # noqa: S603, S607

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@t.dev")
    git("config", "user.name", "t")
    (tmp_path / "a.py").write_text("import sys\n\nprint(sys.argv)\n", encoding="utf-8")
    (tmp_path / "ok.py").write_text("import json\nx = 1\n", encoding="utf-8")  # F401 antigo
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_revisar_so_aponta_o_que_foi_alterado(repo, capsys):
    # F401 já existia? Não: o import de `os` é novo. O `except:` também é novo.
    (repo / "a.py").write_text(
        "import os\nimport sys\n\ntry:\n    print(sys.argv)\nexcept:\n    pass\n", encoding="utf-8"
    )
    assert main(["revisar", "--json"]) == 0
    dados = json.loads(capsys.readouterr().out)
    codigos = {c["codigo"] for c in dados["comentarios"]}
    assert codigos == {"F401", "E722", "S110"}


def test_revisar_nao_comenta_problema_antigo(repo, capsys):
    (repo / "ok.py").write_text("import json\nx = 1\nif x == None:\n    pass\n", encoding="utf-8")
    main(["revisar", "--json"])
    dados = json.loads(capsys.readouterr().out)
    assert [(c["codigo"], c["arquivo"], c["linha"]) for c in dados["comentarios"]] == [
        ("E711", "ok.py", 3)
    ]  # o `import json` sem uso já estava lá e não é comentado


def test_revisar_sem_mudancas_e_arquivo_de_outra_linguagem(repo, capsys):
    assert main(["revisar"]) == 0
    assert "Nenhum apontamento" in capsys.readouterr().out
    (repo / "x.rb").write_text("puts 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "-N", "x.rb"], cwd=repo, check=True)  # noqa: S603, S607
    main(["revisar"])
    assert "linguagem ainda não suportada" in capsys.readouterr().out


def test_revisar_fora_de_repositorio_git_da_erro_claro(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["revisar"]) == 2
    assert capsys.readouterr().err.startswith("Erro:")
