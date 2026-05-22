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

    session_id: str
    user_name: str
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
    llm_provider: str
    llm_model: str
    messages: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    error_message: NotRequired[str]
