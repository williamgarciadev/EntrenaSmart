"""
Service para Configuración de Recordatorio Semanal
===================================================

Lógica de negocio para gestionar recordatorios semanales del entrenador.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from backend.src.models.weekly_reminder_config import WeeklyReminderConfig
from backend.src.models.student import Student
from backend.src.repositories.weekly_reminder_repository import WeeklyReminderRepository
from backend.src.utils.logger import logger


class WeeklyReminderService:
    """Service para gestionar configuración de recordatorios semanales."""

    def __init__(self, db: Session):
        """
        Inicializa el service.

        Args:
            db: Sesión de SQLAlchemy
        """
        self.db = db
        self.repository = WeeklyReminderRepository(db)

    def get_config(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene la configuración actual.

        Returns:
            Dict con configuración o None
        """
        config = self.repository.get_config()
        if not config:
            return None

        return self._config_to_dict(config)

    def get_or_create_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración existente o crea una con valores por defecto.

        Returns:
            Dict con configuración
        """
        config = self.repository.get_or_create_config()
        return self._config_to_dict(config)

    def update_config(
        self,
        is_monday_off: Optional[bool] = None,
        message_full_week: Optional[str] = None,
        message_monday_off: Optional[str] = None,
        send_day: Optional[int] = None,
        send_hour: Optional[int] = None,
        send_minute: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Actualiza la configuración.

        Args:
            is_monday_off: Si el lunes no trabaja
            message_full_week: Mensaje para semana completa
            message_monday_off: Mensaje cuando lunes no trabaja
            send_day: Día de envío (0-6)
            send_hour: Hora de envío (0-23)
            send_minute: Minuto de envío (0-59)
            is_active: Si está activo

        Returns:
            Dict con configuración actualizada o None si no existe
        """
        # Validaciones
        if send_day is not None and not (0 <= send_day <= 6):
            raise ValueError("send_day debe estar entre 0 (Lunes) y 6 (Domingo)")

        if send_hour is not None and not (0 <= send_hour <= 23):
            raise ValueError("send_hour debe estar entre 0 y 23")

        if send_minute is not None and not (0 <= send_minute <= 59):
            raise ValueError("send_minute debe estar entre 0 y 59")

        # Obtener o crear configuración
        existing_config = self.repository.get_config()
        if not existing_config:
            # Si no existe, crear una nueva
            config = self.repository.create_config(
                is_monday_off=is_monday_off if is_monday_off is not None else False,
                message_full_week=message_full_week,
                message_monday_off=message_monday_off,
                send_day=send_day if send_day is not None else 6,
                send_hour=send_hour if send_hour is not None else 18,
                send_minute=send_minute if send_minute is not None else 0,
                is_active=is_active if is_active is not None else True
            )
        else:
            # Actualizar existente
            config = self.repository.update_config(
                config_id=existing_config.id,
                is_monday_off=is_monday_off,
                message_full_week=message_full_week,
                message_monday_off=message_monday_off,
                send_day=send_day,
                send_hour=send_hour,
                send_minute=send_minute,
                is_active=is_active
            )

        if not config:
            return None

        logger.info(
            f"✅ [WEEKLY_REMINDER] Configuración actualizada: "
            f"{config.day_name} {config.send_time_str}, "
            f"monday_off={config.is_monday_off}, "
            f"active={config.is_active}"
        )

        return self._config_to_dict(config)

    def get_active_students(self) -> List[Student]:
        """
        Obtiene todos los estudiantes activos para envío masivo.

        Returns:
            Lista de estudiantes activos
        """
        students = self.db.query(Student).filter(
            Student.is_active == True
        ).all()

        logger.info(f"📊 [WEEKLY_REMINDER] Estudiantes activos encontrados: {len(students)}")
        return students

    def get_message_to_send(self) -> Optional[str]:
        """
        Obtiene el mensaje que se debe enviar según la configuración actual.

        Returns:
            Mensaje a enviar o None si no hay configuración
        """
        config = self.repository.get_config()
        if not config or not config.is_active:
            return None

        return config.current_message

    def _config_to_dict(self, config: WeeklyReminderConfig) -> Dict[str, Any]:
        """
        Convierte un modelo WeeklyReminderConfig a diccionario.

        Args:
            config: Configuración a convertir

        Returns:
            Dict con datos de la configuración
        """
        return {
            "id": config.id,
            "is_monday_off": config.is_monday_off,
            "message_full_week": config.message_full_week,
            "message_monday_off": config.message_monday_off,
            "send_day": config.send_day,
            "send_day_name": config.day_name,
            "send_hour": config.send_hour,
            "send_minute": config.send_minute,
            "send_time": config.send_time_str,
            "is_active": config.is_active,
            "current_message": config.current_message,
            "created_at": config.created_at.isoformat() if config.created_at else None,
            "updated_at": config.updated_at.isoformat() if config.updated_at else None
        }
