"""Serviço de orquestração dos agentes do Assistente de Estudos.

Este módulo concentra a fronteira de API para o fluxo de agentes. A lógica
real dos nós ainda pode ser implementada depois sem alterar os contratos HTTP.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List

from assistente_estudos.core.state import StudyState


class AgentService:
    """Orquestra respostas estruturadas para os fluxos de agentes."""

    _AVAILABLE_STEPS: List[str] = ["planner", "replan", "simulation", "analysis", "report"]

    def list_agents(self) -> List[Dict[str, str]]:
        """Retorna os fluxos de agentes disponíveis na API."""

        return [
            {"name": "planner", "description": "Cria o plano inicial de estudos."},
            {"name": "replan", "description": "Recalcula o plano com base em mudanças."},
            {"name": "simulation", "description": "Simula a execução do cronograma."},
            {"name": "analysis", "description": "Analisa o resultado da simulação."},
            {"name": "report", "description": "Consolida a saída final do fluxo."},
        ]

    def execute_step(self, step: str, state: StudyState) -> Dict[str, Any]:
        """Prepara a resposta estruturada para um passo específico do fluxo."""

        if step not in self._AVAILABLE_STEPS:
            raise ValueError(f"Etapa desconhecida: {step}")

        snapshot = deepcopy(dict(state))
        metadata = dict(snapshot.get("metadata") or {})
        metadata.update(
            {
                "agent_step": step,
                "status": "structural",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        snapshot["metadata"] = metadata

        return {
            "step": step,
            "status": "structural",
            "message": "Estrutura da API pronta para integrar a lógica do agente.",
            "state": snapshot,
        }

    def execute_pipeline(self, state: StudyState) -> Dict[str, Any]:
        """Executa o fluxo completo como composição dos passos disponíveis."""

        results = [self.execute_step(step, state) for step in self._AVAILABLE_STEPS]
        final_state = results[-1]["state"] if results else dict(state)

        return {
            "status": "structural",
            "message": "Pipeline estrutural preparado para consumo pelo frontend.",
            "results": results,
            "state": final_state,
        }
