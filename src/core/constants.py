"""
Constantes del proyecto EntrenaSmart
=====================================

Este módulo define todas las constantes utilizadas en el proyecto.
"""
from enum import IntEnum
from typing import Final


# ====================================
# Días de la Semana
# ====================================

class Weekday(IntEnum):
    """Enumeración de días de la semana."""
    LUNES = 0
    MARTES = 1
    MIERCOLES = 2
    JUEVES = 3
    VIERNES = 4
    SABADO = 5
    DOMINGO = 6


# Mapeo de nombres de días en español
WEEKDAY_NAMES: Final[dict[int, str]] = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo"
}

# Mapeo inverso: nombre -> número
WEEKDAY_NAME_TO_NUMBER: Final[dict[str, int]] = {
    name.lower(): number for number, name in WEEKDAY_NAMES.items()
}


# ====================================
# Intensidad de Entrenamiento
# ====================================

class Intensity(IntEnum):
    """Enumeración de niveles de intensidad de entrenamiento."""
    SUAVE = 1
    MODERADO = 2
    INTENSO = 3
    MUY_INTENSO = 4


INTENSITY_NAMES: Final[dict[int, str]] = {
    1: "Suave",
    2: "Moderado",
    3: "Intenso",
    4: "Muy intenso"
}

INTENSITY_EMOJIS: Final[dict[int, str]] = {
    1: "🟢",
    2: "🟡",
    3: "🟠",
    4: "🔴"
}


# ====================================
# Nivel de Dolor
# ====================================

class PainLevel(IntEnum):
    """Enumeración de niveles de dolor."""
    SIN_DOLOR = 0
    LEVE_MOLESTIA = 1
    DOLOR_LEVE = 2
    DOLOR_MODERADO = 3
    DOLOR_FUERTE = 4
    DOLOR_MUY_FUERTE = 5


PAIN_LEVEL_NAMES: Final[dict[int, str]] = {
    0: "Sin dolor",
    1: "Leve molestia",
    2: "Dolor leve",
    3: "Dolor moderado",
    4: "Dolor fuerte",
    5: "Dolor muy fuerte"
}


# ====================================
# Tipos de Sesión
# ====================================

# Tipos de sesión comunes (se pueden expandir)
SESSION_TYPES: Final[list[str]] = [
    "Funcional",
    "Pierna",
    "Espalda",
    "Pecho",
    "Brazos",
    "Cardio",
    "Core",
    "Full Body",
    "HIIT",
    "Movilidad"
]


# ====================================
# Mensajes de Recordatorio
# ====================================

# Checklist para el recordatorio pre-entrenamiento
REMINDER_CHECKLIST: Final[list[str]] = [
    "Hidrátate (300–400ml)",
    "Mueve un poco las articulaciones",
    "Ten lista la ropa y zapatillas",
    "Comida ligera 1-2 horas antes",
    "Descansa 10 min antes de empezar"
]

# Emoji para tipos de sesión
SESSION_TYPE_EMOJIS: Final[dict[str, str]] = {
    "funcional": "🏋️‍♂️",
    "pierna": "🦵",
    "espalda": "💪",
    "pecho": "💪",
    "brazos": "💪",
    "cardio": "🏃‍♂️",
    "core": "🧘‍♂️",
    "full body": "🏋️",
    "hiit": "⚡",
    "movilidad": "🧘"
}


# ====================================
# Comandos del Bot
# ====================================

# Comandos disponibles para el entrenador
TRAINER_COMMANDS: Final[list[tuple[str, str]]] = [
    ("/start", "Iniciar el bot y ver ayuda"),
    ("/registrarme", "Registrar un nuevo alumno"),
    ("/listar_alumnos", "Listar todos los alumnos"),
    ("/set", "Configurar entrenamiento semanal"),
    ("/mis_sesiones", "Ver sesiones configuradas (alumno)"),
    ("/reporte", "Generar reporte manual"),
    ("/help", "Mostrar ayuda"),
]

# Comandos disponibles para los alumnos
STUDENT_COMMANDS: Final[list[tuple[str, str]]] = [
    ("/start", "Iniciar el bot"),
    ("/mis_sesiones", "Ver mis entrenamientos"),
    ("/help", "Mostrar ayuda"),
]


# ====================================
# Límites y Validaciones
# ====================================

# Límites de tiempo
MIN_REMINDER_MINUTES: Final[int] = 5
MAX_REMINDER_MINUTES: Final[int] = 120
DEFAULT_REMINDER_MINUTES: Final[int] = 30

# Límites de nombres
MAX_STUDENT_NAME_LENGTH: Final[int] = 100
MAX_SESSION_TYPE_LENGTH: Final[int] = 50
MAX_COMMENT_LENGTH: Final[int] = 500

# Límites de valores
MIN_INTENSITY: Final[int] = 1
MAX_INTENSITY: Final[int] = 4
MIN_PAIN_LEVEL: Final[int] = 0
MAX_PAIN_LEVEL: Final[int] = 5


# ====================================
# Formato de Fecha y Hora
# ====================================

TIME_FORMAT: Final[str] = "%H:%M"
DATE_FORMAT: Final[str] = "%Y-%m-%d"
DATETIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"


# ====================================
# Base de Datos
# ====================================

# Nombre de la tabla de jobs de APScheduler
APSCHEDULER_JOBS_TABLE: Final[str] = "apscheduler_jobs"

# Pool de conexiones SQLite
DATABASE_POOL_SIZE: Final[int] = 5
DATABASE_MAX_OVERFLOW: Final[int] = 10


# ====================================
# Reportes
# ====================================

# Número de semanas a incluir en el reporte
REPORT_WEEKS_HISTORY: Final[int] = 4

# Porcentaje mínimo de asistencia para "buen cumplimiento"
GOOD_ATTENDANCE_THRESHOLD: Final[float] = 0.75  # 75%


# ====================================
# Timeouts y Reintentos
# ====================================

# Timeout para comandos de Telegram (segundos)
TELEGRAM_COMMAND_TIMEOUT: Final[int] = 30

# Número de reintentos para operaciones de BD
DB_RETRY_ATTEMPTS: Final[int] = 3

# Delay entre reintentos (segundos)
DB_RETRY_DELAY: Final[int] = 1

