"""Ponto de entrada da API do Assistente de Estudos.

Este arquivo concentra a inicialização da aplicação FastAPI exposta para o
frontend externo consumir.
"""

from __future__ import annotations

from assistente_estudos.api.app import create_app


app = create_app()


def main() -> None:
    """Inicializa a aplicação API."""

    create_app()


if __name__ == "__main__":
    main()
