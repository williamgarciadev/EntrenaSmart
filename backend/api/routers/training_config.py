"""
Router de configuración semanal de entrenamientos.

Endpoints para obtener y actualizar la configuración de entrenamientos por día.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from backend.api.schemas import (
    TrainingDayConfigCreate,
    TrainingDayConfigResponse,
    WeeklyConfigResponse,
    SuccessResponse
)
from backend.api.dependencies import get_current_trainer
from backend.utils.logger import logger

router = APIRouter()

# Simulación de datos en memoria para desarrollo
# En producción, usar servicios de la base de datos existente
MOCK_CONFIG = {
    0: {"weekday": 0, "weekday_name": "Lunes", "session_type": "Pierna", "location": "2do Piso", "is_active": True},
    1: {"weekday": 1, "weekday_name": "Martes", "session_type": "Funcional", "location": "3er Piso", "is_active": True},
    2: {"weekday": 2, "weekday_name": "Miércoles", "session_type": "Brazo", "location": "2do Piso", "is_active": True},
    3: {"weekday": 3, "weekday_name": "Jueves", "session_type": "Espalda", "location": "3er Piso", "is_active": True},
    4: {"weekday": 4, "weekday_name": "Viernes", "session_type": "Pecho", "location": "2do Piso", "is_active": True},
    5: {"weekday": 5, "weekday_name": "Sábado", "session_type": "Hombros", "location": "3er Piso", "is_active": False},
    6: {"weekday": 6, "weekday_name": "Domingo", "session_type": "", "location": "", "is_active": False},
}


@router.get("", response_model=WeeklyConfigResponse)
async def get_weekly_config(trainer: dict = Depends(get_current_trainer)):
    """
    Obtener configuración semanal completa.

    Retorna la configuración de entrenamiento para los 7 días de la semana.
    """
    logger.info("Obteniendo configuración semanal")

    configs = []
    for day in range(7):
        config_data = MOCK_CONFIG.get(day, {
            "weekday": day,
            "weekday_name": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][day],
            "session_type": "",
            "location": "",
            "is_active": False
        })

        # Agregar timestamps simulados
        config_with_timestamps = {
            **config_data,
            "id": day + 1,
            "created_at": "2025-11-16T00:00:00",
            "updated_at": "2025-11-16T00:00:00"
        }
        configs.append(TrainingDayConfigResponse(**config_with_timestamps))

    return WeeklyConfigResponse(configs=configs)


@router.get("/{weekday}", response_model=TrainingDayConfigResponse)
async def get_day_config(
    weekday: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Obtener configuración de un día específico.

    Args:
        weekday: Número del día (0=Lunes, 6=Domingo)
    """
    if not 0 <= weekday <= 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El día debe estar entre 0 (Lunes) y 6 (Domingo)"
        )

    config_data = MOCK_CONFIG.get(weekday)
    if not config_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuración no encontrada para el día {weekday}"
        )

    config_with_timestamps = {
        **config_data,
        "id": weekday + 1,
        "created_at": "2025-11-16T00:00:00",
        "updated_at": "2025-11-16T00:00:00"
    }

    return TrainingDayConfigResponse(**config_with_timestamps)


@router.post("/{weekday}", response_model=SuccessResponse)
async def update_day_config(
    weekday: int,
    config: TrainingDayConfigCreate,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Actualizar configuración de un día específico.

    Args:
        weekday: Número del día (0=Lunes, 6=Domingo)
        config: Datos de la configuración a actualizar
    """
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

    # Actualizar en memoria (en producción, guardar en BD)
    MOCK_CONFIG[weekday] = {
        "weekday": weekday,
        "weekday_name": config.weekday_name,
        "session_type": config.session_type,
        "location": config.location,
        "is_active": True if config.session_type else False
    }

    logger.info(f"Configuración actualizada para el día {config.weekday_name}")

    return SuccessResponse(
        message=f"Configuración actualizada para {config.weekday_name}",
        data={
            "weekday": weekday,
            "session_type": config.session_type,
            "location": config.location
        }
    )


@router.delete("/{weekday}", response_model=SuccessResponse)
async def delete_day_config(
    weekday: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Eliminar configuración de un día específico.

    Args:
        weekday: Número del día (0=Lunes, 6=Domingo)
    """
    if not 0 <= weekday <= 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El día debe estar entre 0 (Lunes) y 6 (Domingo)"
        )

    day_name = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][weekday]

    # Limpiar configuración
    MOCK_CONFIG[weekday] = {
        "weekday": weekday,
        "weekday_name": day_name,
        "session_type": "",
        "location": "",
        "is_active": False
    }

    logger.info(f"Configuración eliminada para {day_name}")

    return SuccessResponse(
        message=f"Configuración eliminada para {day_name}"
    )
