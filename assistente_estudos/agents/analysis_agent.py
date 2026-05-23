"""Agente de análise (template)."""

from __future__ import annotations

from typing import Dict

from assistente_estudos.nodes.analysis_node import analysis_node


def run(state: Dict) -> Dict:
    """Executa o agente de análise."""

    result = analysis_node(state)
    return result or state
