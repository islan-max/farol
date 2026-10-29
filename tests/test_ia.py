import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from farol import ia
from farol.achados import Achado
from farol.action import corpo_da_revisao, executar
from farol.cli import main
from farol.comentarios import corpo
from farol.licoes import licao
from farol.revisao import montar

LC = licao("ruff", "E722")
ACHADO = Achado("a.py", 4, "ruff", "E722", "Do not use bare `except`", None)
FONTE = (
    "def carregar(caminho):\n    try:\n        return open(caminho).read()\n"
    '    except:\n        return ""\n'
)
NOTA = "O `except:` da função carregar captura até Ctrl+C; nomeie o erro, como FileNotFoundError."


class OllamaFalso(BaseHTTPRequestHandler):
    resposta = {"message": {"content": NOTA}}
    pedidos: list = []
    modelos = ["qwen2.5-coder:1.5b"]
    demora = 0.0
    status = 200

    def log_message(self, *_):
        pass

    def do_GET(self):
        corpo_ = json.dumps({"models": [{"name": m} for m in self.modelos]}).encode()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(corpo_)

    def do_POST(self):
        tamanho = int(self.headers["Content-Length"])
        type(self).pedidos.append(json.loads(self.rfile.read(tamanho)))
        time.sleep(type(self).demora)
        self.send_response(type(self).status)
        self.end_headers()
        self.wfile.write(json.dumps(type(self).resposta).encode())


