"""
API Router - Configuración de Recordatorios Semanales
=====================================================

Endpoints para configurar y gestionar recordatorios semanales
que el entrenador envía a todos los alumnos activos.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.src.models.base import get_db
from backend.src.services.weekly_reminder_service import WeeklyReminderService
from backend.src.utils.logger import logger


router = APIRouter(
    prefix="/api/weekly-reminders",
    tags=["Weekly Reminders"]
)


# Schemas Pydantic
class WeeklyReminderConfigUpdate(BaseModel):
    """Schema para actualizar configuración de recordatorio semanal."""
    is_monday_off: Optional[bool] = Field(None, description="Si el lunes no trabaja")
    message_full_week: Optional[str] = Field(None, description="Mensaje cuando trabaja toda la semana")
    message_monday_off: Optional[str] = Field(None, description="Mensaje cuando el lunes no trabaja")
    send_day: Optional[int] = Field(None, ge=0, le=6, description="Día de envío (0=Lunes, 6=Domingo)")
    send_hour: Optional[int] = Field(None, ge=0, le=23, description="Hora de envío (0-23)")
    send_minute: Optional[int] = Field(None, ge=0, le=59, description="Minuto de envío (0-59)")
    is_active: Optional[bool] = Field(None, description="Si está activo")

    class Config:
        json_schema_extra = {
            "example": {
                "is_monday_off": True,
                "send_day": 6,
                "send_hour": 18,
                "send_minute": 0,
                "is_active": True
            }
        }


class WeeklyReminderConfigResponse(BaseModel):
    """Schema de respuesta para configuración de recordatorio semanal."""
    id: int
    is_monday_off: bool
    message_full_week: str
    message_monday_off: str
    send_day: int
    send_day_name: str
    send_hour: int
    send_minute: int
    send_time: str
    is_active: bool
    current_message: str
    created_at: Optional[str]
    updated_at: Optional[str]


# Dependency para obtener servicio
def get_weekly_reminder_service(db: Session = Depends(get_db)) -> WeeklyReminderService:
    """Obtiene instancia de WeeklyReminderService."""
    return WeeklyReminderService(db)


@router.get(
    "/config",
    response_model=WeeklyReminderConfigResponse,
    summary="Obtener configuración de recordatorio semanal",
    description="Obtiene la configuración actual del recordatorio semanal. Si no existe, crea una con valores por defecto."
)
def get_config(
    service: WeeklyReminderService = Depends(get_weekly_reminder_service)
):
    """
    Obtiene la configuración de recordatorio semanal.

    Returns:
        Configuración actual o nueva con valores por defecto
    """
    try:
        logger.info("[API] GET /api/weekly-reminders/config")
        config = service.get_or_create_config()
        return config
    except Exception as e:
        logger.error(f"[API] Error obteniendo configuración: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo configuración: {str(e)}"
        )


@router.put(
    "/config",
    response_model=WeeklyReminderConfigResponse,
    summary="Actualizar configuración de recordatorio semanal",
    description="Actualiza la configuración del recordatorio semanal. Si no existe, la crea."
)
def update_config(
    data: WeeklyReminderConfigUpdate,
    service: WeeklyReminderService = Depends(get_weekly_reminder_service)
):
    """
    Actualiza la configuración de recordatorio semanal.

    Args:
        data: Datos a actualizar

    Returns:
        Configuración actualizada
    """
    try:
        logger.info(f"[API] PUT /api/weekly-reminders/config - Data: {data.model_dump(exclude_none=True)}")

        config = service.update_config(
            is_monday_off=data.is_monday_off,
            message_full_week=data.message_full_week,
            message_monday_off=data.message_monday_off,
            send_day=data.send_day,
            send_hour=data.send_hour,
            send_minute=data.send_minute,
            is_active=data.is_active
        )

        if not config:
            raise HTTPException(
                status_code=404,
                detail="No se pudo actualizar la configuración"
            )

        logger.info(f"[API] Configuración actualizada exitosamente: {config['id']}")
        return config

    except ValueError as e:
        logger.warning(f"[API] Validación fallida: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] Error actualizando configuración: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando configuración: {str(e)}"
        )


@router.get(
    "/preview",
    summary="Previsualizar mensaje actual",
    description="Obtiene el mensaje que se enviará según la configuración actual (trabaja lunes o no)."
)
def preview_message(
    service: WeeklyReminderService = Depends(get_weekly_reminder_service)
):
    """
    Previsualiza el mensaje que se enviará.

    Returns:
        Mensaje actual según configuración
    """
    try:
        logger.info("[API] GET /api/weekly-reminders/preview")

        message = service.get_message_to_send()
        if not message:
            return {
                "message": None,
                "info": "No hay configuración activa o el recordatorio está deshabilitado"
            }

        config = service.get_config()
        return {
            "message": message,
            "is_monday_off": config["is_monday_off"] if config else None,
            "send_schedule": f"{config['send_day_name']} {config['send_time']}" if config else None
        }

    except Exception as e:
        logger.error(f"[API] Error previsualizando mensaje: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error previsualizando mensaje: {str(e)}"
        )


@router.get(
    "/active-students",
    summary="Obtener estudiantes activos",
    description="Obtiene la lista de estudiantes activos que recibirán el recordatorio."
)
def get_active_students(
    service: WeeklyReminderService = Depends(get_weekly_reminder_service)
):
    """
    Obtiene estudiantes activos.

    Returns:
        Lista de estudiantes activos con ID y nombre
    """
    try:
        logger.info("[API] GET /api/weekly-reminders/active-students")

        students = service.get_active_students()
        return {
            "total": len(students),
            "students": [
                {
                    "id": student.id,
                    "name": student.name,
                    "chat_id": student.chat_id
                }
                for student in students
            ]
        }

    except Exception as e:
        logger.error(f"[API] Error obteniendo estudiantes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estudiantes: {str(e)}"
        )


@router.post(
    "/send-test",
    summary="Enviar mensaje de prueba",
    description="Envía el mensaje configurado al entrenador como prueba (solo al chat del entrenador)."
)
async def send_test_message(
    db: Session = Depends(get_db)
):
    """
    Envía un mensaje de prueba al entrenador.

    Returns:
        Resultado del envío
    """
    try:
        logger.info("[API] POST /api/weekly-reminders/send-test")

        # Importar dependencias
        from backend.api.main import get_telegram_bot
        from backend.src.services.weekly_reminder_service import WeeklyReminderService
        from backend.src.core.config import settings

        # Obtener bot
        bot = get_telegram_bot()
        if not bot:
            raise HTTPException(
                status_code=503,
                detail="Bot de Telegram no está disponible"
            )

        # Obtener mensaje
        service = WeeklyReminderService(db)
        message = service.get_message_to_send()
        if not message:
            raise HTTPException(
                status_code=400,
                detail="No hay mensaje configurado o el recordatorio está desactivado"
            )

        # Crear teclado inline con botón para configurar semana
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("📅 Configurar mi semana", callback_data="config_weekly_training")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Enviar al entrenador (trainer_telegram_id)
        await bot.send_message(
            chat_id=settings.trainer_telegram_id,
            text=f"🧪 MENSAJE DE PRUEBA:\n\n{message}",
            reply_markup=reply_markup
        )

        logger.info(f"✅ [API] Mensaje de prueba enviado al entrenador ({settings.trainer_telegram_id})")
        return {
            "success": True,
            "message": "Mensaje de prueba enviado al entrenador"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Error enviando mensaje de prueba: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error enviando mensaje de prueba: {str(e)}"
        )
