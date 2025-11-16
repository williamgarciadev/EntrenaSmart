"""
Services - Capa de lógica de negocio
=====================================

Este módulo contiene la lógica de negocio de la aplicación,
separada de los handlers de Telegram y del acceso a datos.

Servicios disponibles:
- StudentService: Gestión de alumnos
- TrainingService: Gestión de entrenamientos
- FeedbackService: Gestión de feedback
- ReportService: Generación de reportes
- SchedulerService: Programación de tareas automáticas
"""
from src.services.student_service import StudentService
from src.services.training_service import TrainingService
from src.services.feedback_service import FeedbackService
from src.services.report_service import ReportService
from src.services.scheduler_service import SchedulerService

__all__ = [
    "StudentService",
    "TrainingService",
    "FeedbackService",
    "ReportService",
    "SchedulerService",
]

