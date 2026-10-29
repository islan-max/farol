# farol-esperado: S110
def limpar(caminho):
    try:
        caminho.unlink()
    except Exception:
        pass
