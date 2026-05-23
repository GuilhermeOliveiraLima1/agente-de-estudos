"""Agente de planejamento (template).

Implementação estrutural: chama o nó `planner_node` e devolve o estado.
Troque a lógica por regra real conforme avançar.
"""

from __future__ import annotations

from typing import Dict

from assistente_estudos.nodes.planner_node import planner_node


def run(state: Dict) -> Dict:
    """Executa o agente de planejamento."""

    # chamada estrutural ao nó - substitua por lógica real
    result = planner_node(state)
    return result or state
