# src/database/connection.py
import sqlite3
from contextlib import contextmanager
import os

# Define o caminho padrão do banco de dados na raiz do projeto
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../database.db"))

@contextmanager
def get_db_connection(db_path: str = DB_PATH):
    """
    Context Manager que abre uma conexão com o banco de dados,
    configura o retorno de linhas como dicionários e garante o fechamento
    seguro da conexão, executando rollback em caso de falhas.
    """
    conn = sqlite3.connect(db_path, timeout=10.0) # Timeout evita travamento em requisições concorrentes
    
    # Configuração crucial para APIs: transforma tuplas do SQL em objetos fáceis de ler
    # Ex: em vez de acessar row[0], você acessa row['aliquota_nominal'] -> Perfeito para gerar JSONs e gráficos
    conn.row_factory = sqlite3.Row
    
    try:
        # Ativa o modo WAL para alta performance e suporte a dashboards em tempo real
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