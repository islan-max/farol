"""Tipo comum aos analisadores: um apontamento de uma ferramenta em uma linha."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Achado:
    path: str
    line: int
    ferramenta: str  # "ruff" ou "eslint"
    codigo: str | None  # None em erro de sintaxe
    mensagem: str  # mensagem original da ferramenta (inglês)
    url: str | None = None  # página da regra na documentação da ferramenta
