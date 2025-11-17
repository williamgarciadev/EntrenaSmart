# -*- coding: utf-8 -*-
"""
Modelo de Programación de Mensajes
===================================

Define la entidad de programación automática de envío de mensajes
en la base de datos.
"""
from typing import List, Optional
from sqlalchemy import ForeignKey, Integer, Boolean, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.models.base import Base


class MessageSchedule(Base):
    """
    Modelo de Programación de Mensajes.

    Representa una programación para envío automático de mensajes
    a estudiantes en horarios específicos de la semana.
    """

    __tablename__ = "message_schedules"

    # Referencias
    template_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="ID de la plantilla de mensaje a enviar"
    )

    student_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="ID del estudiante destinatario"
    )

    # Configuración de horario
    hour: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Hora del día (0-23)"
    )

    minute: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Minuto de la hora (0-59)"
    )

    days_of_week: Mapped[List[int]] = mapped_column(
        ARRAY(Integer),
        nullable=False,
        comment="Días de la semana (0=Lunes, 6=Domingo)"
    )

    # Estado
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Indica si la programación está activa"
    )

    def __init__(
        self,
        template_id: int,
        student_id: int,
        hour: int,
        minute: int,
        days_of_week: List[int],
        is_active: bool = True
    ):
        """
        Inicializa una nueva programación de mensaje.

        Args:
            template_id: ID de la plantilla
            student_id: ID del estudiante
            hour: Hora del día (0-23)
            minute: Minuto (0-59)
            days_of_week: Lista de días de la semana
            is_active: Si está activa
        """
        self.template_id = template_id
        self.student_id = student_id
        self.hour = hour
        self.minute = minute
        self.days_of_week = days_of_week
        self.is_active = is_active

    def deactivate(self) -> None:
        """Desactiva la programación."""
        self.is_active = False

    def activate(self) -> None:
        """Activa la programación."""
        self.is_active = True

    @property
    def time_str(self) -> str:
        """
        Retorna el horario en formato HH:MM.

        Returns:
            str: Horario formateado
        """
        return f"{self.hour:02d}:{self.minute:02d}"

    def __str__(self) -> str:
        """Representación en string de la programación."""
        return (
            f"MessageSchedule(id={self.id}, template_id={self.template_id}, "
            f"student_id={self.student_id}, time={self.time_str}, "
            f"days={len(self.days_of_week)})"
        )
