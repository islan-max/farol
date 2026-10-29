# farol-esperado: B904,E713,E731
dobro = lambda x: x * 2


def registrar(item, vistos):
    try:
        if not item in vistos:
            vistos.append(dobro(item))
    except TypeError:
        raise ValueError("item inválido")
