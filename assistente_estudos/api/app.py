"""Criação da aplicação FastAPI."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI

from assistente_estudos.api.routes import router
from assistente_estudos.config import APP_TITLE


def create_app(lifespan: Optional[Any] = None) -> FastAPI:
    """Cria e configura a aplicação FastAPI."""
    app = FastAPI(title=APP_TITLE, lifespan=lifespan)
    app.include_router(router)
    return app
