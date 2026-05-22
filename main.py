"""Ponte de entrada para execução com Uvicorn.

Este arquivo existe para permitir o comando `uvicorn main:app --reload` na
raiz do projeto, encaminhando para a aplicação web real do pacote.
"""

from __future__ import annotations

from assistente_estudos.web.app import app
