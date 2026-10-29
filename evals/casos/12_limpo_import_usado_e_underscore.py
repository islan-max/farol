# farol-esperado: nenhum
import sys


def primeiro_e_resto(valores):
    primeiro, *_ = valores
    print(sys.argv, primeiro)
    return primeiro
