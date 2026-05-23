"""Agente de replanejamento (template)."""

from __future__ import annotations

from typing import Dict

from assistente_estudos.nodes.replan_node import replan_node


def run(state: Dict) -> Dict:
    """Executa o agente de replanejamento."""

    result = replan_node(state)
    return result or state
