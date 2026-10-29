"""Escolhe o analisador pela extensão do arquivo."""

from farol.achados import Achado
from farol.analise import ruff


def analisar(path: str, source: str, linhas: set[int] | None = None) -> list[Achado] | None:
    """Achados do arquivo, ou None se a linguagem ainda não é suportada."""
    if path.endswith((".py", ".pyi")):
        return ruff.analisar(path, source, linhas)
    return None
