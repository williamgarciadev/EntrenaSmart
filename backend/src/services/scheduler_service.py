# -*- coding: utf-8 -*-
"""
Servicio de Programación de Tareas con APScheduler
===================================================

Gestiona la programación y ejecución de tareas recurrentes como:
- Recordatorios de entrenamientos (30 minutos antes)
- Reportes semanales de actividad
- Retroalimentación post-entrenamiento

Usa APScheduler con persistencia en SQLite para que los jobs sobrevivan
a reinicios del bot.

Ejemplo:
    >>> from src.services.scheduler_service import SchedulerService
    >>> scheduler = SchedulerService(db, bot)
    >>> scheduler.initialize_scheduler()
    >>> scheduler.start()
    >>> scheduler.schedule_training_reminder(
    ...     training_id=1,
    ...     student_chat_id=123456,
    ...     weekday=0,  # Lunes
    ...     training_time="05:00",
    ...     session_type="Funcional"
    ... )
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import asyncio
import pytz
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger

from backend.src.core.config import settings
from backend.src.utils.logger import logger

# Variables globales para almacenar application, bot y event_loop (evita problemas de serialización)
_global_application = None
_global_bot = None
_global_event_loop = None


def set_global_application(application):
    """Establece la instancia global de la aplicación para usar en recordatorios."""
    global _global_application
    _global_application = application
    logger.info(f"🌍 [GLOBAL] Application establecida globalmente: {application}")


def get_global_application():
    """Obtiene la instancia global de la aplicación."""
    global _global_application
    return _global_application


def set_global_bot(bot):
    """Establece la instancia global del bot para usar en recordatorios."""
    global _global_bot
    _global_bot = bot
    logger.info(f"🌍 [GLOBAL] Bot establecido globalmente: {bot}")


def get_global_bot():
    """Obtiene la instancia global del bot."""
    global _global_bot
    return _global_bot


def set_global_event_loop(event_loop):
    """Establece el event loop global para usar en recordatorios."""
    global _global_event_loop
    _global_event_loop = event_loop
    logger.info(f"🌍 [GLOBAL] Event loop establecido globalmente: {event_loop}")


def get_global_event_loop():
    """Obtiene el event loop global."""
    global _global_event_loop
    return _global_event_loop


class SchedulerService:
    """
    Servicio para programar y gestionar tareas recurrentes con APScheduler.

    Atributos:
        db: Sesión de SQLAlchemy
        bot: Application de Telegram para enviar mensajes
        scheduler: Instancia de AsyncIOScheduler
        timezone: Timezone configurado (ej: "America/Bogota")
    """

    def __init__(self, db: Session, bot=None):
        """
        Inicializa el servicio de scheduler.

        Args:
            db: Sesión de SQLAlchemy para acceso a BD
            bot: Application de Telegram (para enviar mensajes)
        """
        self.db = db
        self.bot = bot
        self.application = bot  # Guardar application (same as bot)
        self.scheduler: Optional[BackgroundScheduler] = None
        self.timezone = settings.timezone

    def initialize_scheduler(self) -> None:
        """
        Inicializa y configura el BackgroundScheduler con persistencia.

        Configuración:
        - JobStore: SQLAlchemy (tabla apscheduler_jobs)
        - Executor: ThreadPoolExecutor (ejecuta en threads de fondo)
        - Timezone: Desde settings (ej: "America/Bogota")

        Raises:
            Exception: Si hay error en inicialización de BD
        """
        try:
            logger.info("🔧 [SCHEDULER] Inicializando SchedulerService...")

            # Obtener el event loop del bot (telegram.ext lo establece en el main thread)
            logger.info("🔧 [SCHEDULER] Intentando obtener event loop...")
            try:
                self.event_loop = asyncio.get_running_loop()
                logger.info(f"✅ [SCHEDULER] Event loop corriendo: {self.event_loop}")
            except RuntimeError as e:
                logger.debug(f"⚠️ [SCHEDULER] get_running_loop() falló: {str(e)}")
                # Si no está disponible ahora, intentar obtenerlo cuando se necesite
                try:
                    self.event_loop = asyncio.get_event_loop()
                    logger.info(f"✅ [SCHEDULER] Event loop obtenido (no corriendo): {self.event_loop}")
                except RuntimeError as e2:
                    self.event_loop = None
                    logger.warning(f"⚠️ [SCHEDULER] No hay event loop disponible: {str(e2)}")

            # Configurar job store con SQLite
            logger.info("🔧 [SCHEDULER] Configurando job store...")
            job_stores = {
                'default': SQLAlchemyJobStore(
                    engine=self.db.get_bind(),
                    tablename='apscheduler_jobs'
                )
            }
            logger.info("✅ [SCHEDULER] Job store configurado")

            # Configuración general
            job_defaults = {
                'coalesce': True,  # Si se saltea un job, ejecutar solo una vez
                'max_instances': 1,  # Solo una instancia del job a la vez
                'misfire_grace_time': 60  # Ejecutar si pasó hace <60 seg
            }

            # Crear scheduler (BackgroundScheduler funciona en su propio thread)
            logger.info("🔧 [SCHEDULER] Creando BackgroundScheduler...")
            self.scheduler = BackgroundScheduler(
                jobstores=job_stores,
                job_defaults=job_defaults,
                timezone=pytz.timezone(self.timezone)
            )
            logger.info("✅ [SCHEDULER] BackgroundScheduler creado")

            # Establecer variables globales para evitar problemas de serialización
            logger.info("🌍 [SCHEDULER] Estableciendo variables globales...")
            set_global_bot(self.bot)
            set_global_application(self.application)
            if self.event_loop:
                set_global_event_loop(self.event_loop)

            logger.info(f"✅ [SCHEDULER] SchedulerService inicializado con timezone: {self.timezone}")
            logger.info(f"   - Bot: {self.bot}")
            logger.info(f"   - Application: {self.application}")
            logger.info(f"   - Event loop: {self.event_loop}")

        except Exception as e:
            logger.error(f"❌ [SCHEDULER] Error inicializando scheduler: {str(e)}", exc_info=True)
            raise

    def start(self) -> None:
        """
        Arranca el scheduler para procesar jobs.

        Debe llamarse después de `initialize_scheduler()`.
        Programa automáticamente el recordatorio semanal del entrenador.
        """
        if self.scheduler is None:
            raise RuntimeError("Scheduler no inicializado. Llama initialize_scheduler() primero.")

        try:
            self.scheduler.start()
            logger.info("Scheduler iniciado correctamente")

            # Programar recordatorio semanal del entrenador automáticamente
            self.schedule_weekly_reminder()

        except Exception as e:
            logger.error(f"Error iniciando scheduler: {str(e)}", exc_info=True)
            raise

    def stop(self) -> None:
        """
        Detiene el scheduler de forma ordenada.

        Cancela todos los jobs pendientes.
        """
        if self.scheduler:
            try:
                self.scheduler.shutdown(wait=False)
                logger.info("Scheduler detenido correctamente")
            except Exception as e:
                logger.error(f"Error deteniendo scheduler: {str(e)}", exc_info=True)

    def schedule_weekly_reminder(self) -> str:
        """
        Programa el recordatorio semanal del entrenador.

        Lee la configuración de WeeklyReminderConfig de la BD y programa
        el envío automático según el día y hora configurados.

        Returns:
            str: ID del job programado o cadena vacía si hay error
        """
        logger.info("📅 [WEEKLY_REMINDER] Programando recordatorio semanal del entrenador...")

        if self.scheduler is None:
            logger.error("❌ [WEEKLY_REMINDER] Scheduler no está inicializado")
            return ""

        try:
            # Obtener configuración de BD
            from backend.src.models.base import get_db
            from backend.src.services.weekly_reminder_service import WeeklyReminderService

            db = get_db()
            try:
                service = WeeklyReminderService(db)
                config = service.get_or_create_config()

                if not config:
                    logger.warning("⚠️ [WEEKLY_REMINDER] No hay configuración de recordatorio semanal")
                    return ""

                if not config["is_active"]:
                    logger.info("ℹ️ [WEEKLY_REMINDER] Recordatorio semanal está desactivado - no se programa")
                    return ""

                send_day = config["send_day"]
                send_hour = config["send_hour"]
                send_minute = config["send_minute"]

                logger.info(f"📊 [WEEKLY_REMINDER] Configuración obtenida:")
                logger.info(f"   - Día: {config['send_day_name']} ({send_day})")
                logger.info(f"   - Hora: {send_hour:02d}:{send_minute:02d}")
                logger.info(f"   - Modo: {'Lunes OFF' if config['is_monday_off'] else 'Semana Completa'}")

            finally:
                db.close()

            # Crear ID único para el job
            job_id = "weekly_reminder_trainer"

            # Cancelar job anterior si existe
            self._cancel_job(job_id)

            # Mapeo de weekday a nombre de día
            weekday_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            trigger_day = weekday_names[send_day]

            # Importar tarea
            from backend.src.services.tasks.weekly_reminder_task import WeeklyReminderTask

            # Programar job semanal
            self.scheduler.add_job(
                WeeklyReminderTask.send_weekly_reminder_sync,
                trigger=CronTrigger(
                    day_of_week=trigger_day,
                    hour=send_hour,
                    minute=send_minute,
                    timezone=self.timezone
                ),
                id=job_id,
                name="Recordatorio Semanal del Entrenador",
                replace_existing=True,
                misfire_grace_time=300  # Ejecutar si pasó hace <5 min
            )

            logger.info(
                f"✅ [WEEKLY_REMINDER] Recordatorio semanal programado: "
                f"{trigger_day} {send_hour:02d}:{send_minute:02d}"
            )
            return job_id

        except Exception as e:
            logger.error(
                f"❌ [WEEKLY_REMINDER] Error programando recordatorio semanal: {str(e)}",
                exc_info=True
            )
            return ""

    def reschedule_weekly_reminder(self) -> bool:
        """
        Reprograma el recordatorio semanal con la configuración actualizada.

        Returns:
            bool: True si fue reprogramado exitosamente
        """
        logger.info("🔄 [WEEKLY_REMINDER] Reprogramando recordatorio semanal...")
        job_id = self.schedule_weekly_reminder()
        return bool(job_id)

    def schedule_training_reminder(
        self,
        training_id: int,
        student_chat_id: int,
        weekday: int,
        training_time: str,
        session_type: str = "",
        location: str = ""
    ) -> str:
        """
        Programa un recordatorio semanal de entrenamiento.

        El recordatorio se envía `reminder_minutes_before` minutos antes
        del horario de entrenamiento.

        Args:
            training_id: ID del entrenamiento en BD
            student_chat_id: Chat ID del alumno en Telegram
            weekday: Día de la semana (0=Lunes, 6=Domingo)
            training_time: Hora del entrenamiento (formato "HH:MM")
            session_type: Tipo de sesión (ej: "Funcional", "Pesas")
            location: Ubicación del entrenamiento (ej: "2do Piso")

        Returns:
            str: ID del job programado

        Example:
            >>> job_id = scheduler.schedule_training_reminder(
            ...     training_id=1,
            ...     student_chat_id=123456,
            ...     weekday=0,  # Lunes
            ...     training_time="05:00",
            ...     session_type="Funcional"
            ... )
            >>> print(job_id)
            'reminder_training_1'
        """
        logger.info(f"📅 [REMINDER] Programando recordatorio:")
        logger.info(f"   - training_id={training_id}")
        logger.info(f"   - student_chat_id={student_chat_id}")
        logger.info(f"   - weekday={weekday}")
        logger.info(f"   - training_time={training_time}")
        logger.info(f"   - session_type={session_type}")

        if self.scheduler is None:
            logger.error("❌ [REMINDER] Scheduler no está inicializado. Ignorando programación.")
            return ""

        try:
            # Crear ID único para el job
            job_id = f"reminder_training_{training_id}"
            logger.info(f"🔑 [REMINDER] Job ID: {job_id}")

            # Cancelar job anterior si existe
            logger.info(f"🔄 [REMINDER] Cancelando job anterior si existe...")
            self._cancel_job(job_id)

            # Calcular hora del recordatorio (training_time - reminder_minutes_before)
            logger.info(f"⏱️ [REMINDER] Calculando hora de recordatorio...")
            reminder_hour, reminder_minute = self._calculate_reminder_time(training_time)
            logger.info(f"   - training_time={training_time}")
            logger.info(f"   - reminder_minutes_before={settings.reminder_minutes_before}")
            logger.info(f"   - reminder_time={reminder_hour:02d}:{reminder_minute:02d}")

            # Mapeo de weekday a nombre de día
            weekday_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            trigger_day = weekday_names[weekday]
            logger.info(f"📆 [REMINDER] Día: {weekday} ({trigger_day})")

            # Importar aquí para evitar circular imports
            from src.services.tasks.reminder_task import ReminderTask
            from apscheduler.triggers.combining import OrTrigger
            from apscheduler.triggers.date import DateTrigger

            # Verificar si hoy es el día del entrenamiento y la hora aún no ha pasado
            now = datetime.now(pytz.timezone(self.timezone))
            today_weekday = now.weekday()
            logger.info(f"📅 [REMINDER] Hora actual: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            logger.info(f"   - today_weekday={today_weekday}")

            triggers = []

            # Si hoy es el día del entrenamiento y la hora aún no ha pasado
            if today_weekday == weekday:
                logger.info(f"✅ [REMINDER] ¡Hoy es el día del entrenamiento!")
                # Crear próxima fecha/hora del recordatorio para hoy
                reminder_datetime = now.replace(
                    hour=reminder_hour,
                    minute=reminder_minute,
                    second=0,
                    microsecond=0
                )
                logger.info(f"⏰ [REMINDER] Hora recordatorio hoy: {reminder_datetime.strftime('%H:%M:%S')}")

                # Si la hora aún no ha pasado, agregar trigger para hoy
                if reminder_datetime > now:
                    logger.info(f"✅ [REMINDER] Hora no ha pasado - agregando DateTrigger para hoy")
                    triggers.append(DateTrigger(
                        run_date=reminder_datetime,
                        timezone=self.timezone
                    ))
                    logger.info(f"✅ [REMINDER] Recordatorio programado para HOY: {reminder_hour:02d}:{reminder_minute:02d}")
                else:
                    logger.info(f"⚠️ [REMINDER] Hora ya pasó - no agregando DateTrigger para hoy")
            else:
                logger.info(f"ℹ️ [REMINDER] Hoy no es el día del entrenamiento")

            # Siempre agregar el trigger semanal para futuras semanas
            logger.info(f"📅 [REMINDER] Agregando CronTrigger semanal para {trigger_day}")
            triggers.append(CronTrigger(
                day_of_week=trigger_day,
                hour=reminder_hour,
                minute=reminder_minute,
                timezone=self.timezone
            ))

            # Combinar triggers (si hay múltiples, usar OR)
            logger.info(f"🔀 [REMINDER] Total triggers: {len(triggers)}")
            if len(triggers) > 1:
                logger.info(f"🔀 [REMINDER] Combinando triggers con OR")
                trigger = OrTrigger(triggers)
            else:
                trigger = triggers[0]
            logger.info(f"✅ [REMINDER] Trigger configurado: {trigger}")

            # Programar job (usar versión síncrona para BackgroundScheduler)
            # IMPORTANTE: NO pasar bot ni event_loop como args (causaría error de serialización)
            # Se obtienen de variables globales en send_reminder_sync
            logger.info(f"📌 [REMINDER] Agregando job al scheduler...")
            logger.info(f"   - Function: ReminderTask.send_reminder_sync")
            logger.info(f"   - Args (serializables): chat_id={student_chat_id}, weekday={weekday}, training_time={training_time}")
            logger.info(f"   - Bot y event_loop obtienen de variables globales en ejecución")

            self.scheduler.add_job(
                ReminderTask.send_reminder_sync,
                trigger=trigger,
                args=[student_chat_id, weekday, training_time],
                id=job_id,
                name=f"Recordatorio entrenamiento {training_id}",
                replace_existing=True,
                misfire_grace_time=300  # Ejecutar si pasó hace <5 min
            )

            logger.info(f"✅ [REMINDER] Job agregado exitosamente")
            logger.info(
                f"✅ [REMINDER] Recordatorio programado completo: training_id={training_id}, "
                f"chat_id={student_chat_id}, dia={trigger_day}, "
                f"hora_recordatorio={reminder_hour:02d}:{reminder_minute:02d}"
            )

            return job_id

        except Exception as e:
            logger.error(
                f"❌ [REMINDER] Error programando recordatorio para training {training_id}: {str(e)}",
                exc_info=True
            )
            return ""

    def cancel_training_reminder(self, training_id: int) -> bool:
        """
        Cancela el recordatorio programado para un entrenamiento.

        Args:
            training_id: ID del entrenamiento a cancelar

        Returns:
            bool: True si fue cancelado, False si no existía

        Example:
            >>> canceled = scheduler.cancel_training_reminder(training_id=1)
        """
        job_id = f"reminder_training_{training_id}"
        return self._cancel_job(job_id)

    def reschedule_training_reminder(
        self,
        training_id: int,
        new_training_time: str
    ) -> bool:
        """
        Reprograma la hora de un recordatorio existente.

        Útil cuando se cambia la hora de un entrenamiento.

        Args:
            training_id: ID del entrenamiento
            new_training_time: Nueva hora (formato "HH:MM")

        Returns:
            bool: True si fue reprogramado, False si no existía

        Example:
            >>> reprogrammed = scheduler.reschedule_training_reminder(
            ...     training_id=1,
            ...     new_training_time="06:00"
            ... )
        """
        if self.scheduler is None:
            return False

        try:
            job_id = f"reminder_training_{training_id}"
            job = self.scheduler.get_job(job_id)

            if not job:
                logger.warning(f"Job {job_id} no encontrado para reprogramar")
                return False

            # Calcular nueva hora
            reminder_hour, reminder_minute = self._calculate_reminder_time(new_training_time)

            # Actualizar trigger
            job.reschedule(
                trigger=CronTrigger(
                    day_of_week=job.trigger.fields[4].expressions[0],  # Mantener día
                    hour=reminder_hour,
                    minute=reminder_minute,
                    timezone=self.timezone
                )
            )

            logger.info(
                f"Recordatorio reprogramado: training_id={training_id}, "
                f"nueva_hora={reminder_hour:02d}:{reminder_minute:02d}"
            )
            return True

        except Exception as e:
            logger.error(f"Error reprogramando recordatorio: {str(e)}", exc_info=True)
            return False

    def _calculate_reminder_time(self, training_time: str) -> tuple:
        """
        Calcula la hora del recordatorio (training_time - reminder_minutes_before).

        Args:
            training_time: Hora del entrenamiento (formato "HH:MM")

        Returns:
            tuple: (hora, minuto) como enteros

        Example:
            >>> hour, minute = scheduler._calculate_reminder_time("05:00")
            >>> # Asumiendo reminder_minutes_before=30
            >>> print(f"{hour:02d}:{minute:02d}")
            '04:30'
        """
        try:
            # Parsear hora
            parts = training_time.split(":")
            hour = int(parts[0])
            minute = int(parts[1])

            # Restar minutos de recordatorio
            time_obj = datetime(2000, 1, 1, hour, minute)
            reminder_time = time_obj - timedelta(minutes=settings.reminder_minutes_before)

            return reminder_time.hour, reminder_time.minute

        except Exception as e:
            logger.error(f"Error calculando hora de recordatorio: {str(e)}")
            return 0, 0  # Default a medianoche si hay error

    def _cancel_job(self, job_id: str) -> bool:
        """
        Auxiliar para cancelar un job por ID.

        Args:
            job_id: ID del job a cancelar

        Returns:
            bool: True si fue cancelado, False si no existía
        """
        if self.scheduler is None:
            return False

        try:
            job = self.scheduler.get_job(job_id)
            if job:
                self.scheduler.remove_job(job_id)
                logger.info(f"Job cancelado: {job_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cancelando job {job_id}: {str(e)}")
            return False

    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """
        Obtiene lista de todos los jobs programados.

        Returns:
            List[Dict]: Lista con info de jobs (id, nombre, próxima ejecución)

        Example:
            >>> jobs = scheduler.get_scheduled_jobs()
            >>> for job in jobs:
            ...     print(f"{job['id']}: {job['next_run_time']}")
        """
        if self.scheduler is None:
            return []

        jobs_info = []
        for job in self.scheduler.get_jobs():
            jobs_info.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': str(getattr(job, 'next_run_time', 'N/A')),
                'trigger': str(job.trigger)
            })

        return jobs_info

    def get_job_info(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información detallada de un job específico.

        Args:
            job_id: ID del job

        Returns:
            Dict o None con info del job

        Example:
            >>> info = scheduler.get_job_info("reminder_training_1")
            >>> if info:
            ...     print(f"Próxima ejecución: {info['next_run_time']}")
        """
        if self.scheduler is None:
            return None

        job = self.scheduler.get_job(job_id)
        if not job:
            return None

        return {
            'id': job.id,
            'name': job.name,
            'next_run_time': str(getattr(job, 'next_run_time', 'N/A')),
            'trigger': str(job.trigger),
            'args': job.args,
            'kwargs': job.kwargs
        }
