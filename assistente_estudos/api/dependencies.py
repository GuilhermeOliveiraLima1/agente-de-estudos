"""Dependências compartilhadas da camada de API."""

from __future__ import annotations

from assistente_estudos.db.database import get_db

__all__ = ["get_db"]
