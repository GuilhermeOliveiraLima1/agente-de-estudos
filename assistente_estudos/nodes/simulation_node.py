"""Ponte entre o grafo principal e o sub-grafo de simulação."""

from __future__ import annotations

from typing import Any, Dict, List

from assistente_estudos.core.state import StudyState


def _extract_topics(current_plan: Dict[str, Any]) -> List[str]:
    topics = current_plan.get("topics", []) if isinstance(current_plan, dict) else []
    if not isinstance(topics, list):
        return []
    return [str(topic) for topic in topics if str(topic).strip()]


def _build_simulation_state(state: StudyState) -> Dict[str, Any]:
    current_plan = state.get("current_plan", {}) or {}
    simulation_input = state.get("simulation_input", {}) or {}
    quantity_questions = state.get("quantity_questions")
    if quantity_questions is None:
        quantity_questions = simulation_input.get("quantity_questions")

    mapped_state: Dict[str, Any] = {
        "usuario_id": state.get("session_id") or state.get("user_name"),
        "current_plan": {
            **current_plan,
            "topics": _extract_topics(current_plan),
        },
        "nivel_dificuldade": simulation_input.get("nivel_dificuldade", "intermediario"),
    }

    if quantity_questions is not None:
        mapped_state["quantity_questions"] = quantity_questions

    if "respostas" in simulation_input:
        mapped_state["respostas"] = simulation_input.get("respostas", [])

    if "questoes" in simulation_input:
        mapped_state["questoes"] = simulation_input.get("questoes", [])

    return mapped_state


def simulation_node(state: StudyState) -> StudyState:
    """Executa o workflow de simulação adaptativa.

    Mapeia os campos relevantes do estado principal para o estado da simulação,
    executa o sub-grafo e devolve os resultados ao fluxo principal.
    """
    from assistente_estudos.nodes.simulation.graph import build_simulation_graph

    graph = build_simulation_graph()
    simulation_state = _build_simulation_state(state)
    resultado = graph.invoke(simulation_state) or {}

    merged_state: StudyState = {
        **state,
        "simulation_output": resultado.get("simulation_output", state.get("simulation_output", {})),
    }

    if resultado.get("simulado_id") is not None:
        merged_state["metadata"] = {
            **(state.get("metadata", {}) or {}),
            "simulado_id": resultado.get("simulado_id"),
        }

    if resultado.get("erro") is not None:
        merged_state["error_message"] = str(resultado.get("erro"))

    return merged_state
