"""IA local opcional (Ollama): escreve uma nota curta ligando a lição ao trecho da pessoa.

Regras que não mudam:
- A IA **nunca cria nem remove** apontamento: a regra vem do ruff/ESLint e a lição é escrita à mão.
  Ela só recebe um apontamento já feito e devolve uma frase para ele.
- Tudo que ela devolve passa por `limpar`, é marcado como "IA local, pode errar" e é descartado em
  silêncio se algo der errado (servidor fora do ar, tempo esgotado, resposta estranha).
- Fala só com o servidor local (padrão `127.0.0.1:11434`); o código revisado não sai da máquina.
"""

import json
import re
import time
import urllib.error
import urllib.request

from farol.achados import Achado
from farol.licoes import Licao

MODELO_PADRAO = "qwen2.5-coder:1.5b"
HOST_PADRAO = "http://127.0.0.1:11434"
TIMEOUT_S = 90
MAX_CHARS = 420
CONTEXTO_LINHAS = 2
SISTEMA = (
    "Você é um mentor de programação. Responda sempre em português do Brasil, em no máximo duas "
    "frases curtas, sem markdown, sem listas e sem blocos de código. Baseie-se só nas informações "
    "dadas e não invente problemas novos."
)


def trecho_em_volta(fonte: str, linha: int, contexto: int = CONTEXTO_LINHAS) -> str:
    linhas = fonte.splitlines()
    return "\n".join(linhas[max(0, linha - 1 - contexto) : linha + contexto])


def pedido(modelo: str, achado: Achado, lc: Licao, trecho: str) -> dict:
    """O texto enviado ao modelo: a lição e a mensagem exata da ferramenta ancoram a resposta."""
    usuario = (
        f"Regra: {lc.titulo}\nO que é: {lc.o_que_e}\nPor que importa: {lc.por_que_importa}\n"
        f"Como corrigir: {lc.como_corrigir}\n"
        f"A ferramenta apontou (linha {achado.line}): {achado.mensagem}\n\n"
        f"Trecho da pessoa:\n{trecho}\n\n"
        "Escreva 2 frases curtas dirigidas a quem escreveu este trecho: o que está errado "
        "exatamente neste código (use os nomes do trecho) e qual mudança fazer."
    )
    return {
        "model": modelo,
        "stream": False,
        "keep_alive": "10m",
        "options": {"temperature": 0.1, "num_predict": 140, "num_ctx": 2048},
        "messages": [
            {"role": "system", "content": SISTEMA},
            {"role": "user", "content": usuario},
        ],
    }


def limpar(texto: str) -> str | None:
    """Deixa só texto simples. Devolve None se a resposta não presta."""
    t = texto.strip()
    if "```" in t:
        return None  # a nota não traz código
    t = re.sub(r"<[^>]*>?", "", t)  # sem HTML nem comentário HTML (não dá para forjar marcadores)
    t = re.sub(r"!?\[[^\]]*\]\([^)]*\)", "", t)  # sem links nem imagens
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"^[#>*\-\s]+", "", t)  # sem título, citação ou lista no começo
    t = t.replace("@", "@​")  # não menciona ninguém
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) < 20:
        return None
    if len(t) > MAX_CHARS:
        corte = t[:MAX_CHARS]
        ponto = max(corte.rfind(". "), corte.rfind("! "), corte.rfind("? "))
        t = corte[: ponto + 1] if ponto > 80 else corte.rstrip() + "…"
    return t


class Ollama:
    def __init__(
        self,
        modelo: str = MODELO_PADRAO,
        host: str = HOST_PADRAO,
        orcamento_s: float = 240.0,
        timeout_s: float = TIMEOUT_S,
    ):
        self.modelo, self.host, self.timeout_s = modelo, host.rstrip("/"), timeout_s
        self.prazo = time.monotonic() + orcamento_s
        self.falhas = 0

    def disponivel(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self.host}/api/tags", timeout=3) as r:  # noqa: S310
                nomes = {m["name"] for m in json.load(r).get("models", [])}
        except (OSError, ValueError, KeyError):
            return False
        return self.modelo in nomes or f"{self.modelo}:latest" in nomes

    def nota(self, achado: Achado, lc: Licao | None, fonte: str) -> str | None:
        """Nota para um apontamento, ou None (nunca levanta erro)."""
        if lc is None or self.falhas >= 2 or time.monotonic() > self.prazo:
            return None
        corpo = json.dumps(pedido(self.modelo, achado, lc, trecho_em_volta(fonte, achado.line)))
        req = urllib.request.Request(  # noqa: S310 - host local, definido por quem roda o Farol
            f"{self.host}/api/chat",
            data=corpo.encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as r:  # noqa: S310
                texto = json.load(r)["message"]["content"]
        except (OSError, ValueError, KeyError, TypeError):
            self.falhas += 1  # duas falhas seguidas e o Farol desiste da IA nesta execução
            return None
        self.falhas = 0
        return limpar(texto)


def anotar(rev, fontes: dict[str, str], cliente: Ollama) -> int:
    """Põe a nota nos comentários por linha (não mexe em quais apontamentos existem)."""
    n = 0
    for c in rev.inline:
        texto = cliente.nota(c.achado, c.licao, fontes.get(c.achado.path, ""))
        if texto:
            c.nota, c.modelo = texto, cliente.modelo
            n += 1
    return n
