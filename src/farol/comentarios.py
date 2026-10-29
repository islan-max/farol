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
    partes = [
        f"**Farol · {lc.titulo}** · `{lc.codigo}` · nível {NIVEIS[lc.nivel]}",
        "",
        lc.o_que_e,
        "",
        f"**Por que importa.** {lc.por_que_importa}",
        "",
        f"**Como corrigir.** {lc.como_corrigir}",
        "",
        "```python",
        "# antes",
        lc.antes,
        "",
        "# depois",
        lc.depois,
        "```",
    ]
    for ex in da_licao(lc.exemplos):
        partes += [
            "",
            f"**Como projetos reais resolvem.** {ex.porque}",
            "",
            "```python",
            ex.trecho,
            "```",
            f"[{ex.repo}]({ex.permalink}) · licença {ex.licenca}",
        ]
    if lc.docs:
        links = " · ".join(f"[{d['titulo']}]({d['url']})" for d in lc.docs)
        partes += ["", f"Para ler mais: {links}"]
    return "\n".join(partes)


def corpo(c: Comentario) -> str:
    a = c.achado
    if c.licao is None:
        titulo = f"`{a.codigo}`" if a.codigo else "Erro de sintaxe"
        partes = [f"**Farol · {titulo}**", "", f"A ferramenta disse (em inglês): {a.mensagem}"]
        if a.url:
            partes += ["", f"[Documentação da regra]({a.url})"]
    else:
        partes = [corpo_licao(c.licao)]
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
