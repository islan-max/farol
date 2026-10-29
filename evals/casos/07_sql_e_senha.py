# farol-esperado: S105,S608
def buscar(cursor, nome):
    password = "abc123"
    cursor.execute(f"SELECT * FROM usuarios WHERE nome = '{nome}'", password)
    return cursor.fetchall()
