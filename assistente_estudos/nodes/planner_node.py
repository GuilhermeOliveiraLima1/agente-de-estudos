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

    topics_raw = resultado.get("topics", [])
    topic_titles = [
        t.title if hasattr(t, "title")
        else (t.get("title") if isinstance(t, dict) else str(t))
        for t in topics_raw
    ]
    current_plan_base = state.get("current_plan") if isinstance(state.get("current_plan"), dict) else {}

    return {
        **state,
        "topics": topics_raw,
        "study_plan": resultado.get("study_plan", []),
        "plan_summary": resultado.get("plan_summary", {}),
        "current_plan": {
            **current_plan_base,
            "topics": topic_titles,
            "discipline": state.get("discipline", current_plan_base.get("discipline", "")),
            "study_plan": resultado.get("study_plan", []),
        },
    }
