# farol-esperado: nenhum
def repetir(itens):
    for _ in range(3):
        print("oi")
    for chave, _ in itens.items():
        print(chave)
    for i, nome in enumerate(itens):
        print(i, nome)
