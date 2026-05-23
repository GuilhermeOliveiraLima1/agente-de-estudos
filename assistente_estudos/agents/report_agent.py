"""Agente de relatório (template)."""

from __future__ import annotations

from typing import Dict

from assistente_estudos.nodes.report_node import report_node


def run(state: Dict) -> Dict:
    """Executa o agente de relatório."""

    result = report_node(state)
    return result or state
