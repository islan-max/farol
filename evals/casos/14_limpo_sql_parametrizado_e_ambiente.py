# farol-esperado: nenhum
import logging
import os
import sqlite3


def buscar(nome):
    senha = os.environ["DB_SENHA"]
    with sqlite3.connect(os.environ["DB_ARQUIVO"]) as conexao:
        try:
            return conexao.execute("SELECT * FROM usuarios WHERE nome = ?", (nome,)).fetchall()
        except sqlite3.Error:
            logging.exception("consulta falhou (%d)", len(senha))
            return []
