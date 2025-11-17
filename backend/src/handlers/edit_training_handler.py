# -*- coding: utf-8 -*-
"""
Handler Conversacional para Edición de Entrenamientos
====================================================

Implementa un ConversationHandler para /editar_sesion que guía al entrenador
a través de un flujo de múltiples pasos para editar entrenamientos existentes.

Flujo:
    1. /editar_sesion → Pedir nombre del alumno
    2. Alumno ingresa nombre → Buscar por fuzzy search
    3. Mostrar entrenamientos → Seleccionar entrenamiento
    4. Mostrar opciones → Elegir (Cambiar Hora, Cambiar Tipo, Eliminar)
    5. Según opción:
       - Cambiar Hora: Pedir hora (HH:MM)
       - Cambiar Tipo: Mostrar tipos disponibles
       - Eliminar: Confirmar eliminación
    6. Confirmar o cancelar

Estados:
    - SELECT_STUDENT (1): Esperando nombre del alumno
    - CONFIRM_STUDENT (2): Seleccionando de resultados
    - SELECT_TRAINING (3): Seleccionando entrenamiento
    - EDIT_OPTIONS (4): Seleccionando acción (Hora, Tipo, Eliminar)
    - ENTER_TIME (5): Ingresando hora
    - SELECT_SESSION_TYPE (6): Seleccionando tipo de sesión
    - CONFIRM_DELETE (7): Confirmando eliminación
"""
import re
from typing import List, Optional
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
from backend.src.utils.fuzzy_search import search_students
from backend.src.utils.conversation_state import EditTrainingState, save_state_to_context_simple, load_state_from_context_simple, clear_state_simple
from backend.src.utils.menu_builder import build_yesno_menu
from backend.src.utils.validation_helpers import validate_time_format, get_time_validation_tips
from backend.src.utils.logger import logger
from backend.src.core.constants import SESSION_TYPES

# Estados del ConversationHandler
SELECT_STUDENT, CONFIRM_STUDENT, SELECT_TRAINING, EDIT_OPTIONS, ENTER_TIME, SELECT_SESSION_TYPE, CONFIRM_DELETE = range(1, 8)


async def edit_training_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Inicia el flujo de edición de entrenamientos.

    Pide el nombre del alumno.

    Returns:
        int: Siguiente estado (SELECT_STUDENT)
    """
    user = update.effective_user

    await update.message.reply_text(
        "👤 ¿Cuál es el nombre del alumno cuyo entrenamiento deseas editar?"
    )

    logger.info(f"Entrenador {user.id} inició flujo de edición de entrenamientos")
    return SELECT_STUDENT


async def edit_student_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Recibe el nombre del alumno y busca coincidencias.

    Returns:
        int: Siguiente estado (CONFIRM_STUDENT) o SELECT_STUDENT si no hay resultados
    """
    user = update.effective_user
    query = update.message.text.strip()

    if not query or len(query) < 2:
        await update.message.reply_text(
            "❌ El nombre debe tener al menos 2 caracteres.\n\n"
            "¿Cuál es el nombre del alumno?"
        )
        return SELECT_STUDENT

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
            return SELECT_STUDENT

        # Guardar resultados en contexto
        context.user_data['search_results'] = found_students

        # Mostrar opciones
        lines = ["👥 Alumnos encontrados:\n"]
        for i, student in enumerate(found_students, 1):
            lines.append(f"{i}. {student.name}")

        lines.append("\nResponde con el número del alumno o escribe un nombre diferente.")

        await update.message.reply_text("\n".join(lines))

        logger.info(f"Búsqueda de alumno: '{query}' → {len(found_students)} resultados")
        return CONFIRM_STUDENT

    except Exception as e:
        logger.error(f"Error buscando alumno: {str(e)}")
        await update.message.reply_text(
            "❌ Error al buscar alumno. Intenta nuevamente."
        )
        return SELECT_STUDENT
    finally:
        if db:
            db.close()


