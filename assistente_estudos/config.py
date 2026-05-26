"""Configurações centrais do Assistente de Planejamento de Estudos Inteligente."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = DATA_DIR / "exports"
STATES_DIR = DATA_DIR / "states"

APP_TITLE = "Assistente de Planejamento de Estudos Inteligente"
API_PREFIX = "/api"
API_HOST = "0.0.0.0"
API_PORT = 8000

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://estudos:estudos123@localhost:5432/assistente_estudos")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
