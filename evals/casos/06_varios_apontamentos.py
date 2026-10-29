# farol-esperado: B006,E711,E722
def processar(itens, extras=[]):
    for item in itens:
        try:
            if item.valor == None:
                continue
            extras.append(item.valor)
        except:
            pass
    return extras
