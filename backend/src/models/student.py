"""
Modelo de Alumno (Student)
===========================

Define la entidad de alumno en la base de datos.
"""
from typing import Optional, List

from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Student(Base):
    """
    Modelo de Alumno.

    Representa a un alumno registrado en el sistema.
    Cada alumno está asociado a un chat_id de Telegram.
    """

    __tablename__ = "students"

    # Campos únicos
    chat_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        unique=True,
        nullable=True,
        index=True,
        comment="ID del chat de Telegram del alumno (NULL hasta que el alumno inicie sesión)"
    )

    # Información del alumno
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nombre del alumno"
    )

    telegram_username: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Username de Telegram (sin @)"
    )

    # Estado
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
        comment="Indica si el alumno está activo"
    )

    # Relaciones
    trainings: Mapped[List["Training"]] = relationship(
        "Training",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="select"
    )

    message_schedules: Mapped[List["MessageSchedule"]] = relationship(
        "MessageSchedule",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __init__(
        self,
        name: str,
        telegram_username: Optional[str] = None,
        chat_id: Optional[int] = None,
        is_active: bool = True
    ):
        """
        Inicializa un nuevo alumno.

        Args:
            name: Nombre del alumno
            telegram_username: Username de Telegram (opcional)
            chat_id: ID del chat de Telegram (opcional, se asigna cuando alumno inicia sesión)
            is_active: Si el alumno está activo (default: True)
        """
        self.name = name
        self.telegram_username = telegram_username
        self.chat_id = chat_id
        self.is_active = is_active

    def deactivate(self) -> None:
        """Desactiva el alumno."""
        self.is_active = False

    def activate(self) -> None:
        """Activa el alumno."""
        self.is_active = True

    @property
    def display_name(self) -> str:
        """
        Nombre para mostrar en mensajes.

        Returns:
            str: Nombre del alumno, con @ si tiene username
        """
        if self.telegram_username:
            return f"{self.name} (@{self.telegram_username})"
        return self.name

    def __str__(self) -> str:
        """Representación en string del alumno."""
        return f"Student(id={self.id}, name='{self.name}', active={self.is_active})"

