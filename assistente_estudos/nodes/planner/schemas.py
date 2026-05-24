"""Schemas Pydantic para saída estruturada do LLM no planner."""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field


class SuggestedResource(BaseModel):
    type: str
    description: str


class Topic(BaseModel):
    order: int
    title: str
    description: str
    prerequisites: List[str]
    difficulty: int = Field(..., ge=1, le=5)
    estimated_hours: float
    learning_objectives: List[str]
    study_tips: List[str]
    suggested_resource: SuggestedResource
    completion_criteria: str


class GeneratedTopics(BaseModel):
    plan_title: str
    summary: str
    total_estimated_hours: str
    personalized_message: str
    topics: List[Topic]
