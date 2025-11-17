"""
Handlers de Comandos de Alumnos
================================

Implementa los handlers de Telegram para los comandos
de los alumnos.
"""
from telegram import Update
from telegram.ext import ContextTypes

from backend.src.models.base import get_db
from backend.src.services.student_service import StudentService
from backend.src.services.training_service import TrainingService
from backend.src.utils.messages import Messages
from backend.src.utils.logger import logger


async def mis_sesiones_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para el comando /mis_sesiones.

    Muestra el horario de entrenamientos del alumno.
    """
    user = update.effective_user

    db = None
    try:
        db = get_db()
        student_service = StudentService(db)
        scheduler = context.application.bot_data.get('scheduler_service')
        training_service = TrainingService(db, scheduler)

        # Buscar alumno por chat_id
        student = student_service.get_student_by_chat_id(user.id)

        if not student:
            await update.message.reply_text(
                "❌ No estás registrado en el sistema.\n\n"
                "Contacta a tu entrenador para que te registre."
            )
            return

        # Obtener entrenamientos con ubicación
        trainings = training_service.get_all_trainings(student.id)

        message = Messages.training_schedule_with_locations(trainings)
        await update.message.reply_text(message)

        logger.info(f"Alumno {student.name} consultó sus sesiones")

    except Exception as e:
        logger.error(f"Error obteniendo sesiones: {str(e)}")
        await update.message.reply_text(
            "❌ Error al obtener tus sesiones. Intenta nuevamente."
        )
    finally:
        if db:
            db.close()


async def handle_feedback_intensity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para callbacks de intensidad de feedback.

    Formato del callback_data: feedback_intensity_{training_id}_{intensity}
    """
    query = update.callback_query
    await query.answer()

    # Parsear callback data
    try:
        parts = query.data.split("_")
        training_id = int(parts[2])
        intensity = int(parts[3])

        # Guardar intensidad en context.user_data para el siguiente paso
        context.user_data['feedback_training_id'] = training_id
        context.user_data['feedback_intensity'] = intensity

        # Solicitar información de dolor
        from src.services.tasks.feedback_task import FeedbackTask
        pain_message = FeedbackTask.format_pain_request()

        await query.edit_message_text(
            f"✅ Intensidad registrada: {intensity}\n\n{pain_message}"
        )

        logger.info(f"Feedback intensidad registrado: {intensity} para training {training_id}")

    except Exception as e:
        logger.error(f"Error procesando callback de intensidad: {str(e)}")
        await query.edit_message_text(
            "❌ Error procesando tu respuesta. Intenta nuevamente."
        )


async def handle_feedback_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para mensajes de texto relacionados con feedback.

    Procesa el nivel de dolor y comentarios del alumno.
    """
    # Verificar si hay un feedback en progreso
    if 'feedback_training_id' not in context.user_data:
        return  # No es un mensaje de feedback

    user = update.effective_user
    text = update.message.text.strip()

    from datetime import datetime
    from src.services.feedback_service import FeedbackService

    db = None
    try:
        # Parsear nivel de dolor (0-5) o comentario
        pain_level = 0
        comments = None

        # Intentar parsear como número
        try:
            pain_level = int(text)
            if not (0 <= pain_level <= 5):
                raise ValueError
        except ValueError:
            # Es un comentario
            comments = text
            pain_level = 1  # Asumir dolor leve si hay comentario

        # Registrar feedback
        db = get_db()
        feedback_service = FeedbackService(db)

        feedback = feedback_service.register_feedback(
            training_id=context.user_data['feedback_training_id'],
            intensity=context.user_data['feedback_intensity'],
            pain_level=pain_level,
            comments=comments,
            session_date=datetime.now().date(),
            completed=True
        )

        await update.message.reply_text(
            "✅ ¡Gracias por tu feedback!\n\n"
            "Tu progreso ha sido registrado."
        )

        # Limpiar datos temporales
        context.user_data.clear()

        logger.info(f"Feedback completo registrado para usuario {user.id}")

    except Exception as e:
        logger.error(f"Error registrando feedback: {str(e)}")
        await update.message.reply_text(
            "❌ Error registrando feedback. Intenta nuevamente."
        )
    finally:
        if db:
            db.close()


async def handle_feedback_completion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para callbacks de completitud de entrenamiento.

    Formato del callback_data: feedback_completed_{training_id}_{yes|no}
    """
    query = update.callback_query
    await query.answer()

    try:
        parts = query.data.split("_")
        training_id = int(parts[2])
        completed = parts[3] == "yes"

        # Guardar en context
        context.user_data['feedback_training_id'] = training_id
        context.user_data['feedback_completed'] = completed

        if completed:
            # Solicitar intensidad
            from src.services.tasks.feedback_task import FeedbackTask
            keyboard = FeedbackTask.create_intensity_keyboard(training_id)

            await query.edit_message_text(
                "¿Cómo te sentiste en la sesión?\n\n"
                "Selecciona la intensidad:",
                reply_markup=keyboard
            )
        else:
            await query.edit_message_text(
                "Entendido. ¿Por qué no completaste el entrenamiento?\n\n"
                "Escribe tu razón:"
            )
            # El próximo mensaje será capturado como comentario

        logger.info(f"Completitud registrada: {completed} para training {training_id}")

    except Exception as e:
        logger.error(f"Error procesando callback de completitud: {str(e)}")
        await query.edit_message_text(
            "❌ Error procesando tu respuesta."
        )

