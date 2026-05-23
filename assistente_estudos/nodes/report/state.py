"""Estado tipado exclusivo do workflow de geração de relatório."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class ReportState(TypedDict, total=False):
    # --- Entrada ---
    usuario_id: str
    analysis_output: Dict[str, Any]    # resultado da análise de desempenho
    simulation_output: Dict[str, Any]  # resultado dos simulados
    current_plan: Dict[str, Any]       # cronograma atual

    # --- Saída ---
    report_data: Dict[str, Any]        # dados estruturados do relatório
    report_text: str                   # texto gerado pelo LLM
    export_path: Optional[str]         # caminho do arquivo exportado (PDF/TXT)
    relatorio_id: str                  # ID do registro salvo no banco

    # Erro, se houver
    erro: Optional[str]
