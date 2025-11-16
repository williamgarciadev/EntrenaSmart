"""
Excepciones personalizadas de EntrenaSmart
===========================================

Este módulo define las excepciones personalizadas del proyecto,
organizadas por categoría para un manejo de errores más específico.
"""


# ====================================
# Excepciones Base
# ====================================

class EntrenaSmarBaseError(Exception):
    """Excepción base para todas las excepciones de EntrenaSmart."""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


# ====================================
# Excepciones de Configuración
# ====================================

class ConfigurationError(EntrenaSmarBaseError):
    """Error en la configuración de la aplicación."""
    pass


class InvalidTimezoneError(ConfigurationError):
    """Zona horaria inválida."""
    pass


# ====================================
# Excepciones de Base de Datos
# ====================================

class DatabaseError(EntrenaSmarBaseError):
    """Error general de base de datos."""
    pass


class RecordNotFoundError(DatabaseError):
    """Registro no encontrado en la base de datos."""

    def __init__(self, model: str, identifier: any):
        message = f"{model} con identificador '{identifier}' no encontrado"
        super().__init__(message, {"model": model, "identifier": identifier})


class DuplicateRecordError(DatabaseError):
    """Intento de crear un registro duplicado."""

    def __init__(self, model: str, field: str, value: any):
        message = f"{model} con {field}='{value}' ya existe"
        super().__init__(message, {"model": model, "field": field, "value": value})


# ====================================
# Excepciones de Validación
# ====================================

class ValidationError(EntrenaSmarBaseError):
    """Error de validación de datos."""
    pass


class InvalidWeekdayError(ValidationError):
    """Día de la semana inválido."""

    def __init__(self, weekday: int):
        message = f"Día de la semana inválido: {weekday}. Debe estar entre 0 (Lunes) y 6 (Domingo)"
        super().__init__(message, {"weekday": weekday})


class InvalidTimeFormatError(ValidationError):
    """Formato de hora inválido."""

    def __init__(self, time_str: str):
        message = f"Formato de hora inválido: '{time_str}'. Debe ser HH:MM en formato 24h"
        super().__init__(message, {"time_str": time_str})


class InvalidIntensityError(ValidationError):
    """Intensidad de entrenamiento inválida."""

    def __init__(self, intensity: int):
        message = f"Intensidad inválida: {intensity}. Debe estar entre 1 (Suave) y 4 (Muy intenso)"
        super().__init__(message, {"intensity": intensity})


# ====================================
# Excepciones de Negocio
# ====================================

class BusinessLogicError(EntrenaSmarBaseError):
    """Error de lógica de negocio."""
    pass


class StudentNotActiveError(BusinessLogicError):
    """El alumno no está activo."""

    def __init__(self, student_id: int):
        message = f"El alumno con ID {student_id} no está activo"
        super().__init__(message, {"student_id": student_id})


class TrainingNotActiveError(BusinessLogicError):
    """El entrenamiento no está activo."""

    def __init__(self, training_id: int):
        message = f"El entrenamiento con ID {training_id} no está activo"
        super().__init__(message, {"training_id": training_id})


class DuplicateTrainingError(BusinessLogicError):
    """Intento de crear un entrenamiento duplicado para el mismo día y hora."""

    def __init__(self, student_id: int, weekday: int, time: str):
        message = (
            f"Ya existe un entrenamiento para el alumno {student_id} "
            f"el día {weekday} a las {time}"
        )
        super().__init__(
            message,
            {"student_id": student_id, "weekday": weekday, "time": time}
        )


# ====================================
# Excepciones de Telegram
# ====================================

class TelegramError(EntrenaSmarBaseError):
    """Error relacionado con Telegram."""
    pass


class UnauthorizedUserError(TelegramError):
    """Usuario no autorizado para ejecutar la acción."""

    def __init__(self, user_id: int):
        message = f"Usuario con ID {user_id} no autorizado para esta acción"
        super().__init__(message, {"user_id": user_id})


class InvalidCommandFormatError(TelegramError):
    """Formato de comando inválido."""

    def __init__(self, command: str, expected_format: str):
        message = f"Formato de comando inválido. Esperado: {expected_format}"
        super().__init__(
            message,
            {"command": command, "expected_format": expected_format}
        )


# ====================================
# Excepciones de Scheduler
# ====================================

class SchedulerError(EntrenaSmarBaseError):
    """Error del sistema de tareas programadas."""
    pass


class JobNotFoundError(SchedulerError):
    """Tarea programada no encontrada."""

    def __init__(self, job_id: str):
        message = f"Tarea programada con ID '{job_id}' no encontrada"
        super().__init__(message, {"job_id": job_id})


class JobAlreadyExistsError(SchedulerError):
    """La tarea programada ya existe."""

    def __init__(self, job_id: str):
        message = f"Tarea programada con ID '{job_id}' ya existe"
        super().__init__(message, {"job_id": job_id})


# ====================================
# Excepciones de Configuración de Entrenamientos
# ====================================

class LocationValidationError(ValidationError):
    """Ubicación de entrenamiento inválida."""

    def __init__(self, message: str):
        super().__init__(message)


class ConfigTrainingError(EntrenaSmarBaseError):
    """Error genérico en configuración de entrenamientos semanales."""

    def __init__(self, message: str, user_message: str = None):
        """
        Inicializa excepción de configuración.

        Args:
            message: Mensaje de log interno
            user_message: Mensaje para mostrar al usuario (opcional)
        """
        self.message = message
        self.user_message = user_message or message
        super().__init__(message)


class StateNotFoundError(ConfigTrainingError):
    """Estado conversacional no encontrado o fue perdido."""

    def __init__(self):
        message = "Estado de configuración no encontrado"
        user_message = "La sesión se interrumpió. Por favor, comienza de nuevo con /config_semana"
        super().__init__(message, user_message)


class WeeklyConfigurationError(ConfigTrainingError):
    """Error al guardar o recuperar configuración semanal."""

    def __init__(self, message: str, user_message: str = None):
        if not user_message:
            user_message = "Error al procesar la configuración. Intenta de nuevo."
        super().__init__(message, user_message)

