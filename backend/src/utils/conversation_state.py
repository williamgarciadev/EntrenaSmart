"""
Módulo de Estado de Conversación
=================================

Gestiona el estado temporal durante flujos ConversationHandler.

Los ConversationHandler de python-telegram-bot mantienen el estado
en `context.user_data`. Este módulo proporciona clases para organizar
y acceder ese estado de forma estructurada y type-safe.

Ejemplo:
    >>> from src.utils.conversation_state import RegistrationState
    >>> state = RegistrationState(user_id=123)
    >>> state.set_student_name("Juan Pérez")
    >>> state.get_student_name()
    'Juan Pérez'
    >>> state.to_dict()
    {'user_id': 123, 'student_name': 'Juan Pérez', ...}
"""
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class RegistrationState:
    """
    Estado durante el flujo de registro de alumno.

    Atributos:
        user_id: ID del usuario Telegram
        student_name: Nombre del alumno siendo registrado
    """
    user_id: int
    student_name: Optional[str] = None

    def set_student_name(self, name: str) -> None:
        """Establece el nombre del alumno."""
        self.student_name = name.strip() if name else None

    def get_student_name(self) -> Optional[str]:
        """Obtiene el nombre del alumno."""
        return self.student_name

    def is_complete(self) -> bool:
        """Verifica si el estado tiene datos suficientes para completar el registro."""
        return bool(self.student_name)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el estado a dict para almacenamiento."""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "RegistrationState":
        """Crea un estado desde un dict."""
        return RegistrationState(**data)


@dataclass
class TrainingState:
    """
    Estado durante el flujo de configuración de entrenamiento.

    Atributos:
        user_id: ID del usuario Telegram
        student_id: ID del alumno seleccionado
        student_name: Nombre del alumno (para mostrar)
        day_of_week: Día de la semana (0-6, lunes-domingo)
        day_name: Nombre del día en español
        session_type: Tipo de sesión (ej: "Funcional")
        time_str: Hora en formato "HH:MM"
    """
    user_id: int
    student_id: Optional[int] = None
    student_name: Optional[str] = None
    day_of_week: Optional[int] = None
    day_name: Optional[str] = None
    session_type: Optional[str] = None
    time_str: Optional[str] = None
    page: int = 0  # Para paginación de menú

    def set_student(self, student_id: int, student_name: str) -> None:
        """Establece el alumno seleccionado."""
        self.student_id = student_id
        self.student_name = student_name

    def set_day(self, day_of_week: int, day_name: str) -> None:
        """Establece el día de la semana."""
        self.day_of_week = day_of_week
        self.day_name = day_name

    def set_session_type(self, session_type: str) -> None:
        """Establece el tipo de sesión."""
        self.session_type = session_type.strip() if session_type else None

    def set_time(self, time_str: str) -> None:
        """Establece la hora."""
        self.time_str = time_str.strip() if time_str else None

    def get_confirmation_details(self) -> Dict[str, Any]:
        """Obtiene detalles para mostrar en confirmación."""
        return {
            "student": self.student_name,
            "day": self.day_name,
            "type": self.session_type,
            "time": self.time_str
        }

    def is_complete(self) -> bool:
        """Verifica si el estado tiene datos suficientes para crear el entrenamiento."""
        return all([
            self.student_id,
            self.day_of_week is not None,
            self.session_type,
            self.time_str
        ])

    def reset(self) -> None:
        """Resetea el estado (mantiene solo user_id y página)."""
        self.student_id = None
        self.student_name = None
        self.day_of_week = None
        self.day_name = None
        self.session_type = None
        self.time_str = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el estado a dict para almacenamiento."""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "TrainingState":
        """Crea un estado desde un dict."""
        return TrainingState(**data)


@dataclass
class ConfigTrainingState:
    """
    Estado durante el flujo de configuración semanal (/config_semana).

    Mantiene la información de un entrenamiento siendo configurado
    para un día específico de la semana.

    Atributos:
        weekday: Número de día (0=Lunes, 6=Domingo)
        weekday_name: Nombre del día en español ("Lunes", etc.)
        session_type: Tipo de entrenamiento ("Pierna", "Funcional", etc.)
        location: Ubicación/piso ("2do Piso", "3er Piso - Zona Pierna", etc.)
    """
    weekday: int
    weekday_name: str
    session_type: str
    location: str

    def is_complete(self) -> bool:
        """Verifica si el estado tiene todos los datos necesarios."""
        return all([
            isinstance(self.weekday, int) and 0 <= self.weekday <= 6,
            bool(self.weekday_name),
            bool(self.session_type),
            bool(self.location)
        ])

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el estado a dict para almacenamiento."""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ConfigTrainingState":
        """Crea un estado desde un dict."""
        return ConfigTrainingState(**data)


@dataclass
class EditTrainingState:
    """
    Estado durante el flujo de edición de entrenamiento.

    Similar a TrainingState, pero también mantiene referencia al
    entrenamiento siendo editado.

    Atributos:
        user_id: ID del usuario Telegram
        training_id: ID del entrenamiento siendo editado
        ... (igual campos que TrainingState)
    """
    user_id: int
    training_id: int
    student_id: Optional[int] = None
    student_name: Optional[str] = None
    day_of_week: Optional[int] = None
    day_name: Optional[str] = None
    session_type: Optional[str] = None
    time_str: Optional[str] = None
    edit_field: Optional[str] = None  # Campo siendo editado: day, time, type

    def set_student(self, student_id: int, student_name: str) -> None:
        """Establece el alumno seleccionado."""
        self.student_id = student_id
        self.student_name = student_name

    def set_day(self, day_of_week: int, day_name: str) -> None:
        """Establece el día de la semana."""
        self.day_of_week = day_of_week
        self.day_name = day_name

    def set_session_type(self, session_type: str) -> None:
        """Establece el tipo de sesión."""
        self.session_type = session_type.strip() if session_type else None

    def set_time(self, time_str: str) -> None:
        """Establece la hora."""
        self.time_str = time_str.strip() if time_str else None

    def set_edit_field(self, field: str) -> None:
        """Establece cuál campo se está editando."""
        self.edit_field = field.lower().strip() if field else None

    def get_edit_field(self) -> Optional[str]:
        """Obtiene el campo siendo editado."""
        return self.edit_field

    def is_complete(self) -> bool:
        """Verifica si los cambios están listos para guardar."""
        if self.edit_field == "day":
            return self.day_of_week is not None
        elif self.edit_field == "time":
            return bool(self.time_str)
        elif self.edit_field == "type":
            return bool(self.session_type)
        return False

    def reset(self) -> None:
        """Resetea el estado (mantiene user_id y training_id)."""
        self.student_id = None
        self.student_name = None
        self.day_of_week = None
        self.day_name = None
        self.session_type = None
        self.time_str = None
        self.edit_field = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el estado a dict para almacenamiento."""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "EditTrainingState":
        """Crea un estado desde un dict."""
        return EditTrainingState(**data)


