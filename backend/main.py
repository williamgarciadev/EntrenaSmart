"""
EntrenaSmart - Bot de Telegram para Entrenadores
=================================================

Punto de entrada principal de la aplicación.
Inicializa el bot, configura handlers y arranca el scheduler.
"""
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from src.core.config import settings
from src.models.base import init_db, get_db
from src.services.scheduler_service import SchedulerService
from src.utils.logger import logger

# Importar handlers
from src.handlers.trainer_handlers import (
    start_command,
    help_command,
    listar_alumnos_command,
    reporte_command,
    commands_menu_handler,
    handle_text_input,
    handle_registration_confirmation,
    handle_training_day_selection,
    handle_training_another_day,
    handle_training_final_confirm
)
from src.handlers.registration_handler import build_registration_conv_handler
from src.handlers.training_handler import build_training_conv_handler
from src.handlers.edit_training_handler import build_edit_training_conv_handler
from src.handlers.config_training_handler import config_training_handler
from src.handlers.student_handlers import (
    mis_sesiones_command,
    handle_feedback_intensity,
    handle_feedback_completion
)
from src.handlers.student_schedule_handler import mi_semana_command


# Tracking de conflictos para detectar loops de reintentos
_conflict_counter = 0
_last_conflict_time = None


async def error_handler(update, context) -> None:
    """
    Manejador centralizado de errores con detección de loops.

    Captura excepciones de los handlers y del polling sin entrar en loop infinito.

    Args:
        update: Update de Telegram (puede ser None si error es en polling)
        context: Context con información del error
    """
    global _conflict_counter, _last_conflict_time

    error = context.error
    error_type = type(error).__name__

    logger.error("="*70)
    logger.error(f"❌ [ERROR_HANDLER] Excepción capturada: {error_type}")
    logger.error(f"   Mensaje: {str(error)}")

    # Logging del update si está disponible
    if update:
        if isinstance(update, Update):
            if update.message:
                logger.error(f"   Usuario: {update.message.from_user.id}")
                logger.error(f"   Mensaje: {update.message.text}")

    logger.error("="*70, exc_info=context.error)

    # Errores críticos de Telegram que NO se deben reintentar indefinidamente
    if isinstance(error, Exception):
        error_msg = str(error).lower()

        # Conflict: terminated by other getUpdates request
        if "conflict" in error_msg and "getupdates" in error_msg:
            from datetime import datetime, timedelta

            # Incrementar contador
            _conflict_counter += 1
            current_time = datetime.now()

            # Verificar si hay conflictos repetidos en corto tiempo
            if _last_conflict_time:
                time_since_last = (current_time - _last_conflict_time).total_seconds()
                if time_since_last < 5:  # Conflicto dentro de 5 segundos
                    logger.critical(
                        f"🚨 [ERROR_HANDLER] CONFLICTO REPETIDO #{_conflict_counter}\n"
                        f"   Hace: {time_since_last:.1f} segundos\n"
                        f"   Causa: Probablemente otra instancia del bot ejecutándose\n"
                        f"   Acción: Aguardando {5+_conflict_counter*2}s antes de reintentar..."
                    )
                    # No relanzar - dejar que polling se recupere con backoff
                else:
                    _conflict_counter = 1  # Reset si pasó suficiente tiempo
                    logger.warning(
                        f"⚠️ [ERROR_HANDLER] Conflicto aislado detectado (#{_conflict_counter})\n"
                        f"   Última: {time_since_last:.1f}s atrás\n"
                        f"   Acción: Reconectando..."
                    )
            else:
                logger.warning(
                    f"⚠️ [ERROR_HANDLER] Primer conflicto detectado\n"
                    f"   Causa: Probablemente hay dos instancias del bot\n"
                    f"   Acción: Reconectando..."
                )

            _last_conflict_time = current_time
            # No relanzar el error - dejar que el polling se recupere automáticamente
            return

        # Rate limiting
        if "too many requests" in error_msg or "429" in error_msg:
            logger.warning(
                f"⚠️ [ERROR_HANDLER] Rate limit detectado\n"
                f"   El bot está siendo throttled por Telegram\n"
                f"   Aguardando antes de reintentar..."
            )
            return

    logger.error(f"⚠️ [ERROR_HANDLER] Error no crítico manejado: {error_type}")


