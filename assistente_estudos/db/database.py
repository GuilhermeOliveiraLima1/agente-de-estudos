"""Configuração da conexão com o banco de dados."""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from assistente_estudos.db.models import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://estudos:estudos123@localhost:5432/assistente_estudos",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Cria todas as tabelas no banco caso ainda não existam."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency do FastAPI que fornece uma sessão de banco por request."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()