"""Rotas da API do Assistente de Estudos.

Organização:
  /api/health              — status do serviço
  /api/usuarios            — CRUD de usuários
  /api/sessoes             — registro de sessões de estudo
  /api/simulados           — registro de resultados de simulados
  /api/analise/{id}        — workflow de análise de desempenho (LangGraph)
  /api/agentes/{no}        — execução individual de cada nó do LangGraph
  /api/agentes/pipeline    — execução completa do fluxo
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from assistente_estudos.api.dependencies import get_db
from assistente_estudos.api.schemas import (
    AgentPipelineResponse,
    AgentStepResponse,
    AnaliseResponse,
    HealthResponse,
    SessaoCreate,
    SessaoResponse,
    SimuladoCreate,
    SimuladoResponse,
    StudyStatePayload,
    UsuarioCreate,
    UsuarioResponse,
)
from assistente_estudos.config import API_PREFIX
from assistente_estudos.db.models import ResultadoSimulado, ScoreProntidao, SessaoEstudo, Usuario
from assistente_estudos.nodes.analysis_node import analysis_node
from assistente_estudos.nodes.planner_node import planner_node
from assistente_estudos.nodes.replan_node import replan_node
from assistente_estudos.nodes.report_node import report_node
from assistente_estudos.nodes.simulation_node import simulation_node

router = APIRouter(prefix=API_PREFIX)


# ---------------------------------------------------------------------------
# Sistema
# ---------------------------------------------------------------------------

@router.get("/health", response_model=HealthResponse, tags=["sistema"])
def health() -> HealthResponse:
    """Verifica se a API está respondendo."""
    return HealthResponse(status="ok", service="assistente-estudos-api")


# ---------------------------------------------------------------------------
# Usuários
# ---------------------------------------------------------------------------

@router.post("/usuarios", response_model=UsuarioResponse, tags=["usuários"])
def criar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    """Cadastra um novo usuário."""
    if db.query(Usuario).filter(Usuario.email == dados.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    usuario = Usuario(nome=dados.nome, email=dados.email)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.get("/usuarios/{usuario_id}", response_model=UsuarioResponse, tags=["usuários"])
def buscar_usuario(usuario_id: str, db: Session = Depends(get_db)):
    """Retorna os dados de um usuário pelo ID."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return usuario


# ---------------------------------------------------------------------------
# Sessões de estudo
# ---------------------------------------------------------------------------

@router.post("/sessoes", response_model=SessaoResponse, tags=["estudo"])
def registrar_sessao(dados: SessaoCreate, db: Session = Depends(get_db)):
    """Registra uma sessão de estudo realizada."""
    sessao = SessaoEstudo(
        usuario_id=dados.usuario_id,
        disciplina=dados.disciplina,
        topico=dados.topico,
        data=datetime.utcnow(),
        duracao_minutos=dados.duracao_minutos,
        concluido=dados.concluido,
        dificuldade_percebida=dados.dificuldade_percebida,
    )
    db.add(sessao)
    db.commit()
    db.refresh(sessao)
    return sessao


# ---------------------------------------------------------------------------
# Simulados
# ---------------------------------------------------------------------------

@router.post("/simulados", response_model=SimuladoResponse, tags=["simulados"])
def registrar_simulado(dados: SimuladoCreate, db: Session = Depends(get_db)):
    """Registra o resultado de um simulado realizado."""
    if dados.acertos > dados.total_questoes:
        raise HTTPException(status_code=400, detail="Acertos não podem superar o total de questões.")
    taxa = round(dados.acertos / dados.total_questoes, 4)
    resultado = ResultadoSimulado(
        usuario_id=dados.usuario_id,
        disciplina=dados.disciplina,
        topico=dados.topico,
        data=datetime.utcnow(),
        total_questoes=dados.total_questoes,
        acertos=dados.acertos,
        taxa_acerto=taxa,
        nivel_dificuldade=dados.nivel_dificuldade,
    )
    db.add(resultado)
    db.commit()
    db.refresh(resultado)
    return resultado


# ---------------------------------------------------------------------------
# Análise de desempenho (workflow LangGraph com 6 nós)
# ---------------------------------------------------------------------------

@router.post("/analise/{usuario_id}", response_model=AnaliseResponse, tags=["análise"])
def executar_analise(usuario_id: str, periodo_dias: int = 30, db: Session = Depends(get_db)):
    """Executa o workflow completo de análise de desempenho.

    Fluxo LangGraph:
    coletar_dados → calcular_scores → calcular_prontidao
    → identificar_fragilidades → gerar_parecer → persistir_resultado
    """
    from assistente_estudos.nodes.analysis.graph import build_analysis_graph

    if not db.query(Usuario).filter(Usuario.id == usuario_id).first():
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    graph = build_analysis_graph()
    resultado = graph.invoke({"usuario_id": usuario_id, "periodo_dias": periodo_dias})

    if resultado.get("erro"):
        raise HTTPException(status_code=500, detail=resultado["erro"])

    return AnaliseResponse(
        usuario_id=usuario_id,
        periodo_dias=periodo_dias,
        indice_prontidao=resultado.get("indice_prontidao"),
        classificacao=resultado.get("classificacao"),
        score_dominio=resultado.get("score_dominio"),
        score_consistencia=resultado.get("score_consistencia"),
        score_retencao=resultado.get("score_retencao"),
        topicos_frageis=resultado.get("topicos_frageis", []),
        tendencia=resultado.get("tendencia"),
        parecer=resultado.get("parecer_llm"),
        resultado_id=resultado.get("resultado_id"),
    )


