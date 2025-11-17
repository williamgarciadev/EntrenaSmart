"""
Templates y Utilidades de Mensajes
===================================

Proporciona templates y funciones de formateo para mensajes
del bot de Telegram.
"""
from typing import List
from src.core.constants import TRAINER_COMMANDS, STUDENT_COMMANDS


class Messages:
    """Mensajes del bot de Telegram."""

    # Mensajes de inicio
    WELCOME_TRAINER = (
        "👋 ¡Hola Entrenador!\n\n"
        "Bienvenido a *EntrenaSmart*, tu asistente para gestionar entrenamientos.\n\n"
        "Comandos disponibles:\n"
        "/registrarme <nombre> - Registrar nuevo alumno\n"
        "/set <nombre> <día> <tipo> <hora> - Configurar entrenamiento\n"
        "/listar_alumnos - Ver alumnos registrados\n"
        "/reporte - Generar reporte manual\n"
        "/help - Ver ayuda completa"
    )

    WELCOME_STUDENT = (
        "👋 ¡Hola!\n\n"
        "Bienvenido a *EntrenaSmart*.\n\n"
        "Recibirás recordatorios automáticos de tus entrenamientos.\n\n"
        "Comandos disponibles:\n"
        "/mis_sesiones - Ver tus entrenamientos\n"
        "/help - Ver ayuda"
    )

    # Mensajes de ayuda
    @staticmethod
    def help_trainer() -> str:
        """Mensaje de ayuda para el entrenador."""
        lines = [
            "📖 *Ayuda - Entrenador*\n",
            "*Comandos disponibles:*\n"
        ]

        for cmd, desc in TRAINER_COMMANDS:
            lines.append(f"{cmd} - {desc}")

        lines.extend([
            "\n*Ejemplos de uso:*",
            "",
            "Registrar alumno:",
            "`/registrarme Juan Pérez`",
            "",
            "Configurar entrenamiento:",
            "`/set Juan Lunes Funcional 05:00`",
            "`/set Juan Miércoles Pierna 17:30`"
        ])

        return "\n".join(lines)

    @staticmethod
    def help_student() -> str:
        """Mensaje de ayuda para alumnos."""
        lines = [
            "📖 *Ayuda - Alumno*\n",
            "*Comandos disponibles:*\n"
        ]

        for cmd, desc in STUDENT_COMMANDS:
            lines.append(f"{cmd} - {desc}")

        lines.extend([
            "\n*Funcionamiento:*",
            "",
            "✅ Recibirás recordatorios automáticos 30 minutos antes de tu entrenamiento",
            "✅ Después del entrenamiento, te pediremos feedback",
            "✅ Cada domingo recibirás tu reporte semanal"
        ])

        return "\n".join(lines)

    # Mensajes de éxito
    @staticmethod
    def student_registered(name: str) -> str:
        """Mensaje de alumno registrado exitosamente."""
        return f"✅ Alumno *{name}* registrado correctamente."

    @staticmethod
    def training_configured(weekday: str, time: str, session_type: str) -> str:
        """Mensaje de entrenamiento configurado."""
        return f"✅ Entrenamiento configurado:\n{weekday} - {session_type} - {time}"

    # Mensajes de error
    ERROR_COMMAND_FORMAT = (
        "❌ Formato de comando incorrecto.\n\n"
        "Usa `/help` para ver la sintaxis correcta."
    )

    ERROR_UNAUTHORIZED = (
        "⛔ No tienes permisos para ejecutar este comando.\n\n"
        "Este comando es solo para el entrenador."
    )

    ERROR_STUDENT_NOT_FOUND = (
        "❌ Alumno no encontrado.\n\n"
        "Verifica que el nombre esté escrito correctamente."
    )

    ERROR_INVALID_WEEKDAY = (
        "❌ Día de la semana inválido.\n\n"
        "Usa: Lunes, Martes, Miércoles, Jueves, Viernes, Sábado, Domingo"
    )

    ERROR_INVALID_TIME = (
        "❌ Formato de hora inválido.\n\n"
        "Usa el formato 24h: HH:MM (ejemplo: 05:00, 17:30)"
    )

    @staticmethod
    def error_generic(error: str) -> str:
        """Mensaje de error genérico."""
        return f"❌ Error: {error}"

    # Listas y reportes
    @staticmethod
    def students_list(students: List[str]) -> str:
        """Lista de alumnos."""
        if not students:
            return "📋 No hay alumnos registrados."

        lines = ["📋 *Alumnos Registrados:*\n"]
        for i, student in enumerate(students, 1):
            lines.append(f"{i}. {student}")

        return "\n".join(lines)

    @staticmethod
    def training_schedule(schedule: dict) -> str:
        """Horario de entrenamientos."""
        if not schedule:
            return "📅 No tienes entrenamientos configurados."

        lines = ["📅 *Tus Entrenamientos:*\n"]

        for day, sessions in sorted(schedule.items()):
            lines.append(f"*{day}:*")
            for session in sessions:
                lines.append(f"  • {session}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def training_schedule_with_locations(trainings: List) -> str:
        """
        Horario de entrenamientos con ubicación.

        Args:
            trainings: Lista de objetos Training

        Returns:
            str: Mensaje formateado con entrenamientos y ubicaciones
        """
        if not trainings:
            return "📅 No tienes entrenamientos configurados."

        # Agrupar por día
        schedule_by_day = {}
        for training in trainings:
            day = training.weekday_name
            if day not in schedule_by_day:
                schedule_by_day[day] = []

            location = training.location or "Sin ubicación"
            session_type = training.session_type or "General"
            time = training.time_str

            schedule_by_day[day].append({
                "time": time,
                "location": location,
                "type": session_type
            })

        # Construir mensaje
        lines = ["📅 *Tus Entrenamientos:*\n"]

        for day in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
            if day in schedule_by_day:
                lines.append(f"*{day}:*")
                for session in schedule_by_day[day]:
                    lines.append(f"  • {session['time']} en {session['location']} ({session['type']})")
                lines.append("")

        return "\n".join(lines)

    # Confirmaciones
    CONFIRM_ACTION = "¿Estás seguro de realizar esta acción?"

    ACTION_CANCELLED = "❌ Acción cancelada."

    ACTION_COMPLETED = "✅ Acción completada exitosamente."

    # Recordatorios de entrenamiento
    @staticmethod
    def training_reminder(
        session_type: str,
        training_time: str,
        location: str = "Zona de Entrenamiento",
        include_checklist: bool = True
    ) -> str:
        """
        Mensaje de recordatorio de entrenamiento.

        Args:
            session_type: Tipo de sesión (ej: "Funcional", "Pesas", "Pierna")
            training_time: Hora del entrenamiento (HH:MM)
            location: Ubicación/piso (ej: "2do Piso", "4to Piso")
            include_checklist: Incluir checklist pre-entrenamiento

        Returns:
            str: Mensaje formateado en HTML
        """
        # Mapeo de tipos de sesión a emojis
        emoji_map = {
            "Pierna": "🦵",
            "Funcional": "💪",
            "Brazo": "💪",
            "Espalda": "🔙",
            "Pecho": "💪",
            "Hombros": "🔺",
            "Técnica": "⚙️",
            "Pesas": "🏋️",
            "Cardio": "🏃",
            "Flexibilidad": "🧘",
            "Otro": "❓"
        }

        emoji = emoji_map.get(session_type, "✨")

        lines = [
            f"{emoji} <b>¡Es hora de entrenar!</b>",
            "",
            f"📅 <b>{training_time}</b> • 📍 <b>{location}</b>",
            f"💪 <b>Sesión:</b> {session_type}",
            "",
            "🔥 <b>Preparación:</b>",
            "   • Llega 5 min antes",
            "   • Calentamiento: 5 min en cinta (vel. 5.0)",
            "   • Nos vemos en el lugar indicado",
            "",
            "¡Vamos con todo! 💪✨",
        ]

        return "\n".join(lines)

