"""Grafo LangGraph do workflow de análise de desempenho.

Este módulo monta e compila o grafo de 6 nós responsável por
coletar dados, calcular scores, identificar fragilidades,
gerar um parecer via LLM e persistir o resultado.
"""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from assistente_estudos.nodes.analysis.nodes import (
    calcular_prontidao_node,
    calcular_scores_node,
    coletar_dados_node,
    gerar_parecer_node,
    identificar_fragilidades_node,
    persistir_resultado_node,
)
from assistente_estudos.nodes.analysis.state import AnalysisState


def build_analysis_graph():
    """Cria e compila o grafo de análise de desempenho."""
    graph = StateGraph(AnalysisState)

    graph.add_node("coletar_dados", coletar_dados_node)
    graph.add_node("calcular_scores", calcular_scores_node)
    graph.add_node("calcular_prontidao", calcular_prontidao_node)
    graph.add_node("identificar_fragilidades", identificar_fragilidades_node)
    graph.add_node("gerar_parecer", gerar_parecer_node)
    graph.add_node("persistir_resultado", persistir_resultado_node)

    graph.set_entry_point("coletar_dados")
    graph.add_edge("coletar_dados", "calcular_scores")
    graph.add_edge("calcular_scores", "calcular_prontidao")
    graph.add_edge("calcular_prontidao", "identificar_fragilidades")
    graph.add_edge("identificar_fragilidades", "gerar_parecer")
    graph.add_edge("gerar_parecer", "persistir_resultado")
    graph.add_edge("persistir_resultado", END)

    return graph.compile()
