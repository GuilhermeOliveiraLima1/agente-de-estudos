"""Schemas Pydantic para saída estruturada do LLM no fluxo de simulação."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class SimulationQuestion(BaseModel):
    topico: str
    disciplina: str
    pergunta: str
    alternativas: List[str] = Field(..., min_length=4, max_length=4)
    resposta_correta: str
    dificuldade: str


class GeneratedSimulationQuestions(BaseModel):
    questoes: List[SimulationQuestion]