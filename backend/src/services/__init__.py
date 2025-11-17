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
from backend.src.services.student_service import StudentService
from backend.src.services.training_service import TrainingService
from backend.src.services.feedback_service import FeedbackService
from backend.src.services.report_service import ReportService
from backend.src.services.scheduler_service import SchedulerService
from backend.src.services.schedule_service import ScheduleService

__all__ = [
    "StudentService",
    "TrainingService",
    "FeedbackService",
    "ReportService",
    "SchedulerService",
    "ScheduleService",
]

