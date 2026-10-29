"""Resumo entre PRs: o que se repete, o que é novo e o que a pessoa parece já dominar.

Não há servidor: o histórico fica em uma issue "Painel do Farol" do próprio repositório, em um
comentário HTML dentro do corpo (`<!-- farol:painel {...} -->`), e é regravado a cada PR revisado.
Só guarda o login (que já é público no PR), o número do PR e os códigos das regras. Fica desligado
por padrão (`painel: on` na Action) porque exige a permissão `issues: write`.
"""

import json
import re
from dataclasses import dataclass

from farol.github import GitHubError
from farol.licoes import todas

TITULO = "Painel do Farol"
ROTULO = "farol"
SITE = "https://islan-max.github.io/farol/licoes"
MAX_PRS_POR_PESSOA = 30
MAX_PESSOAS = 50
MAX_CHARS = 60_000  # o GitHub aceita 65.536 no corpo de uma issue
_DADOS = re.compile(r"<!-- farol:painel (\{.*?\}) -->", re.DOTALL)
_LOGIN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")


@dataclass
class Resumo:
    n_prs: int
    repetem: dict[str, int]  # regra -> em quantos PRs apareceu (2 ou mais)
    novas: list[str]  # só no PR mais recente
    dominadas: list[str]  # já apareceram, mas não nos 2 PRs mais recentes (com 3+ PRs)


def carregar(corpo: str | None) -> dict:
    achado = _DADOS.search(corpo or "")
    if achado:
        try:
            dados = json.loads(achado.group(1))
            if isinstance(dados.get("pessoas"), dict):
                return dados
        except ValueError:
            pass
    return {"v": 1, "pessoas": {}}


def registrar(dados: dict, login: str, pr: int, regras: set[str]) -> None:
    """Junta as regras ao PR (um PR com vários commits acumula); poda o que passou do limite."""
    if not _LOGIN.match(login):
        return
    prs = dados["pessoas"].setdefault(login, {})
    atuais = set(prs.get(str(pr), []))
    prs[str(pr)] = sorted(atuais | {r for r in regras if re.fullmatch(r"[\w@/.-]{1,60}", r)})
    for antigo in sorted(prs, key=int)[:-MAX_PRS_POR_PESSOA]:
        del prs[antigo]
    for fora in list(dados["pessoas"])[:-MAX_PESSOAS]:
        del dados["pessoas"][fora]


def resumir(prs: dict[str, list[str]]) -> Resumo:
    ordem = sorted(prs, key=int)
    contagem: dict[str, int] = {}
    for numero in ordem:
        for regra in prs[numero]:
            contagem[regra] = contagem.get(regra, 0) + 1
    recentes = set().union(*(prs[n] for n in ordem[-2:])) if ordem else set()
    ultimo = set(prs[ordem[-1]]) if ordem else set()
    return Resumo(
        n_prs=len(ordem),
        repetem=dict(sorted(((r, n) for r, n in contagem.items() if n >= 2), key=lambda x: -x[1])),
        novas=sorted(r for r in ultimo if contagem[r] == 1),
        dominadas=sorted(r for r in contagem if r not in recentes) if len(ordem) >= 3 else [],
    )


def _nome(regra: str) -> str:
    lc = next((v for (_, c), v in todas().items() if c == regra), None)
    if lc is None:
        return f"`{regra}`"
    return f"[{lc.titulo}]({SITE}/{lc.codigo}.html) (`{lc.codigo}`)"


def linhas_do_resumo(r: Resumo) -> list[str]:
    linhas = []
    if r.repetem:
        itens = "; ".join(f"{_nome(c)} em {n} PRs" for c, n in r.repetem.items())
        linhas.append(f"- **Se repete:** {itens}")
    if r.novas:
        linhas.append("- **Apareceu agora:** " + "; ".join(_nome(c) for c in r.novas))
    if r.dominadas:
        itens = "; ".join(_nome(c) for c in r.dominadas)
        linhas.append(f"- **Já parece dominado** (não aparece nos 2 PRs mais recentes): {itens}")
    return linhas


