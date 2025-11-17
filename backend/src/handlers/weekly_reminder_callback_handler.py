# -*- coding: utf-8 -*-
"""
Handler para Callback del Recordatorio Semanal
==============================================

Maneja el callback cuando el alumno presiona el botón "Configurar mi semana"
desde el recordatorio semanal.

Flujo guiado con botones inline para evitar errores.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from backend.src.utils.logger import logger


async def handle_weekly_reminder_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja el callback cuando el alumno presiona "Configurar mi semana".

    Inicia el flujo de configuración de entrenamientos con botones inline.
    """
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    chat_id = query.message.chat_id

    logger.info(f"📅 [WEEKLY_CALLBACK] Usuario {user_id} presionó 'Configurar mi semana'")

    # Inicializar datos de configuración semanal
    context.user_data['weekly_config'] = {
        'trainings': [],  # Lista de {day: int, time: str}
        'user_id': user_id,
        'chat_id': chat_id
    }

    # Mostrar botones de días
    await _show_day_selection(query.message, context)

    logger.info(f"✅ [WEEKLY_CALLBACK] Flujo de configuración iniciado para usuario {user_id}")


async def _show_day_selection(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra botones para seleccionar día de la semana."""
    keyboard = [
        [
            InlineKeyboardButton("Lunes", callback_data="wc_day_0"),
            InlineKeyboardButton("Martes", callback_data="wc_day_1")
        ],
        [
            InlineKeyboardButton("Miércoles", callback_data="wc_day_2"),
            InlineKeyboardButton("Jueves", callback_data="wc_day_3")
        ],
        [
            InlineKeyboardButton("Viernes", callback_data="wc_day_4"),
            InlineKeyboardButton("Sábado", callback_data="wc_day_5")
        ],
        [InlineKeyboardButton("Domingo", callback_data="wc_day_6")],
        [InlineKeyboardButton("✅ Finalizar", callback_data="wc_finish")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Mostrar días ya seleccionados
    trainings = context.user_data.get('weekly_config', {}).get('trainings', [])
    if trainings:
        day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        selected = "\n".join([f"• {day_names[t['day']]} a las {t['time']}" for t in trainings])
        text = f"📅 <b>Configurar mi Semana</b>\n\n<b>Entrenamientos agregados:</b>\n{selected}\n\n¿Qué otro día deseas entrenar?"
    else:
        text = "📅 <b>Configurar mi Semana</b>\n\n¿Qué día de la semana deseas entrenar?\n\nPuedes seleccionar varios días, uno por uno."

    await message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
