"""Ponte entre o grafo principal e o sub-grafo de planejamento inicial."""

from __future__ import annotations

from assistente_estudos.core.state import StudyState


def planner_node(state: StudyState) -> StudyState:
    """Executa o workflow de criação do cronograma inicial.

    TODO: mapear os campos de StudyState para PlannerState antes de invocar o grafo.
    """
    from assistente_estudos.nodes.planner.graph import build_planner_graph

    graph = build_planner_graph()
    resultado = graph.invoke({
        "usuario_id": state.get("session_id"),
        "study_goal": state.get("study_goal"),
        "subjects": state.get("subjects", []),
        "priority_subjects": state.get("priority_subjects", []),
        "available_time_hours": state.get("available_time_hours"),
        "study_days_per_week": state.get("study_days_per_week"),
        "learning_preferences": state.get("learning_preferences", {}),
        "constraints": state.get("constraints", {}),
    })

    return {**state, "current_plan": resultado.get("current_plan", {})}