@router.get("/analise/{usuario_id}/historico", tags=["análise"])
def historico_analise(usuario_id: str, limite: int = 10, db: Session = Depends(get_db)):
    """Retorna as últimas N análises de desempenho do usuário."""
    scores = (
        db.query(ScoreProntidao)
        .filter(ScoreProntidao.usuario_id == usuario_id)
        .order_by(ScoreProntidao.criado_em.desc())
        .limit(limite)
        .all()
    )
    return [
        {
            "id": s.id,
            "indice_prontidao": s.indice_prontidao,
            "classificacao": s.classificacao,
            "scores": {
                "dominio": s.score_dominio,
                "consistencia": s.score_consistencia,
                "retencao": s.score_retencao,
            },
            "topicos_frageis": json.loads(s.topicos_frageis) if s.topicos_frageis else [],
            "tendencia": s.tendencia,
            "criado_em": s.criado_em.isoformat(),
        }
        for s in scores
    ]


@router.get("/analise/{usuario_id}/ultimo", tags=["análise"])
def ultima_analise(usuario_id: str, db: Session = Depends(get_db)):
    """Retorna a análise de desempenho mais recente do usuário."""
    score = (
        db.query(ScoreProntidao)
        .filter(ScoreProntidao.usuario_id == usuario_id)
        .order_by(ScoreProntidao.criado_em.desc())
        .first()
    )
    if not score:
        raise HTTPException(status_code=404, detail="Nenhuma análise encontrada para este usuário.")
    return {
        "id": score.id,
        "indice_prontidao": score.indice_prontidao,
        "classificacao": score.classificacao,
        "scores": {
            "dominio": score.score_dominio,
            "consistencia": score.score_consistencia,
            "retencao": score.score_retencao,
        },
        "topicos_frageis": json.loads(score.topicos_frageis) if score.topicos_frageis else [],
        "tendencia": score.tendencia,
        "parecer": score.parecer_llm,
        "criado_em": score.criado_em.isoformat(),
    }


# ---------------------------------------------------------------------------
# Agentes — nós individuais do LangGraph
#
# Padrão para implementação:
#   1. Recebe StudyStatePayload do frontend
#   2. Converte para dict e passa para o nó
#   3. O nó lê o estado, executa sua lógica e devolve o estado atualizado
#   4. A rota retorna o estado atualizado para o frontend
#
# Quando o nó estiver implementado, apenas o corpo da função muda.
# A assinatura da rota e o contrato HTTP permanecem iguais.
# ---------------------------------------------------------------------------

@router.post("/agentes/planner", response_model=AgentStepResponse, tags=["agentes"])
def run_planner(payload: StudyStatePayload, db: Session = Depends(get_db)):
    """Executa o nó de planejamento inicial."""
    state = planner_node(payload.model_dump())
    return AgentStepResponse(step="planner", state=state)


@router.post("/agentes/replan", response_model=AgentStepResponse, tags=["agentes"])
def run_replan(payload: StudyStatePayload, db: Session = Depends(get_db)):
    """Executa o nó de replanejamento."""
    state = replan_node(payload.model_dump())
    return AgentStepResponse(step="replan", state=state)


@router.post("/agentes/simulation", response_model=AgentStepResponse, tags=["agentes"])
def run_simulation(payload: StudyStatePayload, db: Session = Depends(get_db)):
    """Executa o nó de simulação."""
    state = simulation_node(payload.model_dump())
    return AgentStepResponse(step="simulation", state=state)


@router.post("/agentes/analysis", response_model=AgentStepResponse, tags=["agentes"])
def run_analysis(payload: StudyStatePayload, db: Session = Depends(get_db)):
    """Executa o nó de análise."""
    state = analysis_node(payload.model_dump())
    return AgentStepResponse(step="analysis", state=state)


@router.post("/agentes/report", response_model=AgentStepResponse, tags=["agentes"])
def run_report(payload: StudyStatePayload, db: Session = Depends(get_db)):
    """Executa o nó de relatório."""
    state = report_node(payload.model_dump())
    return AgentStepResponse(step="report", state=state)


@router.post("/agentes/pipeline", response_model=AgentPipelineResponse, tags=["agentes"])
def run_pipeline(payload: StudyStatePayload, db: Session = Depends(get_db)):
    """Executa todos os nós em sequência."""
    state = payload.model_dump()
    nos = [
        ("planner", planner_node),
        ("replan", replan_node),
        ("simulation", simulation_node),
        ("analysis", analysis_node),
        ("report", report_node),
    ]
    for _, no in nos:
        state = no(state) or state
    return AgentPipelineResponse(steps=[nome for nome, _ in nos], state=state)

