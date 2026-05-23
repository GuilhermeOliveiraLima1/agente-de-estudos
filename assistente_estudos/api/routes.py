"""Rotas JSON da API de agentes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from assistente_estudos.api.dependencies import get_agent_service
from assistente_estudos.api.schemas import (
    AgentInfo,
    AgentPipelineResponse,
    AgentStepResponse,
    HealthResponse,
    StudyStatePayload,
)
from assistente_estudos.config import API_PREFIX
from assistente_estudos.services.agent_service import AgentService

router = APIRouter(prefix=API_PREFIX, tags=["agents"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Verifica se a API está respondendo."""

    return HealthResponse(status="ok", service="assistente-estudos-api")


@router.get("/agents", response_model=list[AgentInfo])
def list_agents(service: AgentService = Depends(get_agent_service)) -> list[AgentInfo]:
    """Lista os fluxos de agentes disponíveis para o frontend."""

    return [AgentInfo.model_validate(agent) for agent in service.list_agents()]


@router.post("/agents/planner", response_model=AgentStepResponse)
def run_planner(
    payload: StudyStatePayload,
    service: AgentService = Depends(get_agent_service),
) -> AgentStepResponse:
    """Prepara a resposta estrutural da etapa de planejamento."""

    try:
        return AgentStepResponse.model_validate(service.execute_step("planner", payload.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/agents/replan", response_model=AgentStepResponse)
def run_replan(
    payload: StudyStatePayload,
    service: AgentService = Depends(get_agent_service),
) -> AgentStepResponse:
    """Prepara a resposta estrutural da etapa de replanejamento."""

    try:
        return AgentStepResponse.model_validate(service.execute_step("replan", payload.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/agents/simulation", response_model=AgentStepResponse)
def run_simulation(
    payload: StudyStatePayload,
    service: AgentService = Depends(get_agent_service),
) -> AgentStepResponse:
    """Prepara a resposta estrutural da etapa de simulação."""

    try:
        return AgentStepResponse.model_validate(service.execute_step("simulation", payload.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/agents/analysis", response_model=AgentStepResponse)
def run_analysis(
    payload: StudyStatePayload,
    service: AgentService = Depends(get_agent_service),
) -> AgentStepResponse:
    """Prepara a resposta estrutural da etapa de análise."""

    try:
        return AgentStepResponse.model_validate(service.execute_step("analysis", payload.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/agents/report", response_model=AgentStepResponse)
def run_report(
    payload: StudyStatePayload,
    service: AgentService = Depends(get_agent_service),
) -> AgentStepResponse:
    """Prepara a resposta estrutural da etapa de relatório."""

    try:
        return AgentStepResponse.model_validate(service.execute_step("report", payload.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/agents/pipeline", response_model=AgentPipelineResponse)
def run_pipeline(
    payload: StudyStatePayload,
    service: AgentService = Depends(get_agent_service),
) -> AgentPipelineResponse:
    """Executa o pipeline estrutural completo dos agentes."""

    return AgentPipelineResponse.model_validate(service.execute_pipeline(payload.model_dump()))
