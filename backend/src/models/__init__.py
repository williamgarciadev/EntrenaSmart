"""
Models - Modelos de dominio con SQLAlchemy
===========================================

Este módulo contiene los modelos de base de datos:
- Base: Clase base de SQLAlchemy
- Student: Modelo de alumno
- Training: Modelo de entrenamiento programado
- TrainingDayConfig: Configuración semanal de entrenamientos
- Feedback: Modelo de feedback post-entrenamiento
- MessageSchedule: Modelo de programación de mensajes
"""
from backend.src.models.base import Base, engine, SessionLocal, init_db, get_db
from backend.src.models.student import Student
from backend.src.models.training import Training
from backend.src.models.training_day_config import TrainingDayConfig
from backend.src.models.feedback import Feedback
from backend.src.models.message_schedule import MessageSchedule
from backend.src.models.message_template import MessageTemplate
from backend.src.models.weekly_reminder_config import WeeklyReminderConfig

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "init_db",
    "get_db",
    "Student",
    "Training",
    "TrainingDayConfig",
    "Feedback",
    "MessageSchedule",
    "MessageTemplate",
    "WeeklyReminderConfig",
]

