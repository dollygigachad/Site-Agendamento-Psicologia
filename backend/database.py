"""Configuração do banco de dados com gerenciamento correto de sessões.

Suporta alternar para um banco em memória quando a variável de ambiente
`AGENDA_USE_IN_MEMORY_DB` estiver definida para '1'. Isso facilita rodar
o sistema localmente quando o arquivo de DB está bloqueado por outro
processo (ex.: durante testes ou quando outro processo mantém uma
conexão aberta).
"""
import os
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.pool import StaticPool
from pathlib import Path
from contextlib import contextmanager

USE_IN_MEMORY = os.environ.get("AGENDA_USE_IN_MEMORY_DB") == "1"

if USE_IN_MEMORY:
    DB_FILE = Path("<in-memory>")
    DATABASE_URL = "sqlite:///:memory:"
else:
    DB_FILE = Path(__file__).parent / "agendamentotcc.db"
    DATABASE_URL = f"sqlite:///{DB_FILE.as_posix()}"

# Criar engine com configurações otimizadas para SQLite
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

def create_db_and_tables():
    """Criar banco de dados e tabelas."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Obter sessão do banco de dados."""
    with Session(engine) as session:
        yield session

@contextmanager
def get_session_context():
    """Context manager para sessão (uso manual)."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

