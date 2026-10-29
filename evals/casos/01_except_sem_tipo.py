# farol-esperado: E722
def carregar(caminho):
    try:
        with open(caminho, encoding="utf-8") as arq:
            return arq.read()
    except:
        return ""
