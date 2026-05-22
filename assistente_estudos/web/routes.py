"""Rotas da interface web.

Este módulo concentra os endpoints que servirão as páginas e ações da
aplicação, sem implementar regras de negócio nesta base.
"""

from __future__ import annotations

from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request

router = APIRouter()


def _render_page(title: str, subtitle: str) -> HTMLResponse:
    """Gera uma página HTML mínima para a interface web estrutural."""

    content = f"""
    <!doctype html>
    <html lang="pt-BR">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{title}</title>
      </head>
      <body>
        <main>
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </main>
      </body>
    </html>
    """

    return HTMLResponse(content=content)


@router.get("/")
def home(request: Request) -> HTMLResponse:
    """Exibe a página inicial da aplicação web."""

    return _render_page("Assistente de Estudos", "Página inicial da aplicação web.")


@router.get("/cronograma")
def cronograma(request: Request) -> HTMLResponse:
    """Exibe a tela de criação ou visualização do cronograma."""

    return _render_page("Cronograma", "Tela estrutural de cronograma.")


@router.get("/simulados")
def simulados(request: Request) -> HTMLResponse:
    """Exibe a tela relacionada aos simulados adaptativos."""

    return _render_page("Simulados", "Tela estrutural de simulados adaptativos.")


@router.get("/relatorios")
def relatorios(request: Request) -> HTMLResponse:
    """Exibe a tela de relatórios e exportações."""

    return _render_page("Relatórios", "Tela estrutural de relatórios e exportações.")
