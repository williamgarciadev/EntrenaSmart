# -*- coding: utf-8 -*-
"""
Modelo de Configuración Diaria de Entrenamiento
================================================

Define la configuración semanal del entrenador:
qué tipo de entrenamiento y ubicación para cada día de la semana.
"""
from typing import Optional, List
from datetime import datetime

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.models.base import Base


class TrainingDayConfig(Base):
    """
    Configuración de entrenamiento por día de la semana.

    Define qué tipo de entrenamiento y ubicación corresponden a cada día
    de la semana. Esta configuración es establecida por el entrenador
    y aplica a todos los estudiantes.

    Ejemplo:
        - Lunes: Pierna, 2do Piso
        - Miércoles: Funcional, 4to Piso
        - Viernes: Espalda, 2do Piso
    """

    __tablename__ = "training_day_configs"

    # Configuración del día
    weekday: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True,
        comment="Día de la semana (0=Lunes, 6=Domingo)"
    )

    weekday_name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Nombre del día en español (ej: 'Lunes')"
    )

    session_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Tipo de entrenamiento (ej: 'Pierna', 'Funcional', 'Espalda', 'Brazo')"
    )

    location: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Ubicación/piso donde se realiza (ej: '2do Piso', '4to Piso')"
    )

    # Estado
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        comment="Indica si la configuración está activa"
    )

    def __init__(
        self,
        weekday: int,
        weekday_name: str,
        session_type: str,
        location: str,
        is_active: bool = True
    ):
        """
        Inicializa una configuración de entrenamiento diario.

        Args:
            weekday: Día de la semana (0-6)
            weekday_name: Nombre del día en español
            session_type: Tipo de entrenamiento
            location: Ubicación/piso
            is_active: Si está activa
        """
        self.weekday = weekday
        self.weekday_name = weekday_name
        self.session_type = session_type
        self.location = location
        self.is_active = is_active

    def deactivate(self) -> None:
        """Desactiva la configuración."""
        self.is_active = False

    def activate(self) -> None:
        """Activa la configuración."""
        self.is_active = True

    def __str__(self) -> str:
        """Representación en string."""
        return (
            f"TrainingDayConfig(weekday={self.weekday_name}, "
            f"type={self.session_type}, location={self.location})"
        )
