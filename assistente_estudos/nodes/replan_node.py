"""Ponte entre o grafo principal e o sub-grafo de replanejamento."""

from __future__ import annotations

from assistente_estudos.core.state import StudyState


def replan_node(state: StudyState) -> StudyState:
    """Executa o workflow de replanejamento do cronograma.

    TODO: mapear os campos de StudyState para ReplanState antes de invocar o grafo.
    """
    from assistente_estudos.nodes.replan.graph import build_replan_graph

    graph = build_replan_graph()
    resultado = graph.invoke({
        "usuario_id": state.get("session_id"),
        "current_plan": state.get("current_plan", {}),
        "replanning_reason": state.get("replanning_reason"),
        "constraints": state.get("constraints", {}),
    })

    return {**state, "current_plan": resultado.get("updated_plan", state.get("current_plan", {}))}
