"""
Sistema de Logging
==================

Configura el sistema de logging para toda la aplicación.
"""
import logging
import sys
from pathlib import Path
from typing import Optional

from backend.src.core.config import settings


def setup_logger(
    name: str = "entrenasmart",
    level: Optional[str] = None
) -> logging.Logger:
    """
    Configura y retorna un logger.

    Args:
        name: Nombre del logger
        level: Nivel de logging (opcional, usa settings si no se especifica)

    Returns:
        logging.Logger: Logger configurado
    """
    # Crear logger
    logger = logging.getLogger(name)

    # Configurar nivel
    log_level = level or settings.log_level
    logger.setLevel(getattr(logging, log_level))

    # Evitar duplicar handlers
    if logger.handlers:
        return logger

    # Formato de log
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para archivo
    if settings.log_file:
        # Asegurar que el directorio existe
        settings.log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(
            settings.log_file,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Logger global de la aplicación
logger = setup_logger()

