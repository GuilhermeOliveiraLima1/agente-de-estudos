"""Ponte entre o grafo principal e o sub-grafo de simulação."""

from __future__ import annotations

from assistente_estudos.core.state import StudyState


def simulation_node(state: StudyState) -> StudyState:
    """Executa o workflow de simulação adaptativa.

    TODO: mapear os campos de StudyState para SimulationState antes de invocar o grafo.
    """
    from assistente_estudos.nodes.simulation.graph import build_simulation_graph

    graph = build_simulation_graph()
    resultado = graph.invoke({
        "usuario_id": state.get("session_id"),
        "current_plan": state.get("current_plan", {}),
        "nivel_dificuldade": state.get("simulation_input", {}).get("nivel_dificuldade", "intermediario"),
    })

    return {**state, "simulation_output": resultado.get("simulation_output", {})}
