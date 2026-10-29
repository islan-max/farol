"""Catálogo de lições: um arquivo TOML por regra, em `farol/licoes/<linguagem>/`.

É a fonte única de texto para a CLI, a Action e o site.
"""

import tomllib
from dataclasses import dataclass
from functools import cache
from pathlib import Path

DIR = Path(__file__).parent / "licoes"
NIVEIS = ("iniciante", "intermediario", "avancado")
FERRAMENTA_POR_PASTA = {"python": "ruff", "javascript": "eslint"}
CAMPOS = (
    "codigo",
    "ferramenta",
    "titulo",
    "nivel",
    "o_que_e",
    "por_que_importa",
    "como_corrigir",
    "antes",
    "depois",
)


@dataclass(frozen=True)
class Licao:
    codigo: str
    ferramenta: str
    titulo: str
    nivel: str
    o_que_e: str
    por_que_importa: str
    como_corrigir: str
    antes: str
    depois: str
    docs: tuple[dict, ...]
    exemplos: tuple[str, ...]  # ids em exemplos/curados.json
    linguagem: str = "python"  # linguagem dos trechos antes/depois (para o bloco de código)
    extensao: str = (
        ""  # extensão do arquivo de teste quando a regra vale só para um tipo (ex.: "ts")
    )
    categoria: str = ""  # "seguranca" passa na frente quando o teto de comentários aperta


def _ler(arquivo: Path) -> Licao:
    dados = tomllib.loads(arquivo.read_text(encoding="utf-8"))
    faltando = [c for c in CAMPOS if not str(dados.get(c, "")).strip()]
    if faltando:
        raise ValueError(f"{arquivo.name}: campos ausentes ou vazios: {', '.join(faltando)}")
    if dados["nivel"] not in NIVEIS:
        raise ValueError(f"{arquivo.name}: nível inválido {dados['nivel']!r}")
    return Licao(
        **{
            c: dados[c].strip("\n") if c in ("antes", "depois") else dados[c].strip()
            for c in CAMPOS
        },
        docs=tuple(dados.get("docs", [])),
        exemplos=tuple(dados.get("exemplos", [])),
        linguagem=dados.get("linguagem", "python"),
        categoria=dados.get("categoria", ""),
        extensao=dados.get("extensao", ""),
    )


@cache
def todas() -> dict[tuple[str, str], Licao]:
    """Todas as lições, indexadas por (ferramenta, código)."""
    catalogo = {}
    for pasta, ferramenta in FERRAMENTA_POR_PASTA.items():
        for arquivo in sorted((DIR / pasta).glob("*.toml")):
            licao = _ler(arquivo)
            if licao.ferramenta != ferramenta or arquivo.stem != licao.codigo.replace("/", "__"):
                raise ValueError(f"{arquivo}: ferramenta ou nome do arquivo não confere")
            catalogo[(ferramenta, licao.codigo)] = licao
    return catalogo


def licao(ferramenta: str, codigo: str | None) -> Licao | None:
    return todas().get((ferramenta, codigo)) if codigo else None


def codigos(ferramenta: str) -> list[str]:
    return sorted(c for f, c in todas() if f == ferramenta)
