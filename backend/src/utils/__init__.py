"""
Utils - Utilidades compartidas
================================

Este módulo contiene utilidades y funciones auxiliares:
- logger: Configuración de logging
- messages: Templates de mensajes
"""
from .logger import logger, setup_logger
from .messages import Messages

__all__ = [
    "logger",
    "setup_logger",
    "Messages",
]

