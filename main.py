"""Ponto de entrada da aplicação.

Execute com: uvicorn main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from assistente_estudos.api.app import create_app
from assistente_estudos.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = create_app(lifespan=lifespan)
