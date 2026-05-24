"""Schemas de entrada e saída da API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import date

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Sistema
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    service: str


# ---------------------------------------------------------------------------
# Usuários
# ---------------------------------------------------------------------------

class UsuarioCreate(BaseModel):
    nome: str
    email: str


class UsuarioResponse(BaseModel):
    id: str
    nome: str
    email: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Sessões de estudo
# ---------------------------------------------------------------------------

class SessaoCreate(BaseModel):
    usuario_id: str
    disciplina: str
    topico: str
    duracao_minutos: int
    concluido: bool = True
    dificuldade_percebida: Optional[int] = 3


class SessaoResponse(BaseModel):
    id: str
    usuario_id: str
    disciplina: str
    topico: str
    duracao_minutos: int
    concluido: bool

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Plano de Estudo
# ---------------------------------------------------------------------------

class GeneratePlanRequest(BaseModel):
    discipline: str
    subject: str
    level: str
    exam_date: date
    hours_per_day: int
    usuario_id: Optional[str] = None


class PlanResponse(BaseModel):
    id: int
    usuario_id: Optional[str]
    discipline: str
    subject: str
    level: str
    exam_date: str
    hours_per_day: int
    plan_summary: Dict[str, Any]
    topics: List[Any]
    study_plan: List[Any]

    model_config = {"from_attributes": True}

# ---------------------------------------------------------------------------
# Simulados
# ---------------------------------------------------------------------------

class SimuladoCreate(BaseModel):
    usuario_id: str
    disciplina: str
    topico: str
    total_questoes: int
    acertos: int
    nivel_dificuldade: str = "intermediario"


class SimuladoResponse(BaseModel):
    id: str
    usuario_id: str
    disciplina: str
    topico: str
    total_questoes: int
    acertos: int
    taxa_acerto: float
    nivel_dificuldade: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Análise de desempenho
# ---------------------------------------------------------------------------

class AnaliseResponse(BaseModel):
    usuario_id: str
    periodo_dias: int
    indice_prontidao: Optional[float] = None
    classificacao: Optional[str] = None
    score_dominio: Optional[float] = None
    score_consistencia: Optional[float] = None
    score_retencao: Optional[float] = None
    topicos_frageis: List[str] = Field(default_factory=list)
    tendencia: Optional[str] = None
    parecer: Optional[str] = None
    resultado_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Agentes (nós do LangGraph)
# ---------------------------------------------------------------------------

class StudyStatePayload(BaseModel):
    """Payload de entrada para as rotas de agentes."""

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
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentStepResponse(BaseModel):
    """Resposta de uma etapa individual do fluxo de agentes."""

    step: str
    state: Dict[str, Any]


class AgentPipelineResponse(BaseModel):
    """Resposta da execução completa do pipeline de agentes."""

    steps: List[str]
    state: Dict[str, Any]
