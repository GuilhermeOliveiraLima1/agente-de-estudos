"""Ponte entre o grafo principal e o sub-grafo de geração de relatório."""

from __future__ import annotations

from assistente_estudos.core.state import StudyState


def report_node(state: StudyState) -> StudyState:
    """Executa o workflow de geração e exportação do relatório final.

    TODO: mapear os campos de StudyState para ReportState antes de invocar o grafo.
    """
    from assistente_estudos.nodes.report.graph import build_report_graph

    graph = build_report_graph()
    resultado = graph.invoke({
        "usuario_id": state.get("usuario_id") or state.get("session_id"),
        "analysis_output": state.get("analysis_output", {}),
        "simulation_output": state.get("simulation_output", {}),
        "current_plan": state.get("current_plan", {}),
    })

    return {
        **state,
        "report_data": resultado.get("report_data", {}),
        "report_text": resultado.get("report_text", ""),
    }
