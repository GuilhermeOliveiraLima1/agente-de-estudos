"""Criação da aplicação FastAPI da API de agentes."""

from __future__ import annotations

from fastapi import FastAPI

from assistente_estudos.api.routes import router
from assistente_estudos.config import APP_TITLE


def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI principal."""

    app = FastAPI(title=APP_TITLE)
    app.include_router(router)
    return app


app = create_app()
