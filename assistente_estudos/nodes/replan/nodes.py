"""Os nós do workflow de replanejamento.

Fluxo:
    analisar_desvio → recalcular_cronograma → persistir_replanejamento
"""

from __future__ import annotations
from typing import Any, Dict, List, Set
from datetime import datetime, timedelta
import uuid

from assistente_estudos.nodes.replan.state import ReplanState


def analisar_desvio_node(state: ReplanState) -> ReplanState:
    """Compara o plano original com o que foi realizado e lista os desvios.

    Apenas compara sessões realizadas e resultados simulados com o plano atual
    e produz uma lista de desvios detectados.
    """
    current_plan = state.get("current_plan", {})
    sessoes_realizadas = state.get("sessoes_realizadas", [])
    resultados_simulados = state.get("resultados_simulados", [])

    desvios_identificados: List[Dict[str, Any]] = []

    topicos_estudados: Set[str] = set()
    horas_estudadas_por_topico: Dict[str, float] = {}
    topicos_planejados = current_plan.get("topicos", [])

    for sessao in sessoes_realizadas:
        topico = sessao.get("topico", "")
        disciplina = sessao.get("disciplina", "")
        key = f"{disciplina}: {topico}"
        topicos_estudados.add(key)

        duracao = float(sessao.get("duracao_minutos", 0)) / 60.0
        horas_estudadas_por_topico[key] = horas_estudadas_por_topico.get(key, 0.0) + duracao

    for topico in topicos_planejados:
        nome_topico = f"{topico.get('disciplina', '')}: {topico.get('nome', '')}"

        if nome_topico not in topicos_estudados:
            desvios_identificados.append({
                "tipo": "topico_nao_iniciado",
                "topico": nome_topico,
                "disciplina": topico.get("disciplina"),
                "Severidade": "alta",
                "descricao": f"O tópico '{nome_topico}' não foi iniciado ainda."
            })
        else:
            horas_real = horas_estudadas_por_topico.get(nome_topico, 0.0)
            horas_planejadas = float(topico.get("horas_estimadas", 0.0) or 0.0)
            if horas_planejadas > 0 and horas_real < horas_planejadas * 0.8:
                desvios_identificados.append({
                    "tipo": "carga_horaria_insuficiente",
                    "topico": nome_topico,
                    "disciplina": topico.get("disciplina"),
                    "horas_planejadas": horas_planejadas,
                    "horas_realizadas": horas_real,
                    "Severidade": "media",
                    "descricao": f"A carga horária prevista era {horas_planejadas}h, mas foram realizadas apenas {horas_real:.1f}h."
                })

    temas_fragilizados: Dict[str, List[float]] = {}
    for resultado in resultados_simulados:
        topico = resultado.get("topico", "")
        taxa = float(resultado.get("taxa_acerto", 0.0) or 0.0)
        temas_fragilizados.setdefault(topico, []).append(taxa)

    for topico, taxas in temas_fragilizados.items():
        if not taxas:
            continue
        media = sum(taxas) / len(taxas)
        if media < 0.7:
            desvios_identificados.append({
                "tipo": "desempenho_insuficiente",
                "topico": topico,
                "media_taxa_acerto": media,
                "Severidade": "alta" if media < 0.5 else "media",
                "descricao": f"A taxa de acerto média em '{topico}' é {media*100:.0f}%, abaixo do esperado."
            })

    sessoes_incompletas = [s for s in sessoes_realizadas if not s.get("concluido", False)]
    if sessoes_incompletas:
        desvios_identificados.append({
            "tipo": "sessoes_incompletas",
            "quantidade": len(sessoes_incompletas),
            "Severidade": "baixa",
            "descricao": f"{len(sessoes_incompletas)} sessões foram iniciadas mas não concluídas."
        })

    return {**state, "desvios": desvios_identificados}


