"""Interpreta o diff de um PR: quais linhas do lado novo mudaram e quais arquivos revisar."""

import re
from dataclasses import dataclass, field
from fnmatch import fnmatch

MAX_FILES = 40

# Gerados, binários ou vendorizados: revisá-los só produz ruído.
IGNORED = (
    "*.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "poetry.lock",
    "uv.lock",
    "go.sum",
    "*.min.js",
    "*.min.css",
    "*.map",
    "*.snap",
    "node_modules/*",
    "vendor/*",
    "dist/*",
    "build/*",
    "*/node_modules/*",
    "*/vendor/*",
    "*/dist/*",
)

_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


@dataclass
class FileDiff:
    path: str
    added: set[int] = field(default_factory=set)  # nº das linhas adicionadas no arquivo novo


@dataclass
class ReviewInput:
    files: list[FileDiff]
    skipped: list[tuple[str, str]]  # (caminho, motivo)


def parse_patch(path: str, patch: str) -> FileDiff:
    """Lê um patch unificado. Só as linhas adicionadas (lado novo) contam como alteradas."""
    diff = FileDiff(path)
    new_line = 0
    in_hunk = False
    for raw in patch.replace("\r\n", "\n").split("\n"):
        header = _HUNK.match(raw)
        if header:
            new_line = int(header.group(1))
            in_hunk = True
            continue
        if not in_hunk or raw.startswith("\\"):  # "\ No newline at end of file"
            continue
        marker = raw[:1]
        if marker == "+":
            diff.added.add(new_line)
            new_line += 1
        elif marker == " ":  # contexto; uma linha em branco do arquivo chega como " "
            new_line += 1
    return diff


def _ignored(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return any(fnmatch(path, pat) or fnmatch(name, pat) for pat in IGNORED)


def build_input(pr_files: list[dict], *, max_files: int = MAX_FILES) -> ReviewInput:
    """Seleciona o que revisar. Tudo que ficar de fora é registrado com o motivo.

    `pr_files` segue o formato de `GET /repos/{o}/{r}/pulls/{n}/files`.
    """
    files: list[FileDiff] = []
    skipped: list[tuple[str, str]] = []
    for item in pr_files:
        path = item["filename"]
        if item.get("status") == "removed":
            skipped.append((path, "arquivo removido"))
        elif _ignored(path):
            skipped.append((path, "ignorado por padrão (gerado, vendorizado ou lockfile)"))
        elif not item.get("patch"):
            skipped.append((path, "sem diff textual (binário ou grande demais para o GitHub)"))
        elif len(files) >= max_files:
            skipped.append((path, f"além do limite de {max_files} arquivos"))
        else:
            files.append(parse_patch(path, item["patch"]))
    return ReviewInput(files, skipped)


def split_git_diff(text: str) -> list[dict]:
    """Divide a saída de `git diff` em itens no formato de `build_input`.

    shortcut: caminhos que o git coloca entre aspas (acentos, espaços) não são decodificados,
    então esses arquivos ficam de fora; upgrade: tratar aspas quando alguém reclamar.
    """
    itens: list[dict] = []
    atual: dict | None = None
    for linha in text.replace("\r\n", "\n").split("\n"):
        if linha.startswith("diff --git "):
            atual = {"filename": None, "status": "modified", "patch": ""}
            itens.append(atual)
        elif atual is None:
            continue
        elif linha.startswith("+++ ") and not atual["patch"]:
            alvo = linha[4:]
            if alvo == "/dev/null":
                atual["status"] = "removed"
            elif alvo.startswith("b/"):
                atual["filename"] = alvo[2:]
        elif linha.startswith("@@ ") or atual["patch"]:
            atual["patch"] += linha + "\n"
    return [i for i in itens if i["filename"]]
