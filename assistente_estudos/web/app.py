"""Criação da aplicação web principal.

Este módulo concentra a montagem do app FastAPI e a inclusão das rotas da
interface, mantendo a apresentação separada da orquestração.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from assistente_estudos.config import STATIC_DIR, TEMPLATE_DIR
from assistente_estudos.web.routes import router


def create_app() -> FastAPI:
    """Cria e configura a aplicação web."""

    app = FastAPI(title="Assistente de Planejamento de Estudos Inteligente")
    app.include_router(router)
    templates = Jinja2Templates(directory=TEMPLATE_DIR)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app


app = create_app()
