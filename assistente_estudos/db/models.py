"""Modelos do banco de dados do Assistente de Estudos."""

from __future__ import annotations

import uuid
import json
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    sessoes = relationship("SessaoEstudo", back_populates="usuario")
    simulados = relationship("ResultadoSimulado", back_populates="usuario")
    scores = relationship("ScoreProntidao", back_populates="usuario")
    planos = relationship("StudyPlan", back_populates="usuario")


class SessaoEstudo(Base):
    """Registra cada sessão de estudo do usuário."""

    __tablename__ = "sessoes_estudo"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String, ForeignKey("usuarios.id"), nullable=False)
    disciplina = Column(String, nullable=False)
    topico = Column(String, nullable=False)
    data = Column(DateTime, nullable=False, default=datetime.utcnow)
    duracao_minutos = Column(Integer, nullable=False)
    concluido = Column(Boolean, default=True)
    dificuldade_percebida = Column(Integer)  # escala 1-5

    usuario = relationship("Usuario", back_populates="sessoes")

class StudyPlan(Base):
    """Plano de estudo gerado pelo agente planner."""

    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(String, ForeignKey("usuarios.id"), nullable=True)
    discipline = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    level = Column(String(20), nullable=False)
    exam_date = Column(String(10), nullable=False)
    hours_per_day = Column(Integer, nullable=False)

    plan_title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)
    total_estimated_hours = Column(String(50), nullable=False)
    personalized_message = Column(Text, nullable=False)

    topics_json = Column(Text, nullable=False)
    study_plan_json = Column(Text, nullable=False)

    criado_em = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="planos")

    def set_topics(self, topics: list) -> None:
        self.topics_json = json.dumps(topics, ensure_ascii=False)

    def get_topics(self) -> list:
        return json.loads(self.topics_json)

    def set_study_plan(self, study_plan: list) -> None:
        self.study_plan_json = json.dumps(study_plan, ensure_ascii=False)

    def get_study_plan(self) -> list:
        return json.loads(self.study_plan_json)


class ResultadoSimulado(Base):
    """Registra o resultado de cada simulado realizado."""

    __tablename__ = "resultados_simulados"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String, ForeignKey("usuarios.id"), nullable=False)
    disciplina = Column(String, nullable=False)
    topico = Column(String, nullable=False)
    data = Column(DateTime, nullable=False, default=datetime.utcnow)
    total_questoes = Column(Integer, nullable=False)
    acertos = Column(Integer, nullable=False)
    taxa_acerto = Column(Float, nullable=False)  # 0.0 a 1.0
    nivel_dificuldade = Column(String, default="intermediario")  # basico/intermediario/avancado

    usuario = relationship("Usuario", back_populates="simulados")


class ScoreProntidao(Base):
    """Armazena o resultado completo de cada análise de desempenho."""

    __tablename__ = "scores_prontidao"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String, ForeignKey("usuarios.id"), nullable=False)
    score_dominio = Column(Float, nullable=False)
    score_consistencia = Column(Float, nullable=False)
    score_retencao = Column(Float, nullable=False)
    indice_prontidao = Column(Float, nullable=False)
    classificacao = Column(String, nullable=False)  # risco_alto / moderado / alta_probabilidade
    topicos_frageis = Column(Text)  # JSON serializado
    tendencia = Column(String)  # melhorando / estavel / piorando
    parecer_llm = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="scores")
