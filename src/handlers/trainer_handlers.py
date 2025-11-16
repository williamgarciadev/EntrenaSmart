"""
Handlers de Comandos del Entrenador
====================================

Implementa los handlers de Telegram para los comandos
administrativos del entrenador.
"""
from telegram import Update
from telegram.ext import ContextTypes

from src.models.base import get_db
from src.services.student_service import StudentService
from src.services.training_service import TrainingService
from src.services.report_service import ReportService
from src.services.scheduler_service import SchedulerService
from src.services.tasks.reminder_task import ReminderTask
from src.core.config import settings
from src.core.exceptions import (
    ValidationError,
    DuplicateRecordError,
    RecordNotFoundError,
    InvalidWeekdayError,
    InvalidTimeFormatError
)
from src.utils.messages import Messages
from src.utils.menu_builder import build_trainer_commands_menu, build_student_commands_menu, build_yesno_menu
from src.utils.logger import logger
from src.utils.conversation_state import RegistrationState, TrainingState, save_state_to_context_simple, load_state_from_context_simple, clear_state_simple


def is_trainer(user_id: int) -> bool:
    """
    Verifica si el usuario es el entrenador autorizado.

    Args:
        user_id: ID del usuario de Telegram

    Returns:
        bool: True si es el entrenador
    """
    return user_id == settings.trainer_telegram_id


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para el comando /start.

    Envía mensaje de bienvenida según el tipo de usuario.
    """
    user = update.effective_user

    if is_trainer(user.id):
        message = (
            "👋 ¡Hola Entrenador!\n\n"
            "Bienvenido a *EntrenaSmart*, tu asistente para gestionar entrenamientos."
        )
        keyboard = build_trainer_commands_menu()
    else:
        message = (
            "👋 ¡Hola!\n\n"
            "Bienvenido a *EntrenaSmart*.\n\n"
            "Recibirás recordatorios automáticos de tus entrenamientos."
        )
        keyboard = build_student_commands_menu()

    await update.message.reply_text(message, reply_markup=keyboard)
    logger.info(f"Usuario {user.id} ({user.first_name}) ejecutó /start")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para el comando /help."""
    user = update.effective_user

    if is_trainer(user.id):
        message = Messages.help_trainer()
    else:
        message = Messages.help_student()

    await update.message.reply_text(message)
    logger.info(f"Usuario {user.id} ejecutó /help")


async def listar_alumnos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para el comando /listar_alumnos.

    Lista todos los alumnos registrados.
    """
    user = update.effective_user

    # Validar que sea el entrenador
    if not is_trainer(user.id):
        await update.message.reply_text(Messages.ERROR_UNAUTHORIZED)
        return

    db = None
    try:
        db = get_db()
        student_service = StudentService(db)
        students = student_service.list_all_students(active_only=True)

        if not students:
            await update.message.reply_text("📋 No hay alumnos registrados.")
            return

        # Formatear lista
        student_names = [
            f"{s.display_name} {'✅' if s.is_active else '❌'}"
            for s in students
        ]

        message = Messages.students_list(student_names)
        await update.message.reply_text(message)

        logger.info(f"Entrenador listó {len(students)} alumnos")

    except Exception as e:
        logger.error(f"Error listando alumnos: {str(e)}")
        await update.message.reply_text(
            "❌ Error al listar alumnos. Intenta nuevamente."
        )
    finally:
        if db:
            db.close()


async def reporte_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para el comando /reporte.

    Genera y envía el resumen semanal al entrenador.
    """
    user = update.effective_user

    # Validar que sea el entrenador
    if not is_trainer(user.id):
        await update.message.reply_text(Messages.ERROR_UNAUTHORIZED)
        return

    db = None
    try:
        db = get_db()
        report_service = ReportService(db)

        # Generar resumen para entrenador
        summary = report_service.generate_trainer_summary()

        await update.message.reply_text(summary)

        logger.info("Entrenador solicitó reporte manual")

    except Exception as e:
        logger.error(f"Error generando reporte: {str(e)}")
        await update.message.reply_text(
            "❌ Error al generar reporte. Intenta nuevamente."
        )
    finally:
        if db:
            db.close()


