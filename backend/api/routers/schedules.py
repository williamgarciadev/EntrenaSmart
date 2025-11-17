"""
Router de programación de envíos automáticos.

Endpoints para crear, actualizar y listar programaciones de envío
de mensajes a estudiantes en horarios específicos.
Persiste datos en PostgreSQL a través de ScheduleService.
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
from backend.src.models.base import get_db_context
from backend.src.services.schedule_service import ScheduleService
from backend.src.core.exceptions import (
    ValidationError,
    DuplicateRecordError,
    RecordNotFoundError
)

router = APIRouter()


@router.get("", response_model=MessageScheduleListResponse)
async def list_schedules(
    active_only: bool = False,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Listar todas las programaciones de envío desde la BD.

    Args:
        active_only: Si es True, solo retorna programaciones activas
    """
    logger.info(f"Listando programaciones desde BD (active_only={active_only})")

    try:
        with get_db_context() as db:
            service = ScheduleService(db)
            db_schedules = service.list_all_schedules(active_only=active_only)

        # Convertir objetos ORM a response models
        schedules = [
            MessageScheduleResponse(
                id=schedule.id,
                template_id=schedule.template_id,
                student_id=schedule.student_id,
                hour=schedule.hour,
                minute=schedule.minute,
                days_of_week=schedule.days_of_week,
                is_active=schedule.is_active,
                created_at=schedule.created_at,
                updated_at=schedule.updated_at
            )
            for schedule in db_schedules
        ]

        logger.info(f"✅ Obtenidas {len(schedules)} programaciones de la BD")

        return MessageScheduleListResponse(
            schedules=schedules,
            total=len(schedules)
        )

    except Exception as e:
        logger.error(f"Error listando programaciones: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar programaciones"
        )


@router.get("/{schedule_id}", response_model=MessageScheduleResponse)
async def get_schedule(
    schedule_id: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Obtener una programación específica desde la BD.

    Args:
        schedule_id: ID de la programación
    """
    try:
        with get_db_context() as db:
            service = ScheduleService(db)
            schedule = service.get_schedule_by_id(schedule_id)

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Programación {schedule_id} no encontrada"
            )

        logger.info(f"Obtenida programación desde BD: {schedule_id}")

        return MessageScheduleResponse(
            id=schedule.id,
            template_id=schedule.template_id,
            student_id=schedule.student_id,
            hour=schedule.hour,
            minute=schedule.minute,
            days_of_week=schedule.days_of_week,
            is_active=schedule.is_active,
            created_at=schedule.created_at,
            updated_at=schedule.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo programación {schedule_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener programación"
        )


@router.post("", response_model=MessageScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule: MessageScheduleCreate,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Crear una nueva programación de envío en la BD.

    Args:
        schedule: Datos de la programación a crear
    """
    try:
        with get_db_context() as db:
            service = ScheduleService(db)
            new_schedule = service.create_schedule(
                template_id=schedule.template_id,
                student_id=schedule.student_id,
                hour=schedule.hour,
                minute=schedule.minute,
                days_of_week=schedule.days_of_week,
                is_active=schedule.is_active
            )
            # Auto-commit al salir del contexto

        logger.info(f"✅ Programación creada en BD: {new_schedule.id}")

        return MessageScheduleResponse(
            id=new_schedule.id,
            template_id=new_schedule.template_id,
            student_id=new_schedule.student_id,
            hour=new_schedule.hour,
            minute=new_schedule.minute,
            days_of_week=new_schedule.days_of_week,
            is_active=new_schedule.is_active,
            created_at=new_schedule.created_at,
            updated_at=new_schedule.updated_at
        )

    except ValidationError as e:
        logger.warning(f"Error de validación: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DuplicateRecordError as e:
        logger.warning(f"Programación duplicada: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creando programación: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear programación"
        )


@router.put("/{schedule_id}", response_model=MessageScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_update: MessageScheduleUpdate,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Actualizar una programación existente en la BD.

    Args:
        schedule_id: ID de la programación
        schedule_update: Datos a actualizar
    """
    try:
        with get_db_context() as db:
            service = ScheduleService(db)
            updated_schedule = service.update_schedule(
                schedule_id=schedule_id,
                template_id=schedule_update.template_id,
                student_id=schedule_update.student_id,
                hour=schedule_update.hour,
                minute=schedule_update.minute,
                days_of_week=schedule_update.days_of_week,
                is_active=schedule_update.is_active
            )
            # Auto-commit al salir del contexto

        logger.info(f"✅ Programación actualizada en BD: {schedule_id}")

        return MessageScheduleResponse(
            id=updated_schedule.id,
            template_id=updated_schedule.template_id,
            student_id=updated_schedule.student_id,
            hour=updated_schedule.hour,
            minute=updated_schedule.minute,
            days_of_week=updated_schedule.days_of_week,
            is_active=updated_schedule.is_active,
            created_at=updated_schedule.created_at,
            updated_at=updated_schedule.updated_at
        )

    except RecordNotFoundError:
        logger.warning(f"Programación {schedule_id} no encontrada en BD")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Programación {schedule_id} no encontrada"
        )
    except ValidationError as e:
        logger.warning(f"Error de validación: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error actualizando programación {schedule_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar programación"
        )


@router.delete("/{schedule_id}", response_model=SuccessResponse)
async def delete_schedule(
    schedule_id: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Eliminar una programación de la BD.

    Args:
        schedule_id: ID de la programación a eliminar
    """
    try:
        with get_db_context() as db:
            service = ScheduleService(db)
            service.delete_schedule(schedule_id)
            # Auto-commit al salir del contexto

        logger.info(f"✅ Programación eliminada de BD: {schedule_id}")

        return SuccessResponse(
            message=f"Programación {schedule_id} eliminada exitosamente"
        )

    except RecordNotFoundError:
        logger.warning(f"Programación {schedule_id} no encontrada en BD")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Programación {schedule_id} no encontrada"
        )
    except Exception as e:
        logger.error(f"Error eliminando programación {schedule_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar programación"
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
    try:
        with get_db_context() as db:
            service = ScheduleService(db)
            schedule = service.get_schedule_by_id(schedule_id)

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Programación {schedule_id} no encontrada"
            )

        logger.info(f"Enviando mensaje de prueba: programación {schedule_id}")

        # TODO: Implementar envío real de mensaje de prueba
        return {
            "success": True,
            "message": f"Mensaje de prueba enviado exitosamente",
            "schedule_id": schedule_id,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enviando mensaje de prueba: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al enviar mensaje de prueba"
        )
