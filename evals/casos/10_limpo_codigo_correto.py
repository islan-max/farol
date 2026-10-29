# farol-esperado: nenhum
def processar(itens, extras=None):
    extras = [] if extras is None else extras
    for item in itens:
        try:
            if item.valor is None:
                continue
            extras.append(item.valor)
        except AttributeError:
            continue
    return extras
