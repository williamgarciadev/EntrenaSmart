"""
Router de plantillas de mensajes.

Endpoints para crear, actualizar y listar plantillas de mensajes
con variables dinámicas para recordatorios automáticos.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from ..schemas import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateListResponse,
    SuccessResponse
)
from ..dependencies import get_current_trainer
from ..logger import logger
from backend.src.models.base import get_db_context
from backend.src.services.template_service import TemplateService
from backend.src.core.exceptions import (
    ValidationError,
    DuplicateRecordError,
    RecordNotFoundError
)

router = APIRouter()

# DEPRECATED: MOCK_TEMPLATES mantenido solo para compatibilidad temporal
# TODO: Migrar todas las referencias a usar la base de datos
MOCK_TEMPLATES = {
    1: {
        "id": 1,
        "name": "Recordatorio diario",
        "content": "Hola {alumno}, recuerda tu sesión de {tipo_entrenamiento} hoy!",
        "variables": ["alumno", "tipo_entrenamiento"],
        "is_active": True,
        "created_at": "2025-11-16T00:00:00",
        "updated_at": "2025-11-16T00:00:00"
    },
    2: {
        "id": 2,
        "name": "Confirmación de cambio",
        "content": "Tu entrenamiento cambió a {tipo_entrenamiento} en {ubicacion}",
        "variables": ["tipo_entrenamiento", "ubicacion"],
        "is_active": True,
        "created_at": "2025-11-16T00:00:00",
        "updated_at": "2025-11-16T00:00:00"
    },
    3: {
        "id": 3,
        "name": "Motivación",
        "content": "Vas muy bien {alumno}! Sigue así con tu {tipo_entrenamiento}",
        "variables": ["alumno", "tipo_entrenamiento"],
        "is_active": True,
        "created_at": "2025-11-16T00:00:00",
        "updated_at": "2025-11-16T00:00:00"
    },
}


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    active_only: bool = False,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Listar todas las plantillas de mensajes desde la BD.

    Args:
        active_only: Si es True, solo retorna plantillas activas
    """
    logger.info(f"Listando plantillas desde BD (active_only={active_only})")

    try:
        with get_db_context() as db:
            service = TemplateService(db)
            db_templates = service.list_all_templates(active_only=active_only)

        # Convertir objetos ORM a response models
        templates = [
            TemplateResponse(
                id=template.id,
                name=template.name,
                content=template.content,
                variables=template.variables,
                is_active=template.is_active,
                created_at=template.created_at,
                updated_at=template.updated_at
            )
            for template in db_templates
        ]

        logger.info(f"✅ Obtenidas {len(templates)} plantillas de la BD")

        return TemplateListResponse(
            templates=templates,
            total=len(templates)
        )

    except Exception as e:
        logger.error(f"Error listando plantillas: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar plantillas"
        )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Obtener una plantilla específica desde la BD.

    Args:
        template_id: ID de la plantilla
    """
    try:
        with get_db_context() as db:
            service = TemplateService(db)
            template = service.get_template_by_id_or_fail(template_id)

        logger.info(f"Obtenida plantilla desde BD: {template.name}")

        return TemplateResponse(
            id=template.id,
            name=template.name,
            content=template.content,
            variables=template.variables,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at
        )

    except RecordNotFoundError:
        logger.warning(f"Plantilla {template_id} no encontrada en BD")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantilla {template_id} no encontrada"
        )
    except Exception as e:
        logger.error(f"Error obteniendo plantilla {template_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener plantilla"
        )


@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template: TemplateCreate,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Crear una nueva plantilla de mensaje en la BD.

    Args:
        template: Datos de la plantilla a crear
    """
    try:
        # Extraer variables del contenido si no se especifican
        variables = template.variables
        if not variables:
            import re
            variables = list(set(re.findall(r'\{(\w+)\}', template.content)))

        with get_db_context() as db:
            service = TemplateService(db)
            new_template = service.create_template(
                name=template.name,
                content=template.content,
                variables=variables,
                is_active=template.is_active
            )

        logger.info(f"✅ Plantilla creada en BD: {new_template.name}")

        return TemplateResponse(
            id=new_template.id,
            name=new_template.name,
            content=new_template.content,
            variables=new_template.variables,
            is_active=new_template.is_active,
            created_at=new_template.created_at,
            updated_at=new_template.updated_at
        )

    except ValidationError as e:
        logger.warning(f"Error de validación: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DuplicateRecordError as e:
        logger.warning(f"Plantilla duplicada: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creando plantilla: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear plantilla"
        )


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_update: TemplateUpdate,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Actualizar una plantilla existente en la BD.

    Args:
        template_id: ID de la plantilla
        template_update: Datos a actualizar
    """
    try:
        with get_db_context() as db:
            service = TemplateService(db)
            template = service.update_template(
                template_id=template_id,
                name=template_update.name,
                content=template_update.content,
                variables=template_update.variables,
                is_active=template_update.is_active
            )

        logger.info(f"✅ Plantilla actualizada en BD: {template.name}")

        return TemplateResponse(
            id=template.id,
            name=template.name,
            content=template.content,
            variables=template.variables,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at
        )

    except RecordNotFoundError:
        logger.warning(f"Plantilla {template_id} no encontrada en BD")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantilla {template_id} no encontrada"
        )
    except ValidationError as e:
        logger.warning(f"Error de validación: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DuplicateRecordError as e:
        logger.warning(f"Plantilla duplicada: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error actualizando plantilla: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar plantilla"
        )


@router.delete("/{template_id}", response_model=SuccessResponse)
async def delete_template(
    template_id: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Eliminar (desactivar) una plantilla en la BD.

    Args:
        template_id: ID de la plantilla a eliminar
    """
    try:
        with get_db_context() as db:
            service = TemplateService(db)
            template = service.delete_template(template_id)

        logger.info(f"✅ Plantilla eliminada en BD: {template.name}")

        return SuccessResponse(
            message=f"Plantilla '{template.name}' eliminada exitosamente"
        )

    except RecordNotFoundError:
        logger.warning(f"Plantilla {template_id} no encontrada en BD")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantilla {template_id} no encontrada"
        )
    except Exception as e:
        logger.error(f"Error eliminando plantilla: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar plantilla"
        )


@router.post("/{template_id}/preview", response_model=dict)
async def preview_template(
    template_id: int,
    variables_values: dict,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Obtener preview de plantilla con variables reemplazadas.

    Args:
        template_id: ID de la plantilla
        variables_values: Dict con valores para reemplazar variables
    """
    try:
        with get_db_context() as db:
            service = TemplateService(db)
            template = service.get_template_by_id_or_fail(template_id)

        content = template.content

        # Reemplazar variables
        for var, value in variables_values.items():
            content = content.replace(f"{{{var}}}", str(value))

        return {
            "template_id": template.id,
            "name": template.name,
            "original_content": template.content,
            "preview_content": content,
            "variables_replaced": list(variables_values.keys())
        }

    except RecordNotFoundError:
        logger.warning(f"Plantilla {template_id} no encontrada en BD")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantilla {template_id} no encontrada"
        )
    except Exception as e:
        logger.error(f"Error generando preview: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al generar preview"
        )
