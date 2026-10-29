"""Medição descartável: compara modelos do Ollama no runner (tempo, memória e qualidade)."""

import json
import subprocess
import time
import urllib.request


def usado() -> int:
    saida = subprocess.run(
        "free -m | awk '/Mem:/ {print $3}'", shell=True, capture_output=True, text=True
    ).stdout
    return int(saida)


SISTEMA = (
    "Você é um mentor de programação. Responda sempre em português do Brasil, em no máximo "
    "duas frases curtas, sem markdown, sem listas e sem blocos de código. Baseie-se só nas "
    "informações dadas e não invente problemas novos."
)
CASOS = [
    (
        "`except:` sem tipo captura erro demais",
        "Captura qualquer erro, inclusive Ctrl+C.",
        "Quando algo dá errado por um motivo inesperado o programa segue em silêncio.",
        "Nomeie o erro que você espera tratar.",
        4,
        "Do not use bare `except`",
        'def carregar(caminho):\n    try:\n        return open(caminho).read()\n    except:\n        return ""',
    ),
    (
        "Valor padrão mutável em argumento de função",
        "A lista padrão é criada uma única vez, na definição da função.",
        "Todas as chamadas compartilham o mesmo objeto.",
        "Use None como padrão e crie a lista dentro da função.",
        1,
        "Do not use mutable data structures for argument defaults",
        "def marcar(tarefa, feitas=[]):\n    feitas.append(tarefa)\n    return feitas",
    ),
    (
        "SQL montado juntando texto abre brecha para injeção de SQL",
        "A consulta é construída colando valores no texto SQL.",
        "O valor pode conter SQL e mudar o que a consulta faz.",
        "Use parâmetros: o driver envia o valor separado do SQL.",
        2,
        "Possible SQL injection vector through string-based query construction",
        "def buscar(cursor, nome):\n    cursor.execute(f\"SELECT * FROM usuarios WHERE nome = '{nome}'\")\n    return cursor.fetchall()",
    ),
    (
        "Não use eval: ele executa texto como código",
        "eval executa um texto como código JavaScript.",
        "Quem controla o texto passa a executar código na sua página.",
        "Para ler dados, use JSON.parse(texto).",
        2,
        "`eval` can be harmful.",
        "function ler(texto) {\n  return eval('(' + texto + ')');\n}",
    ),
    (
        "Variável criada e nunca usada",
        "Você guarda um valor em uma variável e nenhuma linha a lê depois.",
        "Quase sempre é um resultado que você esqueceu de usar.",
        "Use o valor ou apague a variável.",
        2,
        "Local variable `total` is assigned to but never used",
        "def total_com_frete(precos, frete):\n    total = sum(precos) + frete\n    return sum(precos)",
    ),
]

for modelo in ["qwen2.5-coder:1.5b", "qwen2.5-coder:3b", "qwen2.5-coder:7b"]:
    t0 = time.time()
    subprocess.run(["ollama", "pull", modelo], check=True, capture_output=True)
    print(f"\n########## {modelo}: pull {time.time() - t0:.0f}s", flush=True)
    base = usado()
    for titulo, o_que, por_que, como, linha, msg, codigo in CASOS:
        pedido = {
            "model": modelo,
            "stream": False,
            "keep_alive": "5m",
            "options": {"temperature": 0.1, "num_predict": 140, "num_ctx": 2048},
            "messages": [
                {"role": "system", "content": SISTEMA},
                {
                    "role": "user",
                    "content": (
                        f"Regra: {titulo}\nO que é: {o_que}\nPor que importa: {por_que}\n"
                        f"Como corrigir: {como}\nA ferramenta apontou (linha {linha}): {msg}\n\n"
                        f"Trecho da pessoa:\n{codigo}\n\n"
                        "Escreva 2 frases curtas dirigidas a quem escreveu este trecho: o que está "
                        "errado exatamente neste código (use os nomes do trecho) e qual mudança fazer."
                    ),
                },
            ],
        }
        t1 = time.time()
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/chat",
            data=json.dumps(pedido).encode(),
            headers={"Content-Type": "application/json"},
        )
        r = json.load(urllib.request.urlopen(req, timeout=600))
        n = r.get("eval_count", 0)
        d = r.get("eval_duration", 1) / 1e9
        print(f"--- {titulo} | {time.time() - t1:.1f}s | {n} tokens | {n / max(d, 0.001):.1f} tok/s")
        print(r["message"]["content"].strip(), flush=True)
    print(f"MEMORIA usada a mais com {modelo} carregado: {usado() - base} MB", flush=True)
    subprocess.run(["ollama", "stop", modelo], capture_output=True)
