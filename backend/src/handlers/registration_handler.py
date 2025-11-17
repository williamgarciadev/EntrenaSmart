# -*- coding: utf-8 -*-
"""
Handler Conversacional para Registro de Alumnos
================================================

Implementa un ConversationHandler para /registrarme que guía al entrenador
a través de un flujo de múltiples pasos para registrar un nuevo alumno.

Flujo:
    1. /registrarme → Pedir nombre del alumno
    2. Alumno escribe nombre → Mostrar confirmación con botones
    3. Entrenador confirma → Registrar en BD o cancelar

Estados:
    - NAME (1): Esperando nombre del alumno
    - CONFIRM (2): Esperando confirmación (SÍ/CANCELAR)
"""
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
from backend.src.core.exceptions import DuplicateRecordError, ValidationError
from backend.src.utils.conversation_state import RegistrationState, save_state_to_context_simple, load_state_from_context_simple, clear_state_simple
from backend.src.utils.menu_builder import build_yesno_menu
from backend.src.utils.logger import logger

# Estados del ConversationHandler
NAME, CONFIRM = range(1, 3)


async def registrarme_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Inicia el flujo de registro.

    Pide el nombre del alumno y crea el estado inicial.

    Returns:
        int: Siguiente estado (NAME)
    """
    user = update.effective_user

    # Crear estado inicial
    state = RegistrationState(user_id=user.id)
    save_state_to_context_simple(context, state)

    await update.message.reply_text(
        "👤 ¿Cuál es el nombre del alumno que deseas registrar?"
    )

    logger.info(f"Entrenador {user.id} inició flujo de registro")
    return NAME


async def registrarme_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Recibe el nombre del alumno y pide confirmación.

    Valida que el nombre no esté vacío y muestra un botón de confirmación.

    Returns:
        int: Siguiente estado (CONFIRM)
    """
    user = update.effective_user
    name = update.message.text.strip()

    # Validar nombre
    if not name or len(name) < 2:
        await update.message.reply_text(
            "❌ El nombre debe tener al menos 2 caracteres.\n\n"
            "¿Cuál es el nombre del alumno?"
        )
        return NAME

    # Guardar nombre en estado
    state: RegistrationState = load_state_from_context_simple(context, RegistrationState)
    state.set_student_name(name)
    save_state_to_context_simple(context, state)

    # Pedir confirmación
    keyboard = build_yesno_menu(
        affirmative_callback="reg_confirm_yes",
        negative_callback="reg_confirm_no"
    )

    await update.message.reply_text(
        f"¿Confirmas el registro de '{name}'?",
        reply_markup=keyboard
    )

    logger.info(f"Entrenador {user.id} ingresó nombre: {name}")
    return CONFIRM


async def registrarme_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Procesa la confirmación del registro.

    Si el usuario confirma (SÍ), registra el alumno en la BD.
    Si cancela, descarta el registro.

    Returns:
        int: ConversationHandler.END
    """
    query = update.callback_query
    user = query.from_user

    await query.answer()

    # Obtener estado
    state: RegistrationState = load_state_from_context_simple(context, RegistrationState)
    name = state.get_student_name()

    if query.data == "reg_confirm_yes":
        # Registrar alumno
        db = None
        try:
            logger.info(f"Iniciando registración de alumno: {name}")
            db = get_db()
            student_service = StudentService(db)

            # Registrar sin chat_id ni username (se asignarán cuando alumno inicie sesión)
            logger.info(f"Registrando alumno: name={name}")
            student = student_service.register_student(
                name=name,
                telegram_username=None,
                chat_id=None
            )

            logger.info(f"✅ Alumno creado exitosamente: ID={student.id}, name={name}")
            await query.edit_message_text(
                f"✅ Alumno *{name}* registrado correctamente."
            )

            logger.info(f"Alumno registrado: {name} (ID: {student.id})")

        except DuplicateRecordError as e:
            logger.error(f"DuplicateRecordError: {str(e)}")
            await query.edit_message_text(
                f"❌ Ya existe un alumno registrado con el nombre '{name}'."
            )
        except ValidationError as e:
            logger.error(f"ValidationError: {str(e)}")
            await query.edit_message_text(
                f"❌ Error de validación: {e.message}"
            )
        except Exception as e:
            logger.error(f"Error registrando alumno: {type(e).__name__}: {str(e)}", exc_info=True)
            await query.edit_message_text(
                "❌ Error al registrar alumno. Intenta nuevamente."
            )
        finally:
            if db:
                db.close()
    else:
        # Cancelado
        await query.edit_message_text(
            "❌ Registro cancelado."
        )
        logger.info(f"Entrenador {user.id} canceló registro de {name}")

    # Limpiar estado
    clear_state_simple(context, RegistrationState)

    return ConversationHandler.END


async def registrarme_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancela el flujo de registro en cualquier momento con mensaje contextual.

    Se ejecuta si el usuario escribe /cancelar durante el flujo.

    Returns:
        int: ConversationHandler.END
    """
    user = update.effective_user
    state: RegistrationState = load_state_from_context_simple(context, RegistrationState)

    # Mensaje contextual según el progreso
    if state and state.student_name:
        message = (
            f"❌ Registro cancelado.\n"
            f"No se registró al alumno '{state.student_name}'."
        )
    else:
        message = "❌ Registro cancelado."

    await update.message.reply_text(message)
    logger.info(f"Entrenador {user.id} canceló flujo de registro")

    # Limpiar estado
    clear_state_simple(context, RegistrationState)

    return ConversationHandler.END


def build_registration_conv_handler() -> ConversationHandler:
    """
    Construye y retorna el ConversationHandler para /registrarme.

    Returns:
        ConversationHandler: Handler listo para registrar en Application
    """
    return ConversationHandler(
        entry_points=[CommandHandler("registrarme", registrarme_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, registrarme_name)],
            CONFIRM: [CallbackQueryHandler(registrarme_confirm, pattern=r"^reg_confirm_")],
        },
        fallbacks=[CommandHandler("cancelar", registrarme_cancel)],
        name="registration_flow",
        persistent=False,
    )
