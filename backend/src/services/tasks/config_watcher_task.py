# -*- coding: utf-8 -*-
"""
Config Watcher Task
===================

Tarea que revisa cambios en la configuración del recordatorio semanal
y reprograma automáticamente si detecta cambios.

Esta tarea se ejecuta cada minuto desde APScheduler.
"""
from backend.src.models.base import get_db
from backend.src.services.weekly_reminder_service import WeeklyReminderService
from backend.src.utils.logger import logger


class ConfigWatcherTask:
    """Tarea para detectar cambios en configuración del recordatorio semanal."""

    # Variable de clase para almacenar último hash conocido
    _last_config_hash = None

    @classmethod
    def check_config_changes(cls) -> None:
        """
        Revisa si la configuración del recordatorio semanal cambió.

        Compara la configuración actual de BD con la última conocida.
        Si hay cambios, reprograma el recordatorio automáticamente.
        """
        try:
            db = get_db()
            try:
                service = WeeklyReminderService(db)
                config = service.get_or_create_config()

                # Crear hash de configuración actual
                config_hash = (
                    f"{config['is_active']}_"
                    f"{config['send_day']}_"
                    f"{config['send_hour']}_"
                    f"{config['send_minute']}_"
                    f"{config['is_monday_off']}"
                )

                # Obtener hash anterior
                if cls._last_config_hash is None:
                    cls._last_config_hash = config_hash
                    logger.info(
                        f"👁️ [CONFIG_WATCHER] Hash inicial guardado: {config_hash}"
                    )
                    return

                # Comparar
                if config_hash != cls._last_config_hash:
                    logger.info("🔄 [CONFIG_WATCHER] ¡Detectado cambio en configuración!")
                    logger.info(f"   - Anterior: {cls._last_config_hash}")
                    logger.info(f"   - Actual: {config_hash}")

                    # Importar aquí para evitar circular imports
                    from backend.src.services.scheduler_service import get_global_application

                    # Obtener scheduler desde bot_data
                    application = get_global_application()
                    if application and 'scheduler_service' in application.bot_data:
                        scheduler_service = application.bot_data['scheduler_service']
                        scheduler_service.reschedule_weekly_reminder()
                        logger.info("✅ [CONFIG_WATCHER] Recordatorio reprogramado automáticamente")
                    else:
                        logger.warning("⚠️ [CONFIG_WATCHER] No se pudo obtener scheduler_service")

                    # Actualizar hash
                    cls._last_config_hash = config_hash

            finally:
                db.close()

        except Exception as e:
            logger.error(
                f"❌ [CONFIG_WATCHER] Error revisando cambios: {str(e)}",
                exc_info=True
            )
