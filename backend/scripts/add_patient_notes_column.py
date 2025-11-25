"""Script de migração simples para adicionar a coluna `notes` na tabela `patient`.
Uso: execute com o mesmo Python/venv do projeto.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "agendamentotcc.db"

if not DB_PATH.exists():
    print(f"Arquivo de DB não encontrado: {DB_PATH}")
    raise SystemExit(1)

conn = sqlite3.connect(str(DB_PATH))
cur = conn.cursor()

# Verifica se a coluna 'notes' já existe
cur.execute("PRAGMA table_info(patient);")
cols = [row[1] for row in cur.fetchall()]
if 'notes' in cols:
    print('Coluna "notes" já existe em patient. Nada a fazer.')
    conn.close()
else:
    print('Coluna "notes" não encontrada. Aplicando ALTER TABLE para adicioná-la...')
    try:
        cur.execute('ALTER TABLE patient ADD COLUMN notes TEXT;')
        conn.commit()
        print('Coluna "notes" adicionada com sucesso.')
    except Exception as e:
        print('Erro ao adicionar coluna:', e)
        raise
    finally:
        conn.close()
