"""
Modelo de Programación de Mensajes (MessageSchedule)
=====================================================

Define la entidad de programación de envío automático de mensajes.
"""
from typing import Optional, List
from sqlalchemy import Integer, String, Boolean, ForeignKey, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.src.models.base import Base


class MessageSchedule(Base):
    """
    Modelo de Programación de Mensajes.

    Representa una programación de envío automático de mensajes
    a estudiantes en horarios específicos.
    """

    __tablename__ = "message_schedules"

    # Referencias a plantilla y estudiante
    template_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="ID de la plantilla de mensaje a enviar"
    )

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del estudiante destinatario"
    )

    # Horario
    hour: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Hora de envío (0-23)"
    )

    minute: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Minuto de envío (0-59)"
    )

    # Días de la semana (0=lunes, 6=domingo)
    days_of_week: Mapped[List[int]] = mapped_column(
        ARRAY(Integer),
        nullable=False,
        comment="Días de semana para envío (0=lunes, 6=domingo)"
    )

    # Estado
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
        comment="Indica si la programación está activa"
    )

    # Relación con estudiante
    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="message_schedules",
        lazy="select"
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
            template_id: ID de la plantilla de mensaje
            student_id: ID del estudiante destinatario
            hour: Hora de envío (0-23)
            minute: Minuto de envío (0-59)
            days_of_week: Lista de días de semana (0=lunes, 6=domingo)
            is_active: Si la programación está activa (default: True)
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

    def __str__(self) -> str:
        """Representación en string de la programación."""
        return (
            f"MessageSchedule(id={self.id}, template={self.template_id}, "
            f"student={self.student_id}, time={self.hour:02d}:{self.minute:02d}, "
            f"active={self.is_active})"
        )
