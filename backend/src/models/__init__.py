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
from src.models.base import Base, engine, SessionLocal, init_db, get_db
from src.models.student import Student
from src.models.training import Training
from src.models.training_day_config import TrainingDayConfig
from src.models.feedback import Feedback
from src.models.message_schedule import MessageSchedule

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
]

