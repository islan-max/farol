"""Transforma achados em uma revisão legível: um comentário por regra, com teto de ruído."""

from dataclasses import dataclass, field

from farol.achados import Achado
from farol.licoes import Licao, licao

TETO_INLINE = 10


@dataclass
class Comentario:
    achado: Achado  # a primeira ocorrência da regra
    licao: Licao | None
    tambem: list[Achado] = field(default_factory=list)  # as outras ocorrências da mesma regra


@dataclass
class Revisao:
    inline: list[Comentario]  # viram comentários na linha, no máximo TETO_INLINE
    excedente: list[Comentario]  # o que passou do teto: vai agrupado no corpo da review
    total: int  # nº de achados antes de deduplicar


def _chave(a: Achado) -> tuple:
    # Erro de sintaxe não tem código: cada arquivo tem o seu.
    return (a.ferramenta, a.codigo) if a.codigo else (a.ferramenta, None, a.path)


def _prioridade(c: Comentario) -> tuple:
    # Lições de segurança primeiro; depois a ordem natural do arquivo.
    a = c.achado
    return (0 if c.licao and c.licao.categoria == "seguranca" else 1, a.path, a.line)


def montar(achados: list[Achado], teto: int = TETO_INLINE) -> Revisao:
    grupos: dict[tuple, Comentario] = {}
    for a in sorted(achados, key=lambda a: (a.path, a.line, a.codigo or "")):
        c = grupos.get(_chave(a))
        if c is None:
            grupos[_chave(a)] = Comentario(a, licao(a.ferramenta, a.codigo))
        else:
            c.tambem.append(a)
    ordenados = sorted(grupos.values(), key=_prioridade)
    return Revisao(ordenados[:teto], ordenados[teto:], len(achados))
