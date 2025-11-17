"""
Repository para Configuración de Recordatorio Semanal
======================================================

Maneja operaciones CRUD para WeeklyReminderConfig.
"""
from typing import Optional
from sqlalchemy.orm import Session
from backend.src.models.weekly_reminder_config import WeeklyReminderConfig


class WeeklyReminderRepository:
    """Repository para gestionar configuración de recordatorios semanales."""

    def __init__(self, db: Session):
        """
        Inicializa el repository.

        Args:
            db: Sesión de SQLAlchemy
        """
        self.db = db

    def get_config(self) -> Optional[WeeklyReminderConfig]:
        """
        Obtiene la configuración activa (solo puede haber una).

        Returns:
            WeeklyReminderConfig o None si no existe
        """
        return self.db.query(WeeklyReminderConfig).first()

    def create_config(
        self,
        is_monday_off: bool = False,
        message_full_week: Optional[str] = None,
        message_monday_off: Optional[str] = None,
        send_day: int = 6,
        send_hour: int = 18,
        send_minute: int = 0,
        is_active: bool = True
    ) -> WeeklyReminderConfig:
        """
        Crea una nueva configuración.

        Args:
            is_monday_off: Si el lunes no trabaja
            message_full_week: Mensaje para semana completa (usa default si es None)
            message_monday_off: Mensaje cuando lunes no trabaja (usa default si es None)
            send_day: Día de envío (0-6)
            send_hour: Hora de envío (0-23)
            send_minute: Minuto de envío (0-59)
            is_active: Si está activo

        Returns:
            WeeklyReminderConfig creado
        """
        config_data = {
            "is_monday_off": is_monday_off,
            "send_day": send_day,
            "send_hour": send_hour,
            "send_minute": send_minute,
            "is_active": is_active
        }

        # Solo incluir mensajes si se proporcionan (para usar defaults del modelo)
        if message_full_week is not None:
            config_data["message_full_week"] = message_full_week
        if message_monday_off is not None:
            config_data["message_monday_off"] = message_monday_off

        config = WeeklyReminderConfig(**config_data)
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def update_config(
        self,
        config_id: int,
        is_monday_off: Optional[bool] = None,
        message_full_week: Optional[str] = None,
        message_monday_off: Optional[str] = None,
        send_day: Optional[int] = None,
        send_hour: Optional[int] = None,
        send_minute: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Optional[WeeklyReminderConfig]:
        """
        Actualiza una configuración existente.

        Args:
            config_id: ID de la configuración
            is_monday_off: Si el lunes no trabaja
            message_full_week: Mensaje para semana completa
            message_monday_off: Mensaje cuando lunes no trabaja
            send_day: Día de envío (0-6)
            send_hour: Hora de envío (0-23)
            send_minute: Minuto de envío (0-59)
            is_active: Si está activo

        Returns:
            WeeklyReminderConfig actualizado o None si no existe
        """
        config = self.db.query(WeeklyReminderConfig).filter(
            WeeklyReminderConfig.id == config_id
        ).first()

        if not config:
            return None

        # Actualizar solo los campos proporcionados
        if is_monday_off is not None:
            config.is_monday_off = is_monday_off
        if message_full_week is not None:
            config.message_full_week = message_full_week
        if message_monday_off is not None:
            config.message_monday_off = message_monday_off
        if send_day is not None:
            config.send_day = send_day
        if send_hour is not None:
            config.send_hour = send_hour
        if send_minute is not None:
            config.send_minute = send_minute
        if is_active is not None:
            config.is_active = is_active

        self.db.commit()
        self.db.refresh(config)
        return config

    def delete_config(self, config_id: int) -> bool:
        """
        Elimina una configuración.

        Args:
            config_id: ID de la configuración

        Returns:
            True si fue eliminada, False si no existía
        """
        config = self.db.query(WeeklyReminderConfig).filter(
            WeeklyReminderConfig.id == config_id
        ).first()

        if not config:
            return False

        self.db.delete(config)
        self.db.commit()
        return True

    def get_or_create_config(self) -> WeeklyReminderConfig:
        """
        Obtiene la configuración existente o crea una con valores por defecto.

        Returns:
            WeeklyReminderConfig
        """
        config = self.get_config()
        if not config:
            config = self.create_config()
        return config
