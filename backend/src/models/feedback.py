# -*- coding: utf-8 -*-
"""
Modelo de Feedback
==================

Define la entidad de feedback post-entrenamiento en la base de datos.
"""
from typing import Optional

from sqlalchemy import ForeignKey, String, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Feedback(Base):
    """
    Modelo de Feedback Post-Entrenamiento.

    Representa la retroalimentacion que proporciona un alumno despues
    de completar una sesion de entrenamiento.
    """

    __tablename__ = "feedbacks"

    # Clave foranea
    training_id: Mapped[int] = mapped_column(
        ForeignKey("trainings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la sesion de entrenamiento"
    )

    # Evaluacion de la sesion
    intensity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Intensidad percibida de la sesion (1-4)"
    )

    pain_level: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Nivel de dolor/molestia despues (0-5)"
    )

    notes: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Notas adicionales del alumno"
    )

    # Relaciones
    training: Mapped["Training"] = relationship(
        "Training",
        back_populates="feedbacks",
        lazy="joined"
    )

    def __init__(
        self,
        training_id: int,
        intensity: int,
        pain_level: int = 0,
        notes: Optional[str] = None
    ):
        """
        Inicializa un nuevo feedback.

        Args:
            training_id: ID de la sesion
            intensity: Intensidad (1-4)
            pain_level: Nivel de dolor (0-5)
            notes: Notas adicionales
        """
        self.training_id = training_id
        self.intensity = intensity
        self.pain_level = pain_level
        self.notes = notes

    @property
    def intensity_emoji(self) -> str:
        """
        Obtiene emoji segun la intensidad.

        Returns:
            str: Emoji representativo de la intensidad
        """
        emojis = {
            1: "😴",  # Muy ligero
            2: "😐",  # Moderado
            3: "💪",  # Intenso
            4: "🔥",  # Muy intenso
        }
        return emojis.get(self.intensity, "?")

    @property
    def pain_emoji(self) -> str:
        """
        Obtiene emoji segun el nivel de dolor.

        Returns:
            str: Emoji representativo del dolor
        """
        if self.pain_level == 0:
            return "😊"  # Sin dolor
        elif self.pain_level <= 2:
            return "😐"  # Molestia leve
        elif self.pain_level <= 4:
            return "😟"  # Molestia moderada
        else:
            return "😫"  # Molestia severa

    def __str__(self) -> str:
        """Representacion en string del feedback."""
        return (
            f"Feedback(id={self.id}, training_id={self.training_id}, "
            f"intensity={self.intensity}, pain={self.pain_level})"
        )
