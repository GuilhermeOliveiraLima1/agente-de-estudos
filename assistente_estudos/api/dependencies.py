"""Dependências compartilhadas da camada de API."""

from __future__ import annotations

from functools import lru_cache

from assistente_estudos.services.agent_service import AgentService


@lru_cache(maxsize=1)
def get_agent_service() -> AgentService:
    """Retorna uma instância única do serviço de agentes."""

    return AgentService()
