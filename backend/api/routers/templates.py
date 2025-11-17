"""
Router de plantillas de mensajes.

Endpoints para crear, actualizar y listar plantillas de mensajes
con variables dinámicas para recordatorios automáticos.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from ..schemas import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateListResponse,
    SuccessResponse
)
from ..dependencies import get_current_trainer
from ..logger import logger

router = APIRouter()

# Simulación de datos en memoria para desarrollo
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

_next_id = 4


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    active_only: bool = False,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Listar todas las plantillas de mensajes.

    Args:
        active_only: Si es True, solo retorna plantillas activas
    """
    logger.info("Listando plantillas de mensajes")

    templates = list(MOCK_TEMPLATES.values())

    if active_only:
        templates = [t for t in templates if t["is_active"]]

    return TemplateListResponse(
        templates=[TemplateResponse(**t) for t in templates],
        total=len(templates)
    )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Obtener una plantilla específica.

    Args:
        template_id: ID de la plantilla
    """
    if template_id not in MOCK_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantilla {template_id} no encontrada"
        )

    template = MOCK_TEMPLATES[template_id]
    logger.info(f"Obteniendo plantilla: {template['name']}")

    return TemplateResponse(**template)


@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template: TemplateCreate,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Crear una nueva plantilla de mensaje.

    Args:
        template: Datos de la plantilla a crear
    """
    global _next_id

    # Validar que el nombre sea único
    for t in MOCK_TEMPLATES.values():
        if t["name"].lower() == template.name.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una plantilla con el nombre '{template.name}'"
            )

    # Extraer variables del contenido si no se especifican
    variables = template.variables
    if not variables:
        import re
        variables = list(set(re.findall(r'\{(\w+)\}', template.content)))

    now = datetime.now().isoformat()
    new_template = {
        "id": _next_id,
        "name": template.name,
        "content": template.content,
        "variables": variables,
        "is_active": template.is_active,
        "created_at": now,
        "updated_at": now
    }

    MOCK_TEMPLATES[_next_id] = new_template
    _next_id += 1

    logger.info(f"Plantilla creada: {template.name}")

    return TemplateResponse(**new_template)


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_update: TemplateUpdate,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Actualizar una plantilla existente.

    Args:
        template_id: ID de la plantilla
        template_update: Datos a actualizar
    """
    if template_id not in MOCK_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantilla {template_id} no encontrada"
        )

    template = MOCK_TEMPLATES[template_id]

    # Actualizar campos si se proporcionan
    if template_update.name is not None:
        template["name"] = template_update.name
    if template_update.content is not None:
        template["content"] = template_update.content
    if template_update.variables is not None:
        template["variables"] = template_update.variables
    if template_update.is_active is not None:
        template["is_active"] = template_update.is_active

    template["updated_at"] = datetime.now().isoformat()

    logger.info(f"Plantilla actualizada: {template['name']}")

    return TemplateResponse(**template)


@router.delete("/{template_id}", response_model=SuccessResponse)
async def delete_template(
    template_id: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Eliminar una plantilla.

    Args:
        template_id: ID de la plantilla a eliminar
    """
    if template_id not in MOCK_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantilla {template_id} no encontrada"
        )

    template = MOCK_TEMPLATES.pop(template_id)
    logger.info(f"Plantilla eliminada: {template['name']}")

    return SuccessResponse(
        message=f"Plantilla '{template['name']}' eliminada exitosamente"
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
    if template_id not in MOCK_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantilla {template_id} no encontrada"
        )

    template = MOCK_TEMPLATES[template_id]
    content = template["content"]

    # Reemplazar variables
    for var, value in variables_values.items():
        content = content.replace(f"{{{var}}}", str(value))

    return {
        "template_id": template_id,
        "name": template["name"],
        "original_content": template["content"],
        "preview_content": content,
        "variables_replaced": list(variables_values.keys())
    }