async def commands_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para procesar clics en los botones del menú de comandos.

    Ejecuta el comando correspondiente cuando el usuario hace clic en un botón.
    """
    query = update.callback_query
    user = query.from_user

    await query.answer()

    # Mapeo de callbacks a funciones de handlers
    callbacks = {
        "cmd_registrarme": _handle_registrarme,
        "cmd_set": _handle_set,
        "cmd_listar_alumnos": _callback_listar_alumnos,
        "cmd_reporte": _callback_reporte,
        "cmd_help": _callback_help,
        "cmd_mis_sesiones": _handle_mis_sesiones,
    }

    callback_data = query.data
    handler = callbacks.get(callback_data)

    if handler:
        await handler(update, context)
    else:
        await query.edit_message_text("❌ Comando no disponible.")


async def _handle_registrarme(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja el clic en 'Registrar Alumno'.

    Inicia el flujo de registro directamente.
    """
    query = update.callback_query
    user = query.from_user

    await query.answer()

    # Marcar en context que estamos iniciando flujo de registro desde botón
    context.user_data["_registration_from_button"] = True

    # Editar mensaje para pedir nombre
    await query.edit_message_text(
        "👤 ¿Cuál es el nombre del alumno que deseas registrar?"
    )

    logger.info(f"Entrenador {user.id} inició registro desde botón")