async def edit_confirm_student(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Confirma la selección del alumno y obtiene sus entrenamientos.

    Returns:
        int: Siguiente estado (SELECT_TRAINING) o SELECT_STUDENT si hay error
    """
    user = update.effective_user
    response = update.message.text.strip()
    search_results = context.user_data.get('search_results', [])

    # Intentar obtener por número
    if response.isdigit():
        idx = int(response) - 1
        if 0 <= idx < len(search_results):
            student = search_results[idx]
        else:
            await update.message.reply_text(
                f"❌ Número inválido. Elige entre 1 y {len(search_results)}."
            )
            return CONFIRM_STUDENT
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
            return SELECT_STUDENT

    # Obtener entrenamientos
    db = None
    try:
        db = get_db()
        scheduler = context.application.bot_data.get('scheduler_service')
        training_service = TrainingService(db, scheduler)
        trainings = training_service.get_all_trainings(student.id)

        if not trainings:
            await update.message.reply_text(
                f"❌ {student.name} no tiene entrenamientos registrados."
            )
            return SELECT_STUDENT

        # Guardar alumno y entrenamientos en contexto
        context.user_data['student'] = student
        context.user_data['trainings'] = trainings

        # Mostrar entrenamientos con ubicación
        config_service = ConfigTrainingService(db)
        lines = [f"📅 Entrenamientos de {student.name}:\n"]
        for i, training in enumerate(trainings, 1):
            session_type = f" ({training.session_type})" if training.session_type else ""
            location = f" en {training.location}" if training.location else ""
            lines.append(f"{i}. {training.weekday_name} - {training.time_str}{session_type}{location}")

        lines.append("\nResponde con el número del entrenamiento a editar.")

        await update.message.reply_text("\n".join(lines))

        logger.info(f"Alumno seleccionado: {student.name} (ID: {student.id})")
        return SELECT_TRAINING
    except Exception as e:
        logger.error(f"Error confirmando alumno: {str(e)}")
        await update.message.reply_text(
            "❌ Error al procesar la selección. Intenta nuevamente."
        )
        return CONFIRM_STUDENT
    finally:
        if db:
            db.close()


async def edit_select_training(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Confirma la selección del entrenamiento.

    Returns:
        int: Siguiente estado (EDIT_OPTIONS) o SELECT_TRAINING si hay error
    """
    user = update.effective_user
    response = update.message.text.strip()
    trainings = context.user_data.get('trainings', [])

    if not response.isdigit():
        await update.message.reply_text(
            f"❌ Responde con un número entre 1 y {len(trainings)}."
        )
        return SELECT_TRAINING

    idx = int(response) - 1
    if not (0 <= idx < len(trainings)):
        await update.message.reply_text(
            f"❌ Número inválido. Elige entre 1 y {len(trainings)}."
        )
        return SELECT_TRAINING

    training = trainings[idx]

    # Crear estado de edición
    state = EditTrainingState(
        user_id=user.id,
        training_id=training.id,
        student_id=training.student_id
    )
    save_state_to_context_simple(context, state)

    # Mostrar opciones
    lines = [
        f"Editando: {training.weekday_name} - {training.time_str}",
        "",
        "¿Qué deseas cambiar?",
        "[1] Cambiar Hora",
        "[2] Cambiar Tipo de Sesión",
        "[3] Eliminar Entrenamiento",
        "[0] Cancelar"
    ]

    await update.message.reply_text("\n".join(lines))

    logger.info(f"Entrenamiento seleccionado: {training.id}")
    return EDIT_OPTIONS


async def edit_select_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Procesa la opción seleccionada.

    Returns:
        int: Siguiente estado según la opción (ENTER_TIME, SELECT_SESSION_TYPE, CONFIRM_DELETE, o END)
    """
    user = update.effective_user
    response = update.message.text.strip()

    if response == "1":
        # Cambiar hora
        await update.message.reply_text(
            "⏰ ¿Nueva hora? (Formato: HH:MM)\n\nEjemplo: 05:00 o 17:30"
        )
        logger.info(f"Opción seleccionada: Cambiar Hora")
        return ENTER_TIME

    elif response == "2":
        # Cambiar tipo
        lines = ["🏋️ Tipos de sesión disponibles:\n"]
        for i, tipo in enumerate(SESSION_TYPES, 1):
            lines.append(f"[{i}] {tipo}")
        lines.append("\nResponde con el número del tipo.")

        await update.message.reply_text("\n".join(lines))
        logger.info(f"Opción seleccionada: Cambiar Tipo")
        return SELECT_SESSION_TYPE

    elif response == "3":
        # Eliminar
        keyboard = build_yesno_menu(
            affirmative_callback="edit_delete_yes",
            negative_callback="edit_delete_no"
        )

        await update.message.reply_text(
            "❌ ¿Estás seguro de que deseas eliminar este entrenamiento?",
            reply_markup=keyboard
        )
        logger.info(f"Opción seleccionada: Eliminar")
        return CONFIRM_DELETE

    elif response == "0":
        # Cancelar
        await update.message.reply_text("❌ Edición cancelada.")
        clear_state_simple(context, EditTrainingState)
        return ConversationHandler.END

    else:
        await update.message.reply_text(
            "❌ Opción inválida. Elige [1], [2], [3] o [0]."
        )
        return EDIT_OPTIONS


async def edit_enter_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Recibe la nueva hora y actualiza el entrenamiento con validación mejorada.

    Returns:
        int: ConversationHandler.END
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
        return ENTER_TIME

    db = None
    try:
        state: EditTrainingState = load_state_from_context_simple(context, EditTrainingState)

        db = get_db()
        scheduler = context.application.bot_data.get('scheduler_service')
        training_service = TrainingService(db, scheduler)
        training = training_service.update_training(
            training_id=state.training_id,
            time_str=time_str
        )

        await update.message.reply_text(
            f"✅ Hora actualizada: {training.weekday_name} - {time_str}"
        )

        logger.info(f"Entrenamiento {state.training_id} actualizado a {time_str}")

    except Exception as e:
        logger.error(f"Error actualizando hora: {str(e)}")
        await update.message.reply_text(
            "❌ Error al actualizar la hora. Intenta nuevamente."
        )
    finally:
        if db:
            db.close()

    clear_state_simple(context, EditTrainingState)
    return ConversationHandler.END


async def edit_select_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Recibe el tipo de sesión seleccionado y actualiza.

    Returns:
        int: ConversationHandler.END
    """
    user = update.effective_user
    response = update.message.text.strip()

    if not response.isdigit():
        await update.message.reply_text(
            f"❌ Responde con un número entre 1 y {len(SESSION_TYPES)}."
        )
        return SELECT_SESSION_TYPE

    idx = int(response) - 1
    if not (0 <= idx < len(SESSION_TYPES)):
        await update.message.reply_text(
            f"❌ Número inválido. Elige entre 1 y {len(SESSION_TYPES)}."
        )
        return SELECT_SESSION_TYPE

    session_type = SESSION_TYPES[idx]

    db = None
    try:
        state: EditTrainingState = load_state_from_context_simple(context, EditTrainingState)

        db = get_db()
        scheduler = context.application.bot_data.get('scheduler_service')
        training_service = TrainingService(db, scheduler)
        training = training_service.set_session_type(
            training_id=state.training_id,
            session_type=session_type
        )

        await update.message.reply_text(
            f"✅ Tipo de sesión actualizado: {training.weekday_name} - {session_type}"
        )

        logger.info(f"Entrenamiento {state.training_id} tipo actualizado a {session_type}")

    except Exception as e:
        logger.error(f"Error actualizando tipo: {str(e)}")
        await update.message.reply_text(
            "❌ Error al actualizar el tipo. Intenta nuevamente."
        )
    finally:
        if db:
            db.close()

    clear_state_simple(context, EditTrainingState)
    return ConversationHandler.END


async def edit_confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Procesa la confirmación de eliminación.

    Returns:
        int: ConversationHandler.END
    """
    query = update.callback_query
    await query.answer()

    if query.data == "edit_delete_yes":
        db = None
        try:
            state: EditTrainingState = load_state_from_context_simple(context, EditTrainingState)

            db = get_db()
            scheduler = context.application.bot_data.get('scheduler_service')
            training_service = TrainingService(db, scheduler)
            training_service.delete_training(training_id=state.training_id)

            await query.edit_message_text(
                "✅ Entrenamiento eliminado."
            )

            logger.info(f"Entrenamiento {state.training_id} eliminado")

        except Exception as e:
            logger.error(f"Error eliminando entrenamiento: {str(e)}")
            await query.edit_message_text(
                "❌ Error al eliminar. Intenta nuevamente."
            )
        finally:
            if db:
                db.close()
    else:
        await query.edit_message_text(
            "❌ Eliminación cancelada."
        )
        logger.info(f"Eliminación de entrenamiento cancelada")

    clear_state_simple(context, EditTrainingState)
    return ConversationHandler.END


async def edit_training_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancela el flujo en cualquier momento con mensaje contextual.

    Returns:
        int: ConversationHandler.END
    """
    user = update.effective_user
    state: EditTrainingState = load_state_from_context_simple(context, EditTrainingState)

    # Mensaje contextual según el progreso
    if state and state.edit_field:
        message = (
            f"❌ Edición cancelada.\n"
            f"No se realizaron cambios en el entrenamiento."
        )
    else:
        message = "❌ Edición cancelada."

    await update.message.reply_text(message)
    logger.info(f"Entrenador {user.id} canceló edición de entrenamientos")

    clear_state_simple(context, EditTrainingState)
    return ConversationHandler.END


def build_edit_training_conv_handler() -> ConversationHandler:
    """
    Construye y retorna el ConversationHandler para /editar_sesion.

    Returns:
        ConversationHandler: Handler listo para registrar en Application
    """
    return ConversationHandler(
        entry_points=[CommandHandler("editar_sesion", edit_training_start)],
        states={
            SELECT_STUDENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_student_name)],
            CONFIRM_STUDENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_confirm_student)],
            SELECT_TRAINING: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_select_training)],
            EDIT_OPTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_select_option)],
            ENTER_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_enter_time)],
            SELECT_SESSION_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_select_type)],
            CONFIRM_DELETE: [CallbackQueryHandler(edit_confirm_delete, pattern=r"^edit_delete_")],
        },
        fallbacks=[CommandHandler("cancelar", edit_training_cancel)],
        name="edit_training_flow",
        persistent=False,
    )
