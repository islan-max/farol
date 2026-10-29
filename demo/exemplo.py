import os
import json


def adicionar(item, itens=[]):
    itens.append(item)
    return itens


def carregar(caminho):
    password = "abc123"
    try:
        return open(caminho).read()
    except:
        pass


def a(x):
    if x == None:
        return f"vazio"
    l = x
    return l
