"""Linha de comando: `farol revisar` e `farol explicar`."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from farol import __version__
from farol.analise import FerramentaIndisponivel, analisar
from farol.comentarios import corpo, corpo_licao, resumo_excedente
from farol.diffs import build_input, split_git_diff
from farol.licoes import todas
from farol.revisao import TETO_INLINE, Revisao, montar


def _git(*args: str) -> str:
    proc = subprocess.run(  # noqa: S603 - argumentos fixos; o único valor livre é um nome de ref
        ["git", "-c", "core.quotepath=false", *args],  # noqa: S607
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git falhou")
    return proc.stdout


def git_diff(base: str | None) -> str:
    """Diff do diretório de trabalho contra HEAD, ou contra o ponto onde a branch saiu de `base`."""
    ponto_de_partida = _git("merge-base", base, "HEAD").strip() if base else "HEAD"
    return _git("diff", ponto_de_partida)


def revisar(
    diff_texto: str, raiz: Path, teto: int = TETO_INLINE
) -> tuple[Revisao, list[tuple[str, str]]]:
    entrada = build_input(split_git_diff(diff_texto))
    achados, ignorados = [], list(entrada.skipped)
    for arquivo in entrada.files:
        try:
            fonte = (raiz / arquivo.path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            ignorados.append((arquivo.path, "não consegui ler o arquivo"))
            continue
        try:
            resultado = analisar(arquivo.path, fonte, arquivo.added)
        except FerramentaIndisponivel as erro:
            ignorados.append((arquivo.path, str(erro)))
            continue
        if resultado is None:
            ignorados.append((arquivo.path, "linguagem ainda não suportada"))
        else:
            achados += resultado
    return montar(achados, teto), ignorados


def texto(rev: Revisao, ignorados: list[tuple[str, str]]) -> str:
    if not rev.total:
        saida = ["Nenhum apontamento nas linhas alteradas. Bom trabalho!"]
    else:
        saida = [f"{rev.total} apontamento(s) nas linhas alteradas.\n"]
        for c in rev.inline:
            saida += [f"── {c.achado.path}:{c.achado.line}", corpo(c), ""]
        if rev.excedente:
            saida += ["Além disso (limite de comentários atingido):", resumo_excedente(rev)]
    if ignorados:
        saida += ["", "Não revisados:"] + [f"- {p}: {m}" for p, m in ignorados]
    return "\n".join(saida)


def como_json(rev: Revisao, ignorados: list[tuple[str, str]]) -> str:
    def item(c, inline: bool) -> dict:
        a = c.achado
        return {
            "arquivo": a.path,
            "linha": a.line,
            "codigo": a.codigo,
            "inline": inline,
            "titulo": c.licao.titulo if c.licao else None,
            "mensagem": a.mensagem,
            "tambem_em": [f"{x.path}:{x.line}" for x in c.tambem],
        }

    dados = {
        "total": rev.total,
        "comentarios": [item(c, True) for c in rev.inline]
        + [item(c, False) for c in rev.excedente],
        "nao_revisados": [{"arquivo": p, "motivo": m} for p, m in ignorados],
    }
    return json.dumps(dados, ensure_ascii=False, indent=2)


def _explicar(codigo: str) -> int:
    achada = next((lc for (_, c), lc in todas().items() if c.lower() == codigo.lower()), None)
    if achada is None:
        disponiveis = ", ".join(sorted(c for _, c in todas()))
        print(f"Não tenho lição para {codigo!r}. Disponíveis: {disponiveis}", file=sys.stderr)
        return 2
    print(corpo_licao(achada))
    return 0


def main(argv: list[str] | None = None) -> int:
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="farol", description="Revisão de PR que ensina.")
    parser.add_argument("--version", action="version", version=f"Farol {__version__}")
    sub = parser.add_subparsers(dest="comando")
    rev = sub.add_parser("revisar", help="revisa as linhas alteradas (git diff)")
    rev.add_argument("--base", help="compara com o ponto onde a branch saiu de BASE (ex.: main)")
    rev.add_argument("--diff", help="lê um diff pronto de ARQUIVO (ou '-' para a entrada padrão)")
    rev.add_argument("--json", action="store_true", help="saída em JSON")
    rev.add_argument("--teto", type=int, default=TETO_INLINE, help="máximo de comentários")
    exp = sub.add_parser("explicar", help="mostra a lição de uma regra, ex.: E722")
    exp.add_argument("codigo")
    args = parser.parse_args(argv)

    if args.comando == "explicar":
        return _explicar(args.codigo)
    if args.comando == "revisar":
        try:
            if args.diff == "-":
                entrada = sys.stdin.read()
            elif args.diff:
                entrada = Path(args.diff).read_text(encoding="utf-8")
            else:
                entrada = git_diff(args.base)
            resultado, ignorados = revisar(entrada, Path.cwd(), args.teto)
        except (RuntimeError, OSError) as erro:
            print(f"Erro: {erro}", file=sys.stderr)
            return 2
        print(como_json(resultado, ignorados) if args.json else texto(resultado, ignorados))
        return 0
    parser.print_help()
    return 0
