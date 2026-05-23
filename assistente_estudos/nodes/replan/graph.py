"""Grafo LangGraph do workflow de replanejamento."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from assistente_estudos.nodes.replan.nodes import (
    analisar_desvio_node,
    persistir_replanejamento_node,
    recalcular_cronograma_node,
)
from assistente_estudos.nodes.replan.state import ReplanState


def build_replan_graph():
    """Cria e compila o grafo de replanejamento."""
    graph = StateGraph(ReplanState)

    graph.add_node("analisar_desvio", analisar_desvio_node)
    graph.add_node("recalcular_cronograma", recalcular_cronograma_node)
    graph.add_node("persistir_replanejamento", persistir_replanejamento_node)

    graph.set_entry_point("analisar_desvio")
    graph.add_edge("analisar_desvio", "recalcular_cronograma")
    graph.add_edge("recalcular_cronograma", "persistir_replanejamento")
    graph.add_edge("persistir_replanejamento", END)

    return graph.compile()
