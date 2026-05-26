"""Serviço de criação do cronograma de estudos com revisão espaçada."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, List


def create_schedule(
    topics: List[Any],
    exam_date: date,
    hours_per_day: int,
) -> list:
    """Distribui os tópicos em dias de estudo até a data do exame.

    Cada tópico pode ocupar mais de um dia se suas horas estimadas
    superarem hours_per_day. Também insere revisões espaçadas (D+1, D+7, D+14).
    """
    current_day = date.today()
    if exam_date is None:
        exam_date = current_day + timedelta(days=30)
    schedule = []

    for topic in topics:
        if current_day > exam_date:
            break

        remaining_hours = topic.estimated_hours
        day_offset = 0

        while remaining_hours > 0:
            study_date = current_day + timedelta(days=day_offset)
            if study_date > exam_date:
                break

            hours_today = min(remaining_hours, hours_per_day)
            remaining_hours -= hours_today

            schedule.append({
                "date": study_date.isoformat(),
                "type": "study",
                "order": topic.order,
                "topic": topic.title,
                "difficulty": topic.difficulty,
                "hours": hours_today,
                "learning_objectives": topic.learning_objectives,
                "study_tips": topic.study_tips,
                "completion_criteria": topic.completion_criteria,
            })
            day_offset += 1

        last_study_day = current_day + timedelta(days=day_offset - 1)
        for delta, label in [(1, "D+1"), (7, "D+7"), (14, "D+14")]:
            review_date = last_study_day + timedelta(days=delta)
            if review_date <= exam_date:
                schedule.append({
                    "date": review_date.isoformat(),
                    "type": "review",
                    "order": topic.order,
                    "topic": topic.title,
                    "review_type": label,
                    "difficulty": topic.difficulty,
                })

        current_day += timedelta(days=day_offset)

    schedule.sort(key=lambda x: x["date"])
    return schedule