def recalcular_cronograma_node(state: ReplanState) -> ReplanState:
    """Gera um novo cronograma ajustado com base nos desvios identificados."""

    current_plan = state.get("current_plan", {})
    desvios = state.get("desvios", [])

    novo_cronograma = {
        "id": current_plan.get("id", str(uuid.uuid4())),
        "versao": (current_plan.get("versao") or 0) + 1,
        "data_criacao": datetime.now().isoformat(),
        "data_modificacao": datetime.now().isoformat(),
        "topicos": [],
        "meta_geral": current_plan.get("meta_geral", ""),
        "horas_semanais": current_plan.get("horas_semanais", 0),
    }

    desvios_altos = [d for d in desvios if d.get("Severidade") == "alta"]

    topicos_priorizados: List[Dict[str, Any]] = []
    topicos_originais = [dict(t) for t in current_plan.get("topicos", [])]
    topicos_existentes = {f"{t.get('disciplina', '')}: {t.get('nome', '')}": dict(t) for t in topicos_originais}

    for desvio in desvios_altos:
        topico_nome = desvio.get("topico", "")
        if topico_nome in topicos_existentes:
            topico = dict(topicos_existentes[topico_nome])
            topico["prioridade"] = "alta"
            topico["status"] = "em_andamento"
            if desvio.get("tipo") == "carga_horaria_insuficiente":
                horas_adicionais = float(desvio.get("horas_planejadas", 0) or 0) - float(desvio.get("horas_realizadas", 0) or 0)
                topico["horas_estimadas"] = float(desvio.get("horas_planejadas", 0) or 0) + horas_adicionais * 1.5
            topicos_priorizados.append(topico)
        else:
            topicos_priorizados.append({
                "disciplina": desvio.get("disciplina", ""),
                "nome": desvio.get("topico", ""),
                "prioridade": "alta",
                "status": "pendente",
                "horas_estimadas": 2.0,
                "desvio_detectado": desvio.get("tipo"),
            })

    topicos_com_desvios = set(d.get("topico", "") for d in desvios)
    for topico in topicos_originais:
        key = f"{topico.get('disciplina')}: {topico.get('nome')}"
        if key not in topicos_com_desvios:
            t = dict(topico)
            t["prioridade"] = t.get("prioridade", "media")
            t["status"] = t.get("status", "pendente")
            topicos_priorizados.append(t)

    prioridade_ordem = {"alta": 0, "media": 1, "baixa": 2}
    topicos_priorizados.sort(key=lambda t: prioridade_ordem.get(t.get("prioridade", "media"), 1))

    data_atual = datetime.now()
    for i, topico in enumerate(topicos_priorizados):
        dias_offset = i * 7
        data_inicio = data_atual + timedelta(days=dias_offset)
        data_fim = data_inicio + timedelta(days=7)
        topico["data_inicio"] = data_inicio.isoformat()
        topico["data_fim"] = data_fim.isoformat()

    novo_cronograma["topicos"] = topicos_priorizados

    racional = gerar_racional_replanejamento(desvios, topicos_priorizados)
    novo_cronograma["racional"] = racional

    return {**state, "updated_plan": novo_cronograma}


def gerar_racional_replanejamento(desvios: List[Dict[str, Any]], topicos: List[Dict[str, Any]]) -> str:
    """Gera um texto explicativo do replanejamento."""
    total_desvios = len(desvios)
    desvios_altos = len([d for d in desvios if d.get("Severidade") == "alta"])

    racional = f"""Replanejamento realizado em {datetime.now().strftime('%d/%m/%Y')}.

Total de {total_desvios} desvios identificados, sendo {desvios_altos} de alta prioridade.

Ações tomadas:
- Tópicos com baixo desempenho foram priorizados para as próximas semanas
- Carga horária foi redistribuída conforme a disponibilidade
- Novos prazos foram atribuídos para garantir acompanhamento

Próximos passos recomendados:
- Focar primeiro nos tópicos com prioridade alta
- Realizar novos simulados após completar os tópicos prioritários
- Revisar conteúdo antes de avançar para novos tópicos
"""
    return racional


def persistir_replanejamento_node(state: ReplanState) -> ReplanState:
    """Salva o novo cronograma e o registro de replanejamento no banco.

    Tentativa prudente de persistir sessões baseadas no `updated_plan`.
    Em caso de erro a função registra `erro` no estado e garante fechamento da sessão.
    """
    from assistente_estudos.db.database import SessionLocal
    from assistente_estudos.db.models import SessaoEstudo

    updated_plan = state.get("updated_plan", {})
    usuario_id = state.get("usuario_id") or state.get("usuario") or state.get("session_id")
    replan_id = str(uuid.uuid4())

    db = SessionLocal()
    try:
        for topico in updated_plan.get("topicos", []):
            data_inicio_iso = topico.get("data_inicio")
            data_obj = None
            if data_inicio_iso:
                try:
                    data_obj = datetime.fromisoformat(data_inicio_iso)
                except Exception:
                    data_obj = None

            duracao_min = None
            if topico.get("horas_estimadas") is not None:
                try:
                    duracao_min = int(float(topico.get("horas_estimadas", 0)) * 60)
                except Exception:
                    duracao_min = None

            sessao_kwargs = {
                "id": str(uuid.uuid4()),
                "usuario_id": usuario_id,
                "disciplina": topico.get("disciplina", ""),
                "topico": topico.get("nome", ""),
                "data": data_obj,
                "duracao_minutos": duracao_min,
                "concluido": False,
            }
            sessao_kwargs = {k: v for k, v in sessao_kwargs.items() if v is not None}
            try:
                sessao = SessaoEstudo(**sessao_kwargs)
                db.add(sessao)
            except Exception:
                continue

        db.commit()
        return {**state, "replan_id": replan_id}
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        return {**state, "erro": str(e)}
    finally:
        db.close()
