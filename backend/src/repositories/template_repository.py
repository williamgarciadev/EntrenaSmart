# -*- coding: utf-8 -*-
"""
Repositorio de Plantillas de Mensajes
======================================
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.src.models.message_template import MessageTemplate
from backend.src.repositories.base_repository import BaseRepository
from backend.src.core.exceptions import RecordNotFoundError, DuplicateRecordError


class TemplateRepository(BaseRepository[MessageTemplate]):
    """Repositorio para operaciones de plantillas de mensajes."""

    def __init__(self, db: Session):
        """Inicializa con sesión de BD."""
        super().__init__(db, MessageTemplate)

    def create_template(
        self,
        name: str,
        content: str,
        variables: List[str],
        is_active: bool = True
    ) -> MessageTemplate:
        """
        Crea una nueva plantilla.

        Args:
            name: Nombre único de la plantilla
            content: Contenido del mensaje con variables
            variables: Lista de variables disponibles
            is_active: Si la plantilla está activa

        Returns:
            MessageTemplate: Plantilla creada

        Raises:
            DuplicateRecordError: Si ya existe una plantilla con ese nombre
        """
        # Verificar si ya existe
        existing = self.get_by_name(name)
        if existing:
            raise DuplicateRecordError("MessageTemplate", {"name": name})

        template = MessageTemplate(
            name=name,
            content=content,
            variables=variables,
            is_active=is_active
        )
        return self.create(template)

    def get_by_name(self, name: str) -> Optional[MessageTemplate]:
        """Obtiene plantilla por nombre."""
        return self.db.query(MessageTemplate).filter(
            MessageTemplate.name == name
        ).first()

    def get_by_name_or_fail(self, name: str) -> MessageTemplate:
        """Obtiene plantilla por nombre o lanza excepción."""
        template = self.get_by_name(name)
        if not template:
            raise RecordNotFoundError("MessageTemplate", {"name": name})
        return template

    def get_active_templates(self) -> List[MessageTemplate]:
        """Obtiene todas las plantillas activas."""
        return self.db.query(MessageTemplate).filter(
            MessageTemplate.is_active == True
        ).order_by(MessageTemplate.name).all()

    def get_all_templates(self) -> List[MessageTemplate]:
        """Obtiene todas las plantillas."""
        return self.db.query(MessageTemplate).order_by(
            MessageTemplate.name
        ).all()

    def update_template(
        self,
        template_id: int,
        name: Optional[str] = None,
        content: Optional[str] = None,
        variables: Optional[List[str]] = None,
        is_active: Optional[bool] = None
    ) -> MessageTemplate:
        """
        Actualiza una plantilla existente.

        Args:
            template_id: ID de la plantilla
            name: Nuevo nombre (opcional)
            content: Nuevo contenido (opcional)
            variables: Nuevas variables (opcional)
            is_active: Nuevo estado (opcional)

        Returns:
            MessageTemplate: Plantilla actualizada

        Raises:
            RecordNotFoundError: Si no existe la plantilla
            DuplicateRecordError: Si el nuevo nombre ya existe
        """
        template = self.get_by_id_or_fail(template_id)

        # Verificar nombre duplicado si se está cambiando
        if name and name != template.name:
            existing = self.get_by_name(name)
            if existing:
                raise DuplicateRecordError("MessageTemplate", {"name": name})
            template.name = name

        if content is not None:
            template.content = content

        if variables is not None:
            template.variables = variables

        if is_active is not None:
            template.is_active = is_active

        return self.update(template)

    def deactivate_template(self, template_id: int) -> MessageTemplate:
        """Desactiva una plantilla."""
        template = self.get_by_id_or_fail(template_id)
        template.is_active = False
        return self.update(template)

    def activate_template(self, template_id: int) -> MessageTemplate:
        """Activa una plantilla."""
        template = self.get_by_id_or_fail(template_id)
        template.is_active = True
        return self.update(template)

    def get_by_id_or_fail(self, template_id: int) -> MessageTemplate:
        """Obtiene plantilla por ID o falla."""
        template = self.get_by_id(template_id)
        if not template:
            raise RecordNotFoundError("MessageTemplate", {"id": template_id})
        return template
