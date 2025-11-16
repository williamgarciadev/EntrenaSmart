"""
Configuración de la aplicación con Pydantic Settings
=====================================================

Este módulo maneja toda la configuración de la aplicación mediante
variables de entorno, proporcionando validación de tipos y valores
por defecto seguros.
"""
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import pytz


class Settings(BaseSettings):
    """
    Configuración de la aplicación EntrenaSmart.

    Lee variables de entorno desde el archivo .env y valida los tipos.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ====================================
    # Configuración del Bot de Telegram
    # ====================================
    telegram_bot_token: str = Field(
        ...,
        description="Token del bot de Telegram (obtener de @BotFather)"
    )

    trainer_telegram_id: int = Field(
        ...,
        description="ID de Telegram del entrenador autorizado"
    )

    # ====================================
    # Configuración de Recordatorios
    # ====================================
    reminder_minutes_before: int = Field(
        default=30,
        description="Minutos antes del entrenamiento para enviar recordatorio",
        ge=5,
        le=120
    )

    # ====================================
    # Configuración de Zona Horaria
    # ====================================
    timezone: str = Field(
        default="America/Bogota",
        description="Zona horaria para los recordatorios"
    )

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        """Valida que la zona horaria sea válida."""
        try:
            pytz.timezone(v)
            return v
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(
                f"Zona horaria inválida: {v}. "
                "Ver lista en: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
            )

    # ====================================
    # Configuración de Base de Datos
    # ====================================
    database_path: Path = Field(
        default=Path("storage/entrenasmart.db"),
        description="Ruta de la base de datos SQLite"
    )

    @property
    def database_url(self) -> str:
        """URL de conexión a la base de datos."""
        return f"sqlite:///{self.database_path}"

    # ====================================
    # Configuración de Logging
    # ====================================
    log_level: str = Field(
        default="INFO",
        description="Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    log_file: Path = Field(
        default=Path("logs/bot.log"),
        description="Ruta del archivo de log"
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Valida que el nivel de log sea válido."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"Nivel de log inválido: {v}. "
                f"Debe ser uno de: {', '.join(valid_levels)}"
            )
        return v_upper

    # ====================================
    # Configuración de Reportes
    # ====================================
    weekly_report_day: int = Field(
        default=6,
        description="Día de la semana para reporte semanal (0=Lunes, 6=Domingo)",
        ge=0,
        le=6
    )

    weekly_report_time: str = Field(
        default="20:00",
        description="Hora para enviar reporte semanal (formato 24h: HH:MM)"
    )

    @field_validator("weekly_report_time")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """Valida que el formato de hora sea válido."""
        try:
            hours, minutes = v.split(":")
            h, m = int(hours), int(minutes)
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError
            return f"{h:02d}:{m:02d}"
        except (ValueError, AttributeError):
            raise ValueError(
                f"Formato de hora inválido: {v}. "
                "Debe ser HH:MM en formato 24h (ej: 20:00)"
            )

    # ====================================
    # Configuración de Desarrollo
    # ====================================
    debug: bool = Field(
        default=False,
        description="Modo debug"
    )

    environment: str = Field(
        default="production",
        description="Entorno de ejecución (development, production)"
    )

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Valida que el entorno sea válido."""
        valid_envs = {"development", "production", "testing"}
        v_lower = v.lower()
        if v_lower not in valid_envs:
            raise ValueError(
                f"Entorno inválido: {v}. "
                f"Debe ser uno de: {', '.join(valid_envs)}"
            )
        return v_lower

    # ====================================
    # Propiedades Calculadas
    # ====================================

    @property
    def is_development(self) -> bool:
        """Retorna True si está en modo desarrollo."""
        return self.environment == "development" or self.debug

    @property
    def is_production(self) -> bool:
        """Retorna True si está en modo producción."""
        return self.environment == "production" and not self.debug

    def ensure_directories(self) -> None:
        """Crea los directorios necesarios si no existen."""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Crear directorio de backups
        backup_dir = self.database_path.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """
    Obtiene la instancia singleton de configuración.

    Usa lru_cache para asegurar que solo se cree una instancia.

    Returns:
        Settings: Configuración de la aplicación
    """
    return Settings()


# Instancia global de configuración
settings = get_settings()

