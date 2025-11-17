# -*- coding: utf-8 -*-
"""
Handler para Configuración de Entrenamientos Semanales
=====================================================

Maneja el flujo conversacional para que el entrenador configure
la programación semanal de entrenamientos.

Comando: /config_semana

ARQUITECTURA:
- Usa ConfigTrainingState para type-safe state management
- Usa get_db_context() para transacciones automáticas
- Usa LocationValidator para validación estricta
- Usa excepciones específicas para manejo de errores
"""
from typing import List
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)

from backend.src.models.base import get_db_context
from backend.src.services.config_training_service import ConfigTrainingService
from backend.src.handlers.training_state_manager import TrainingStateManager
from backend.src.utils.validators import LocationValidator
from backend.src.core.exceptions import (
    LocationValidationError,
    StateNotFoundError,
    ValidationError,
    DatabaseError,
    ConfigTrainingError
)
from backend.src.utils.logger import logger

# Estados del ConversationHandler
SELECT_DAY = 1
SELECT_SESSION_TYPE = 2
SELECT_LOCATION = 3
CONFIRM_DATA = 4        # Confirmar si los datos son correctos
CONFIRM_CONTINUE = 5    # Preguntar si configura otro día

# Datos de la conversación
DAYS_SPANISH = {
    "Lunes": 0,
    "Martes": 1,
    "Miércoles": 2,
    "Jueves": 3,
    "Viernes": 4,
    "Sábado": 5,
    "Domingo": 6
}

SESSION_TYPES = ["Pierna", "Funcional", "Brazo", "Espalda", "Pecho", "Hombros"]


# ============================================================================
# Funciones del Flujo Conversacional
# ============================================================================

async def config_training_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Inicia el flujo de configuración semanal.

    Muestra los días disponibles para configurar.
    """
    logger.info(f"[CONFIG_START] Usuario iniciando configuración")

    await update.message.reply_text(
        "🏋️ *Configurador de Entrenamientos Semanales*\n\n"
        "Vamos a programar los entrenamientos para la semana.\n\n"
        "¿Qué día quieres configurar?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["Lunes", "Martes", "Miércoles"],
                ["Jueves", "Viernes", "Sábado"],
                ["Domingo", "Salir"]
            ],
            one_time_keyboard=True,
            input_field_placeholder="Selecciona un día..."
        )
    )
    return SELECT_DAY


async def config_training_select_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Procesa la selección del día.

    Valida que el día exista y guarda en estado.
    """
    day_text = update.message.text.strip()
    logger.debug(f"[SELECT_DAY] Usuario seleccionó: {day_text}")

    # Verificar salida
    if day_text == "Salir":
        return await _finalize_config(update, context)

    # Validar día
    if day_text not in DAYS_SPANISH:
        await update.message.reply_text(
            "❌ Día no válido. Por favor, selecciona un día de la lista."
        )
        return SELECT_DAY

    # Guardar día seleccionado en estado
    weekday_num = DAYS_SPANISH[day_text]
    TrainingStateManager.save_config_state(
        context,
        weekday=weekday_num,
        weekday_name=day_text,
        session_type="",  # Temporal, se completa después
        location=""       # Temporal, se completa después
    )

    # Solicitar tipo de entrenamiento
    await update.message.reply_text(
        f"📌 Día seleccionado: *{day_text}*\n\n"
        f"¿Qué tipo de entrenamiento será?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [SESSION_TYPES],
            one_time_keyboard=True,
            input_field_placeholder="Selecciona el tipo..."
        )
    )
    return SELECT_SESSION_TYPE


