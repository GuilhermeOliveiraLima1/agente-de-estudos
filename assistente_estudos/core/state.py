"""Definição do estado tipado compartilhado entre os nós do LangGraph.

Este módulo concentra todos os campos que podem circular entre as etapas do
sistema, mantendo a estrutura explícita e fácil de evoluir.
"""

from __future__ import annotations

from typing import Any, Dict, List, NotRequired, TypedDict


class StudyState(TypedDict, total=False):
    """Estado principal do assistente de estudos.

    Os campos abaixo representam os dados que podem ser produzidos, ajustados
    ou consumidos durante a execução do fluxo de planejamento, simulação,
    análise e geração de relatório.
    """

    # --- Identificação de sessão/usuário ---
    usuario_id: str
    session_id: str
    user_name: str

    # --- Entradas do planner ---
    discipline: str
    subject: str
    level: str
    exam_date: str
    hours_per_day: int

    # --- Saídas do planner ---
    topics: List[Any]          # lista de Topic gerados pelo LLM
    study_plan: List[Any]      # cronograma dia-a-dia
    plan_summary: Dict[str, Any]  # título, resumo, horas estimadas, mensagem

    # --- Campos do fluxo geral ---
    study_goal: str
    available_time_hours: float
    study_days_per_week: int
    subjects: List[str]
    priority_subjects: List[str]
    learning_preferences: Dict[str, Any]
    constraints: Dict[str, Any]
    current_plan: Dict[str, Any]
    replanning_reason: str
    simulation_input: Dict[str, Any]
    simulation_output: Dict[str, Any]
    analysis_output: Dict[str, Any]
    report_data: Dict[str, Any]
    report_text: str
    metadata: Dict[str, Any]

    error_message: NotRequired[str]

