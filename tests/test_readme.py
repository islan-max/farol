import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).parent.parent


def test_tabela_de_licoes_do_readme_esta_em_dia():
    proc = subprocess.run(  # noqa: S603
        [sys.executable, str(RAIZ / "scripts" / "atualizar_readme.py"), "--conferir"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr


def test_readme_so_aponta_para_arquivos_que_existem():
    texto = (RAIZ / "README.md").read_text(encoding="utf-8")
    import re

    locais = set(re.findall(r'(?:srcset|src|href)="((?:docs|\.github)/[^"#]+|[A-Z_]+\.md)"', texto))
    locais |= set(re.findall(r"\]\(((?:docs/)?[A-Za-z_./-]+\.(?:md|svg|png))\)", texto))
    faltando = sorted(p for p in locais if not (RAIZ / p).exists())
    assert not faltando, faltando
    assert len(locais) >= 12  # imagens claras e escuras, documentação e arquivos da comunidade
