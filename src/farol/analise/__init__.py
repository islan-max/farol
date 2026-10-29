"""Escolhe o analisador pela extensão do arquivo."""

from farol.achados import Achado
from farol.analise import eslint, ruff
from farol.analise.eslint import FerramentaIndisponivel

__all__ = ["FerramentaIndisponivel", "analisar"]


def analisar(path: str, source: str, linhas: set[int] | None = None) -> list[Achado] | None:
    """Achados do arquivo, ou None se a linguagem ainda não é suportada.

    Levanta `FerramentaIndisponivel` quando falta algo no ambiente (ex.: Node.js).
    """
    if path.endswith((".py", ".pyi")):
        return ruff.analisar(path, source, linhas)
    if path.endswith(eslint.EXTENSOES):
        return eslint.analisar(path, source, linhas)
    return None
