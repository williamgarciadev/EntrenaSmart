# -*- coding: utf-8 -*-
"""
Tarea de Recordatorio de Entrenamiento
======================================

Implementa el envío de recordatorios de entrenamiento a través de Telegram.
Se ejecuta automáticamente vía APScheduler.

Ejemplo:
    >>> from src.services.tasks.reminder_task import ReminderTask
    >>> ReminderTask.send_reminder_sync(
    ...     bot=app,
    ...     student_chat_id=123456,
    ...     session_type="Funcional",
    ...     training_time="05:00"
    ... )
"""
import asyncio
import concurrent.futures
from datetime import datetime
from typing import Optional

from backend.src.utils.logger import logger
from backend.src.utils.messages import Messages


class ReminderTask:
    """
    Tarea para enviar recordatorios de entrenamiento a alumnos.
    """

    @staticmethod
    def send_reminder_sync(
        student_chat_id: int,
        weekday: int,
        training_time: str
    ) -> bool:
        """
        Versión síncrona para ejecutar desde BackgroundScheduler.

        Ejecuta la coroutine async en el event loop correcto usando
        asyncio.run_coroutine_threadsafe() para evitar problemas
        de serialización con APScheduler.

        Obtiene el bot y event_loop desde variables globales para evitar
        problemas de serialización de pickle.

        Args:
            student_chat_id: Chat ID del alumno
            weekday: Día de la semana (0=Lunes, 6=Domingo)
            training_time: Hora del entrenamiento (formato "HH:MM")

        Returns:
            bool: True si la tarea fue enviada, False si hubo error
        """
        from backend.src.models.base import get_db
        from backend.src.services.config_training_service import ConfigTrainingService

        logger.info(f"🔔 [SEND_REMINDER] ===== INICIANDO ENVÍO DE RECORDATORIO =====")
        logger.info(f"🔔 [SEND_REMINDER] Parámetros recibidos:")
        logger.info(f"   - student_chat_id: {student_chat_id}")
        logger.info(f"   - weekday: {weekday}")
        logger.info(f"   - training_time: {training_time}")

        # Obtener configuración del día (tipo + ubicación)
        db = None
        try:
            db = get_db()
            config_service = ConfigTrainingService(db)
            config = config_service.get_day_config(weekday)

            if config:
                session_type = config.session_type
                location = config.location
                logger.info(f"✅ [SEND_REMINDER] Configuración obtenida: {session_type} en {location}")
            else:
                logger.warning(f"⚠️ [SEND_REMINDER] No hay configuración para el día {weekday}")
                session_type = "Entrenamiento"
                location = "Zona de Entrenamiento"
        except Exception as e:
            logger.error(f"❌ [SEND_REMINDER] Error obteniendo configuración: {str(e)}")
            session_type = "Entrenamiento"
            location = "Zona de Entrenamiento"
        finally:
            if db:
                db.close()

        # Obtener application y event_loop desde variables globales
        from src.services.scheduler_service import get_global_application, get_global_event_loop
        application = get_global_application()
        bot = application.bot if application else None
        event_loop = get_global_event_loop()

        logger.info(f"🌍 [SEND_REMINDER] Variables globales obtenidas:")
        logger.info(f"   - application: {application}")
        logger.info(f"   - bot: {bot}")
        logger.info(f"   - event_loop: {event_loop}")

        try:
            # Construir mensaje usando template de Messages
            logger.info(f"📝 [SEND_REMINDER] Construyendo mensaje de recordatorio...")
            message_text = Messages.training_reminder(
                session_type=session_type,
                location=location,
                training_time=training_time,
                include_checklist=True
            )
            logger.info(f"✅ [SEND_REMINDER] Mensaje construido: {len(message_text)} caracteres")
            logger.info(f"📄 [SEND_REMINDER] Preview: {message_text[:100]}...")

            logger.info(f"🔍 [SEND_REMINDER] Estado del event_loop global:")
            if event_loop:
                logger.info(f"   - Event loop disponible: {event_loop}")
                logger.info(f"   - is_running(): {event_loop.is_running()}")
                logger.info(f"   - is_closed(): {event_loop.is_closed()}")
            else:
                logger.error(f"❌ [SEND_REMINDER] ¡Event loop global es None!")

            if event_loop and event_loop.is_running():
                logger.info(f"✅ [SEND_REMINDER] Event loop está corriendo - usando run_coroutine_threadsafe")
                # BackgroundScheduler ejecuta en thread separado, usar run_coroutine_threadsafe
                try:
                    logger.info(f"📤 [SEND_REMINDER] Enviando mensaje con run_coroutine_threadsafe...")
                    logger.info(f"   - chat_id: {student_chat_id}")
                    logger.info(f"   - text_length: {len(message_text)}")
                    logger.info(f"   - parse_mode: HTML")

                    future = asyncio.run_coroutine_threadsafe(
                        bot.send_message(
                            chat_id=student_chat_id,
                            text=message_text,
                            parse_mode="HTML"
                        ),
                        event_loop
                    )
                    logger.info(f"✅ [SEND_REMINDER] Future creado: {future}")

                    # Esperar a que se envíe (con timeout configurable)
                    from src.core.config import settings
                    timeout_seconds = settings.task_future_timeout
                    logger.info(f"⏳ [SEND_REMINDER] Esperando resultado (timeout={timeout_seconds}s)...")
                    result = future.result(timeout=timeout_seconds)
                    logger.info(f"✅ [SEND_REMINDER] Resultado obtenido: {result}")

                    logger.info(
                        f"✅ [SEND_REMINDER] ===== RECORDATORIO ENVIADO EXITOSAMENTE =====\n"
                        f"   - chat_id: {student_chat_id}\n"
                        f"   - session_type: {session_type}\n"
                        f"   - training_time: {training_time}"
                    )
                    return True

                except concurrent.futures.TimeoutError as e:
                    logger.error(f"❌ [SEND_REMINDER] Timeout esperando resultado (>{timeout_seconds}s): {str(e)}")
                    logger.error(f"   Sugerencia: Aumentar TASK_FUTURE_TIMEOUT en variables de entorno")
                    return False
                except Exception as e:
                    logger.error(f"❌ [SEND_REMINDER] Error enviando con run_coroutine_threadsafe: {str(e)}", exc_info=True)
                    return False
            else:
                # Fallback: si no hay event loop o no está corriendo, loguear
                logger.error(f"❌ [SEND_REMINDER] ===== FALLO: NO HAY EVENT LOOP DISPONIBLE O NO ESTÁ CORRIENDO =====")
                logger.error(f"   - Bot: {bot}")
                logger.error(f"   - Event loop: {event_loop}")
                if event_loop:
                    logger.error(f"   - is_closed(): {event_loop.is_closed()}")
                    logger.error(f"   - is_running(): {event_loop.is_running()}")
                return False

        except Exception as e:
            logger.error(
                f"❌ [SEND_REMINDER] ===== ERROR GENERAL EN SEND_REMINDER =====\n"
                f"   chat_id={student_chat_id}: {str(e)}",
                exc_info=True
            )
            return False

    @staticmethod
    async def send_reminder(
        bot,
        student_chat_id: int,
        session_type: str,
        training_time: str
    ) -> bool:
        """
        Versión async (opcional, para uso manual).

        Args:
            bot: Application de Telegram
            student_chat_id: Chat ID del alumno
            session_type: Tipo de sesión (ej: "Funcional", "Pesas")
            training_time: Hora del entrenamiento (formato "HH:MM")

        Returns:
            bool: True si fue enviado exitosamente, False si hubo error
        """
        try:
            # Construir mensaje usando template de Messages
            message_text = Messages.training_reminder(
                session_type=session_type,
                training_time=training_time,
                include_checklist=True
            )

            # Enviar mensaje
            await bot.send_message(
                chat_id=student_chat_id,
                text=message_text,
                parse_mode="HTML"
            )

            logger.info(
                f"Recordatorio enviado: chat_id={student_chat_id}, "
                f"type={session_type}, time={training_time}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Error enviando recordatorio a {student_chat_id}: {str(e)}",
                exc_info=True
            )
            return False
