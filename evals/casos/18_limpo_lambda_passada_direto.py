# farol-esperado: nenhum
ordenados = sorted([3, 1, 2], key=lambda n: -n)


def testar_a():
    assert ordenados == [3, 2, 1]


def testar_b():
    assert ordenados[0] == 3
