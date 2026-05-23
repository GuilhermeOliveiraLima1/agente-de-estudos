"""Ponte de entrada para execução com Uvicorn.

Este arquivo existe para permitir o comando `uvicorn main:app --reload` na
raiz do projeto, encaminhando para a aplicação API real do pacote.
"""

from __future__ import annotations

from assistente_estudos.api.app import app
