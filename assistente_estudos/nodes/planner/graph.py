"""Grafo LangGraph do workflow de planejamento inicial."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from assistente_estudos.nodes.planner.nodes import (
    coletar_preferencias_node,
    gerar_cronograma_node,
    persistir_cronograma_node,
    validar_cronograma_node,
)
from assistente_estudos.nodes.planner.state import PlannerState


def build_planner_graph():
    """Cria e compila o grafo de planejamento inicial."""
    graph = StateGraph(PlannerState)

    graph.add_node("coletar_preferencias", coletar_preferencias_node)
    graph.add_node("gerar_cronograma", gerar_cronograma_node)
    graph.add_node("validar_cronograma", validar_cronograma_node)
    graph.add_node("persistir_cronograma", persistir_cronograma_node)

    graph.set_entry_point("coletar_preferencias")
    graph.add_edge("coletar_preferencias", "gerar_cronograma")
    graph.add_edge("gerar_cronograma", "validar_cronograma")
    graph.add_edge("validar_cronograma", "persistir_cronograma")
    graph.add_edge("persistir_cronograma", END)

    return graph.compile()
