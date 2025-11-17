# -*- coding: utf-8 -*-
"""
Handler para Callback del Recordatorio Semanal
==============================================

Maneja el callback cuando el alumno presiona el botón "Configurar mi semana"
desde el recordatorio semanal.
"""
from telegram import Update
from telegram.ext import ContextTypes

from backend.src.utils.logger import logger


async def handle_weekly_reminder_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja el callback cuando el alumno presiona "Configurar mi semana".

    Inicia el flujo de configuración de entrenamientos para el alumno.
    """
    query = update.callback_query
    await query.answer()

    logger.info(f"📅 [WEEKLY_CALLBACK] Usuario {query.from_user.id} presionó 'Configurar mi semana'")

    # Enviar mensaje inicial del flujo
    await query.message.reply_text(
        "📅 <b>Configurar mi Semana de Entrenamientos</b>\n\n"
        "¡Perfecto! Vamos a programar tus entrenamientos para esta semana.\n\n"
        "Por favor, envíame los días y horas que deseas entrenar.\n\n"
        "<b>Formato:</b> <code>Lunes, Miércoles y Viernes 5:00 AM</code>\n\n"
        "O puedes enviar cada día por separado si prefieres.",
        parse_mode="HTML"
    )

    logger.info(f"✅ [WEEKLY_CALLBACK] Flujo de configuración iniciado para usuario {query.from_user.id}")
