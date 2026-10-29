"""Exemplos reais de projetos abertos, escolhidos e conferidos à mão (`curados.json`).

Cada exemplo é um trecho curto com permalink de um commit, licença permissiva e uma frase
dizendo por que ele resolve o caso da lição. Nada é buscado em tempo de execução.
"""

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

ARQUIVO = Path(__file__).with_name("curados.json")


@dataclass(frozen=True)
class Exemplo:
    id: str
    regra: str
    repo: str
    licenca: str
    permalink: str
    trecho: str
    porque: str


@cache
def todos() -> dict[str, Exemplo]:
    itens = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    return {i["id"]: Exemplo(**i) for i in itens}


def da_licao(ids: tuple[str, ...]) -> list[Exemplo]:
    return [todos()[i] for i in ids]
