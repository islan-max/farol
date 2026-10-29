import re
from pathlib import Path

RAIZ = Path(__file__).parent.parent
ARQUIVOS = [*sorted((RAIZ / ".github" / "workflows").glob("*.yml")), RAIZ / "action.yml"]
USA = re.compile(r"^\s*-?\s*uses:\s*(\S+)", re.MULTILINE)
SHA = re.compile(r"^[\w.-]+/[\w.-]+(/[\w./-]+)?@[0-9a-f]{40}$")


def test_actions_de_terceiros_estao_fixadas_por_sha():
    soltas = []
    for arquivo in ARQUIVOS:
        for alvo in USA.findall(arquivo.read_text(encoding="utf-8")):
            if alvo.startswith("./") or SHA.match(alvo):
                continue
            soltas.append(f"{arquivo.name}: {alvo}")
    assert not soltas, "fixe por SHA do commit (com a versão em comentário): " + ", ".join(soltas)


def test_workflows_pedem_so_as_permissoes_necessarias():
    for arquivo in (RAIZ / ".github" / "workflows").glob("*.yml"):
        texto = arquivo.read_text(encoding="utf-8")
        assert re.search(r"^permissions:", texto, re.MULTILINE), f"{arquivo.name} sem permissions"
        assert "write-all" not in texto
