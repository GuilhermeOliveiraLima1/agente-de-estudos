"""Ponte entre o grafo principal e o sub-grafo de planejamento."""

from __future__ import annotations

from assistente_estudos.core.state import StudyState


def planner_node(state: StudyState) -> StudyState:
    """Executa o workflow de criação do cronograma inicial."""
    from assistente_estudos.nodes.planner.graph import build_planner_graph

    graph = build_planner_graph()
    resultado = graph.invoke({
        "usuario_id": state.get("session_id"),
        "discipline": state.get("discipline"),
        "subject": state.get("subject"),
        "level": state.get("level"),
        "exam_date": state.get("exam_date"),
        "hours_per_day": state.get("hours_per_day"),
    })

    return {
        **state,
        "topics": resultado.get("topics", []),
        "study_plan": resultado.get("study_plan", []),
        "plan_summary": resultado.get("plan_summary", {}),
        "current_plan": resultado.get("study_plan", []), 
    }
