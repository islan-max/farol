from farol import painel
from farol.action import corpo_da_revisao, executar
from farol.github import GitHubError
from farol.revisao import montar

FONTE = "import os\n\n\ndef f(a, b=[]):\n    return a\n"  # F401 (linha 1) e B006 (linha 4)


def test_registrar_acumula_regras_do_mesmo_pr_e_ignora_login_invalido():
    dados = painel.carregar(None)
    painel.registrar(dados, "ana", 7, {"E722"})
    painel.registrar(dados, "ana", 7, {"F401"})  # outro commit do mesmo PR
    painel.registrar(dados, "<script>", 8, {"E722"})
    assert dados["pessoas"] == {"ana": {"7": ["E722", "F401"]}}


def test_resumo_repete_novo_e_dominado():
    r = painel.resumir(
        {
            "1": ["E722", "F401"],
            "2": ["E722"],
            "3": ["B006"],
            "4": [],
            "5": ["S105"],
        }
    )
    assert r.n_prs == 5
    assert r.repetem == {"E722": 2}
    assert r.novas == ["S105"]
    # B006 só apareceu no PR 3 e não está nos 2 mais recentes (4 e 5): também conta como dominada.
    assert r.dominadas == ["B006", "E722", "F401"]


def test_dominado_exige_tres_prs_e_ausencia_nos_dois_mais_recentes():
    assert painel.resumir({"1": ["E722"], "2": []}).dominadas == []  # só 2 PRs
    assert painel.resumir({"1": ["E722"], "2": [], "3": []}).dominadas == ["E722"]
    assert painel.resumir({"1": ["E722"], "2": [], "3": ["E722"]}).dominadas == []
    assert painel.resumir({}).repetem == {}


def test_prs_sao_ordenados_como_numero_e_nao_como_texto():
    r = painel.resumir({"9": ["X"], "10": [], "11": []})
    assert r.dominadas == ["X"]  # "10" < "9" como texto daria outra ordem


def test_render_e_carregar_ida_e_volta_e_corpo_estranho_vira_vazio():
    dados = painel.carregar(None)
    painel.registrar(dados, "ana", 1, {"E722"})
    corpo = painel.renderizar(dados)
    assert corpo.startswith("# Painel do Farol") and "## ana" in corpo
    assert painel.carregar(corpo) == dados
    assert painel.carregar("texto qualquer") == {"v": 1, "pessoas": {}}
    assert painel.carregar("<!-- farol:painel {quebrado -->") == {"v": 1, "pessoas": {}}
    assert painel.carregar(None)["pessoas"] == {}


def test_limites_de_prs_por_pessoa_e_de_pessoas():
    dados = painel.carregar(None)
    for n in range(1, 50):
        painel.registrar(dados, "ana", n, {"E722"})
    assert len(dados["pessoas"]["ana"]) == painel.MAX_PRS_POR_PESSOA
    assert "1" not in dados["pessoas"]["ana"] and "49" in dados["pessoas"]["ana"]
    for i in range(80):
        painel.registrar(dados, f"pessoa{i}", 1, set())
    assert len(dados["pessoas"]) == painel.MAX_PESSOAS


def test_texto_para_a_review_so_com_historico():
    assert painel.para_a_review(painel.resumir({"1": ["E722"]})) is None
    texto = painel.para_a_review(painel.resumir({"1": ["E722"], "2": ["E722"]}))
    assert "Seu progresso" in texto and "Se repete" in texto and "licoes/E722.html" in texto


class ApiDeIssues:
    repo = "dono/repo"

    def __init__(self, issue=None, erro=None):
        self.issue, self.erro = issue, erro
        self.criadas, self.alteradas = [], []

    def paginar(self, caminho):
        if self.erro:
            raise self.erro
        if "/issues?" in caminho:
            assert "labels=farol" in caminho
            return [self.issue] if self.issue else [{"number": 99, "body": "x", "pull_request": {}}]
        return []

    def enviar(self, caminho, corpo):
        self.criadas.append((caminho, corpo))
        return {}

    def alterar(self, caminho, corpo):
        self.alteradas.append((caminho, corpo))
        return {}


def test_atualizar_cria_a_issue_na_primeira_vez_e_edita_depois():
    api = ApiDeIssues()
    resumo = painel.atualizar(api, 1, "ana", {"E722"})
    assert resumo.n_prs == 1
    ((caminho, corpo),) = api.criadas
    assert caminho == "/repos/dono/repo/issues" and corpo["labels"] == ["farol"]
    assert api.alteradas == []

    api2 = ApiDeIssues(issue={"number": 5, "body": corpo["body"]})
    resumo = painel.atualizar(api2, 2, "ana", {"E722"})
    assert resumo.repetem == {"E722": 2}
    assert api2.criadas == [] and api2.alteradas[0][0] == "/repos/dono/repo/issues/5"
    assert "ana" in api2.alteradas[0][1]["body"]


def test_atualizar_nao_derruba_a_revisao_se_o_github_recusar(capsys):
    assert (
        painel.atualizar(ApiDeIssues(erro=GitHubError(403, "sem permissão")), 1, "ana", {"A"})
        is None
    )
    assert "não consegui atualizar o painel" in capsys.readouterr().out


def test_corpo_da_revisao_traz_o_progresso():
    rev = montar([])
    assert "Seu progresso" in corpo_da_revisao(
        rev, [], "a" * 40, "**Seu progresso neste repositório**"
    )
    assert "Seu progresso" not in corpo_da_revisao(rev, [], "a" * 40)


# --- integração com a Action -------------------------------------------------------------------


class ApiDaAction(ApiDeIssues):
    def paginar(self, caminho):
        if caminho.endswith("/files"):
            patch = "@@ -0,0 +1,5 @@\n" + "+x\n" * 5
            return [{"filename": "a.py", "status": "added", "patch": patch}]
        return super().paginar(caminho)

    def texto_do_arquivo(self, repo, caminho, ref):
        return FONTE

    def enviar(self, caminho, corpo):
        (
            self.criadas if caminho.endswith("/issues") else self.__dict__.setdefault("reviews", [])
        ).append((caminho, corpo))
        return {}


def evento(login="ana", tipo="User", repo="dono/repo"):
    return {
        "pull_request": {
            "number": 4,
            "user": {"login": login, "type": tipo},
            "head": {"sha": "a" * 40, "repo": {"full_name": repo}},
        }
    }


def test_action_com_painel_registra_as_regras_do_pr():
    api = ApiDaAction()
    executar(api, evento(), None, painel=True)
    assert len(api.criadas) == 1
    assert painel.carregar(api.criadas[0][1]["body"])["pessoas"] == {"ana": {"4": ["B006", "F401"]}}


def test_action_sem_painel_nao_mexe_em_issues():
    api = ApiDaAction()
    executar(api, evento(), None)
    assert api.criadas == [] and api.alteradas == []


def test_painel_ignora_bot_e_fork():
    bot = ApiDaAction()
    executar(bot, evento("dependabot[bot]", "Bot"), None, painel=True)
    assert bot.criadas == []
    fork = ApiDaAction()
    executar(fork, evento(repo="outra/repo"), None, painel=True)
    assert fork.criadas == [] and fork.alteradas == []
