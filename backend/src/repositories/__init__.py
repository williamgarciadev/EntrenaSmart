"""
Repositories - Patrón Repository para acceso a datos
=====================================================

Este módulo implementa el patrón Repository para abstracción
de acceso a datos, separando la lógica de negocio de las
operaciones de persistencia.

Repositorios disponibles:
- BaseRepository: Repositorio genérico con operaciones CRUD
- StudentRepository: Operaciones específicas de alumnos
- TrainingRepository: Operaciones específicas de entrenamientos
- FeedbackRepository: Operaciones específicas de feedback
"""
from backend.src.repositories.base_repository import BaseRepository
from backend.src.repositories.student_repository import StudentRepository
from backend.src.repositories.training_repository import TrainingRepository
from backend.src.repositories.feedback_repository import FeedbackRepository
from backend.src.repositories.schedule_repository import ScheduleRepository

__all__ = [
    "BaseRepository",
    "StudentRepository",
    "TrainingRepository",
    "FeedbackRepository",
    "ScheduleRepository",
]

