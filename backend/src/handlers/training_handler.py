# -*- coding: utf-8 -*-
"""
Handler Conversacional para Configuración de Entrenamientos
===========================================================

Implementa un ConversationHandler para /set que guía al entrenador
a través de un flujo de múltiples pasos para configurar entrenamientos.

Flujo:
    1. /set → Pedir nombre del alumno
    2. Alumno ingresa nombre → Buscar por fuzzy search
    3. Mostrar resultados → Seleccionar alumno
    4. Mostrar días disponibles → Seleccionar día
    5. Ingresar hora (HH:MM) → Guardar entrenamiento parcial
    6. ¿Otro día? SÍ/NO
    7. Si SÍ → Volver a paso 4 (sin día ya seleccionado)
    8. Si NO → Resumen y confirmar registro en BD

Estados:
    - SELECTING_STUDENT (1): Esperando nombre del alumno
    - CONFIRMING_STUDENT (2): Seleccionando de resultados
    - SELECTING_DAY (3): Seleccionando día de la semana
    - ENTERING_TIME (4): Ingresando hora (HH:MM)
    - ANOTHER_DAY (5): ¿Desea agregar otro día?
    - FINAL_CONFIRMATION (6): Resumen y confirmación final
"""
import re
from typing import List, Dict, Any
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from backend.src.models.base import get_db
from backend.src.services.student_service import StudentService
from backend.src.services.training_service import TrainingService
from backend.src.services.config_training_service import ConfigTrainingService
from backend.src.core.exceptions import ValidationError, RecordNotFoundError
from backend.src.utils.fuzzy_search import search_students
from backend.src.utils.conversation_state import TrainingState, save_state_to_context_simple, load_state_from_context_simple, clear_state_simple
from backend.src.utils.menu_builder import build_day_menu, build_yesno_menu
from backend.src.utils.validation_helpers import validate_time_format, validate_student_name, get_time_validation_tips
from backend.src.utils.logger import logger
from backend.src.core.constants import WEEKDAY_NAMES, WEEKDAY_NAME_TO_NUMBER

# Estados del ConversationHandler
SELECTING_STUDENT, CONFIRMING_STUDENT, SELECTING_DAY, ENTERING_TIME, ANOTHER_DAY, FINAL_CONFIRMATION = range(1, 7)


async def set_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Inicia el flujo de configuración de entrenamientos.

    Pide el nombre del alumno y crea el estado inicial.

    Returns:
        int: Siguiente estado (SELECTING_STUDENT)
    """
    user = update.effective_user

    # Crear estado inicial
    state = TrainingState(user_id=user.id)
    save_state_to_context_simple(context, state)

    # Almacenar lista de días seleccionados (para múltiples entrenamientos)
    context.user_data['selected_trainings'] = []

    await update.message.reply_text(
        "👤 ¿Cuál es el nombre del alumno?"
    )

    logger.info(f"Entrenador {user.id} inició flujo de configuración de entrenamientos")
    return SELECTING_STUDENT


async def set_student_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Recibe el nombre del alumno y busca coincidencias.

    Usa fuzzy_search para tolerar errores de tipeo.

    Returns:
        int: Siguiente estado (CONFIRMING_STUDENT) o SELECTING_STUDENT si no hay resultados
    """
    user = update.effective_user
    query = update.message.text.strip()

    if not query or len(query) < 2:
        await update.message.reply_text(
            "❌ El nombre debe tener al menos 2 caracteres.\n\n"
            "¿Cuál es el nombre del alumno?"
        )
        return SELECTING_STUDENT

    db = None
    try:
        db = get_db()
        student_service = StudentService(db)
        students = student_service.list_all_students(active_only=True)

        # Buscar por fuzzy search
        found_students = search_students(query, students, cutoff=0.6, max_results=5)

        if not found_students:
            await update.message.reply_text(
                f"❌ No se encontraron alumnos con '{query}'.\n\n"
                "¿Cuál es el nombre del alumno?"
            )
            return SELECTING_STUDENT

        # Guardar resultados en contexto
        context.user_data['search_results'] = found_students

        # Mostrar opciones
        lines = ["👥 Alumnos encontrados:\n"]
        for i, student in enumerate(found_students, 1):
            lines.append(f"{i}. {student.name}")

        lines.append("\nResponde con el número del alumno o escribe un nombre diferente.")

        await update.message.reply_text("\n".join(lines))

        logger.info(f"Búsqueda de alumno: '{query}' → {len(found_students)} resultados")
        return CONFIRMING_STUDENT

    except Exception as e:
        logger.error(f"Error buscando alumno: {str(e)}")
        await update.message.reply_text(
            "❌ Error al buscar alumno. Intenta nuevamente."
        )
        return SELECTING_STUDENT
    finally:
        if db:
            db.close()


