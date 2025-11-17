"""
Router de configuración semanal de entrenamientos.

Endpoints para obtener y actualizar la configuración de entrenamientos por día.
Persiste datos en PostgreSQL a través de ConfigTrainingService.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from ..schemas import (
    TrainingDayConfigCreate,
    TrainingDayConfigResponse,
    WeeklyConfigResponse,
    SuccessResponse
)
from ..dependencies import get_current_trainer
from ..logger import logger
from src.models.base import get_db_context
from src.services.config_training_service import ConfigTrainingService
from src.core.exceptions import RecordNotFoundError, ValidationError

router = APIRouter()


@router.get("/weekly", response_model=WeeklyConfigResponse)
async def get_weekly_config(trainer: dict = Depends(get_current_trainer)):
    """
    Obtener configuración semanal completa.

    Retorna la configuración de entrenamiento para los 7 días de la semana desde la BD.
    """
    logger.info("Obteniendo configuración semanal desde BD")

    try:
        with get_db_context() as db:
            service = ConfigTrainingService(db)
            db_configs = service.get_all_configs()

        # Convertir objetos ORM a response models
        configs = [
            TrainingDayConfigResponse(
                id=config.id,
                weekday=config.weekday,
                weekday_name=config.weekday_name,
                session_type=config.session_type,
                location=config.location,
                is_active=config.is_active,
                created_at=config.created_at,
                updated_at=config.updated_at
            )
            for config in db_configs
        ]

        logger.info(f"✅ Obtenidas {len(configs)} configuraciones de la BD")
        return WeeklyConfigResponse(configs=configs)

    except Exception as e:
        logger.error(f"Error obteniendo configuración semanal: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener configuración semanal"
        )


@router.get("/day/{weekday}", response_model=TrainingDayConfigResponse)
async def get_day_config(
    weekday: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Obtener configuración de un día específico desde la BD.

    Args:
        weekday: Número del día (0=Lunes, 6=Domingo)
    """
    if not 0 <= weekday <= 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El día debe estar entre 0 (Lunes) y 6 (Domingo)"
        )

    try:
        with get_db_context() as db:
            service = ConfigTrainingService(db)
            config = service.get_day_config(weekday)

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuración no encontrada para el día {weekday}"
            )

        logger.info(f"Obtenida configuración para día {weekday}: {config.session_type}")

        return TrainingDayConfigResponse(
            id=config.id,
            weekday=config.weekday,
            weekday_name=config.weekday_name,
            session_type=config.session_type,
            location=config.location,
            is_active=config.is_active,
            created_at=config.created_at,
            updated_at=config.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo configuración del día {weekday}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener configuración del día"
        )


@router.post("/day", response_model=SuccessResponse)
async def update_day_config(
    config: TrainingDayConfigCreate,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Actualizar configuración de un día específico en la BD.

    Args:
        config: Datos de la configuración a actualizar (incluye weekday)
    """
    weekday = config.weekday
    if not 0 <= weekday <= 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El día debe estar entre 0 (Lunes) y 6 (Domingo)"
        )

    # Validar tipos de entrenamiento permitidos
    VALID_TYPES = ["Pierna", "Funcional", "Brazo", "Espalda", "Pecho", "Hombros"]
    if config.session_type and config.session_type not in VALID_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de entrenamiento inválido. Debe ser uno de: {', '.join(VALID_TYPES)}"
        )

    try:
        with get_db_context() as db:
            service = ConfigTrainingService(db)
            config_obj = service.configure_day(
                weekday=weekday,
                session_type=config.session_type,
                location=config.location
            )
            # Auto-commit al salir del contexto

        logger.info(f"✅ Configuración guardada en BD para {config.weekday_name}")

        return SuccessResponse(
            message=f"Configuración actualizada para {config.weekday_name}",
            data={
                "weekday": weekday,
                "session_type": config.session_type,
                "location": config.location
            }
        )

    except ValidationError as e:
        logger.warning(f"Error de validación: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error actualizando configuración: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar configuración"
        )


@router.delete("/day/{weekday}", response_model=SuccessResponse)
async def delete_day_config(
    weekday: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Eliminar configuración de un día específico de la BD.

    Args:
        weekday: Número del día (0=Lunes, 6=Domingo)
    """
    if not 0 <= weekday <= 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El día debe estar entre 0 (Lunes) y 6 (Domingo)"
        )

    day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    day_name = day_names[weekday]

    try:
        with get_db_context() as db:
            service = ConfigTrainingService(db)
            service.delete_day_config(weekday)
            # Auto-commit al salir del contexto

        logger.info(f"✅ Configuración eliminada de BD para {day_name}")

        return SuccessResponse(
            message=f"Configuración eliminada para {day_name}"
        )

    except RecordNotFoundError:
        logger.warning(f"Intento de eliminar configuración inexistente para día {weekday}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay configuración para {day_name}"
        )
    except Exception as e:
        logger.error(f"Error eliminando configuración: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar configuración"
        )