async def config_training_select_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Procesa la selección del tipo de entrenamiento.

    Valida y normaliza la capitalización.
    """
    session_type = update.message.text.strip()
    logger.debug(f"[SELECT_TYPE] Usuario ingresó: {session_type}")

    # Validar tipo
    if session_type not in SESSION_TYPES and session_type.lower() not in [s.lower() for s in SESSION_TYPES]:
        await update.message.reply_text(
            "❌ Tipo de entrenamiento no válido. "
            f"Selecciona uno de: {', '.join(SESSION_TYPES)}"
        )
        return SELECT_SESSION_TYPE

    # Normalizar capitalización
    for st in SESSION_TYPES:
        if st.lower() == session_type.lower():
            session_type = st
            break

    # Actualizar estado con tipo de entrenamiento
    try:
        state = TrainingStateManager.get_config_state(context)
        TrainingStateManager.save_config_state(
            context,
            weekday=state.weekday,
            weekday_name=state.weekday_name,
            session_type=session_type,
            location=""  # Temporal
        )
    except StateNotFoundError:
        logger.error("[SELECT_TYPE] Estado perdido")
        await update.message.reply_text(
            "❌ La sesión se interrumpió. Por favor, vuelve a comenzar con /config_semana"
        )
        return ConversationHandler.END

    # Solicitar ubicación
    await update.message.reply_text(
        f"📍 Tipo seleccionado: *{session_type}*\n\n"
        f"¿En qué piso o zona se realizará? (Ej: '2do Piso', '3er Piso - Zona Pierna')",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return SELECT_LOCATION


async def config_training_select_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Procesa la ubicación y solicita confirmación.

    Valida ubicación con LocationValidator.
    """
    location_input = update.message.text.strip()
    logger.debug(f"[SELECT_LOCATION] Usuario ingresó: {location_input}")

    # Validar ubicación
    try:
        location = LocationValidator.validate(location_input)
    except LocationValidationError as e:
        await update.message.reply_text(e.message)
        return SELECT_LOCATION

    # Actualizar estado con ubicación
    try:
        state = TrainingStateManager.get_config_state(context)
        TrainingStateManager.save_config_state(
            context,
            weekday=state.weekday,
            weekday_name=state.weekday_name,
            session_type=state.session_type,
            location=location
        )
    except StateNotFoundError:
        logger.error("[SELECT_LOCATION] Estado perdido")
        await update.message.reply_text(
            "❌ La sesión se interrumpió. Por favor, vuelve a comenzar con /config_semana"
        )
        return ConversationHandler.END

    # Mostrar resumen para confirmación
    summary = (
        f"📋 *Resumen de Configuración*\n\n"
        f"🗓️ Día: {state.weekday_name}\n"
        f"💪 Tipo: {state.session_type}\n"
        f"📍 Ubicación: {location}\n\n"
        f"¿Es correcto?"
    )

    await update.message.reply_text(
        summary,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["Sí", "No"]],
            one_time_keyboard=True
        )
    )
    return CONFIRM_DATA


