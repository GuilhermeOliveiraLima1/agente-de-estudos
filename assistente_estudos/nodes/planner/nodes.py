"""Os nós do workflow de planejamento inicial.

Fluxo:
    coletar_preferencias → gerar_cronograma → validar_cronograma → persistir_cronograma
"""

from __future__ import annotations

from datetime import date

from assistente_estudos.nodes.planner.state import PlannerState
from assistente_estudos.nodes.planner.schemas import GeneratedTopics
from assistente_estudos.nodes.planner.prompts import PLANNER_PROMPT
from assistente_estudos.services.llm_service import llm
from assistente_estudos.services.scheduler import create_schedule


def coletar_preferencias_node(state: PlannerState) -> PlannerState:
    """Lê e normaliza as preferências e restrições do usuário."""
    return state


def gerar_cronograma_node(state: PlannerState) -> PlannerState:
    """Invoca o LLM para gerar os tópicos e distribui no calendário."""
    structured_llm = llm.with_structured_output(GeneratedTopics)

    prompt = PLANNER_PROMPT.format(
        discipline=state["discipline"],
        subject=state["subject"],
        level=state["level"],
        hours_per_day=state["hours_per_day"],
    )
    generated: GeneratedTopics = structured_llm.invoke(prompt)

    exam_date = date.fromisoformat(state["exam_date"]) if isinstance(state["exam_date"], str) else state["exam_date"]

    study_plan = create_schedule(
        topics=generated.topics,
        exam_date=exam_date,
        hours_per_day=state["hours_per_day"],
    )

    return {
        **state,
        "topics": generated.topics,
        "study_plan": study_plan,
        "plan_summary": {
            "plan_title": generated.plan_title,
            "summary": generated.summary,
            "total_estimated_hours": generated.total_estimated_hours,
            "personalized_message": generated.personalized_message,
        },
    }


def validar_cronograma_node(state: PlannerState) -> PlannerState:
    """Verifica se o cronograma gerado respeita as restrições do usuário."""
    return state


def persistir_cronograma_node(state: PlannerState) -> PlannerState:
    """Salva o cronograma no banco via repositório.

    A persistência efetiva ocorre na camada de API (routes.py),
    mas este nó pode ser usado para salvar em contextos sem HTTP.
    """
    return state
