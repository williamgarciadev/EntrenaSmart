# -*- coding: utf-8 -*-
"""
Modelo de Entrenamiento (Training)
===================================

Define la entidad de sesion de entrenamiento en la base de datos.
"""
from typing import Optional, List
from datetime import datetime

from sqlalchemy import ForeignKey, String, Integer, Time, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.models.base import Base


class Training(Base):
    """
    Modelo de Sesion de Entrenamiento.

    Representa una sesion de entrenamiento configurada para un alumno
    en un dia y hora especificos.
    """

    __tablename__ = "trainings"

    # Clave foranea
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del alumno que tiene esta sesion"
    )

    # Configuracion de la sesion
    weekday: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Dia de la semana (0=Lunes, 6=Domingo)"
    )

    weekday_name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Nombre del dia en espanol (ej: 'Lunes')"
    )

    time_str: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
        comment="Hora de la sesion en formato HH:MM"
    )

    session_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Tipo de sesion (ej: 'Funcional', 'Pesas', 'Cardio')"
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Ubicacion del entrenamiento (ej: '2do Piso', '4to Piso')"
    )

    training_day_config_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("training_day_configs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Referencia a la configuracion del dia de entrenamiento"
    )

    # Estado
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        index=True,
        comment="Indica si la sesion esta activa"
    )

    # Relaciones
    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="trainings",
        lazy="joined"
    )

    training_day_config: Mapped[Optional["TrainingDayConfig"]] = relationship(
        "TrainingDayConfig",
        lazy="joined",
        foreign_keys=[training_day_config_id]
    )

    feedbacks: Mapped[List["Feedback"]] = relationship(
        "Feedback",
        back_populates="training",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __init__(
        self,
        student_id: int,
        weekday: int,
        weekday_name: str,
        time_str: str,
        session_type: str,
        is_active: bool = True,
        location: Optional[str] = None,
        training_day_config_id: Optional[int] = None
    ):
        """
        Inicializa una nueva sesion de entrenamiento.

        Args:
            student_id: ID del alumno
            weekday: Dia de la semana (0-6)
            weekday_name: Nombre del dia en espanol
            time_str: Hora en formato HH:MM
            session_type: Tipo de sesion
            is_active: Si la sesion esta activa
            location: Ubicacion del entrenamiento
            training_day_config_id: ID de la configuracion del dia
        """
        self.student_id = student_id
        self.weekday = weekday
        self.weekday_name = weekday_name
        self.time_str = time_str
        self.session_type = session_type
        self.is_active = is_active
        self.location = location
        self.training_day_config_id = training_day_config_id

    def deactivate(self) -> None:
        """Desactiva la sesion."""
        self.is_active = False

    def activate(self) -> None:
        """Activa la sesion."""
        self.is_active = True

    def __str__(self) -> str:
        """Representacion en string de la sesion."""
        location_str = f", location={self.location}" if self.location else ""
        return (
            f"Training(id={self.id}, student_id={self.student_id}, "
            f"day={self.weekday_name}, time={self.time_str}, "
            f"type={self.session_type}{location_str})"
        )