async def config_training_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Confirma y guarda la configuración en BD.

    Usa get_db_context() para transacciones automáticas.
    Usa excepciones específicas para manejo granular de errores.
    """
    response = update.message.text.strip()
    logger.debug(f"[CONFIRM] Usuario respondió: {response}")

    if response == "Sí":
        # Obtener estado
        try:
            state = TrainingStateManager.get_config_state(context)
        except StateNotFoundError:
            logger.error("[CONFIRM] Estado perdido")
            await update.message.reply_text(
                "❌ La sesión se interrumpió. Por favor, vuelve a comenzar con /config_semana"
            )
            return ConversationHandler.END

        # Guardar en BD con context manager (transacción automática)
        try:
            with get_db_context() as db:
                service = ConfigTrainingService(db)
                service.configure_day(
                    weekday=state.weekday,
                    session_type=state.session_type,
                    location=state.location
                )
                # Auto-commit al salir del context manager

            logger.info(
                f"[CONFIRM] Guardado: {state.weekday_name} - {state.session_type} ({state.location})"
            )

            # Limpiar estado después de guardar
            TrainingStateManager.clear_config_state(context)

            # Preguntar si configura otro día
            await update.message.reply_text(
                f"✅ ¡{state.weekday_name} configurado como {state.session_type} en {state.location}!\n\n"
                f"¿Quieres configurar otro día?",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup(
                    [["Sí", "No"]],
                    one_time_keyboard=True
                )
            )

            return CONFIRM_CONTINUE

        except ValidationError as e:
            # Error de validación (datos inválidos)
            logger.warning(f"[CONFIRM] Validación fallida: {e.message}")
            await update.message.reply_text(
                f"❌ Error de validación: {e.message}\n"
                f"Por favor, comienza de nuevo."
            )
            TrainingStateManager.clear_config_state(context)
            return ConversationHandler.END

        except DatabaseError as e:
            # Error de base de datos
            logger.error(f"[CONFIRM] Error de BD: {e.message}", exc_info=True)
            await update.message.reply_text(
                "❌ Error de base de datos. Por favor, intenta más tarde."
            )
            return ConversationHandler.END

        except ConfigTrainingError as e:
            # Error específico de configuración
            logger.error(f"[CONFIRM] Error de configuración: {e.message}", exc_info=True)
            await update.message.reply_text(f"❌ {e.user_message}")
            return ConversationHandler.END

        except Exception as e:
            # Error inesperado
            logger.critical(f"[CONFIRM] Error inesperado: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Error inesperado. Por favor, intenta de nuevo."
            )
            return ConversationHandler.END

    elif response == "No":
        # Volver a editar desde el inicio
        logger.debug("[CONFIRM] Usuario rechazó, volviendo a SELECT_DAY")

        await update.message.reply_text(
            "📝 No hay problema. Volvamos a empezar.\n\n"
            "¿Qué día quieres configurar?",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["Lunes", "Martes", "Miércoles"],
                    ["Jueves", "Viernes", "Sábado"],
                    ["Domingo", "Salir"]
                ],
                one_time_keyboard=True,
                input_field_placeholder="Selecciona un día..."
            )
        )
        return SELECT_DAY

    else:
        await update.message.reply_text(
            "Por favor, responde 'Sí' o 'No'."
        )
        return CONFIRM_CONTINUE


async def config_training_continue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Maneja la continuación: ¿Otro día? Sí/No.

    Si responde No, finaliza y muestra resumen semanal.
    """
    response = update.message.text.strip()
    logger.debug(f"[CONTINUE] Usuario respondió: {response}")

    if response == "Sí":
        # Reiniciar desde selección de día
        await update.message.reply_text(
            "¿Qué otro día quieres configurar?",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["Lunes", "Martes", "Miércoles"],
                    ["Jueves", "Viernes", "Sábado"],
                    ["Domingo", "Salir"]
                ],
                one_time_keyboard=True,
                input_field_placeholder="Selecciona un día..."
            )
        )
        return SELECT_DAY

    elif response == "No":
        # Finalizar y mostrar resumen
        return await _finalize_config(update, context)

    else:
        await update.message.reply_text(
            "Por favor, responde 'Sí' o 'No'."
        )
        return CONFIRM_CONTINUE


async def config_training_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela el flujo."""
    logger.info("[CANCEL] Usuario canceló configuración")
    TrainingStateManager.clear_config_state(context)

    await update.message.reply_text(
        "❌ Configuración cancelada.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# ============================================================================
# Funciones Helper
# ============================================================================

async def _finalize_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Finaliza la configuración y muestra el resumen semanal.

    Helper privada para reutilizar en config_training_select_day y
    config_training_continue.
    """
    logger.info("[FINALIZE] Finalizando configuración")

    try:
        with get_db_context() as db:
            service = ConfigTrainingService(db)
            summary = service.format_weekly_summary()

        await update.message.reply_text(
            f"✅ *Configuración Completada*\n\n"
            f"Programación de la semana:\n\n{summary}",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    except DatabaseError as e:
        logger.error(f"[FINALIZE] Error de BD: {e.message}", exc_info=True)
        await update.message.reply_text(
            "❌ Error al obtener el resumen. Por favor, intenta más tarde.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    except Exception as e:
        logger.critical(f"[FINALIZE] Error inesperado: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Error inesperado. Configuración completada pero sin resumen.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END


# ============================================================================
# ConversationHandler Configuration
# ============================================================================

config_training_handler = ConversationHandler(
    entry_points=[CommandHandler("config_semana", config_training_start)],
    states={
        SELECT_DAY: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                config_training_select_day
            )
        ],
        SELECT_SESSION_TYPE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                config_training_select_type
            )
        ],
        SELECT_LOCATION: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                config_training_select_location
            )
        ],
        CONFIRM_DATA: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                config_training_confirm  # ← Confirmar si los datos son correctos
            )
        ],
        CONFIRM_CONTINUE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                config_training_continue  # ← Preguntar si configura otro día
            )
        ]
    },
    fallbacks=[CommandHandler("cancelar", config_training_cancel)],
    per_user=True
)
