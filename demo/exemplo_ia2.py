def marcar(tarefa, feitas=[]):
    feitas.append(tarefa)
    return feitas


def total_com_frete(precos, frete):
    total = sum(precos) + frete
    return sum(precos)


def carregar(caminho):
    try:
        return open(caminho).read()
    except:
        return ""
# rerun 1793281306
