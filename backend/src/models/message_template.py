"""
Modelo de Plantilla de Mensaje (MessageTemplate)
=================================================

Define la entidad de plantilla de mensaje para envíos automáticos.
"""
from typing import List
from sqlalchemy import String, Boolean, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from backend.src.models.base import Base


class MessageTemplate(Base):
    """
    Modelo de Plantilla de Mensaje.

    Representa una plantilla de mensaje con variables dinámicas
    para envíos automáticos a estudiantes.
    """

    __tablename__ = "message_templates"

    # Información de la plantilla
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Nombre único de la plantilla"
    )

    content: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        comment="Contenido del mensaje con variables {var}"
    )

    variables: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
        comment="Lista de variables disponibles en la plantilla"
    )

    # Estado
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Si la plantilla está activa para uso"
    )

    def __repr__(self) -> str:
        return f"<MessageTemplate(id={self.id}, name='{self.name}', active={self.is_active})>"
