# -*- coding: utf-8 -*-
"""
Handler para ver programación de entrenamientos del estudiante
==============================================================

Comando: /mi-semana
Permite al estudiante ver su programación semanal con detalles
de tipo de entrenamiento y ubicación.
"""
from telegram import Update
from telegram.ext import ContextTypes

from src.models.base import get_db
from src.models.student import Student
from src.services.training_service import TrainingService
from src.services.config_training_service import ConfigTrainingService
from src.utils.logger import logger


async def mi_semana_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Muestra la programación semanal del estudiante.

    Combina la información de:
    - Training: días y horas que el estudiante eligió
    - TrainingDayConfig: tipo de entrenamiento y ubicación de cada día
    """
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        logger.info(f"📅 [MI_SEMANA] Solicitado por chat_id={chat_id}, user_id={user_id}")

        # Obtener BD
        db = get_db()

        # Buscar estudiante por chat_id
        student = db.query(Student).filter(Student.chat_id == chat_id).first()

        if not student:
            await update.message.reply_text(
                "❌ No estás registrado como alumno.\n\n"
                "Por favor, contacta a tu entrenador para registrarte."
            )
            logger.warning(f"⚠️ [MI_SEMANA] Estudiante no encontrado para chat_id={chat_id}")
            return

        # Obtener entrenamientos del estudiante
        training_service = TrainingService(db)
        trainings = training_service.get_all_trainings(student.id)

        if not trainings:
            await update.message.reply_text(
                "📅 No tienes entrenamientos programados aún.\n\n"
                "Contacta a tu entrenador para que te asigne entrenamientos."
            )
            logger.info(f"ℹ️ [MI_SEMANA] Student {student.id} no tiene entrenamientos")
            return

        # Obtener configuración de la semana
        config_service = ConfigTrainingService(db)
        config = config_service.get_all_configs()
        config_dict = {c.weekday: c for c in config}

        # Agrupar entrenamientos por día
        schedule_by_day = {}
        for training in trainings:
            if not training.is_active:
                continue

            day_name = training.weekday_name
            weekday_num = training.weekday

            if day_name not in schedule_by_day:
                schedule_by_day[day_name] = {
                    "times": [],
                    "weekday": weekday_num,
                    "config": config_dict.get(weekday_num)
                }

            schedule_by_day[day_name]["times"].append(training.time_str)

        # Construir mensaje
        lines = [
            "📅 <b>Tu Programación Semanal</b>\n",
            f"Alumno: <b>{student.name}</b>\n"
        ]

        # Ordenar por día de la semana
        day_order = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        for day_name in day_order:
            if day_name not in schedule_by_day:
                continue

            info = schedule_by_day[day_name]
            times = sorted(info["times"])
            config = info["config"]

            lines.append(f"<b>📍 {day_name}</b>")

            if config:
                session_type = config.session_type
                location = config.location
                for time in times:
                    lines.append(f"   🕐 {time} → {session_type} en {location}")
            else:
                # Si no hay configuración, mostrar solo la hora
                for time in times:
                    lines.append(f"   🕐 {time} → (Sin configuración aún)")

            lines.append("")

        lines.extend([
            "<i>Recuerda: recibirás un recordatorio 30 minutos antes de cada entrenamiento.</i>",
            "",
            "📝 Para cambios, contacta a tu entrenador."
        ])

        message = "\n".join(lines)
        await update.message.reply_text(
            message,
            parse_mode="HTML"
        )

        logger.info(f"✅ [MI_SEMANA] Programación mostrada para {student.name} ({student.id})")

    except Exception as e:
        logger.error(f"❌ [MI_SEMANA] Error: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "❌ Error al obtener tu programación. Por favor, intenta de nuevo."
        )