async def _handle_set(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el clic en 'Configurar Entrenamiento'."""
    query = update.callback_query
    user = query.from_user

    await query.answer()

    # Marcar en context que estamos iniciando flujo de entrenamiento desde botón
    context.user_data["_training_setup_active"] = True

    # Inicializar estado del entrenamiento
    from src.utils.conversation_state import TrainingState
    state = TrainingState(user_id=user.id)
    save_state_to_context_simple(context, state)

    # Inicializar lista de entrenamientos si no existe
    if "selected_trainings" not in context.user_data:
        context.user_data["selected_trainings"] = []

    # Editar mensaje para pedir nombre
    await query.edit_message_text(
        "👤 ¿Cuál es el nombre del alumno?"
    )

    logger.info(f"Entrenador {user.id} inició configuración de entrenamientos desde botón")


async def _callback_listar_alumnos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Wrapper para listar alumnos desde callback."""
    query = update.callback_query
    user = query.from_user

    # Validar que sea el entrenador
    if not is_trainer(user.id):
        await query.edit_message_text("⛔ No tienes permisos para ejecutar este comando.")
        return

    db = None
    try:
        db = get_db()
        student_service = StudentService(db)
        students = student_service.list_all_students(active_only=True)

        if not students:
            await query.edit_message_text("📋 No hay alumnos registrados.")
            return

        # Formatear lista
        student_names = [
            f"{s.display_name} {'✅' if s.is_active else '❌'}"
            for s in students
        ]

        message = Messages.students_list(student_names)
        await query.edit_message_text(message)

        logger.info(f"Entrenador listó {len(students)} alumnos desde callback")

    except Exception as e:
        logger.error(f"Error listando alumnos: {str(e)}")
        await query.edit_message_text(
            "❌ Error al listar alumnos. Intenta nuevamente."
        )
    finally:
        if db:
            db.close()


async def _callback_reporte(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Wrapper para generar reporte desde callback."""
    query = update.callback_query
    user = query.from_user

    # Validar que sea el entrenador
    if not is_trainer(user.id):
        await query.edit_message_text("⛔ No tienes permisos para ejecutar este comando.")
        return

    db = None
    try:
        db = get_db()
        report_service = ReportService(db)

        # Generar resumen para entrenador
        summary = report_service.generate_trainer_summary()

        await query.edit_message_text(summary)

        logger.info("Entrenador solicitó reporte manual desde callback")

    except Exception as e:
        logger.error(f"Error generando reporte: {str(e)}")
        await query.edit_message_text(
            "❌ Error al generar reporte. Intenta nuevamente."
        )
    finally:
        if db:
            db.close()


async def _callback_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Wrapper para mostrar ayuda desde callback."""
    query = update.callback_query
    user = query.from_user

    if is_trainer(user.id):
        message = Messages.help_trainer()
    else:
        message = Messages.help_student()

    await query.edit_message_text(message)
    logger.info(f"Usuario {user.id} solicitó ayuda desde callback")


async def _handle_mis_sesiones(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el clic en 'Mis Sesiones' (alumno)."""
    query = update.callback_query
    await query.edit_message_text(
        "📅 Para ver tus sesiones, usa:\n\n"
        "`/mis_sesiones`"
    )


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler CENTRAL para coordinar todos los flujos de entrada de texto.

    Detecta qué flujo está activo y delega al handler correspondiente.
    """
    user = update.effective_user

    logger.debug(f"[handle_text_input] Flags: reg={context.user_data.get('_registration_from_button')}, train={context.user_data.get('_training_setup_active')}, train_confirm={context.user_data.get('_training_confirm_student')}, train_time={context.user_data.get('_training_enter_time')}")

    # FLUJO 1: Registro desde botón
    if context.user_data.get("_registration_from_button"):
        await _handle_registration_from_button_impl(update, context)
        return

    # FLUJO 2: Nombre del alumno en entrenamientos
    if context.user_data.get("_training_setup_active"):
        await handle_training_student_name(update, context)
        return

    # FLUJO 3: Confirmación de alumno en entrenamientos
    if context.user_data.get("_training_confirm_student"):
        await handle_training_confirm_student(update, context)
        return

    # FLUJO 4: Hora en entrenamientos
    if context.user_data.get("_training_enter_time"):
        await handle_training_enter_time(update, context)
        return


async def _handle_registration_from_button_impl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Implementación del flujo de registro desde botón."""
    user = update.effective_user

    name = update.message.text.strip()

    # Validar nombre
    if not name or len(name) < 2:
        await update.message.reply_text(
            "❌ El nombre debe tener al menos 2 caracteres.\n\n"
            "¿Cuál es el nombre del alumno?"
        )
        return

    # Guardar nombre en estado
    state = RegistrationState(user_id=user.id)
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

    logger.info(f"Botón registro - Nombre ingresado: {name}")

    # Limpiar flag de iniciación desde botón
    context.user_data["_registration_from_button"] = False


async def handle_training_student_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Procesa el nombre del alumno en flujo de entrenamientos.

    Ejecuta la búsqueda de alumno y muestra los resultados.
    """
    from src.utils.fuzzy_search import search_students

    if not update.message or not update.message.text:
        logger.warning("[training_student_name] No hay mensaje de texto")
        return

    query = update.message.text.strip()

    # Validar entrada
    if not query or len(query) < 2:
        logger.info(f"[training_student_name] Nombre muy corto: '{query}'")
        await update.message.reply_text(
            "❌ El nombre debe tener al menos 2 caracteres.\n\n"
            "¿Cuál es el nombre del alumno?"
        )
        return

    db = None
    try:
        db = get_db()
        student_service = StudentService(db)
        students = student_service.list_all_students(active_only=True)

        if not students:
            await update.message.reply_text(
                "❌ No hay alumnos registrados. Registra alumnos primero."
            )
            context.user_data["_training_setup_active"] = False
            return

        # Buscar por fuzzy search
        found_students = search_students(query, students, cutoff=0.6, max_results=5)

        if not found_students:
            await update.message.reply_text(
                f"❌ No se encontraron alumnos con '{query}'.\n\n"
                "¿Cuál es el nombre del alumno?"
            )
            return

        # Guardar resultados en contexto
        context.user_data['search_results'] = found_students

        # Mostrar opciones
        lines = ["👥 Alumnos encontrados:\n"]
        for i, student in enumerate(found_students, 1):
            lines.append(f"{i}. {student.name}")
        lines.append("\nResponde con el número del alumno.")

        await update.message.reply_text("\n".join(lines))

        # Transicionar al siguiente flujo
        context.user_data["_training_confirm_student"] = True
        context.user_data["_training_setup_active"] = False

        logger.info(f"[training_student_name] Búsqueda: '{query}' → {len(found_students)} resultados")

    except Exception as e:
        logger.error(f"[training_student_name] Error: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "❌ Error al buscar alumno. Intenta nuevamente."
        )
        context.user_data["_training_setup_active"] = False
    finally:
        if db:
            db.close()


async def handle_training_confirm_student(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Procesa la selección del alumno en flujo de entrenamientos.

    Valida el número y muestra el menú de días.
    """
    if not update.message or not update.message.text:
        return

    response = update.message.text.strip()
    search_results = context.user_data.get('search_results', [])

    try:
        # Intentar obtener por número
        if response.isdigit():
            idx = int(response) - 1
            if 0 <= idx < len(search_results):
                student = search_results[idx]

                # Guardar el alumno seleccionado en estado
                state: TrainingState = load_state_from_context_simple(context, TrainingState)
                state.set_student(student.id, student.name)
                save_state_to_context_simple(context, state)

                # Limpiar flag de confirmación
                context.user_data["_training_confirm_student"] = False

                # Mostrar menú de días
                from src.utils.menu_builder import build_day_menu
                keyboard = build_day_menu()

                await update.message.reply_text(
                    f"✅ Alumno seleccionado: {student.name}\n\n"
                    "📅 Selecciona el día de la semana:",
                    reply_markup=keyboard
                )

                logger.info(f"[training_confirm_student] Alumno: {student.name} (ID: {student.id})")
                return

            else:
                await update.message.reply_text(
                    f"❌ Número inválido. Elige entre 1 y {len(search_results)}."
                )
                return

        else:
            # Si no es número, asumir que es un nuevo nombre para buscar
            context.user_data["_training_setup_active"] = True
            context.user_data["_training_confirm_student"] = False
            await update.message.reply_text(
                "👤 ¿Cuál es el nombre del alumno?"
            )
            return

    except Exception as e:
        logger.error(f"[training_confirm_student] Error: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "❌ Error al confirmar alumno. Intenta nuevamente."
        )
        context.user_data["_training_confirm_student"] = False


async def handle_training_day_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Procesa la selección de día en flujo de entrenamientos.

    Extrae el día del callback y pide la hora.
    """
    from src.core.constants import WEEKDAY_NAMES

    query = update.callback_query
    await query.answer()

    try:
        # Extraer día del callback_data: "day_<number>" (0=Lunes, 6=Domingo)
        day_number = int(query.data.split("_")[1])
        day_name = WEEKDAY_NAMES[day_number]

        # Guardar día en estado
        state: TrainingState = load_state_from_context_simple(context, TrainingState)
        state.set_day(day_number, day_name)
        save_state_to_context_simple(context, state)

        # Pedir la hora
        await query.edit_message_text(
            f"⏰ ¿A qué hora el {day_name}? (Formato: HH:MM)\n\nEjemplo: 05:00 o 17:30"
        )

        # Marcar que esperamos la hora
        context.user_data["_training_enter_time"] = True

        logger.info(f"[training_day_selection] Día seleccionado: {day_name}")

    except Exception as e:
        logger.error(f"[training_day_selection] Error: {str(e)}", exc_info=True)
        await query.edit_message_text(
            "❌ Error al seleccionar el día. Intenta nuevamente."
        )


async def handle_training_enter_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Procesa la hora del entrenamiento en flujo de entrenamientos.

    Valida formato HH:MM y agrega el entrenamiento a la lista temporal.
    """
    import re

    if not update.message or not update.message.text:
        return

    time_str = update.message.text.strip()

    # Validar formato HH:MM
    if not re.match(r"^([0-1][0-9]|2[0-3]):([0-5][0-9])$", time_str):
        await update.message.reply_text(
            "❌ Formato inválido.\n\n"
            "Usa HH:MM (24h). Ejemplo: 05:00 o 17:30"
        )
        return

    try:
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

        # Transicionar al siguiente flujo
        context.user_data["_training_enter_time"] = False

        logger.info(f"[training_enter_time] Hora: {time_str}")

    except Exception as e:
        logger.error(f"[training_enter_time] Error: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "❌ Error al procesar la hora. Intenta nuevamente."
        )


async def handle_training_another_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Procesa la decisión de agregar otro día en flujo de entrenamientos.

    Si SÍ: Vuelve a mostrar menú de días
    Si NO: Muestra resumen y pide confirmación final
    """
    from src.utils.menu_builder import build_day_menu

    query = update.callback_query
    await query.answer()

    try:
        state: TrainingState = load_state_from_context_simple(context, TrainingState)

        if query.data == "train_another_yes":
            # Mostrar menú de días nuevamente (para agregar otro día)
            keyboard = build_day_menu()

            await query.edit_message_text(
                f"📅 ¿Qué otro día va a asistir {state.student_name}?",
                reply_markup=keyboard
            )

            logger.info(f"[training_another_day] Usuario elige agregar otro día")

        else:  # train_another_no
            # Mostrar resumen y pedir confirmación final
            trainings = context.user_data.get('selected_trainings', [])

            # Construir resumen
            lines = [f"📋 Resumen para {state.student_name}:\n"]
            for i, training in enumerate(trainings, 1):
                lines.append(f"{i}. {training['day_name']} - {training['time']}")

            lines.append("\n¿Confirmas estos entrenamientos?")

            keyboard = build_yesno_menu(
                affirmative_callback="train_confirm_yes",
                negative_callback="train_confirm_no"
            )

            await query.edit_message_text(
                "\n".join(lines),
                reply_markup=keyboard
            )

            logger.info(f"[training_another_day] Usuario elige NO agregar otro día - Mostrando confirmación")

    except Exception as e:
        logger.error(f"[training_another_day] Error: {str(e)}", exc_info=True)
        await query.edit_message_text(
            "❌ Error procesando la selección. Intenta nuevamente."
        )


async def handle_training_final_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Procesa la confirmación final de entrenamientos.

    Si SÍ: Registra todos los entrenamientos en BD
    Si NO: Cancela la operación
    """
    query = update.callback_query
    await query.answer()

    try:
        state: TrainingState = load_state_from_context_simple(context, TrainingState)
        trainings = context.user_data.get('selected_trainings', [])

        if query.data == "train_confirm_yes":
            # Registrar entrenamientos en BD
            db = None
            try:
                db = get_db()
                scheduler = context.application.bot_data.get('scheduler_service')
                training_service = TrainingService(db, scheduler)

                # Registrar cada entrenamiento
                for training in trainings:
                    training_service.add_training(
                        student_id=training['student_id'],
                        weekday=training['day_number'],
                        weekday_name=training['day_name'],
                        time_str=training['time']
                    )

                await query.edit_message_text(
                    f"✅ Entrenamientos registrados para {state.student_name}:\n\n"
                    + "\n".join([f"• {t['day_name']} - {t['time']}" for t in trainings])
                )

                logger.info(f"[training_final_confirm] Entrenamientos registrados: {state.student_name} - {len(trainings)} sesiones")
            except Exception as e:
                logger.error(f"[training_final_confirm] Error registrando entrenamientos: {str(e)}", exc_info=True)
                await query.edit_message_text(
                    "❌ Error al registrar entrenamientos. Intenta nuevamente."
                )
            finally:
                if db:
                    db.close()

        else:  # train_confirm_no
            await query.edit_message_text(
                "❌ Configuración cancelada."
            )
            logger.info(f"[training_final_confirm] Entrenador canceló configuración")

    except Exception as e:
        logger.error(f"[training_final_confirm] Error: {str(e)}", exc_info=True)
        await query.edit_message_text(
            "❌ Error al registrar entrenamientos. Intenta nuevamente."
        )

    finally:
        # Limpiar estado
        clear_state_simple(context, TrainingState)
        context.user_data.pop('selected_trainings', None)
        context.user_data.pop('search_results', None)
        context.user_data.pop('_training_setup_active', None)
        context.user_data.pop('_training_confirm_student', None)
        context.user_data.pop('_training_enter_time', None)


async def handle_registration_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para procesar la confirmación de registro iniciado desde botón.

    Maneja los callbacks: reg_confirm_yes, reg_confirm_no
    """
    query = update.callback_query
    user = query.from_user

    await query.answer()

    # Obtener el estado guardado
    state: RegistrationState = load_state_from_context_simple(context, RegistrationState)
    name = state.get_student_name()

    if query.data == "reg_confirm_yes":
        # Registrar alumno
        db = None
        try:
            db = get_db()
            student_service = StudentService(db)

            # Registrar sin chat_id (se asignará cuando alumno inicie sesión)
            student = student_service.register_student(
                name=name,
                telegram_username=user.username
            )

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
    if "_registration_from_button" in context.user_data:
        context.user_data["_registration_from_button"] = False
