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
from assistente_estudos.nodes.report.tools import TOOLS

# =========================
# LLM (Ollama)
# =========================
llm = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0.7,
)


# =========================
# Helpers
# =========================
def _build_section(title: str, text: str) -> str:
    return f"{title}\n{'=' * len(title)}\n{text.strip()}\n\n"


def _summarize_metrics(source: dict[str, Any], label: str) -> str:
    if not source:
        return f"Nenhum dado de {label} disponível."

    lines: list[str] = []

    for key, value in source.items():
        if isinstance(value, dict):
            lines.append(
                f"- {key}: "
                f"{', '.join(f'{subkey}={subvalue}' for subkey, subvalue in value.items())}"
            )
        else:
            lines.append(f"- {key}: {value}")

    return "\n".join(lines)


def _safe_extract_summary(data: dict[str, Any], fallback: str) -> str:
    if not data:
        return fallback

    if isinstance(data, str):
        return data

    if "summary" in data:
        return str(data["summary"])

    return (
        ", ".join(
            f"{k}: {v}"
            for k, v in data.items()
            if not isinstance(v, dict)
        )
        or fallback
    )


# =========================
# Nodes
# =========================
def coletar_dados_node(state: ReportState) -> ReportState:
    """Consolida os dados em report_data."""

    try:
        analysis_output = state.get("analysis_output", {}) or {}
        simulation_output = state.get("simulation_output", {}) or {}
        current_plan = state.get("current_plan", {}) or {}

        report_data = {
            "analysis_summary": {
                "headline": _safe_extract_summary(
                    analysis_output,
                    "Nenhuma análise disponível."
                ),
                "details": analysis_output,
            },
            "simulation_summary": {
                "headline": _safe_extract_summary(
                    simulation_output,
                    "Nenhuma simulação disponível."
                ),
                "details": simulation_output,
            },
            "plan_summary": {
                "headline": _safe_extract_summary(
                    current_plan,
                    "Nenhum cronograma disponível."
                ),
                "details": current_plan,
            },
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "usuario_id": state.get("usuario_id"),
        }

        state["report_data"] = report_data

    except Exception as e:
        state["erro"] = f"Erro ao coletar dados: {str(e)}"

    return state


def gerar_relatorio_node(state: ReportState) -> ReportState:
    """Gera o relatório usando LLM via Ollama."""

    try:
        report_data = state.get("report_data", {}) or {}

        prompt = f"""
            Você é um assistente educacional especializado
            em análise de desempenho acadêmico.

            Você possui acesso a ferramentas externas
            para calcular métricas, analisar frequência
            e gerar recomendações.

            Sempre utilize as ferramentas disponíveis
            quando necessário.

            Gere um relatório com:

            1. Resumo Executivo
            2. Análise de Desempenho
            3. Pontos de Melhoria
            4. Próximos Passos

            Dados:
            {json.dumps(report_data, ensure_ascii=False, indent=2)}

            Regras:
            - Português do Brasil
            - Linguagem clara
            - Relatório organizado
            - Recomendações práticas
            """

        llm_with_tools = llm.bind_tools(TOOLS)

        response = llm_with_tools.invoke(prompt)

        state["report_text"] = response.content

    except Exception as e:
        state["erro"] = f"Erro ao gerar relatório: {str(e)}"

    return state


def exportar_relatorio_node(state: ReportState) -> ReportState:
    """Exporta o relatório para TXT."""

    try:
        report_text = state.get("report_text", "") or ""

        export_dir = Path(EXPORTS_DIR)
        export_dir.mkdir(parents=True, exist_ok=True)

        report_id = uuid4().hex

        export_path = export_dir / f"relatorio_{report_id}.txt"

        with export_path.open("w", encoding="utf-8") as arquivo:
            arquivo.write("Assistente de Estudos - Relatório\n")
            arquivo.write(
                f"Gerado em: {datetime.utcnow().isoformat()}Z\n\n"
            )
            arquivo.write(report_text)

        state["export_path"] = str(export_path)

    except Exception as e:
        state["erro"] = f"Erro ao exportar relatório: {str(e)}"

    return state


def persistir_relatorio_node(state: ReportState) -> ReportState:
    """Salva o relatório em um arquivo JSON."""

    try:
        relatorio_id = uuid4().hex

        export_path = state.get("export_path")
        report_text = state.get("report_text", "") or ""
        report_data = state.get("report_data", {}) or {}

        registro = {
            "id": relatorio_id,
            "usuario_id": state.get("usuario_id"),
            "export_path": export_path,
            "report_text": report_text,
            "report_data": report_data,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }

        export_dir = Path(EXPORTS_DIR)
        export_dir.mkdir(parents=True, exist_ok=True)

        registro_path = export_dir / f"relatorio_{relatorio_id}.json"

        with registro_path.open("w", encoding="utf-8") as arquivo:
            json.dump(
                registro,
                arquivo,
                ensure_ascii=False,
                indent=2,
            )

        state["relatorio_id"] = relatorio_id

    except Exception as e:
        state["erro"] = f"Erro ao persistir relatório: {str(e)}"

    return state