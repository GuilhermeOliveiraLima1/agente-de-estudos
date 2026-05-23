"""Schemas de entrada e saída da API de agentes."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StudyStatePayload(BaseModel):
    """Representa o estado trocado entre frontend e backend."""

    session_id: Optional[str] = None
    user_name: Optional[str] = None
    study_goal: Optional[str] = None
    available_time_hours: Optional[float] = None
    study_days_per_week: Optional[int] = None
    subjects: List[str] = Field(default_factory=list)
    priority_subjects: List[str] = Field(default_factory=list)
    learning_preferences: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    current_plan: Dict[str, Any] = Field(default_factory=dict)
    replanning_reason: Optional[str] = None
    simulation_input: Dict[str, Any] = Field(default_factory=dict)
    simulation_output: Dict[str, Any] = Field(default_factory=dict)
    analysis_output: Dict[str, Any] = Field(default_factory=dict)
    report_data: Dict[str, Any] = Field(default_factory=dict)
    report_text: Optional[str] = None
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentStepResponse(BaseModel):
    """Resposta estruturada para uma etapa específica do fluxo."""

    step: str
    status: str
    message: str
    state: Dict[str, Any]


class AgentPipelineResponse(BaseModel):
    """Resposta estruturada para a execução completa do pipeline."""

    status: str
    message: str
    results: List[Dict[str, Any]]
    state: Dict[str, Any]


class AgentInfo(BaseModel):
    """Metadados sobre os agentes disponíveis na API."""

    name: str
    description: str


class HealthResponse(BaseModel):
    """Resposta simples para verificação de saúde."""

    status: str
    service: str
