"""
Servicio de Gestión de Plantillas de Mensajes
==============================================

Implementa la lógica de negocio para operaciones relacionadas
con plantillas de mensajes.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.src.models.message_template import MessageTemplate
from backend.src.repositories.template_repository import TemplateRepository
from backend.src.core.exceptions import (
    ValidationError,
    RecordNotFoundError,
    DuplicateRecordError
)


class TemplateService:
    """
    Servicio de gestión de plantillas de mensajes.

    Encapsula la lógica de negocio relacionada con plantillas.
    """

    def __init__(self, db: Session):
        """
        Inicializa el servicio de plantillas.

        Args:
            db: Sesión de base de datos
        """
        self.db = db
        self.repository = TemplateRepository(db)

    def create_template(
        self,
        name: str,
        content: str,
        variables: List[str],
        is_active: bool = True
    ) -> MessageTemplate:
        """
        Crea una nueva plantilla de mensaje.

        Args:
            name: Nombre único de la plantilla
            content: Contenido del mensaje con variables {var}
            variables: Lista de variables disponibles
            is_active: Si la plantilla está activa (default: True)

        Returns:
            MessageTemplate: Plantilla creada

        Raises:
            ValidationError: Si los datos son inválidos
            DuplicateRecordError: Si ya existe una plantilla con ese nombre
        """
        # Validaciones
        if not name or len(name.strip()) == 0:
            raise ValidationError(
                "El nombre de la plantilla es requerido",
                {"name": name}
            )

        if len(name) > 100:
            raise ValidationError(
                "El nombre de la plantilla no puede exceder 100 caracteres",
                {"name": name}
            )

        if not content or len(content.strip()) == 0:
            raise ValidationError(
                "El contenido de la plantilla es requerido",
                {"content": content}
            )

        if len(content) > 1000:
            raise ValidationError(
                "El contenido de la plantilla no puede exceder 1000 caracteres",
                {"content_length": len(content)}
            )

        # Validar que las variables en el contenido estén en la lista
        import re
        content_vars = set(re.findall(r'\{(\w+)\}', content))
        provided_vars = set(variables)

        missing_vars = content_vars - provided_vars
        if missing_vars:
            raise ValidationError(
                f"Variables en el contenido no están en la lista de variables: {missing_vars}",
                {"missing_variables": list(missing_vars)}
            )

        return self.repository.create_template(
            name=name.strip(),
            content=content.strip(),
            variables=variables,
            is_active=is_active
        )

    def get_template_by_id(self, template_id: int) -> Optional[MessageTemplate]:
        """
        Obtiene una plantilla por su ID.

        Args:
            template_id: ID de la plantilla

        Returns:
            MessageTemplate: Plantilla encontrada o None
        """
        return self.repository.get_by_id(template_id)

    def get_template_by_id_or_fail(self, template_id: int) -> MessageTemplate:
        """
        Obtiene una plantilla por su ID o lanza excepción.

        Args:
            template_id: ID de la plantilla

        Returns:
            MessageTemplate: Plantilla encontrada

        Raises:
            RecordNotFoundError: Si no se encuentra la plantilla
        """
        return self.repository.get_by_id_or_fail(template_id)

    def list_all_templates(self, active_only: bool = False) -> List[MessageTemplate]:
        """
        Lista todas las plantillas.

        Args:
            active_only: Si True, solo retorna plantillas activas

        Returns:
            List[MessageTemplate]: Lista de plantillas
        """
        if active_only:
            return self.repository.get_active_templates()
        return self.repository.get_all_templates()

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
            ValidationError: Si los datos son inválidos
            RecordNotFoundError: Si no existe la plantilla
            DuplicateRecordError: Si el nuevo nombre ya existe
        """
        # Validaciones similares a create_template
        if name is not None:
            if not name or len(name.strip()) == 0:
                raise ValidationError(
                    "El nombre de la plantilla es requerido",
                    {"name": name}
                )
            if len(name) > 100:
                raise ValidationError(
                    "El nombre de la plantilla no puede exceder 100 caracteres",
                    {"name": name}
                )
            name = name.strip()

        if content is not None:
            if not content or len(content.strip()) == 0:
                raise ValidationError(
                    "El contenido de la plantilla es requerido",
                    {"content": content}
                )
            if len(content) > 1000:
                raise ValidationError(
                    "El contenido de la plantilla no puede exceder 1000 caracteres",
                    {"content_length": len(content)}
                )
            content = content.strip()

            # Validar variables si se están actualizando ambos campos
            if variables is not None:
                import re
                content_vars = set(re.findall(r'\{(\w+)\}', content))
                provided_vars = set(variables)

                missing_vars = content_vars - provided_vars
                if missing_vars:
                    raise ValidationError(
                        f"Variables en el contenido no están en la lista de variables: {missing_vars}",
                        {"missing_variables": list(missing_vars)}
                    )

        return self.repository.update_template(
            template_id=template_id,
            name=name,
            content=content,
            variables=variables,
            is_active=is_active
        )

    def delete_template(self, template_id: int) -> MessageTemplate:
        """
        Elimina (desactiva) una plantilla.

        Args:
            template_id: ID de la plantilla

        Returns:
            MessageTemplate: Plantilla desactivada

        Raises:
            RecordNotFoundError: Si no existe la plantilla
        """
        return self.repository.deactivate_template(template_id)

    def activate_template(self, template_id: int) -> MessageTemplate:
        """
        Activa una plantilla.

        Args:
            template_id: ID de la plantilla

        Returns:
            MessageTemplate: Plantilla activada

        Raises:
            RecordNotFoundError: Si no existe la plantilla
        """
        return self.repository.activate_template(template_id)
