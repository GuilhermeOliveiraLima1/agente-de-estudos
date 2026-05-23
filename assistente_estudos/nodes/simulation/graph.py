"""Grafo LangGraph do workflow de simulação adaptativa."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from assistente_estudos.nodes.simulation.nodes import (
    avaliar_resultado_node,
    executar_simulacao_node,
    persistir_simulacao_node,
    preparar_simulacao_node,
)
from assistente_estudos.nodes.simulation.state import SimulationState


def build_simulation_graph():
    """Cria e compila o grafo de simulação adaptativa."""
    graph = StateGraph(SimulationState)

    graph.add_node("preparar_simulacao", preparar_simulacao_node)
    graph.add_node("executar_simulacao", executar_simulacao_node)
    graph.add_node("avaliar_resultado", avaliar_resultado_node)
    graph.add_node("persistir_simulacao", persistir_simulacao_node)

    graph.set_entry_point("preparar_simulacao")
    graph.add_edge("preparar_simulacao", "executar_simulacao")
    graph.add_edge("executar_simulacao", "avaliar_resultado")
    graph.add_edge("avaliar_resultado", "persistir_simulacao")
    graph.add_edge("persistir_simulacao", END)

    return graph.compile()