async def post_init(application: Application) -> None:
    """
    Callback ejecutado después de la inicialización del bot.

    Inicializa el scheduler de recordatorios.

    Args:
        application: Aplicación de Telegram
    """
    logger.info("="*70)
    logger.info("🚀 [POST_INIT] INICIALIZANDO SCHEDULER DE RECORDATORIOS")
    logger.info("="*70)

    try:
        # Inicializar scheduler con sesión temporal, luego cerrar para evitar conflictos SQLite
        logger.info("📦 [POST_INIT] Obteniendo sesión de BD temporal...")
        db = get_db()
        logger.info("✅ [POST_INIT] Sesión obtenida")

        try:
            logger.info("📦 [POST_INIT] Creando SchedulerService...")
            scheduler = SchedulerService(db, application)
            logger.info(f"✅ [POST_INIT] SchedulerService creado: {scheduler}")

            logger.info("📦 [POST_INIT] Inicializando scheduler...")
            scheduler.initialize_scheduler()
            logger.info("✅ [POST_INIT] Scheduler inicializado")

            logger.info("📦 [POST_INIT] Iniciando scheduler...")
            scheduler.start()
            logger.info("✅ [POST_INIT] Scheduler iniciado")

            # Almacenar scheduler en contexto para que los handlers puedan usarlo
            logger.info("📦 [POST_INIT] Almacenando scheduler en bot_data...")
            application.bot_data['scheduler_service'] = scheduler
            logger.info("✅ [POST_INIT] Scheduler almacenado")
        finally:
            # Cerrar sesión temporal - el scheduler no la necesita permantentemente
            # y esto evita conflictos de concurrencia en SQLite con nuevas sesiones
            logger.info("📦 [POST_INIT] Cerrando sesión temporal de BD...")
            db.close()
            logger.info("✅ [POST_INIT] Sesión temporal cerrada (scheduler usará sesiones nuevas)")

        logger.info("✅ [POST_INIT] Scheduler de recordatorios inicializado correctamente")
    except Exception as e:
        logger.error(f"❌ [POST_INIT] Error inicializando scheduler: {str(e)}", exc_info=True)
        # Continuar con el bot incluso si el scheduler falla

    logger.info("="*70)
    logger.info("✅ [POST_INIT] BOT INICIALIZADO CORRECTAMENTE")
    logger.info("="*70)
    logger.info(f"   - Timezone: {settings.timezone}")
    logger.info(f"   - Recordatorios: {settings.reminder_minutes_before} minutos antes")
    logger.info(f"   - Entorno: {settings.environment}")
    logger.info(f"   - Debug: {settings.debug}")
    logger.info("="*70)


async def post_shutdown(application: Application) -> None:
    """
    Callback ejecutado al detener el bot.

    Detiene el scheduler de forma ordenada y limpia todos los recursos.

    Args:
        application: Aplicación de Telegram
    """
    logger.info("=" * 70)
    logger.info("🛑 [POST_SHUTDOWN] Iniciando shutdown ordenado...")
    logger.info("=" * 70)

    try:
        # 1. Detener scheduler primero
        logger.info("📦 [POST_SHUTDOWN] Deteniendo scheduler...")
        scheduler = application.bot_data.get('scheduler_service')
        if scheduler:
            try:
                scheduler.stop()
                logger.info("✅ [POST_SHUTDOWN] Scheduler detenido correctamente")
            except Exception as e:
                logger.warning(f"⚠️ [POST_SHUTDOWN] Error deteniendo scheduler: {str(e)}")
        else:
            logger.info("ℹ️ [POST_SHUTDOWN] No hay scheduler para detener")

        # 2. Limpiar datos de la aplicación
        logger.info("📦 [POST_SHUTDOWN] Limpiando datos de la aplicación...")
        application.bot_data.clear()
        logger.info("✅ [POST_SHUTDOWN] Datos limpiados")

        # 3. Registrar shutdown completado
        logger.info("=" * 70)
        logger.info("✅ [POST_SHUTDOWN] Bot detenido correctamente")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"❌ [POST_SHUTDOWN] Error crítico deteniendo bot: {str(e)}", exc_info=True)
        raise


