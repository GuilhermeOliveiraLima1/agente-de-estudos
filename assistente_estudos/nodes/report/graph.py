"""Grafo LangGraph do workflow de geração de relatório."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from assistente_estudos.nodes.report.nodes import (
    coletar_dados_node,
    exportar_relatorio_node,
    gerar_relatorio_node,
    persistir_relatorio_node,
)
from assistente_estudos.nodes.report.state import ReportState


def build_report_graph():
    """Cria e compila o grafo de geração de relatório."""
    graph = StateGraph(ReportState)

    graph.add_node("coletar_dados", coletar_dados_node)
    graph.add_node("gerar_relatorio", gerar_relatorio_node)
    graph.add_node("exportar_relatorio", exportar_relatorio_node)
    graph.add_node("persistir_relatorio", persistir_relatorio_node)

    graph.set_entry_point("coletar_dados")
    graph.add_edge("coletar_dados", "gerar_relatorio")
    graph.add_edge("gerar_relatorio", "exportar_relatorio")
    graph.add_edge("exportar_relatorio", "persistir_relatorio")
    graph.add_edge("persistir_relatorio", END)

    return graph.compile()
