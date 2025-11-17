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
from backend.src.models.base import get_db_context
from backend.src.services.message_schedule_service import MessageScheduleService
from backend.src.core.exceptions import (
    ValidationError,
    DuplicateRecordError,
    RecordNotFoundError
)
from backend.src.repositories.student_repository import StudentRepository

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
            service = MessageScheduleService(db)
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
            service = MessageScheduleService(db)
            schedule = service.get_schedule_by_id_or_fail(schedule_id)

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

    except RecordNotFoundError:
        logger.warning(f"Programación {schedule_id} no encontrada en BD")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Programación {schedule_id} no encontrada"
        )
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
            service = MessageScheduleService(db)
            new_schedule = service.create_schedule(
                template_id=schedule.template_id,
                student_id=schedule.student_id,
                hour=schedule.hour,
                minute=schedule.minute,
                days_of_week=schedule.days_of_week,
                is_active=schedule.is_active
            )

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
            service = MessageScheduleService(db)
            schedule = service.update_schedule(
                schedule_id=schedule_id,
                template_id=schedule_update.template_id,
                student_id=schedule_update.student_id,
                hour=schedule_update.hour,
                minute=schedule_update.minute,
                days_of_week=schedule_update.days_of_week,
                is_active=schedule_update.is_active
            )

        logger.info(f"✅ Programación actualizada en BD: {schedule.id}")

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
        logger.error(f"Error actualizando programación: {e}", exc_info=True)
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
    Eliminar (desactivar) una programación en la BD.

    Args:
        schedule_id: ID de la programación a eliminar
    """
    try:
        with get_db_context() as db:
            service = MessageScheduleService(db)
            schedule = service.delete_schedule(schedule_id)

        logger.info(f"✅ Programación eliminada en BD: {schedule_id}")

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
        logger.error(f"Error eliminando programación: {e}", exc_info=True)
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
            service = MessageScheduleService(db)
            schedule = service.get_schedule_by_id_or_fail(schedule_id)

            # Obtener estudiante para tener el chat_id
            student_repo = StudentRepository(db)
            student = student_repo.get_by_id(schedule.student_id)

            if not student:
                logger.warning(f"Estudiante {schedule.student_id} no encontrado")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Estudiante {schedule.student_id} no encontrado"
                )

            if not student.chat_id:
                logger.warning(f"Estudiante {student.name} no tiene chat_id configurado")
                return {
                    "success": False,
                    "message": f"El estudiante {student.name} no tiene un chat de Telegram configurado",
                    "schedule_id": schedule_id,
                    "timestamp": datetime.now().isoformat(),
                    "error": "NO_CHAT_ID"
                }

        logger.info(f"Enviando mensaje de prueba: programación {schedule_id}")

        # Obtener template de la BD
        try:
            from backend.src.services.template_service import TemplateService
            with get_db_context() as db_template:
                template_service = TemplateService(db_template)
                template = template_service.get_template_by_id(schedule.template_id)

            if not template:
                logger.warning(f"Plantilla {schedule.template_id} no encontrada en BD")
                # Fallback a MOCK_TEMPLATES para compatibilidad temporal
                from ..routers.templates import MOCK_TEMPLATES
                template_dict = MOCK_TEMPLATES.get(schedule.template_id)
                if not template_dict:
                    return {
                        "success": False,
                        "message": f"Plantilla {schedule.template_id} no encontrada",
                        "schedule_id": schedule_id,
                        "timestamp": datetime.now().isoformat(),
                        "error": "TEMPLATE_NOT_FOUND"
                    }
                message_content = template_dict["content"]
                template_name = template_dict["name"]
            else:
                message_content = template.content
                template_name = template.name

        except Exception as template_error:
            logger.error(f"Error obteniendo plantilla: {template_error}", exc_info=True)
            return {
                "success": False,
                "message": f"Error obteniendo plantilla: {str(template_error)}",
                "schedule_id": schedule_id,
                "timestamp": datetime.now().isoformat(),
                "error": "TEMPLATE_ERROR"
            }

        # Construir mensaje reemplazando variables
        message_content = message_content.replace("{alumno}", student.name)
        message_content = message_content.replace("{tipo_entrenamiento}", "Entrenamiento")

        # Intentar enviar mensaje usando el bot de Telegram
        try:
            import os
            from telegram import Bot

            # Obtener token desde variable de entorno
            telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")

            if not telegram_token:
                logger.error("TELEGRAM_BOT_TOKEN no está configurado")
                return {
                    "success": False,
                    "message": "Token de Telegram no configurado en el servidor",
                    "schedule_id": schedule_id,
                    "timestamp": datetime.now().isoformat(),
                    "error": "TOKEN_NOT_CONFIGURED"
                }

            # Crear instancia del bot para enviar mensaje
            bot = Bot(token=telegram_token)

            # Enviar mensaje de prueba
            await bot.send_message(
                chat_id=student.chat_id,
                text=f"🧪 <b>MENSAJE DE PRUEBA</b>\n\n{message_content}",
                parse_mode="HTML"
            )

            logger.info(f"✅ Mensaje de prueba enviado a {student.name} (chat_id: {student.chat_id})")
            return {
                "success": True,
                "message": f"Mensaje de prueba enviado exitosamente a {student.name}",
                "schedule_id": schedule_id,
                "timestamp": datetime.now().isoformat(),
                "chat_id": student.chat_id
            }
        except Exception as send_error:
            logger.error(f"Error enviando mensaje a Telegram: {send_error}", exc_info=True)
            return {
                "success": False,
                "message": f"Error al enviar mensaje: {str(send_error)}",
                "schedule_id": schedule_id,
                "timestamp": datetime.now().isoformat(),
                "error": "TELEGRAM_ERROR",
                "debug_info": {
                    "student": student.name,
                    "chat_id": student.chat_id,
                    "template": template_name
                }
            }

    except RecordNotFoundError:
        logger.warning(f"Programación {schedule_id} no encontrada en BD")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Programación {schedule_id} no encontrada"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enviando mensaje de prueba: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar mensaje de prueba: {str(e)}"
        )
