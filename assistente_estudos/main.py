"""Ponto de entrada da aplicação web.

Este arquivo concentra a inicialização do aplicativo web e a conexão com a
camada de orquestração, sem implementar comportamento funcional nesta base.
"""

from __future__ import annotations

from assistente_estudos.core.graph_builder import build_graph
from assistente_estudos.web.app import create_app


def main() -> None:
    """Inicializa a aplicação web."""

    build_graph()
    create_app()


if __name__ == "__main__":
    main()
