"""Modelos do banco de dados do Assistente de Estudos."""

from __future__ import annotations

import uuid
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
