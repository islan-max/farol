# farol-esperado: nenhum
import requests


def dobro(x):
    return x * 2


def registrar(item, vistos):
    try:
        if item not in vistos:
            vistos.append(dobro(item))
    except TypeError as erro:
        raise ValueError("item inválido") from erro


def baixar(url):
    return requests.get(url, timeout=10).text
