"""Script simples para testar o workflow de replanejamento.

Uso:
    python scripts/test_replan.py         # apenas análise + recalculo
    python scripts/test_replan.py --persist  # tenta persistir no DB (pode falhar se DB não estiver configurado)
"""
from datetime import datetime, timedelta
import json
import sys

from assistente_estudos.nodes.replan.nodes import (
    analisar_desvio_node,
    recalcular_cronograma_node,
    persistir_replanejamento_node,
)


def make_mock_state():
    current_plan = {
        "id": "plan-123",
        "versao": 1,
        "meta_geral": "Preparar prova final",
        "horas_semanais": 8,
        "topicos": [
            {"disciplina": "Matematica", "nome": "Derivadas", "horas_estimadas": 4.0},
            {"disciplina": "Fisica", "nome": "Cinematica", "horas_estimadas": 3.0},
            {"disciplina": "Quimica", "nome": "Estequiometria", "horas_estimadas": 2.0},
        ],
    }

    sessoes_realizadas = [
        {
            "id": "s1",
            "disciplina": "Matematica",
            "topico": "Derivadas",
            "data": (datetime.now() - timedelta(days=10)).isoformat(),
            "duracao_minutos": 60,
            "concluido": True,
            "dificuldade_percebida": "media",
        },
        {
            "id": "s2",
            "disciplina": "Fisica",
            "topico": "Cinematica",
            "data": (datetime.now() - timedelta(days=5)).isoformat(),
            "duracao_minutos": 30,
            "concluido": False,
            "dificuldade_percebida": "alta",
        },
    ]

    resultados_simulados = [
        {"id": "r1", "disciplina": "Matematica", "topico": "Derivadas", "data": datetime.now().isoformat(), "taxa_acerto": 0.85},
        {"id": "r2", "disciplina": "Quimica", "topico": "Estequiometria", "data": datetime.now().isoformat(), "taxa_acerto": 0.45},
    ]

    state = {
        "usuario_id": "user-1",
        "current_plan": current_plan,
        "sessoes_realizadas": sessoes_realizadas,
        "resultados_simulados": resultados_simulados,
        "constraints": {},
    }
    return state


def pretty_print(obj, title=None):
    if title:
        print(f"=== {title} ===")
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def main():
    persist = "--persist" in sys.argv

    state = make_mock_state()
    pretty_print(state["current_plan"], "Plano atual")

    state_analisado = analisar_desvio_node(state)
    pretty_print(state_analisado.get("desvios", []), "Desvios identificados")

    state_recalc = recalcular_cronograma_node(state_analisado)
    pretty_print(state_recalc.get("updated_plan", {}), "Novo cronograma")

    if persist:
        print("Tentando persistir (pode falhar se o DB não estiver configurado)...")
        try:
            state_persist = persistir_replanejamento_node(state_recalc)
            pretty_print({"replan_id": state_persist.get("replan_id"), "erro": state_persist.get("erro")}, "Persistência")
        except Exception as e:
            print("Erro ao persistir:", e)


if __name__ == "__main__":
    main()
