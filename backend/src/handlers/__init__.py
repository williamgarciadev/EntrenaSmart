"""
Handlers - Manejadores de comandos y mensajes de Telegram
==========================================================

Este módulo contiene los handlers que procesan los comandos
y mensajes del bot de Telegram.

Handlers disponibles:
- trainer_handlers: Comandos del entrenador
- student_handlers: Comandos y respuestas de alumnos
"""
from backend.src.handlers.trainer_handlers import (
    start_command,
    help_command,
    listar_alumnos_command,
    reporte_command,
    is_trainer
)

from backend.src.handlers.registration_handler import build_registration_conv_handler
from backend.src.handlers.training_handler import build_training_conv_handler
from backend.src.handlers.edit_training_handler import build_edit_training_conv_handler

from backend.src.handlers.student_handlers import (
    mis_sesiones_command,
    handle_feedback_intensity,
    handle_feedback_text,
    handle_feedback_completion
)

__all__ = [
    # Comandos comunes
    "start_command",
    "help_command",

    # ConversationHandlers del entrenador
    "build_registration_conv_handler",
    "build_training_conv_handler",
    "build_edit_training_conv_handler",

    # Comandos del entrenador (simples)
    "listar_alumnos_command",
    "reporte_command",
    "is_trainer",

    # Comandos de alumnos
    "mis_sesiones_command",
    "handle_feedback_intensity",
    "handle_feedback_text",
    "handle_feedback_completion",
]

