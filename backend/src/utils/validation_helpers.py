"""
Utilidades de Validación con Feedback Visual
============================================

Proporciona funciones para validación con emojis y mensajes amigables.

Ejemplo:
    >>> validate_time_format("05:00")
    (True, "⏰ 05:00 ✅")

    >>> validate_time_format("25:00")
    (False, "❌ Formato inválido. Usa HH:MM (24h). Ejemplo: 05:00")
"""
import re
from typing import Tuple


def validate_time_format(time_str: str) -> Tuple[bool, str]:
    """
    Valida formato de hora HH:MM con feedback visual.

    Args:
        time_str: String con la hora a validar (ej: "05:00")

    Returns:
        Tuple con (es_válido, mensaje_feedback)

    Example:
        >>> is_valid, msg = validate_time_format("05:00")
        >>> is_valid
        True
        >>> msg
        "⏰ 05:00 ✅"
    """
    time_str = time_str.strip()

    # Patrón: HH:MM en formato 24h
    pattern = r"^([0-1][0-9]|2[0-3]):([0-5][0-9])$"

    if re.match(pattern, time_str):
        return True, f"⏰ {time_str} ✅"

    # Proporcionar feedback específico según el error
    if ":" not in time_str:
        return False, "❌ Falta el ':' separador. Usa HH:MM (ejemplo: 05:00)"

    parts = time_str.split(":")
    if len(parts) != 2:
        return False, "❌ Usa exactamente HH:MM (ejemplo: 05:00)"

    try:
        hh, mm = int(parts[0]), int(parts[1])
        if hh < 0 or hh > 23:
            return False, f"❌ Hora {hh} inválida. Usa 00-23 (ejemplo: 05:00)"
        if mm < 0 or mm > 59:
            return False, f"❌ Minutos {mm} inválidos. Usa 00-59 (ejemplo: 05:00)"
    except ValueError:
        return False, "❌ Hora debe ser números. Usa HH:MM (ejemplo: 05:00)"

    return False, "❌ Formato inválido. Usa HH:MM (24h). Ejemplo: 05:00"


def validate_student_name(name: str) -> Tuple[bool, str]:
    """
    Valida nombre de alumno con feedback visual.

    Args:
        name: String con el nombre a validar

    Returns:
        Tuple con (es_válido, mensaje_feedback)

    Example:
        >>> is_valid, msg = validate_student_name("Juan Pérez")
        >>> is_valid
        True
    """
    name = name.strip()

    if not name:
        return False, "❌ El nombre no puede estar vacío."

    if len(name) < 2:
        return False, f"❌ El nombre '{name}' es muy corto. Mínimo 2 caracteres."

    if len(name) > 100:
        return False, f"❌ El nombre es muy largo. Máximo 100 caracteres."

    # Validar que contenga caracteres válidos
    if not re.match(r"^[a-záéíóúñ\s\-']+$", name, re.IGNORECASE):
        return False, "❌ El nombre contiene caracteres inválidos."

    return True, f"👤 '{name}' ✅"


def format_time_suggestion(hour: int, minute: int) -> str:
    """
    Formatea una sugerencia de hora con emoji.

    Args:
        hour: Hora (0-23)
        minute: Minuto (0-59)

    Returns:
        String formateado con emoji

    Example:
        >>> format_time_suggestion(5, 0)
        "🌅 05:00 (madrugada)"
    """
    time_str = f"{hour:02d}:{minute:02d}"

    if 5 <= hour < 12:
        emoji = "🌅"
        period = "(mañana)"
    elif 12 <= hour < 17:
        emoji = "☀️"
        period = "(tarde)"
    elif 17 <= hour < 21:
        emoji = "🌆"
        period = "(atardecer)"
    elif 21 <= hour < 24:
        emoji = "🌙"
        period = "(noche)"
    else:  # 0-5
        emoji = "🌃"
        period = "(madrugada)"

    return f"{emoji} {time_str} {period}"


def get_time_validation_tips() -> str:
    """
    Retorna consejos de validación para horas.

    Returns:
        String con tips formateados
    """
    return (
        "⏰ Tips para ingresar la hora:\n"
        "• Usa formato 24h (00:00 a 23:59)\n"
        "• Ejemplo: 05:00 para las 5 am\n"
        "• Ejemplo: 17:30 para las 5:30 pm"
    )


def get_name_validation_tips() -> str:
    """
    Retorna consejos de validación para nombres.

    Returns:
        String con tips formateados
    """
    return (
        "👤 Tips para ingresar el nombre:\n"
        "• Mínimo 2 caracteres\n"
        "• Máximo 100 caracteres\n"
        "• Usa solo letras, espacios y guiones\n"
        "• Ejemplo: Juan Pérez"
    )
