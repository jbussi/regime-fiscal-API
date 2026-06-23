import sqlite3
from contextlib import contextmanager
import os

# 1. Encontra a pasta onde este arquivo está (src/database)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))

# 2. Define o caminho definitivo na raiz do projeto
DB_PATH = os.path.join(BASE_DIR, "database.db")

@contextmanager
def get_db_connection(db_path: str = DB_PATH):
    """
    Context Manager que abre uma conexão com o banco de dados,
    configura o retorno de linhas como dicionários e garante o fechamento
    seguro da conexão, executando rollback em caso de falhas.
    """
    conn = sqlite3.connect(db_path, timeout=10.0) # Timeout evita travamento
    
    # Configuração crucial para APIs: transforma tuplas do SQL em objetos fáceis de ler (row['coluna'])
    conn.row_factory = sqlite3.Row
    
    try:
        # Ativa o modo WAL para alta performance e concorrência simultânea
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;") # Garante integridade referencial
        
        yield conn
        
        # Se o bloco 'with' terminar sem exceções, commita as alterações
        conn.commit()
    except Exception as e:
        # Se qualquer query falhar, desfaz as alterações para não corromper o banco
        conn.rollback()
        raise e
    finally:
        # Garante o fechamento da conexão de forma absoluta
        conn.close()