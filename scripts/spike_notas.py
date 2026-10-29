"""Medição descartável: gera notas de IA com o código real do Farol (farol.ia) e compara modelos.

Casos: o `antes` de cada lição e os achados dos casos de avaliação com problema. A saída é lida
por uma pessoa, que classifica cada nota (não há nota automática de qualidade).
"""

import os
import subprocess
import time
from pathlib import Path

from farol.analise import analisar
from farol.ia import Ollama
from farol.licoes import licao, todas

MODELOS = ["qwen2.5-coder:1.5b", "qwen2.5-coder:7b"]


def usado_mb() -> int:
    saida = subprocess.run(
        "free -m | awk '/Mem:/ {print $3}'", shell=True, capture_output=True, text=True
    ).stdout
    return int(saida)


casos = []
for (ferramenta, codigo), lc in sorted(todas().items()):
    ext = lc.extensao or ("py" if ferramenta == "ruff" else "js")
    fonte = lc.antes
    achado = next((a for a in analisar(f"x.{ext}", fonte) or [] if a.codigo == codigo), None)
    if achado:
        casos.append((f"licao {codigo}", achado, lc, fonte))
for arq in sorted(Path("evals/casos").glob("*.py")):
    fonte = arq.read_text(encoding="utf-8")
    if "farol-esperado: nenhum" in fonte.splitlines()[0]:
        continue
    vistos = set()
    for achado in analisar(arq.name, fonte) or []:
        lc = licao("ruff", achado.codigo)
        if lc and achado.codigo not in vistos:
            vistos.add(achado.codigo)
            casos.append((f"eval {arq.stem}", achado, lc, fonte))
print(f"{len(casos)} casos", flush=True)

resumo = ["# Notas da IA local por modelo", ""]
for modelo in MODELOS:
    subprocess.run(["ollama", "pull", modelo], check=True, capture_output=True)
    cliente = Ollama(modelo, orcamento_s=3600, timeout_s=300)
    assert cliente.disponivel(), modelo
    base = None
    tempos, descartadas = [], 0
    print(f"\n########## {modelo}", flush=True)
    resumo += [f"## {modelo}", ""]
    for origem, achado, lc, fonte in casos:
        t0 = time.time()
        nota = cliente.nota(achado, lc, fonte)
        dt = time.time() - t0
        if base is None:
            base = usado_mb()  # já com o modelo carregado pela primeira chamada
        tempos.append(dt)
        descartadas += nota is None
        linha = (
            f"[{origem}] {achado.codigo} linha {achado.line} | {dt:.1f}s | {nota or '(DESCARTADA)'}"
        )
        print(linha, flush=True)
        resumo.append(f"- {linha}")
    medio = sum(tempos) / len(tempos)
    rodape = (
        f"MEDIA {medio:.1f}s por nota, max {max(tempos):.1f}s, {descartadas} descartadas, "
        f"memoria usada com o modelo carregado: {usado_mb()} MB (total do runner)"
    )
    print(rodape, flush=True)
    resumo += ["", rodape, ""]
    subprocess.run(["ollama", "stop", modelo], capture_output=True)

destino = os.environ.get("GITHUB_STEP_SUMMARY")
if destino:
    Path(destino).write_text("\n".join(resumo), encoding="utf-8")
