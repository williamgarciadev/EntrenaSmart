# -*- coding: utf-8 -*-
"""
Handlers para Configuración Semanal Guiada
==========================================

Maneja el flujo completo de configuración semanal con botones inline.

Callbacks:
- wc_day_X: Usuario selecciona día X (0-6)
- wc_time_HH_MM: Usuario selecciona hora HH:MM
- wc_finish: Usuario finaliza configuración
- wc_cancel: Usuario cancela configuración
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from backend.src.models.base import get_db
from backend.src.models.student import Student
from backend.src.models.training import Training
from backend.src.services.training_service import TrainingService
from backend.src.utils.logger import logger


async def handle_weekly_day_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja cuando el usuario selecciona un día de la semana.

    Muestra botones de horarios comunes.
    """
    query = update.callback_query
    await query.answer()

    # Extraer día seleccionado (formato: wc_day_0)
    day_num = int(query.data.split('_')[-1])

    logger.info(f"📅 [WC] Usuario {query.from_user.id} seleccionó día {day_num}")

    # Guardar día temporalmente
    if 'weekly_config' not in context.user_data:
        context.user_data['weekly_config'] = {'trainings': []}

    context.user_data['weekly_config']['selected_day'] = day_num

    # Mostrar botones de horarios
    await _show_time_selection(query, context, day_num)


async def _show_time_selection(query, context: ContextTypes.DEFAULT_TYPE, day_num: int) -> None:
    """Muestra botones para seleccionar hora."""
    day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    # Horarios comunes
    keyboard = [
        [
            InlineKeyboardButton("5:00 AM", callback_data="wc_time_05_00"),
            InlineKeyboardButton("6:00 AM", callback_data="wc_time_06_00")
        ],
        [
            InlineKeyboardButton("7:00 AM", callback_data="wc_time_07_00"),
            InlineKeyboardButton("8:00 AM", callback_data="wc_time_08_00")
        ],
        [
            InlineKeyboardButton("5:00 PM", callback_data="wc_time_17_00"),
            InlineKeyboardButton("6:00 PM", callback_data="wc_time_18_00")
        ],
        [
            InlineKeyboardButton("7:00 PM", callback_data="wc_time_19_00"),
            InlineKeyboardButton("8:00 PM", callback_data="wc_time_20_00")
        ],
        [InlineKeyboardButton("« Volver", callback_data="wc_back_to_days")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"📅 <b>{day_names[day_num]}</b>\n\n¿A qué hora deseas entrenar este día?"

    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def handle_weekly_time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja cuando el usuario selecciona una hora.

    Guarda el entrenamiento y vuelve a la selección de días.
    """
    query = update.callback_query
    await query.answer()

    # Extraer hora (formato: wc_time_05_00)
    parts = query.data.split('_')
    hour = int(parts[2])
    minute = int(parts[3])
    time_str = f"{hour:02d}:{minute:02d}"

    # Obtener día guardado
    config = context.user_data.get('weekly_config', {})
    day_num = config.get('selected_day')

    if day_num is None:
        await query.answer("Error: No se seleccionó día", show_alert=True)
        return

    logger.info(f"⏰ [WC] Usuario {query.from_user.id} seleccionó hora {time_str} para día {day_num}")

    # Guardar entrenamiento
    trainings = config.get('trainings', [])
    trainings.append({'day': day_num, 'time': time_str})
    config['trainings'] = trainings
    context.user_data['weekly_config'] = config

    # Confirmar y volver a selección de días
    day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    await query.answer(f"✅ {day_names[day_num]} {time_str} agregado", show_alert=False)

    # Mostrar días nuevamente
    await _show_day_selection(query.message, context, edit=True)


async def _show_day_selection(message, context: ContextTypes.DEFAULT_TYPE, edit=False) -> None:
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
        [InlineKeyboardButton("✅ Finalizar y Guardar", callback_data="wc_finish")]
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

    if edit:
        await message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        await message.reply_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )


async def handle_weekly_finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja cuando el usuario finaliza la configuración.

    Crea los entrenamientos en la base de datos.
    """
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    chat_id = query.message.chat_id

    config = context.user_data.get('weekly_config', {})
    trainings = config.get('trainings', [])

    if not trainings:
        await query.answer("⚠️ No has agregado ningún entrenamiento", show_alert=True)
        return

    logger.info(f"✅ [WC] Usuario {user_id} finalizó configuración con {len(trainings)} entrenamientos")

    # Buscar estudiante por chat_id
    db = get_db()
    try:
        student = db.query(Student).filter(Student.chat_id == chat_id).first()

        if not student:
            await query.edit_message_text(
                "❌ No estás registrado como alumno.\n\n"
                "Por favor, contacta a tu entrenador para registrarte.",
                parse_mode="HTML"
            )
            return

        # Obtener scheduler desde bot_data para programar recordatorios
        scheduler_service = context.application.bot_data.get('scheduler_service')
        if not scheduler_service:
            logger.warning("⚠️ [WC] SchedulerService no disponible - recordatorios no se programarán")

        # Obtener configuraciones de entrenamiento por día (para session_type y location)
        from backend.src.models.training_day_config import TrainingDayConfig
        day_configs = {}
        for t in trainings:
            config = db.query(TrainingDayConfig).filter(
                TrainingDayConfig.weekday == t['day']
            ).first()
            if config:
                day_configs[t['day']] = {
                    'session_type': config.session_type,
                    'location': config.location
                }

        # Eliminar entrenamientos anteriores del estudiante (para esta semana)
        training_service = TrainingService(db, scheduler_service)
        existing = training_service.get_all_trainings(student.id)
        for training in existing:
            training_service.delete_training(training.id)

        logger.info(f"🗑️ [WC] Eliminados {len(existing)} entrenamientos anteriores de {student.name}")

        # Crear nuevos entrenamientos con recordatorios automáticos
        day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        created_list = []

        for t in trainings:
            # Obtener session_type y location de la configuración del día
            config = day_configs.get(t['day'], {})
            session_type = config.get('session_type', 'Entrenamiento')
            location = config.get('location', '')

            training = training_service.add_training(
                student_id=student.id,
                weekday=t['day'],
                weekday_name=day_names[t['day']],
                time_str=t['time'],
                session_type=session_type,
                location=location
            )
            created_list.append(f"• {day_names[t['day']]} a las {t['time']}")
            logger.info(f"✅ [WC] Creado entrenamiento: {day_names[t['day']]} {t['time']} ({session_type})")

        # Mensaje de confirmación
        summary = "\n".join(created_list)
        await query.edit_message_text(
            f"✅ <b>¡Semana Configurada!</b>\n\n"
            f"<b>Tus entrenamientos:</b>\n{summary}\n\n"
            f"Recibirás recordatorios automáticos 30 minutos antes de cada sesión.\n\n"
            f"¡Nos vemos en el gym! 💪",
            parse_mode="HTML"
        )

        # Limpiar contexto
        context.user_data.pop('weekly_config', None)

    except Exception as e:
        logger.error(f"❌ [WC] Error guardando entrenamientos: {str(e)}", exc_info=True)
        await query.edit_message_text(
            "❌ Ocurrió un error al guardar tus entrenamientos.\n\n"
            "Por favor, inténtalo de nuevo o contacta a tu entrenador."
        )
    finally:
        db.close()


async def handle_weekly_back_to_days(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el botón 'Volver' desde selección de hora."""
    query = update.callback_query
    await query.answer()

    await _show_day_selection(query.message, context, edit=True)
