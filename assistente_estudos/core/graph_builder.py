"""Montagem do grafo LangGraph do Assistente de Estudos.

Este módulo centraliza a criação do grafo, registrando os nós do fluxo e
mantendo a composição desacoplada da implementação de cada etapa.
"""

from __future__ import annotations

from langgraph.graph import StateGraph

from assistente_estudos.core.state import StudyState
from assistente_estudos.nodes.analysis_node import analysis_node
from assistente_estudos.nodes.planner_node import planner_node
from assistente_estudos.nodes.replan_node import replan_node
from assistente_estudos.nodes.report_node import report_node
from assistente_estudos.nodes.simulation_node import simulation_node


def build_graph() -> StateGraph:
    """Cria e retorna a estrutura base do grafo de execução."""

    graph = StateGraph(StudyState)
    graph.add_node("planner", planner_node)
    graph.add_node("replan", replan_node)
    graph.add_node("simulation", simulation_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("report", report_node)
    return graph
