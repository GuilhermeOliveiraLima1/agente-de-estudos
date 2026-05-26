"""Os nós do workflow de geração de relatório.

Fluxo:
    coletar_dados → gerar_relatorio → exportar_relatorio → persistir_relatorio
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from langchain_ollama import ChatOllama

from assistente_estudos.config import (
    EXPORTS_DIR,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)

from assistente_estudos.nodes.report.state import ReportState

from assistente_estudos.nodes.report.tools import (
    calcular_media_notas,
    analisar_frequencia,
    gerar_recomendacoes,
    formatar_relatorio,
)

# ==========================================
# LLM (Ollama)
# ==========================================
llm = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0.7,
)

# ==========================================
# NODE 1 — COLETAR DADOS
# ==========================================
def coletar_dados_node(state: ReportState) -> ReportState:
    try:
        analysis_output = state.get("analysis_output", {}) or {}
        simulation_output = state.get("simulation_output", {}) or {}
        current_plan = state.get("current_plan", {}) or {}

        report_data = {
            "analysis_summary": {
                "details": analysis_output,
            },
            "simulation_summary": {
                "details": simulation_output,
            },
            "plan_summary": {
                "details": current_plan,
            },
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "usuario_id": state.get("usuario_id"),
        }

        state["report_data"] = report_data

    except Exception as e:
        state["erro"] = f"Erro ao coletar dados: {str(e)}"

    return state


# NODE 2 — GERAR RELATÓRIO
# ==========================================
def gerar_relatorio_node(
    state: ReportState,
) -> ReportState:
    """
    Gera relatório usando:
    - Tools
    - LLM
    """

    try:

        report_data = (
            state.get(
                "report_data",
                {},
            )
            or {}
        )

        simulation_output = (
            state.get(
                "simulation_output",
                {},
            )
            or {}
        )

        analysis_output = (
            state.get(
                "analysis_output",
                {},
            )
            or {}
        )

        # ==================================
        # EXECUTANDO TOOLS
        # ==================================

        media = simulation_output.get(
            "media",
            0,
        )

        notas = [
            media,
            simulation_output.get(
                "acertos",
                0,
            ),
        ]

        frequencia = analysis_output.get(
            "frequencia_estudos",
            0,
        )

        resultado_media = (
            calcular_media_notas.func(
                notas
            )
        )

        resultado_frequencia = (
            analisar_frequencia.func(
                frequencia
            )
        )

        resultado_recomendacoes = (
            gerar_recomendacoes.func(
                media
            )
        )

        # ==================================
        # PROMPT
        # ==================================

        prompt = f"""
        Você é um assistente educacional
        especializado em análise de
        desempenho acadêmico.

        Os dados abaixo foram processados
        por ferramentas analíticas do sistema.

        RESULTADOS DAS TOOLS:

        {resultado_media}

        {resultado_frequencia}

        {resultado_recomendacoes}

        DADOS COMPLETOS:

        {json.dumps(report_data, ensure_ascii=False, indent=2)}

        Gere um relatório contendo:

        1. Resumo Executivo
        2. Análise de Desempenho
        3. Pontos Fortes
        4. Pontos de Melhoria
        5. Recomendações
        6. Próximos Passos

        Regras:
        - Português do Brasil
        - Linguagem clara
        - Relatório organizado
        - Relatório profissional
        - Use os resultados das tools
        """

        response = llm.invoke(prompt)

        texto_relatorio = str(
            response.content
        )

        # ==================================
        # TOOL DE FORMATAÇÃO
        # ==================================

        relatorio_final = (
            formatar_relatorio.func(
                texto_relatorio
            )
        )

        state["report_text"] = (
            relatorio_final
        )

        # ==================================
        # RESULTADOS DAS TOOLS
        # ==================================

        state["tool_results"] = {
            "media":
                resultado_media,

            "frequencia":
                resultado_frequencia,

            "recomendacoes":
                resultado_recomendacoes,
        }

    except Exception as e:

        state["erro"] = (
            f"Erro ao gerar relatório: {str(e)}"
        )

    return state



# ==========================================
# NODE 3 — EXPORTAR RELATÓRIO (TXT)
# ==========================================
def exportar_relatorio_node(state: ReportState) -> ReportState:
    try:
        report_text = state.get("report_text", "") or ""

        export_dir = Path(EXPORTS_DIR)
        export_dir.mkdir(parents=True, exist_ok=True)

        report_id = uuid4().hex

        txt_path = export_dir / f"relatorio_{report_id}.txt"

        with txt_path.open("w", encoding="utf-8") as arquivo:
            arquivo.write("Assistente de Estudos - Relatório\n")
            arquivo.write(f"Gerado em: {datetime.utcnow().isoformat()}Z\n\n")
            arquivo.write(report_text)

        state["export_txt_path"] = str(txt_path)
        state["report_id"] = report_id

    except Exception as e:
        state["erro"] = f"Erro ao exportar relatório: {str(e)}"

    return state


# ==========================================
# NODE 4 — PERSISTIR RELATÓRIO (JSON)
# ==========================================
def persistir_relatorio_node(state: ReportState) -> ReportState:
    try:
        export_dir = Path(EXPORTS_DIR)
        export_dir.mkdir(parents=True, exist_ok=True)

        report_id = state.get("report_id")

        registro = {
            "report_id": report_id,
            "usuario_id": state.get("usuario_id"),
            "report_text": state.get("report_text"),
            "tool_results": state.get("tool_results"),
            "report_data": state.get("report_data"),
            "export_txt_path": state.get("export_txt_path"),
            "created_at": datetime.utcnow().isoformat() + "Z",
        }

        json_path = export_dir / f"relatorio_{report_id}.json"

        with json_path.open("w", encoding="utf-8") as arquivo:
            json.dump(registro, arquivo, ensure_ascii=False, indent=2)

        state["metadata_path"] = str(json_path)

    except Exception as e:
        state["erro"] = f"Erro ao persistir relatório: {str(e)}"

    return state