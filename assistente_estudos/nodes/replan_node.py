"""Ponte entre o grafo principal e o sub-grafo de replanejamento."""

from __future__ import annotations

from assistente_estudos.core.state import StudyState


def replan_node(state: StudyState) -> StudyState:
    """Executa o workflow de replanejamento do cronograma."""

    from assistente_estudos.nodes.replan.graph import build_replan_graph
    from assistente_estudos.db.database import SessionLocal
    from assistente_estudos.db.models import SessaoEstudo, ResultadoSimulado

    usuario_id = state.get("session_id") or state.get("usuario_id")

    db = SessionLocal()
    sessoes_realizadas = []
    resultados_simulados = []
    try:
        sessoes = db.query(SessaoEstudo).filter(SessaoEstudo.usuario_id == usuario_id).all()
        sessoes_realizadas = [
            {
                "id": s.id,
                "disciplina": s.disciplina,
                "topico": s.topico,
                "data": s.data.isoformat() if getattr(s, "data", None) else None,
                "duracao_minutos": getattr(s, "duracao_minutos", None),
                "concluido": getattr(s, "concluido", False),
                "dificuldade_percebida": getattr(s, "dificuldade_percebida", None),
            }
            for s in sessoes
        ]

        resultados = db.query(ResultadoSimulado).filter(ResultadoSimulado.usuario_id == usuario_id).all()
        resultados_simulados = [
            {
                "id": r.id,
                "disciplina": r.disciplina,
                "topico": r.topico,
                "data": r.data.isoformat() if getattr(r, "data", None) else None,
                "taxa_acerto": getattr(r, "taxa_acerto", None),
                "nivel_dificuldade": getattr(r, "nivel_dificuldade", None),
            }
            for r in resultados
        ]
    except Exception:
        # em caso de erro no DB, manter listas vazias e prosseguir
        sessoes_realizadas = []
        resultados_simulados = []
    finally:
        try:
            db.close()
        except Exception:
            pass




    graph = build_replan_graph()
    resultado = graph.invoke({
        "usuario_id": state.get("usuario_id") or state.get("session_id"),
        "current_plan": state.get("current_plan", {}),
        "replanning_reason": state.get("replanning_reason", "Ajustes baseados no progresso real"),
        "sessoes_realizadas": sessoes_realizadas,
        "resultados_simulados": resultados_simulados,
        "constraints": state.get("constraints", {}),
    })

    return {
        **state,
        "current_plan": resultado.get("updated_plan", state.get("current_plan", {})),
        "replan_id": resultado.get("replan_id"),
        "desvios": resultado.get("desvios", []),
    }