@pytest.fixture
def servidor():
    OllamaFalso.pedidos = []
    OllamaFalso.resposta = {"message": {"content": NOTA}}
    OllamaFalso.demora, OllamaFalso.status = 0.0, 200
    http = HTTPServer(("127.0.0.1", 0), OllamaFalso)
    threading.Thread(target=http.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{http.server_port}"
    http.shutdown()


def test_nota_usa_a_mensagem_da_ferramenta_a_licao_e_o_trecho_no_pedido(servidor):
    cliente = ia.Ollama(host=servidor)
    assert cliente.disponivel()
    assert cliente.nota(ACHADO, LC, FONTE) == NOTA
    (pedido,) = OllamaFalso.pedidos
    usuario = pedido["messages"][1]["content"]
    assert "Do not use bare `except`" in usuario and LC.por_que_importa in usuario
    assert "    except:" in usuario and "return open(caminho)" in usuario  # a linha e as vizinhas
    assert pedido["stream"] is False and pedido["options"]["temperature"] <= 0.2


def test_modelo_ausente_ou_servidor_fora_do_ar_nao_esta_disponivel(servidor):
    assert not ia.Ollama(modelo="outro:7b", host=servidor).disponivel()
    assert not ia.Ollama(host="http://127.0.0.1:9").disponivel()


@pytest.mark.parametrize(
    "bruto",
    [
        "x",
        "```python\nprint(1)\n```\nIsso aqui é uma resposta com bloco de código.",
        "",
    ],
)
def test_resposta_estranha_e_descartada(bruto):
    assert ia.limpar(bruto) is None


def test_limpar_tira_html_marcador_link_mencao_e_lista():
    sujo = (
        "- <!-- farol:revisao:abc --> Veja [aqui](http://x.dev) https://y.dev "
        "e fale com @alguem sobre o `except:`."
    )
    limpo = ia.limpar(sujo)
    assert "<" not in limpo and "farol:revisao" not in limpo.replace("farol", "")
    assert "http" not in limpo and "](" not in limpo
    assert "@alguem" not in limpo and "@​alguem" in limpo
    assert "`except:`" in limpo


def test_limpar_corta_no_fim_de_uma_frase():
    longa = " ".join(f"Frase número {i} do texto." for i in range(60))
    limpo = ia.limpar(longa)
    assert len(limpo) <= ia.MAX_CHARS and limpo.endswith(".")


@pytest.mark.parametrize("falha", ["status", "json", "sem_campo"])
def test_falhas_nunca_viram_erro_e_duas_seguidas_desligam_a_ia(servidor, falha):
    if falha == "status":
        OllamaFalso.status = 500
    elif falha == "json":
        OllamaFalso.resposta = "isso nao e um objeto"
    else:
        OllamaFalso.resposta = {"outra": 1}
    cliente = ia.Ollama(host=servidor)
    assert cliente.nota(ACHADO, LC, FONTE) is None
    assert cliente.nota(ACHADO, LC, FONTE) is None
    OllamaFalso.status, OllamaFalso.resposta = 200, {"message": {"content": NOTA}}
    assert cliente.nota(ACHADO, LC, FONTE) is None  # já desistiu nesta execução


def test_tempo_esgotado_devolve_none(servidor):
    OllamaFalso.demora = 1.5
    assert ia.Ollama(host=servidor, timeout_s=0.3).nota(ACHADO, LC, FONTE) is None


def test_orcamento_de_tempo_acabou_nao_chama_o_servidor(servidor):
    cliente = ia.Ollama(host=servidor, orcamento_s=-1)
    assert cliente.nota(ACHADO, LC, FONTE) is None and OllamaFalso.pedidos == []


def test_sem_licao_nao_ha_nota():
    sem_licao = Achado("a.py", 1, "ruff", "Z999", "msg", None)
    assert ia.Ollama().nota(sem_licao, None, FONTE) is None


def test_a_ia_so_acrescenta_nota_e_nao_muda_quais_apontamentos_existem(servidor):
    rev = montar([ACHADO, Achado("a.py", 3, "ruff", "F401", "m", None)])
    antes = [(c.achado.codigo, c.achado.line) for c in rev.inline]
    assert ia.anotar(rev, {"a.py": FONTE}, ia.Ollama(host=servidor)) == 2
    assert [(c.achado.codigo, c.achado.line) for c in rev.inline] == antes
    assert all(c.nota == NOTA for c in rev.inline)


def test_comentario_mostra_a_nota_com_aviso_e_sem_nota_fica_igual(servidor):
    c = montar([ACHADO]).inline[0]
    sem = corpo(c)
    assert "No seu código" not in sem
    ia.anotar(montar([ACHADO]), {"a.py": FONTE}, ia.Ollama(host=servidor))
    c.nota, c.modelo = NOTA, "qwen2.5-coder:1.5b"
    com = corpo(c)
    assert "> **No seu código** (nota da IA local `qwen2.5-coder:1.5b`, pode errar)" in com
    assert com.replace(com.split("\n\n", 2)[1], "").count("Por que importa") == 1
    assert com.splitlines()[0] == sem.splitlines()[0]  # o título continua em primeiro


def test_review_avisa_no_corpo_quando_ha_nota_de_ia():
    rev = montar([ACHADO])
    rev.inline[0].nota, rev.inline[0].modelo = NOTA, "qwen2.5-coder:1.5b"
    assert "foram escritas por uma IA local" in corpo_da_revisao(rev, [], "a" * 40)
    rev.inline[0].nota = None
    assert "IA local" not in corpo_da_revisao(rev, [], "a" * 40)


class ApiFalsa:
    repo = "dono/repo"

    def __init__(self):
        self.enviados = []

    def paginar(self, caminho):
        if caminho.endswith("/files"):
            return [
                {
                    "filename": "a.py",
                    "status": "added",
                    "patch": "@@ -0,0 +1,5 @@\n+x\n+x\n+x\n+x\n+x",
                }
            ]
        return []

    def texto_do_arquivo(self, repo, caminho, ref):
        return FONTE

    def enviar(self, caminho, corpo_):
        self.enviados.append(corpo_)


EVENTO = {
    "pull_request": {"number": 1, "head": {"sha": "a" * 40, "repo": {"full_name": "dono/repo"}}}
}


def test_action_com_ia_publica_a_nota_e_sem_ia_nao(servidor):
    com = ApiFalsa()
    executar(com, EVENTO, None, ia=ia.Ollama(host=servidor))
    assert NOTA in com.enviados[0]["comments"][0]["body"]
    sem = ApiFalsa()
    executar(sem, EVENTO, None)
    assert "No seu código" not in sem.enviados[0]["comments"][0]["body"]


def test_action_com_ia_fora_do_ar_publica_a_licao_normalmente():
    api = ApiFalsa()
    executar(api, EVENTO, None, ia=ia.Ollama(host="http://127.0.0.1:9", timeout_s=1))
    corpo_ = api.enviados[0]["comments"][0]["body"]
    assert "Por que importa" in corpo_ and "No seu código" not in corpo_


def test_cli_com_ia_mostra_a_nota_e_sem_servidor_avisa_e_segue(
    servidor, tmp_path, monkeypatch, capsys
):
    (tmp_path / "a.py").write_text(FONTE, encoding="utf-8")
    diff = "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -0,0 +1,5 @@\n" + "".join(
        f"+{linha}\n" for linha in FONTE.splitlines()
    )
    (tmp_path / "m.diff").write_text(diff, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert main(["revisar", "--diff", "m.diff", "--ia", "--ollama", servidor]) == 0
    assert NOTA in capsys.readouterr().out
    assert main(["revisar", "--diff", "m.diff", "--ia", "--ollama", "http://127.0.0.1:9"]) == 0
    saida = capsys.readouterr()
    assert "sigo sem IA" in saida.err and "Por que importa" in saida.out
