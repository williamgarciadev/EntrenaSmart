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
from src.repositories.base_repository import BaseRepository
from src.repositories.student_repository import StudentRepository
from src.repositories.training_repository import TrainingRepository
from src.repositories.feedback_repository import FeedbackRepository

__all__ = [
    "BaseRepository",
    "StudentRepository",
    "TrainingRepository",
    "FeedbackRepository",
]

