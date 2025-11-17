"""
Modelo de Configuración de Recordatorio Semanal
================================================

Define la configuración para el envío automático de recordatorios
semanales del entrenador a todos los alumnos activos.
"""
from sqlalchemy import Integer, String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.src.models.base import Base


class WeeklyReminderConfig(Base):
    """
    Configuración del recordatorio semanal del entrenador.

    El entrenador puede configurar:
    - Si trabaja o no los lunes
    - Mensajes personalizados para cada caso
    - Día y hora de envío del recordatorio
    """

    __tablename__ = "weekly_reminder_configs"

    # Configuración del lunes
    is_monday_off: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Si el lunes no trabaja (True = no trabaja)"
    )

    # Mensajes
    message_full_week: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="Hola muy buenas noches, espero estés bien, ¿para esta semana como te gustaría programar tu semana de entrenamiento personalizado?\n\nQuedo atento a tu respuesta.",
        comment="Mensaje cuando trabaja toda la semana"
    )

    message_monday_off: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="Hola hola buenas noches espero estés bien, quiera saber esta semana qué días y hora deseas tus entrenamientos.\n\nEl día de mañana lunes no estaré activo en REPS GYM\n\nQuedo atento a tu mensaje.",
        comment="Mensaje cuando el lunes no trabaja"
    )

    # Programación de envío
    send_day: Mapped[int] = mapped_column(
        Integer,
        default=6,  # Domingo
        nullable=False,
        comment="Día de la semana para envío (0=Lunes, 6=Domingo)"
    )

    send_hour: Mapped[int] = mapped_column(
        Integer,
        default=18,  # 6 PM
        nullable=False,
        comment="Hora de envío (0-23)"
    )

    send_minute: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Minuto de envío (0-59)"
    )

    # Estado
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Si el recordatorio automático está activo"
    )

    def __repr__(self) -> str:
        """Representación del modelo."""
        day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        day_name = day_names[self.send_day]
        status = "Activo" if self.is_active else "Inactivo"
        monday_status = "No trabaja lunes" if self.is_monday_off else "Trabaja toda la semana"

        return (
            f"<WeeklyReminderConfig("
            f"{monday_status}, "
            f"{day_name} {self.send_hour:02d}:{self.send_minute:02d}, "
            f"{status}"
            f")>"
        )

    @property
    def send_time_str(self) -> str:
        """Retorna la hora de envío en formato HH:MM."""
        return f"{self.send_hour:02d}:{self.send_minute:02d}"

    @property
    def day_name(self) -> str:
        """Retorna el nombre del día de envío."""
        day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        return day_names[self.send_day]

    @property
    def current_message(self) -> str:
        """Retorna el mensaje actual según configuración de lunes."""
        return self.message_monday_off if self.is_monday_off else self.message_full_week
