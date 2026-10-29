# farol-esperado: nenhum
def classificar(idade, ativo):
    if idade == 18 and ativo:
        return "recém-adulto"
    if ativo is False:
        return "inativo"
    return "outro"