# Constantes para los estados de conversación
class ConversationState:
    """Constantes para los estados de ConversationHandler."""

    # Estado para registro de alumno
    REGISTRATION_ENTERING_NAME = "registration_entering_name"
    REGISTRATION_CONFIRMING = "registration_confirming"

    # Estados para configuración de entrenamiento
    TRAINING_SELECTING_STUDENT = "training_selecting_student"
    TRAINING_SELECTING_DAY = "training_selecting_day"
    TRAINING_SELECTING_TYPE = "training_selecting_type"
    TRAINING_ENTERING_TIME = "training_entering_time"
    TRAINING_CONFIRMING = "training_confirming"

    # Estados para edición de entrenamiento
    EDIT_SELECTING_TRAINING = "edit_selecting_training"
    EDIT_SELECTING_FIELD = "edit_selecting_field"
    EDIT_ENTERING_VALUE = "edit_entering_value"
    EDIT_CONFIRMING = "edit_confirming"

    # Estado para cancelación
    END = "end"  # Fin de la conversación


def load_state_from_context(context_user_data: Dict[str, Any], state_key: str, state_class) -> Any:
    """
    Carga un estado desde context.user_data.

    Args:
        context_user_data: context.user_data del CallbackContext
        state_key: Clave del estado en user_data
        state_class: Clase del estado (RegistrationState, TrainingState, etc.)

    Returns:
        Instancia del estado, o None si no existe

    Example:
        >>> state = load_state_from_context(
        ...     context.user_data,
        ...     "training_state",
        ...     TrainingState
        ... )
    """
    data = context_user_data.get(state_key)
    if data is None:
        return None

    if isinstance(data, dict):
        return state_class.from_dict(data)
    elif isinstance(data, state_class):
        return data

    return None


def save_state_to_context(context_user_data: Dict[str, Any], state_key: str, state) -> None:
    """
    Guarda un estado en context.user_data.

    Args:
        context_user_data: context.user_data del CallbackContext
        state_key: Clave donde guardar el estado
        state: Instancia del estado

    Example:
        >>> state = TrainingState(user_id=123)
        >>> save_state_to_context(context.user_data, "training_state", state)
    """
    if state is None:
        context_user_data.pop(state_key, None)
    else:
        context_user_data[state_key] = state.to_dict()


def clear_state(context_user_data: Dict[str, Any], state_key: str) -> None:
    """
    Limpia un estado de context.user_data.

    Args:
        context_user_data: context.user_data del CallbackContext
        state_key: Clave del estado a limpiar

    Example:
        >>> clear_state(context.user_data, "training_state")
    """
    context_user_data.pop(state_key, None)


# Funciones wrapper simplificadas para uso en handlers
def _get_state_key(state_or_class) -> str:
    """Obtiene la clave del estado basado en el nombre de la clase."""
    if hasattr(state_or_class, '__name__'):
        # Es una clase
        class_name = state_or_class.__name__
    else:
        # Es una instancia
        class_name = state_or_class.__class__.__name__

    # Convertir CamelCase a snake_case
    # RegistrationState -> registration_state
    import re
    key = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
    return key


def save_state_to_context_simple(context, state: Any) -> None:
    """
    Guarda un estado en context.user_data (versión simplificada).

    Automáticamente infiere la clave basado en el tipo de estado.

    Args:
        context: CallbackContext
        state: Instancia del estado (RegistrationState, TrainingState, etc.)
    """
    state_key = _get_state_key(state)
    save_state_to_context(context.user_data, state_key, state)


def load_state_from_context_simple(context, state_class):
    """
    Carga un estado desde context.user_data (versión simplificada).

    Automáticamente infiere la clave basado en el tipo de estado.

    Args:
        context: CallbackContext
        state_class: Clase del estado (RegistrationState, TrainingState, etc.)

    Returns:
        Instancia del estado o None
    """
    state_key = _get_state_key(state_class)
    return load_state_from_context(context.user_data, state_key, state_class)


def clear_state_simple(context, state_class) -> None:
    """
    Limpia un estado de context.user_data (versión simplificada).

    Automáticamente infiere la clave basado en el tipo de estado.

    Args:
        context: CallbackContext
        state_class: Clase del estado (RegistrationState, TrainingState, etc.)
    """
    state_key = _get_state_key(state_class)
    clear_state(context.user_data, state_key)
