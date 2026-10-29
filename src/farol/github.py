"""Cliente mínimo da API REST do GitHub (só biblioteca padrão, sem dependências)."""

import json
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"
TIMEOUT_S = 30


class GitHubError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(f"GitHub respondeu {status}: {message[:200]}")
        self.status = status


class Api:
    def __init__(self, token: str, repo: str, base: str = API):
        self.token, self.repo, self.base = token, repo, base

    def _pedir(self, metodo: str, caminho: str, corpo: dict | None, accept: str) -> bytes:
        dados = json.dumps(corpo).encode() if corpo is not None else None
        req = urllib.request.Request(  # noqa: S310 - base é https://api.github.com
            self.base + caminho,
            data=dados,
            method=metodo,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": accept,
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "farol",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resposta:  # noqa: S310
                return resposta.read()
        except urllib.error.HTTPError as erro:
            raise GitHubError(erro.code, erro.read().decode("utf-8", "replace")) from erro
        except urllib.error.URLError as erro:
            raise GitHubError(0, str(erro.reason)) from erro

    def json(self, caminho: str) -> dict | list:
        return json.loads(self._pedir("GET", caminho, None, "application/vnd.github+json"))

    def paginar(self, caminho: str, limite_paginas: int = 30) -> list:
        itens: list = []
        sep = "&" if "?" in caminho else "?"
        for pagina in range(1, limite_paginas + 1):
            parte = self.json(f"{caminho}{sep}per_page=100&page={pagina}")
            itens += parte
            if len(parte) < 100:
                break
        return itens

    def texto_do_arquivo(self, repo: str, caminho: str, ref: str) -> str:
        url = f"/repos/{repo}/contents/{urllib.parse.quote(caminho)}?ref={ref}"
        return self._pedir("GET", url, None, "application/vnd.github.raw").decode("utf-8")

    def enviar(self, caminho: str, corpo: dict) -> dict:
        return json.loads(self._pedir("POST", caminho, corpo, "application/vnd.github+json"))
