"""Ponto de entrada da GitHub Action: revisa o PR do evento e comenta (ou escreve o resumo).

Só lê texto pela API; nada do PR é executado. Roda com o evento `pull_request`.
"""

import hashlib
import json
import os
import re
import sys

from farol.achados import Achado
from farol.analise import FerramentaIndisponivel, analisar
from farol.comentarios import corpo, resumo_excedente
from farol.diffs import build_input
from farol.github import Api, GitHubError
from farol.ia import MODELO_PADRAO, Ollama, anotar
from farol.painel import atualizar as atualizar_painel
from farol.painel import para_a_review
from farol.revisao import TETO_INLINE, Revisao, montar

RODAPE = (
    "<sub>Farol revisa só as linhas alteradas neste PR, com ruff e ESLint e lições escritas à mão. "
    "As regras e as lições não vêm de IA. Cada regra comenta uma vez por arquivo.</sub>"
)
_MARCA_REGRA = re.compile(r"<!-- farol:regra:([A-Za-z0-9_-]+):([0-9a-f]{10}) -->")


def _hash(path: str) -> str:
    return hashlib.sha1(path.encode(), usedforsecurity=False).hexdigest()[:10]


def marca_regra(a: Achado) -> str:
    return f"<!-- farol:regra:{a.codigo or 'sintaxe'}:{_hash(a.path)} -->"


def marca_revisao(sha: str) -> str:
    return f"<!-- farol:revisao:{sha} -->"


def regras_ja_comentadas(comentarios: list[dict]) -> set[tuple[str, str]]:
    return {m.groups() for c in comentarios for m in _MARCA_REGRA.finditer(c.get("body") or "")}


def _achar(api: Api, repo_cabeca: str, sha: str, pr_files: list[dict]):
    entrada = build_input(pr_files)
    achados: list[Achado] = []
    nao_revisados = list(entrada.skipped)
    fontes: dict[str, str] = {}
    for arquivo in entrada.files:
        try:
            fonte = api.texto_do_arquivo(repo_cabeca, arquivo.path, sha)
        except (GitHubError, UnicodeDecodeError) as erro:
            nao_revisados.append((arquivo.path, f"não consegui ler o arquivo ({erro})"[:120]))
            continue
        fontes[arquivo.path] = fonte
        try:
            resultado = analisar(arquivo.path, fonte, arquivo.added)
        except FerramentaIndisponivel as erro:
            nao_revisados.append((arquivo.path, str(erro)))
            continue
        if resultado is None:
            nao_revisados.append((arquivo.path, "linguagem ainda não suportada"))
        else:
            achados += resultado
    return achados, nao_revisados, fontes


def corpo_da_revisao(
    rev: Revisao,
    nao_revisados: list[tuple[str, str]],
    sha: str,
    progresso: str | None = None,
) -> str:
    linhas = [f"## Farol: {rev.total} apontamento(s) nas linhas alteradas", ""]
    if len(rev.inline) < rev.total:
        linhas += [
            "Cada regra aparece uma vez; as outras ocorrências estão listadas no comentário.",
            "",
        ]
    if rev.excedente:
        linhas += ["Passou do limite de comentários, então estes ficaram só aqui:", ""]
        linhas += [resumo_excedente(rev), ""]
    if nao_revisados:
        linhas += ["**Não revisados:**"]
        linhas += [f"- `{p}`: {m}" for p, m in nao_revisados[:10]]
        if len(nao_revisados) > 10:
            linhas.append(f"- e mais {len(nao_revisados) - 10} arquivo(s)")
        linhas.append("")
    if progresso:
        linhas += [progresso, ""]
    modelos = {c.modelo for c in rev.inline if c.nota}
    if modelos:
        quais = ", ".join(sorted(modelos))
        linhas += [
            f"As notas **No seu código** foram escritas por uma IA local ({quais}) e podem errar; "
            "a explicação da regra é sempre a lição escrita à mão.",
            "",
        ]
    return "\n".join([*linhas, RODAPE, marca_revisao(sha)])


def comentario_inline(c) -> dict:
    return {
        "path": c.achado.path,
        "line": c.achado.line,
        "side": "RIGHT",
        "body": corpo(c) + "\n\n" + marca_regra(c.achado),
    }


def resumo_markdown(rev: Revisao, nao_revisados: list[tuple[str, str]]) -> str:
    if not rev.total:
        return "## Farol\n\nNenhum apontamento nas linhas alteradas. Bom trabalho!"
    partes = [f"## Farol: {rev.total} apontamento(s) nas linhas alteradas"]
    for c in rev.inline:
        partes += ["", f"### `{c.achado.path}:{c.achado.line}`", corpo(c)]
    if rev.excedente:
        partes += ["", "### Além disso", resumo_excedente(rev)]
    if nao_revisados:
        partes += ["", "**Não revisados:**"] + [f"- `{p}`: {m}" for p, m in nao_revisados[:10]]
    return "\n".join(partes)


