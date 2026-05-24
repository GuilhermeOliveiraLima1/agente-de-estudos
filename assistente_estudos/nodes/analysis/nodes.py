"""Os seis nós do workflow de análise de desempenho.

Fluxo:
    coletar_dados → calcular_scores → calcular_prontidao
    → identificar_fragilidades → gerar_parecer → persistir_resultado
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List

from assistente_estudos.nodes.analysis.state import AnalysisState


# ---------------------------------------------------------------------------
# Nó 1 — Coletar dados do banco
# ---------------------------------------------------------------------------

def coletar_dados_node(state: AnalysisState) -> AnalysisState:
    """Busca sessões de estudo e resultados de simulados do banco de dados."""
    from assistente_estudos.db.database import SessionLocal
    from assistente_estudos.db.models import ResultadoSimulado, SessaoEstudo

    periodo = state.get("periodo_dias", 30)
    desde = datetime.utcnow() - timedelta(days=periodo)
    usuario_id = state["usuario_id"]

    db = SessionLocal()
    try:
        sessoes = (
            db.query(SessaoEstudo)
            .filter(SessaoEstudo.usuario_id == usuario_id, SessaoEstudo.data >= desde)
            .order_by(SessaoEstudo.data)
            .all()
        )
        simulados = (
            db.query(ResultadoSimulado)
            .filter(ResultadoSimulado.usuario_id == usuario_id, ResultadoSimulado.data >= desde)
            .order_by(ResultadoSimulado.data)
            .all()
        )

        return {
            **state,
            "sessoes": [
                {
                    "disciplina": s.disciplina,
                    "topico": s.topico,
                    "data": s.data.isoformat(),
                    "duracao_minutos": s.duracao_minutos,
                    "concluido": s.concluido,
                    "dificuldade_percebida": s.dificuldade_percebida,
                }
                for s in sessoes
            ],
            "resultados_simulados": [
                {
                    "disciplina": r.disciplina,
                    "topico": r.topico,
                    "data": r.data.isoformat(),
                    "total_questoes": r.total_questoes,
                    "acertos": r.acertos,
                    "taxa_acerto": r.taxa_acerto,
                    "nivel_dificuldade": r.nivel_dificuldade,
                }
                for r in simulados
            ],
        }
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Nó 2 — Calcular os três scores componentes
# ---------------------------------------------------------------------------

def calcular_scores_node(state: AnalysisState) -> AnalysisState:
    """Calcula Score de Domínio, Consistência e Retenção."""
    sessoes = state.get("sessoes", [])
    simulados = state.get("resultados_simulados", [])

    # Domínio: média ponderada de taxa de acerto nos simulados
    if simulados:
        score_dominio = sum(r["taxa_acerto"] for r in simulados) / len(simulados) * 100
    else:
        score_dominio = 0.0

    # Consistência: proporção de sessões de estudo concluídas
    if sessoes:
        concluidas = sum(1 for s in sessoes if s["concluido"])
        score_consistencia = (concluidas / len(sessoes)) * 100
    else:
        score_consistencia = 0.0

    # Retenção: evolução de desempenho entre primeira e segunda metade dos simulados
    if len(simulados) >= 4:
        metade = len(simulados) // 2
        media_inicial = sum(r["taxa_acerto"] for r in simulados[:metade]) / metade
        media_recente = sum(r["taxa_acerto"] for r in simulados[metade:]) / (len(simulados) - metade)
        delta = (media_recente - media_inicial) * 100
        score_retencao = min(100.0, max(0.0, 50.0 + delta))
    elif simulados:
        score_retencao = score_dominio
    else:
        score_retencao = 0.0

    return {
        **state,
        "score_dominio": round(score_dominio, 2),
        "score_consistencia": round(score_consistencia, 2),
        "score_retencao": round(score_retencao, 2),
    }


# ---------------------------------------------------------------------------
# Nó 3 — Calcular índice de Prontidão e classificar risco
# ---------------------------------------------------------------------------

def calcular_prontidao_node(state: AnalysisState) -> AnalysisState:
    """Aplica a fórmula de Prontidão e classifica o nível de risco."""
    dominio = state.get("score_dominio", 0.0)
    consistencia = state.get("score_consistencia", 0.0)
    retencao = state.get("score_retencao", 0.0)

    # Prontidão = (Domínio × 0.5) + (Consistência × 0.3) + (Retenção × 0.2)
    indice = (dominio * 0.5) + (consistencia * 0.3) + (retencao * 0.2)

    if indice <= 50:
        classificacao = "risco_alto"
    elif indice <= 75:
        classificacao = "moderado"
    else:
        classificacao = "alta_probabilidade"

    return {
        **state,
        "indice_prontidao": round(indice, 2),
        "classificacao": classificacao,
    }


# ---------------------------------------------------------------------------
# Nó 4 — Identificar fragilidades e tendência
# ---------------------------------------------------------------------------

def identificar_fragilidades_node(state: AnalysisState) -> AnalysisState:
    """Detecta tópicos fracos e a tendência de evolução do desempenho."""
    simulados = state.get("resultados_simulados", [])

    # Tópicos com média de acerto abaixo de 60 %
    medias: Dict[str, List[float]] = defaultdict(list)
    for r in simulados:
        medias[r["topico"]].append(r["taxa_acerto"])

    topicos_frageis = [
        topico
        for topico, taxas in medias.items()
        if sum(taxas) / len(taxas) < 0.6
    ]

    # Tendência: primeira metade vs segunda metade dos simulados
    if len(simulados) >= 2:
        metade = max(1, len(simulados) // 2)
        media_antiga = sum(r["taxa_acerto"] for r in simulados[:metade]) / metade
        media_nova = sum(r["taxa_acerto"] for r in simulados[metade:]) / (len(simulados) - metade)
        delta = media_nova - media_antiga
        if delta > 0.05:
            tendencia = "melhorando"
        elif delta < -0.05:
            tendencia = "piorando"
        else:
            tendencia = "estavel"
    else:
        tendencia = "sem_dados_suficientes"

    return {
        **state,
        "topicos_frageis": topicos_frageis,
        "tendencia": tendencia,
    }


# ---------------------------------------------------------------------------
# Nó 5 — Gerar parecer com LLM + Tools
# ---------------------------------------------------------------------------

def gerar_parecer_node(state: AnalysisState) -> AnalysisState:
    """Pré-computa os resultados das tools e invoca o LLM para gerar o parecer."""
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_ollama import ChatOllama

    from assistente_estudos.nodes.analysis.tools import (
        calcular_media_por_topico,
        detectar_tendencia_semanal,
        identificar_topicos_criticos,
    )

    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3:8b")

    # Pré-computa os resultados das tools diretamente (sem bind_tools)
    simulados = state.get("resultados_simulados", [])
    medias_por_topico = calcular_media_por_topico.func(simulados) if simulados else {}
    scores_historicos = [r["taxa_acerto"] * 100 for r in simulados]
    tendencia_semanal = detectar_tendencia_semanal.func(scores_historicos) if len(scores_historicos) >= 2 else "sem_historico_suficiente"
    topicos_criticos = identificar_topicos_criticos.func(medias_por_topico, 0.6) if medias_por_topico else []

    classificacao_legivel = {
        "risco_alto": "Risco Alto (0–50)",
        "moderado": "Moderado (51–75)",
        "alta_probabilidade": "Alta Probabilidade (76–100)",
    }.get(state.get("classificacao", ""), state.get("classificacao", ""))

    medias_formatadas = ", ".join(
        f"{t}: {v*100:.1f}%" for t, v in medias_por_topico.items()
    ) or "Sem dados"

    prompt = (
        f"Analise o desempenho acadêmico do estudante e gere um parecer personalizado.\n\n"
        f"DADOS DO ESTUDANTE:\n"
        f"- Índice de Prontidão: {state.get('indice_prontidao')} / 100\n"
        f"- Classificação: {classificacao_legivel}\n"
        f"- Score de Domínio (acerto nos simulados): {state.get('score_dominio')}%\n"
        f"- Score de Consistência (sessões concluídas): {state.get('score_consistencia')}%\n"
        f"- Score de Retenção (evolução ao longo do tempo): {state.get('score_retencao')}%\n"
        f"- Média por tópico: {medias_formatadas}\n"
        f"- Tópicos críticos (abaixo de 60%): {', '.join(topicos_criticos) or 'Nenhum'}\n"
        f"- Tendência de desempenho: {tendencia_semanal}\n"
        f"- Sessões de estudo analisadas: {len(state.get('sessoes', []))}\n"
        f"- Simulados realizados: {len(simulados)}\n\n"
        f"Redija um parecer em português com exatamente 3 parágrafos: "
        f"(1) pontos fortes, (2) o que precisa melhorar, (3) ações concretas para a próxima semana."
    )

    llm = ChatOllama(model=ollama_model, base_url=ollama_url)
    mensagens = [
        SystemMessage(content="Você é um analista de desempenho acadêmico experiente. Seja direto, empático e propositivo."),
        HumanMessage(content=prompt),
    ]

    resposta = llm.invoke(mensagens)
    parecer = resposta.content if hasattr(resposta, "content") else str(resposta)

    return {**state, "parecer_llm": parecer}


# ---------------------------------------------------------------------------
# Nó 6 — Persistir resultado no banco
# ---------------------------------------------------------------------------

def persistir_resultado_node(state: AnalysisState) -> AnalysisState:
    """Salva o score de prontidão completo no banco de dados."""
    from assistente_estudos.db.database import SessionLocal
    from assistente_estudos.db.models import ScoreProntidao

    db = SessionLocal()
    try:
        score = ScoreProntidao(
            usuario_id=state["usuario_id"],
            score_dominio=state.get("score_dominio", 0.0),
            score_consistencia=state.get("score_consistencia", 0.0),
            score_retencao=state.get("score_retencao", 0.0),
            indice_prontidao=state.get("indice_prontidao", 0.0),
            classificacao=state.get("classificacao", ""),
            topicos_frageis=json.dumps(state.get("topicos_frageis", []), ensure_ascii=False),
            tendencia=state.get("tendencia", ""),
            parecer_llm=state.get("parecer_llm", ""),
        )
        db.add(score)
        db.commit()
        db.refresh(score)
        return {**state, "resultado_id": score.id}
    finally:
        db.close()
