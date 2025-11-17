"""
Router de programación de envíos automáticos.

Endpoints para crear, actualizar y listar programaciones de envío
de mensajes a estudiantes en horarios específicos.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from ..schemas import (
    MessageScheduleCreate,
    MessageScheduleUpdate,
    MessageScheduleResponse,
    MessageScheduleListResponse,
    SuccessResponse
)
from ..dependencies import get_current_trainer
from ..logger import logger

router = APIRouter()

# Simulación de datos en memoria para desarrollo
MOCK_SCHEDULES = {
    1: {
        "id": 1,
        "template_id": 1,
        "student_id": 1,
        "hour": 9,
        "minute": 0,
        "days_of_week": [0, 1, 2, 3, 4],  # Lunes a viernes
        "is_active": True,
        "created_at": "2025-11-16T00:00:00",
        "updated_at": "2025-11-16T00:00:00"
    },
    2: {
        "id": 2,
        "template_id": 2,
        "student_id": 2,
        "hour": 14,
        "minute": 30,
        "days_of_week": [1, 3, 5],  # Martes, jueves, sábado
        "is_active": True,
        "created_at": "2025-11-16T00:00:00",
        "updated_at": "2025-11-16T00:00:00"
    },
}

_next_id = 3


@router.get("", response_model=MessageScheduleListResponse)
async def list_schedules(
    active_only: bool = False,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Listar todas las programaciones de envío.

    Args:
        active_only: Si es True, solo retorna programaciones activas
    """
    logger.info("Listando programaciones de envío")

    schedules = list(MOCK_SCHEDULES.values())

    if active_only:
        schedules = [s for s in schedules if s["is_active"]]

    return MessageScheduleListResponse(
        schedules=[MessageScheduleResponse(**s) for s in schedules],
        total=len(schedules)
    )


@router.get("/{schedule_id}", response_model=MessageScheduleResponse)
async def get_schedule(
    schedule_id: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Obtener una programación específica.

    Args:
        schedule_id: ID de la programación
    """
    if schedule_id not in MOCK_SCHEDULES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Programación {schedule_id} no encontrada"
        )

    schedule = MOCK_SCHEDULES[schedule_id]
    logger.info(f"Obteniendo programación: {schedule_id}")

    return MessageScheduleResponse(**schedule)


@router.post("", response_model=MessageScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule: MessageScheduleCreate,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Crear una nueva programación de envío.

    Args:
        schedule: Datos de la programación a crear
    """
    global _next_id

    # Validar que la programación sea única (mismo template, estudiante y horario)
    for s in MOCK_SCHEDULES.values():
        if (s["template_id"] == schedule.template_id and
            s["student_id"] == schedule.student_id and
            s["hour"] == schedule.hour and
            s["minute"] == schedule.minute):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una programación con estos mismos datos"
            )

    now = datetime.now().isoformat()
    new_schedule = {
        "id": _next_id,
        "template_id": schedule.template_id,
        "student_id": schedule.student_id,
        "hour": schedule.hour,
        "minute": schedule.minute,
        "days_of_week": schedule.days_of_week,
        "is_active": schedule.is_active,
        "created_at": now,
        "updated_at": now
    }

    MOCK_SCHEDULES[_next_id] = new_schedule
    _next_id += 1

    logger.info(f"Programación creada: {_next_id - 1}")

    return MessageScheduleResponse(**new_schedule)


@router.put("/{schedule_id}", response_model=MessageScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_update: MessageScheduleUpdate,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Actualizar una programación existente.

    Args:
        schedule_id: ID de la programación
        schedule_update: Datos a actualizar
    """
    if schedule_id not in MOCK_SCHEDULES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Programación {schedule_id} no encontrada"
        )

    schedule = MOCK_SCHEDULES[schedule_id]

    # Actualizar campos si se proporcionan
    if schedule_update.template_id is not None:
        schedule["template_id"] = schedule_update.template_id
    if schedule_update.student_id is not None:
        schedule["student_id"] = schedule_update.student_id
    if schedule_update.hour is not None:
        schedule["hour"] = schedule_update.hour
    if schedule_update.minute is not None:
        schedule["minute"] = schedule_update.minute
    if schedule_update.days_of_week is not None:
        schedule["days_of_week"] = schedule_update.days_of_week
    if schedule_update.is_active is not None:
        schedule["is_active"] = schedule_update.is_active

    schedule["updated_at"] = datetime.now().isoformat()

    logger.info(f"Programación actualizada: {schedule_id}")

    return MessageScheduleResponse(**schedule)


@router.delete("/{schedule_id}", response_model=SuccessResponse)
async def delete_schedule(
    schedule_id: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Eliminar una programación.

    Args:
        schedule_id: ID de la programación a eliminar
    """
    if schedule_id not in MOCK_SCHEDULES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Programación {schedule_id} no encontrada"
        )

    schedule = MOCK_SCHEDULES.pop(schedule_id)
    logger.info(f"Programación eliminada: {schedule_id}")

    return SuccessResponse(
        message=f"Programación {schedule_id} eliminada exitosamente"
    )


@router.post("/{schedule_id}/test", response_model=dict)
async def test_schedule(
    schedule_id: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Enviar un mensaje de prueba con la programación.

    Args:
        schedule_id: ID de la programación
    """
    if schedule_id not in MOCK_SCHEDULES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Programación {schedule_id} no encontrada"
        )

    schedule = MOCK_SCHEDULES[schedule_id]
    logger.info(f"Enviando mensaje de prueba: programación {schedule_id}")

    return {
        "success": True,
        "message": f"Mensaje de prueba enviado exitosamente",
        "schedule_id": schedule_id,
        "timestamp": datetime.now().isoformat()
    }