def anotacoes(rev: Revisao) -> list[str]:
    """Linhas `::notice` do log do job: aparecem no diff do PR mesmo sem permissão de escrita."""

    def limpar(texto: str) -> str:
        return texto.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")

    saida = []
    for c in rev.inline:
        a = c.achado
        titulo = c.licao.titulo if c.licao else (a.codigo or "Erro de sintaxe")
        texto = c.licao.o_que_e if c.licao else a.mensagem
        saida.append(
            f"::notice file={a.path},line={a.line},title={limpar(titulo)}::{limpar(texto)}"
        )
    return saida


def executar(
    api: Api,
    evento: dict,
    caminho_resumo: str | None,
    teto: int = TETO_INLINE,
    ia: Ollama | None = None,
    painel: bool = False,
) -> int:
    pr = evento["pull_request"]
    numero, sha = pr["number"], pr["head"]["sha"]
    repo_cabeca = pr["head"]["repo"]["full_name"] if pr["head"].get("repo") else api.repo
    de_fork = repo_cabeca != api.repo

    base = f"/repos/{api.repo}/pulls/{numero}"
    reviews = [] if de_fork else api.paginar(f"{base}/reviews")
    if any(marca_revisao(sha) in (r.get("body") or "") for r in reviews):
        print(f"Este commit ({sha[:7]}) já foi revisado; nada a fazer.")
        return 0

    achados, nao_revisados, fontes = _achar(api, repo_cabeca, sha, api.paginar(f"{base}/files"))
    progresso = None
    autor = pr.get("user") or {}
    if painel and not de_fork and autor.get("type") != "Bot" and autor.get("login"):
        # As regras do PR inteiro (antes de tirar as já comentadas) entram no histórico.
        regras = {a.codigo for a in achados if a.codigo}
        resumo = atualizar_painel(api, numero, autor["login"], regras)
        progresso = para_a_review(resumo) if resumo else None
    if not de_fork:
        comentados = regras_ja_comentadas(api.paginar(f"{base}/comments"))
        achados = [a for a in achados if (a.codigo or "sintaxe", _hash(a.path)) not in comentados]
    rev = montar(achados, teto)
    if ia and rev.total:
        anotadas = anotar(rev, fontes, ia)
        print(f"IA local ({ia.modelo}): {anotadas} nota(s) de {len(rev.inline)} comentário(s).")

    pode_comentar = not de_fork and rev.total > 0
    if pode_comentar:
        try:
            api.enviar(
                f"{base}/reviews",
                {
                    "commit_id": sha,
                    "event": "COMMENT",
                    "body": corpo_da_revisao(rev, nao_revisados, sha, progresso),
                    "comments": [comentario_inline(c) for c in rev.inline],
                },
            )
            print(f"Review publicada com {len(rev.inline)} comentário(s).")
            return 0
        except GitHubError as erro:
            if erro.status not in (403, 422):
                raise
            print(f"Não consegui comentar nas linhas ({erro}); caio para o resumo do job.")
            pode_comentar = False
            # 422: alguma linha fora do diff; 403: token sem permissão (ex.: PR de fork)

    texto = resumo_markdown(rev, nao_revisados)
    if caminho_resumo:
        with open(caminho_resumo, "a", encoding="utf-8") as arq:
            arq.write(texto + "\n")
    print("\n".join(anotacoes(rev)))
    return 0


def _ia(env) -> Ollama | None:
    """IA local só se pedida (`FAROL_IA=ollama`) e se o servidor responder; senão segue sem."""
    if env.get("FAROL_IA", "off") != "ollama":
        return None
    cliente = Ollama(env.get("FAROL_MODELO") or MODELO_PADRAO)
    if cliente.disponivel():
        return cliente
    print(f"Aviso: o Ollama não respondeu com o modelo {cliente.modelo}; sigo sem IA.")
    return None


def main() -> int:
    env = os.environ
    if env.get("GITHUB_EVENT_NAME") != "pull_request":
        # Nunca pull_request_target: ele roda com permissão de escrita sobre código de fora.
        print("O Farol só roda no evento pull_request.", file=sys.stderr)
        return 2
    with open(env["GITHUB_EVENT_PATH"], encoding="utf-8") as arq:
        evento = json.load(arq)
    api = Api(env["GITHUB_TOKEN"], env["GITHUB_REPOSITORY"])
    try:
        return executar(
            api,
            evento,
            env.get("GITHUB_STEP_SUMMARY"),
            int(env.get("FAROL_TETO", "10")),
            _ia(env),
            env.get("FAROL_PAINEL", "off") == "on",
        )
    except GitHubError as erro:
        print(f"Erro ao falar com o GitHub: {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
