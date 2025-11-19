# -*- coding: utf-8 -*-
"""
Tarea de Recordatorio Semanal del Entrenador
============================================

Implementa el envío del mensaje semanal del entrenador a todos los alumnos activos.
Se ejecuta automáticamente vía APScheduler según la configuración.

Este mensaje pregunta a los alumnos cómo quieren programar su semana.
"""
import asyncio
from typing import List
from backend.src.utils.logger import logger


class WeeklyReminderTask:
    """
    Tarea para enviar recordatorio semanal del entrenador a todos los alumnos activos.
    """

    @staticmethod
    def send_weekly_reminder_sync() -> bool:
        """
        Versión síncrona para ejecutar desde BackgroundScheduler.

        Obtiene la configuración actual, obtiene todos los estudiantes activos,
        y les envía el mensaje correspondiente (lunes off o semana completa).

        Returns:
            bool: True si se enviaron todos los mensajes, False si hubo error
        """
        from backend.src.models.base import get_db
        from backend.src.services.weekly_reminder_service import WeeklyReminderService
        from backend.src.services.scheduler_service import get_global_application, get_global_event_loop

        logger.info("=" * 70)
        logger.info("📢 [WEEKLY_REMINDER] ===== INICIANDO ENVÍO MASIVO SEMANAL =====")
        logger.info("=" * 70)

        db = None
        try:
            # Obtener configuración y estudiantes
            db = get_db()
            service = WeeklyReminderService(db)

            # Obtener configuración
            config_dict = service.get_config()
            if not config_dict:
                logger.warning("⚠️ [WEEKLY_REMINDER] No hay configuración de recordatorio semanal")
                return False

            if not config_dict["is_active"]:
                logger.info("ℹ️ [WEEKLY_REMINDER] Recordatorio semanal está desactivado")
                return False

            # Obtener mensaje a enviar
            message = service.get_message_to_send()
            if not message:
                logger.warning("⚠️ [WEEKLY_REMINDER] No hay mensaje configurado")
                return False

            # Obtener estudiantes activos
            students = service.get_active_students()
            if not students:
                logger.info("ℹ️ [WEEKLY_REMINDER] No hay estudiantes activos")
                return True  # No es error, simplemente no hay nadie a quien enviar

            logger.info(f"📊 [WEEKLY_REMINDER] Estudiantes activos: {len(students)}")
            logger.info(f"📝 [WEEKLY_REMINDER] Mensaje a enviar:")
            logger.info(f"   Modo: {'Lunes OFF' if config_dict['is_monday_off'] else 'Semana Completa'}")
            logger.info(f"   Longitud: {len(message)} caracteres")

            # Obtener bot y event_loop
            application = get_global_application()
            bot = application.bot if application else None
            event_loop = get_global_event_loop()

            if not bot:
                logger.error("❌ [WEEKLY_REMINDER] Bot no está disponible")
                return False

            if not event_loop:
                logger.error("❌ [WEEKLY_REMINDER] Event loop no está disponible")
                return False

            logger.info(f"✅ [WEEKLY_REMINDER] Bot y event loop obtenidos correctamente")

            # Crear teclado inline con botón para configurar semana
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup

            keyboard = [
                [InlineKeyboardButton("📅 Configurar mi semana", callback_data="config_weekly_training")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Enviar mensajes a todos los estudiantes
            success_count = 0
            error_count = 0

            for student in students:
                try:
                    logger.info(f"📤 [WEEKLY_REMINDER] Enviando a {student.name} (chat_id: {student.chat_id})")

                    # Ejecutar coroutine en el event loop correcto
                    future = asyncio.run_coroutine_threadsafe(
                        bot.send_message(
                            chat_id=student.chat_id,
                            text=message,
                            parse_mode=None,  # Enviar como texto plano
                            reply_markup=reply_markup
                        ),
                        event_loop
                    )

                    # Esperar resultado con timeout configurable
                    from backend.src.core.config import settings
                    timeout_seconds = settings.task_future_timeout
                    future.result(timeout=timeout_seconds)
                    success_count += 1
                    logger.info(f"   ✅ Enviado a {student.name}")

                except Exception as e:
                    error_count += 1
                    logger.error(
                        f"   ❌ Error enviando a {student.name} (chat_id: {student.chat_id}): {str(e)}"
                    )

            logger.info("=" * 70)
            logger.info(f"📊 [WEEKLY_REMINDER] RESUMEN DEL ENVÍO:")
            logger.info(f"   ✅ Exitosos: {success_count}/{len(students)}")
            logger.info(f"   ❌ Errores: {error_count}/{len(students)}")
            logger.info("=" * 70)

            return error_count == 0

        except Exception as e:
            logger.error(f"❌ [WEEKLY_REMINDER] Error crítico: {str(e)}", exc_info=True)
            return False
        finally:
            if db:
                db.close()
                logger.debug("🔒 [WEEKLY_REMINDER] Sesión de BD cerrada")