async def set_confirm_student(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Confirma la selección del alumno.

    El usuario responde con el número del alumno o escribe un nombre diferente.

    Returns:
        int: Siguiente estado (SELECTING_DAY) o SELECTING_STUDENT si hay error
    """
    user = update.effective_user
    response = update.message.text.strip()
    search_results = context.user_data.get('search_results', [])

    try:
        # Intentar obtener por número
        if response.isdigit():
            idx = int(response) - 1
            if 0 <= idx < len(search_results):
                student = search_results[idx]
            else:
                await update.message.reply_text(
                    f"❌ Número inválido. Elige entre 1 y {len(search_results)}."
                )
                return CONFIRMING_STUDENT
        else:
            # Buscar por nombre exacto
            student = None
            for s in search_results:
                if s.name.lower() == response.lower():
                    student = s
                    break

            if not student:
                await update.message.reply_text(
                    "❌ Alumno no encontrado en los resultados.\n\n"
                    "¿Cuál es el nombre del alumno?"
                )
                return SELECTING_STUDENT

        # Guardar alumno en estado
        state: TrainingState = load_state_from_context_simple(context, TrainingState)
        state.set_student(student.id, student.name)
        save_state_to_context_simple(context, state)

        await update.message.reply_text(
            f"✅ Alumno seleccionado: {student.name}"
        )

        # Pasar a seleccionar día
        keyboard = build_day_menu()
        await update.message.reply_text(
            f"📅 ¿Qué día va a asistir {student.name}?",
            reply_markup=keyboard
        )

        logger.info(f"Alumno seleccionado: {student.name} (ID: {student.id})")
        return SELECTING_DAY

    except Exception as e:
        logger.error(f"Error confirmando alumno: {str(e)}")
        await update.message.reply_text(
            "❌ Error al procesar la selección. Intenta nuevamente."
        )
        return CONFIRMING_STUDENT


async def set_select_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Recibe la selección del día y pide la hora.

    Returns:
        int: Siguiente estado (ENTERING_TIME)
    """
    query = update.callback_query
    await query.answer()

    # Extraer día del callback_data: "day_<number>" (0=Lunes, 6=Domingo)
    day_number = int(query.data.split("_")[1])
    day_name = WEEKDAY_NAMES[day_number]

    # Guardar día en estado
    state: TrainingState = load_state_from_context_simple(context, TrainingState)
    state.set_day(day_number, day_name)
    save_state_to_context_simple(context, state)

    await query.edit_message_text(
        f"⏰ ¿A qué hora el {day_name}? (Formato: HH:MM)\n\nEjemplo: 05:00 o 17:30"
    )

    logger.info(f"Día seleccionado: {day_name}")
    return ENTERING_TIME


async def set_enter_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Recibe la hora y valida el formato con feedback visual.

    Returns:
        int: Siguiente estado (ANOTHER_DAY) o ENTERING_TIME si hay error
    """
    user = update.effective_user
    time_str = update.message.text.strip()

    # Validar formato HH:MM con feedback mejorado
    is_valid, feedback_msg = validate_time_format(time_str)

    if not is_valid:
        # Mostrar feedback de error + tips
        tips = get_time_validation_tips()
        await update.message.reply_text(
            f"{feedback_msg}\n\n{tips}"
        )
        return ENTERING_TIME

    # Guardar hora en estado
    state: TrainingState = load_state_from_context_simple(context, TrainingState)
    state.set_time(time_str)
    save_state_to_context_simple(context, state)

    # Guardar entrenamiento en lista temporal
    training_data = {
        'student_id': state.student_id,
        'day_number': state.day_of_week,
        'day_name': state.day_name,
        'time': time_str
    }
    context.user_data['selected_trainings'].append(training_data)

    # Preguntar si desea agregar otro día
    keyboard = build_yesno_menu(
        affirmative_callback="train_another_yes",
        negative_callback="train_another_no"
    )

    await update.message.reply_text(
        f"✅ Entrenamiento agregado: {state.day_name} - {time_str}\n\n"
        f"¿Deseas agregar otro día para {state.student_name}?",
        reply_markup=keyboard
    )

    logger.info(f"Hora ingresada: {time_str}")
    return ANOTHER_DAY


async def set_another_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Procesa la decisión de agregar otro día.

    Si el usuario elige SÍ, vuelve a mostrar el menú de días (sin el ya seleccionado).
    Si elige NO, va a confirmación final.

    Returns:
        int: Siguiente estado (SELECTING_DAY) o FINAL_CONFIRMATION
    """
    query = update.callback_query
    await query.answer()

    if query.data == "train_another_yes":
        # Mostrar días disponibles (sin el ya seleccionado)
        state: TrainingState = load_state_from_context_simple(context, TrainingState)
        already_selected = [t['day_number'] for t in context.user_data.get('selected_trainings', [])]

        # Construir menú excluyendo días ya seleccionados
        keyboard = build_day_menu(exclude_days=already_selected)

        await query.edit_message_text(
            f"📅 ¿Qué otro día va a asistir {state.student_name}?",
            reply_markup=keyboard
        )

        logger.info(f"Usuario elige agregar otro día (excluyendo: {already_selected})")
        return SELECTING_DAY
    else:
        # Ir a confirmación final
        return await show_final_confirmation(update, context)


async def show_final_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Muestra el resumen de todos los entrenamientos y pide confirmación.

    Returns:
        int: Siguiente estado (FINAL_CONFIRMATION)
    """
    query = update.callback_query
    await query.answer()

    state: TrainingState = load_state_from_context_simple(context, TrainingState)
    trainings = context.user_data.get('selected_trainings', [])

    # Construir resumen con ubicaciones
    lines = [f"📋 Resumen para {state.student_name}:\n"]
    db = None
    try:
        db = get_db()
        config_service = ConfigTrainingService(db)
        for i, training in enumerate(trainings, 1):
            day_config = config_service.get_day_config(training['day_number'])
            location = day_config.location if day_config else "Sin ubicación"
            session_type = day_config.session_type if day_config else ""
            lines.append(f"{i}. {training['day_name']} - {training['time']} en {location} ({session_type})")
    except Exception:
        # Si hay error obteniendo config, mostrar sin ubicación
        for i, training in enumerate(trainings, 1):
            lines.append(f"{i}. {training['day_name']} - {training['time']}")
    finally:
        if db:
            db.close()

    lines.append("\n¿Confirmas estos entrenamientos?")

    keyboard = build_yesno_menu(
        affirmative_callback="train_confirm_yes",
        negative_callback="train_confirm_no"
    )

    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=keyboard
    )

    logger.info(f"Mostrado resumen con {len(trainings)} entrenamientos")
    return FINAL_CONFIRMATION


async def set_final_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Registra los entrenamientos o cancela.

    Returns:
        int: ConversationHandler.END
    """
    query = update.callback_query
    await query.answer()

    state: TrainingState = load_state_from_context_simple(context, TrainingState)
    trainings = context.user_data.get('selected_trainings', [])

    if query.data == "train_confirm_yes":
        db = None
        try:
            db = get_db()

            # Obtener scheduler si está disponible
            scheduler = context.application.bot_data.get('scheduler_service')
            training_service = TrainingService(db, scheduler)
            config_service = ConfigTrainingService(db)

            # Registrar cada entrenamiento
            for training in trainings:
                # Obtener configuración del día para obtener ubicación y tipo
                day_config = config_service.get_day_config(training['day_number'])

                training_service.add_training(
                    student_id=training['student_id'],
                    weekday=training['day_number'],
                    weekday_name=training['day_name'],
                    time_str=training['time'],
                    session_type=day_config.session_type if day_config else "",
                    location=day_config.location if day_config else None,
                    training_day_config_id=day_config.id if day_config else None
                )

            await query.edit_message_text(
                f"✅ Entrenamientos registrados para {state.student_name}:\n\n"
                + "\n".join([f"• {t['day_name']} - {t['time']}" for t in trainings])
            )

            logger.info(f"Entrenamientos registrados: {state.student_name} - {len(trainings)} sesiones")

        except Exception as e:
            logger.error(f"Error registrando entrenamientos: {str(e)}")
            await query.edit_message_text(
                "❌ Error al registrar entrenamientos. Intenta nuevamente."
            )
        finally:
            if db:
                db.close()
    else:
        await query.edit_message_text(
            "❌ Configuración cancelada."
        )
        logger.info(f"Configuración cancelada por entrenador")

    # Limpiar estado
    clear_state_simple(context, TrainingState)
    context.user_data.pop('selected_trainings', None)
    context.user_data.pop('search_results', None)

    return ConversationHandler.END


async def set_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancela el flujo en cualquier momento con mensaje contextual.

    Returns:
        int: ConversationHandler.END
    """
    user = update.effective_user
    state: TrainingState = load_state_from_context_simple(context, TrainingState)
    trainings = context.user_data.get('selected_trainings', [])

    # Mensaje contextual según lo que se haya hecho
    if trainings:
        message = (
            f"❌ Configuración cancelada.\n\n"
            f"Se descartaron {len(trainings)} entrenamiento(s) sin registrar."
        )
    elif state and state.student_name:
        message = (
            f"❌ Configuración de entrenamientos cancelada.\n"
            f"No se registraron entrenamientos para {state.student_name}."
        )
    else:
        message = "❌ Configuración cancelada."

    await update.message.reply_text(message)
    logger.info(f"Entrenador {user.id} canceló configuración de entrenamientos (trainings pendientes: {len(trainings)})")

    # Limpiar estado
    clear_state_simple(context, TrainingState)
    context.user_data.pop('selected_trainings', None)
    context.user_data.pop('search_results', None)

    return ConversationHandler.END


def build_training_conv_handler() -> ConversationHandler:
    """
    Construye y retorna el ConversationHandler para /set.

    Returns:
        ConversationHandler: Handler listo para registrar en Application
    """
    return ConversationHandler(
        entry_points=[CommandHandler("set", set_start)],
        states={
            SELECTING_STUDENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_student_name)],
            CONFIRMING_STUDENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_confirm_student)],
            SELECTING_DAY: [CallbackQueryHandler(set_select_day, pattern=r"^day_")],
            ENTERING_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_enter_time)],
            ANOTHER_DAY: [CallbackQueryHandler(set_another_day, pattern=r"^train_another_")],
            FINAL_CONFIRMATION: [CallbackQueryHandler(set_final_confirm, pattern=r"^train_confirm_")],
        },
        fallbacks=[CommandHandler("cancelar", set_cancel)],
        name="training_flow",
        persistent=False,
    )
