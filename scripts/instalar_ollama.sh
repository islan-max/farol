#!/usr/bin/env bash
# Instala o Ollama em um runner Linux x64 do GitHub, sobe o servidor e baixa o modelo.
# Uso: instalar_ollama.sh <modelo>   (ex.: qwen2.5-coder:1.5b)
# O pacote é conferido com o sha256 publicado na própria release; versão fixada abaixo.
set -euo pipefail

MODELO="${1:?informe o modelo}"
OLLAMA_VERSAO="v0.40.13"
BASE="https://github.com/ollama/ollama/releases/download/${OLLAMA_VERSAO}"
PACOTE="ollama-linux-amd64.tar.zst"
DESTINO="${RUNNER_TEMP:-/tmp}/ollama"

mkdir -p "$DESTINO" && cd "$DESTINO"
curl -fsSL -o "$PACOTE" "${BASE}/${PACOTE}"
curl -fsSL -o sha256sum.txt "${BASE}/sha256sum.txt"
grep " \./${PACOTE}\$" sha256sum.txt | sed 's# \./# #' | sha256sum -c -
tar --zstd -xf "$PACOTE"

export PATH="$DESTINO/bin:$PATH"
(ollama serve > "$DESTINO/ollama.log" 2>&1 &)
for _ in $(seq 1 30); do
  curl -fs http://127.0.0.1:11434/api/version > /dev/null && break
  sleep 1
done
ollama pull "$MODELO"
echo "Ollama ${OLLAMA_VERSAO} pronto com ${MODELO}."
