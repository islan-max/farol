from farol.diffs import build_input, parse_patch

PATCH = r"""@@ -1,3 +1,4 @@
 import os
+import sys
 
-x = 1
+x = 2
@@ -10,2 +11,3 @@ def f():
     a = 1
+    b = 2
     return a
\ No newline at end of file
"""


def test_so_linhas_adicionadas_contam_com_numero_do_arquivo_novo():
    diff = parse_patch("a.py", PATCH)
    assert diff.added == {2, 4, 12}


def test_patch_com_crlf_e_vazio():
    assert parse_patch("a.py", PATCH.replace("\n", "\r\n")).added == {2, 4, 12}
    assert parse_patch("a.py", "").added == set()


def pr_file(nome, patch="@@ -0,0 +1 @@\n+x", status="added"):
    return {"filename": nome, "patch": patch, "status": status}


def test_build_input_separa_revisaveis_de_ignorados_com_motivo():
    entrada = build_input(
        [
            pr_file("src/a.py"),
            pr_file("uv.lock"),
            pr_file("web/vendor/lib.js"),
            pr_file("img.png", patch=""),
            pr_file("velho.py", status="removed"),
        ]
    )
    assert [f.path for f in entrada.files] == ["src/a.py"]
    assert {p for p, _ in entrada.skipped} == {
        "uv.lock",
        "web/vendor/lib.js",
        "img.png",
        "velho.py",
    }


def test_build_input_respeita_limite_de_arquivos():
    entrada = build_input([pr_file(f"{i}.py") for i in range(5)], max_files=2)
    assert len(entrada.files) == 2
    assert [m for _, m in entrada.skipped] == ["além do limite de 2 arquivos"] * 3
