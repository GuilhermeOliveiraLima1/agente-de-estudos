"""Agente de simulação (template)."""

from __future__ import annotations

from typing import Dict

from assistente_estudos.nodes.simulation_node import simulation_node


def run(state: Dict) -> Dict:
    """Executa o agente de simulação."""

    result = simulation_node(state)
    return result or state
