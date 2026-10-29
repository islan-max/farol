"""Texto (Markdown) dos comentários: o mesmo na CLI, na Action e nos testes."""

from farol.exemplos import da_licao
from farol.licoes import Licao
from farol.revisao import Comentario, Revisao

MAX_LOCAIS = 5
NIVEIS = {"iniciante": "iniciante", "intermediario": "intermediário", "avancado": "avançado"}


def _locais(achados) -> str:
    locais = [f"`{a.path}:{a.line}`" for a in achados[:MAX_LOCAIS]]
    resto = len(achados) - MAX_LOCAIS
    return ", ".join(locais) + (f" e mais {resto}" if resto > 0 else "")


def corpo_licao(lc: Licao) -> str:
    """A lição inteira, sem depender de onde ela foi encontrada (usado por `farol explicar`)."""
    comentario = "#" if lc.linguagem == "python" else "//"
    partes = [
        f"**Farol · {lc.titulo}** · `{lc.codigo}` · nível {NIVEIS[lc.nivel]}",
        "",
        lc.o_que_e,
        "",
        f"**Por que importa.** {lc.por_que_importa}",
        "",
        f"**Como corrigir.** {lc.como_corrigir}",
        "",
        f"```{lc.linguagem}",
        f"{comentario} antes",
        lc.antes,
        "",
        f"{comentario} depois",
        lc.depois,
        "```",
    ]
    for ex in da_licao(lc.exemplos):
        partes += [
            "",
            f"**Como projetos reais resolvem.** {ex.porque}",
            "",
            f"```{lc.linguagem}",
            ex.trecho,
            "```",
            f"[{ex.repo}]({ex.permalink}) · licença {ex.licenca}",
        ]
    if lc.docs:
        links = " · ".join(f"[{d['titulo']}]({d['url']})" for d in lc.docs)
        partes += ["", f"Para ler mais: {links}"]
    return "\n".join(partes)


def _com_nota(texto: str, c: Comentario) -> str:
    if not c.nota:
        return texto
    titulo, _, resto = texto.partition("\n")
    aviso = f"nota da IA local `{c.modelo}`, pode errar"
    return f"{titulo}\n\n> **No seu código** ({aviso}): {c.nota}\n{resto}"


def corpo(c: Comentario) -> str:
    a = c.achado
    if c.licao is None:
        titulo = f"`{a.codigo}`" if a.codigo else "Erro de sintaxe"
        partes = [f"**Farol · {titulo}**", "", f"A ferramenta disse (em inglês): {a.mensagem}"]
        if a.url:
            partes += ["", f"[Documentação da regra]({a.url})"]
    else:
        partes = [_com_nota(corpo_licao(c.licao), c)]
    if c.tambem:
        partes += ["", f"Também aparece em: {_locais(c.tambem)}."]
    return "\n".join(partes)


def resumo_excedente(rev: Revisao) -> str:
    """Lista curta, por regra, do que passou do teto de comentários."""
    linhas = []
    for c in rev.excedente:
        nome = c.licao.titulo if c.licao else (c.achado.codigo or "Erro de sintaxe")
        linhas.append(f"- **{nome}**: {_locais([c.achado, *c.tambem])}")
    return "\n".join(linhas)