def main() -> None:
    """
    Función principal que inicializa y ejecuta el bot.
    """
    # Asegurar que existen los directorios necesarios
    settings.ensure_directories()

    # Inicializar base de datos
    logger.info("Inicializando base de datos...")
    init_db()
    logger.info("Base de datos inicializada")

    # Crear aplicación
    logger.info("Creando aplicación de Telegram...")
    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # Registrar error handler PRIMERO (antes de otros handlers)
    logger.info("Registrando error handler centralizado...")
    application.add_error_handler(error_handler)
    logger.info("✅ Error handler registrado")

    # Registrar handlers de comandos
    logger.info("Registrando handlers...")

    # IMPORTANTE: Registrar CommandHandlers ANTES de ConversationHandlers
    # Para asegurar que /start, /help, etc. se procesen primero

    # Comandos comunes (registrar primero)
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("listar_alumnos", listar_alumnos_command))
    application.add_handler(CommandHandler("reporte", reporte_command))
    application.add_handler(CommandHandler("mis_sesiones", mis_sesiones_command))
    application.add_handler(CommandHandler("mi_semana", mi_semana_command))

    # ConversationHandler para configuración de entrenamientos (registrar aquí antes de otros handlers)
    application.add_handler(config_training_handler)

    # Callbacks del menú de comandos
    application.add_handler(
        CallbackQueryHandler(
            commands_menu_handler,
            pattern=r"^cmd_"
        )
    )

    # Handler CENTRAL para entrada de texto (coordina todos los flujos)
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text_input
        )
    )

    # Handler para confirmación de registro
    application.add_handler(
        CallbackQueryHandler(
            handle_registration_confirmation,
            pattern=r"^reg_confirm_"
        )
    )

    # Handler para selección de día en flujo de entrenamientos
    application.add_handler(
        CallbackQueryHandler(
            handle_training_day_selection,
            pattern=r"^day_"
        )
    )

    # Handler para "¿otro día?" en flujo de entrenamientos
    application.add_handler(
        CallbackQueryHandler(
            handle_training_another_day,
            pattern=r"^train_another_"
        )
    )

    # Handler para confirmación final en flujo de entrenamientos
    application.add_handler(
        CallbackQueryHandler(
            handle_training_final_confirm,
            pattern=r"^train_confirm_"
        )
    )

    # ConversationHandlers
    application.add_handler(build_registration_conv_handler())
    application.add_handler(build_training_conv_handler())
    application.add_handler(build_edit_training_conv_handler())

    # Callbacks de feedback (registrar al final)
    application.add_handler(
        CallbackQueryHandler(
            handle_feedback_intensity,
            pattern=r"^feedback_intensity_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            handle_feedback_completion,
            pattern=r"^feedback_completed_"
        )
    )

    logger.info("Handlers registrados correctamente")

    # Iniciar bot
    logger.info("=" * 70)
    logger.info("🚀 EntrenaSmart Bot iniciando...")
    logger.info(f"   Entorno: {settings.environment}")
    logger.info(f"   Debug: {settings.debug}")
    logger.info(f"   Timezone: {settings.timezone}")
    logger.info(f"   Token: {settings.telegram_bot_token[:10]}...***")
    logger.info("=" * 70)

    # Ejecutar bot
    logger.info("Iniciando polling de Telegram...")
    logger.info("   - allowed_updates: Update.ALL_TYPES")
    logger.info("   - drop_pending_updates: True")

    try:
        logger.info("El bot está conectando a Telegram...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    except KeyboardInterrupt:
        logger.info("⏹️ [POLLING] Bot detenido por el usuario (KeyboardInterrupt)")
        raise
    except Exception as e:
        logger.error(f"❌ [POLLING] Error fatal en polling: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}", exc_info=True)
        raise

