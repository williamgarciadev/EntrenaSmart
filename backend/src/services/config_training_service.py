# -*- coding: utf-8 -*-
"""
Servicio de Configuración de Entrenamientos Diarios
====================================================

Gestiona la configuración semanal del entrenador:
qué tipo de entrenamiento y ubicación para cada día.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.src.models.training_day_config import TrainingDayConfig
from backend.src.repositories.config_training_repository import ConfigTrainingRepository
from backend.src.core.exceptions import ValidationError, RecordNotFoundError
from backend.src.utils.logger import logger


class ConfigTrainingService:
    """Servicio para gestionar configuración semanal de entrenamientos."""

    def __init__(self, db: Session):
        """
        Inicializa el servicio.

        Args:
            db: Sesión de SQLAlchemy
        """
        self.db = db
        self.repository = ConfigTrainingRepository(db)

    def configure_day(
        self,
        weekday: int,
        session_type: str,
        location: str
    ) -> TrainingDayConfig:
        """
        Configura o actualiza el entrenamiento de un día.

        Args:
            weekday: Día de la semana (0=Lunes, 6=Domingo)
            session_type: Tipo de entrenamiento (ej: "Pierna", "Funcional")
            location: Ubicación/piso (ej: "2do Piso")

        Returns:
            TrainingDayConfig creado o actualizado

        Raises:
            ValidationError: Si los datos no son válidos
        """
        logger.info(f"[CONFIG_DAY] Iniciando configuración: weekday={weekday}, type={session_type}, loc={location}")

        # Validar
        if not isinstance(weekday, int) or weekday < 0 or weekday > 6:
            raise ValidationError("Día de la semana inválido (debe ser 0-6)")

        if not session_type or not isinstance(session_type, str):
            raise ValidationError("Tipo de entrenamiento inválido")

        if not location or not isinstance(location, str):
            raise ValidationError("Ubicación inválida")

        logger.info(f"[CONFIG_DAY] Validación OK, llamando repositorio...")

        # Crear o actualizar
        try:
            config = self.repository.update_by_weekday(weekday, session_type, location)
            logger.info(f"[CONFIG_DAY] Configuración guardada OK")

            logger.info(
                f"Entrenamiento configurado: {config.weekday_name} → "
                f"{session_type} en {location}"
            )
            return config
        except Exception as e:
            logger.error(f"[CONFIG_DAY] Error en repositorio: {e}", exc_info=True)
            raise

    def get_day_config(self, weekday: int) -> Optional[TrainingDayConfig]:
        """
        Obtiene la configuración de un día específico.

        Args:
            weekday: Día de la semana

        Returns:
            TrainingDayConfig o None si no existe
        """
        return self.repository.get_by_weekday(weekday)

    def get_weekly_schedule(self) -> Dict[str, Dict[str, str]]:
        """
        Obtiene la programación completa de la semana.

        Returns:
            Diccionario con la configuración de cada día activo

        Ejemplo:
            {
                "Lunes": {"session_type": "Pierna", "location": "2do Piso"},
                "Miércoles": {"session_type": "Funcional", "location": "4to Piso"}
            }
        """
        configs = self.repository.get_all_active()
        schedule = {}

        for config in configs:
            schedule[config.weekday_name] = {
                "session_type": config.session_type,
                "location": config.location
            }

        return schedule

    def get_all_configs(self) -> List[TrainingDayConfig]:
        """
        Obtiene todas las configuraciones activas.

        Returns:
            Lista de TrainingDayConfig
        """
        return self.repository.get_all_active()

    def format_weekly_summary(self) -> str:
        """
        Genera un resumen formateado de la semana programada.

        Returns:
            String con el resumen de la semana

        Ejemplo:
            "Lunes: Pierna (2do Piso)
             Miércoles: Funcional (4to Piso)
             Viernes: Espalda (2do Piso)"
        """
        configs = self.repository.get_all_active()

        if not configs:
            return "No hay entrenamientos configurados para esta semana."

        lines = []
        for config in configs:
            line = f"{config.weekday_name}: {config.session_type} ({config.location})"
            lines.append(line)

        return "\n".join(lines)

    def delete_day_config(self, weekday: int) -> None:
        """
        Elimina la configuración de un día.

        Args:
            weekday: Día de la semana

        Raises:
            RecordNotFoundError: Si no existe configuración para ese día
        """
        config = self.repository.get_by_weekday(weekday)
        if not config:
            raise RecordNotFoundError(f"No hay configuración para {weekday}")

        self.repository.delete(config.id)
        logger.info(f"Configuración de entrenamiento eliminada para {config.weekday_name}")