def para_a_review(r: Resumo) -> str | None:
    """Trecho curto para o corpo da review; só quando há histórico (2+ PRs) e algo a dizer."""
    linhas = linhas_do_resumo(r) if r.n_prs >= 2 else []
    if not linhas:
        return None
    return "\n".join(["**Seu progresso neste repositório**", "", *linhas])


def renderizar(dados: dict) -> str:
    partes = [
        f"# {TITULO}",
        "",
        "Histórico, por pessoa, das regras que o Farol apontou nos PRs deste repositório: o que "
        "se repete, o que apareceu agora e o que já parece dominado. É atualizado pela Action a "
        "cada PR revisado; só guarda o login, o número do PR e os códigos das regras.",
    ]
    for login, prs in sorted(dados["pessoas"].items()):
        r = resumir(prs)
        corpo = linhas_do_resumo(r) or ["- Nada a destacar ainda."]
        partes += ["", f"## {login}", f"{r.n_prs} PR(s) revisado(s).", "", *corpo]
    partes += ["", f"<!-- farol:painel {json.dumps(dados, separators=(',', ':'))} -->"]
    return "\n".join(partes)


TENTATIVAS = 3


def _achar_painel(api, base: str) -> dict | None:
    """A issue do painel; havendo duas (corrida), vale a de menor número: todos escolhem igual."""
    todas_ = [
        i
        for i in api.paginar(f"{base}/issues?state=open&labels={ROTULO}")
        if "pull_request" not in i and _DADOS.search(i.get("body") or "")
    ]
    return min(todas_, key=lambda i: i["number"]) if todas_ else None


def _sobreviveu(dados: dict, login: str, pr: int, regras: set[str]) -> bool:
    registro = dados["pessoas"].get(login, {}).get(str(pr))
    return registro is not None and regras <= set(registro)


def atualizar(api, pr: int, login: str, regras: set[str]) -> Resumo | None:
    """Regrava o painel com o PR atual e devolve o resumo da pessoa. Nunca derruba a revisão.

    O GitHub não tem gravação condicional para o corpo de uma issue, então dois PRs revisados juntos
    podem se sobrescrever. Por isso, depois de gravar, relê e confere se o registro deste PR
    sobreviveu; se não, soma de novo e grava outra vez (até TENTATIVAS).
    shortcut: continua não sendo atômico (uma gravação logo após a conferência ainda pode perder um
    registro), upgrade: mover o histórico para um armazenamento com compare-and-swap.
    """
    try:
        base = f"/repos/{api.repo}"
        for tentativa in range(1, TENTATIVAS + 1):
            issue = _achar_painel(api, base)
            dados = carregar(issue["body"] if issue else None)
            registrar(dados, login, pr, regras)
            corpo = renderizar(dados)
            while len(corpo) > MAX_CHARS and len(dados["pessoas"]) > 1:
                del dados["pessoas"][next(iter(dados["pessoas"]))]  # descarta a pessoa mais antiga
                corpo = renderizar(dados)
            if issue:
                api.alterar(f"{base}/issues/{issue['number']}", {"body": corpo})
            else:
                api.enviar(f"{base}/issues", {"title": TITULO, "body": corpo, "labels": [ROTULO]})
            atual = _achar_painel(api, base)
            relido = carregar(atual["body"] if atual else None)
            if _sobreviveu(relido, login, pr, regras):
                return resumir(relido["pessoas"].get(login, {}))
            print(
                f"Aviso: outro PR sobrescreveu o painel; tentando de novo "
                f"({tentativa}/{TENTATIVAS})."
            )
        print("Aviso: o painel pode ficar sem o registro deste PR (gravações simultâneas).")
        return resumir(dados["pessoas"].get(login, {}))
    except GitHubError as erro:
        print(f"Aviso: não consegui atualizar o painel ({erro}).")
        return None
