"""
Tests unitarios para el módulo conversation_state.
"""
import pytest

from src.utils.conversation_state import (
    RegistrationState,
    TrainingState,
    EditTrainingState,
    ConversationState,
    load_state_from_context,
    save_state_to_context,
    clear_state
)


class TestRegistrationState:
    """Tests para la clase RegistrationState."""

    def test_crear_estado_inicial(self):
        """Debe crear un estado inicial vacío."""
        state = RegistrationState(user_id=123)

        assert state.user_id == 123
        assert state.student_name is None
        assert not state.is_complete()

    def test_establecer_nombre(self):
        """Debe establecer el nombre del alumno."""
        state = RegistrationState(user_id=123)
        state.set_student_name("Juan Pérez")

        assert state.get_student_name() == "Juan Pérez"
        assert state.is_complete()

    def test_establecer_nombre_con_espacios(self):
        """Debe limpiar espacios al establecer nombre."""
        state = RegistrationState(user_id=123)
        state.set_student_name("  Juan Pérez  ")

        assert state.get_student_name() == "Juan Pérez"

    def test_establecer_nombre_vacío(self):
        """Debe manejar nombre vacío."""
        state = RegistrationState(user_id=123)
        state.set_student_name("")

        assert state.get_student_name() is None
        assert not state.is_complete()

    def test_convertir_a_dict(self):
        """Debe convertir el estado a dict."""
        state = RegistrationState(user_id=123)
        state.set_student_name("Juan Pérez")

        data = state.to_dict()

        assert data["user_id"] == 123
        assert data["student_name"] == "Juan Pérez"

    def test_crear_desde_dict(self):
        """Debe crear un estado desde un dict."""
        data = {"user_id": 123, "student_name": "Juan Pérez"}
        state = RegistrationState.from_dict(data)

        assert state.user_id == 123
        assert state.student_name == "Juan Pérez"
        assert state.is_complete()


class TestTrainingState:
    """Tests para la clase TrainingState."""

    def test_crear_estado_inicial(self):
        """Debe crear un estado inicial vacío."""
        state = TrainingState(user_id=123)

        assert state.user_id == 123
        assert state.student_id is None
        assert state.day_of_week is None
        assert not state.is_complete()

    def test_establecer_alumno(self):
        """Debe establecer el alumno seleccionado."""
        state = TrainingState(user_id=123)
        state.set_student(1, "Juan Pérez")

        assert state.student_id == 1
        assert state.student_name == "Juan Pérez"

    def test_establecer_día(self):
        """Debe establecer el día de la semana."""
        state = TrainingState(user_id=123)
        state.set_day(0, "Lunes")

        assert state.day_of_week == 0
        assert state.day_name == "Lunes"

    def test_establecer_tipo_sesión(self):
        """Debe establecer el tipo de sesión."""
        state = TrainingState(user_id=123)
        state.set_session_type("Funcional")

        assert state.session_type == "Funcional"

    def test_establecer_hora(self):
        """Debe establecer la hora."""
        state = TrainingState(user_id=123)
        state.set_time("05:00")

        assert state.time_str == "05:00"

    def test_detalles_confirmación(self):
        """Debe retornar detalles formateados para confirmación."""
        state = TrainingState(user_id=123)
        state.set_student(1, "Juan Pérez")
        state.set_day(0, "Lunes")
        state.set_session_type("Funcional")
        state.set_time("05:00")

        details = state.get_confirmation_details()

        assert details["student"] == "Juan Pérez"
        assert details["day"] == "Lunes"
        assert details["type"] == "Funcional"
        assert details["time"] == "05:00"

    def test_está_completo(self):
        """Debe verificar si el estado está completo."""
        state = TrainingState(user_id=123)

        assert not state.is_complete()

        state.set_student(1, "Juan")
        assert not state.is_complete()

        state.set_day(0, "Lunes")
        assert not state.is_complete()

        state.set_session_type("Funcional")
        assert not state.is_complete()

        state.set_time("05:00")
        assert state.is_complete()

    def test_resetear_estado(self):
        """Debe resetear el estado manteniendo user_id."""
        state = TrainingState(user_id=123)
        state.set_student(1, "Juan")
        state.set_day(0, "Lunes")

        state.reset()

        assert state.user_id == 123
        assert state.student_id is None
        assert state.day_of_week is None
        assert not state.is_complete()

    def test_convertir_a_dict_y_desde_dict(self):
        """Debe convertir a dict y recrear desde dict."""
        state_original = TrainingState(user_id=123)
        state_original.set_student(1, "Juan Pérez")
        state_original.set_day(2, "Miércoles")
        state_original.set_session_type("Pesas")
        state_original.set_time("19:00")

        data = state_original.to_dict()
        state_recreado = TrainingState.from_dict(data)

        assert state_recreado.user_id == state_original.user_id
        assert state_recreado.student_id == state_original.student_id
        assert state_recreado.day_of_week == state_original.day_of_week
        assert state_recreado.session_type == state_original.session_type
        assert state_recreado.time_str == state_original.time_str


class TestEditTrainingState:
    """Tests para la clase EditTrainingState."""

    def test_crear_estado_inicial(self):
        """Debe crear un estado inicial."""
        state = EditTrainingState(user_id=123, training_id=456)

        assert state.user_id == 123
        assert state.training_id == 456
        assert state.edit_field is None

    def test_establecer_campo_edición(self):
        """Debe establecer el campo siendo editado."""
        state = EditTrainingState(user_id=123, training_id=456)
        state.set_edit_field("day")

        assert state.get_edit_field() == "day"

    def test_establecer_campo_edición_normaliza(self):
        """Debe normalizar el nombre del campo."""
        state = EditTrainingState(user_id=123, training_id=456)
        state.set_edit_field("  DAY  ")

        assert state.get_edit_field() == "day"

    def test_está_completo_día(self):
        """Debe verificar si está completo para editar día."""
        state = EditTrainingState(user_id=123, training_id=456)
        state.set_edit_field("day")

        assert not state.is_complete()

        state.set_day(0, "Lunes")
        assert state.is_complete()

    def test_está_completo_hora(self):
        """Debe verificar si está completo para editar hora."""
        state = EditTrainingState(user_id=123, training_id=456)
        state.set_edit_field("time")

        assert not state.is_complete()

        state.set_time("05:00")
        assert state.is_complete()

    def test_está_completo_tipo(self):
        """Debe verificar si está completo para editar tipo."""
        state = EditTrainingState(user_id=123, training_id=456)
        state.set_edit_field("type")

        assert not state.is_complete()

        state.set_session_type("Funcional")
        assert state.is_complete()

    def test_resetear_estado(self):
        """Debe resetear el estado manteniendo user_id y training_id."""
        state = EditTrainingState(user_id=123, training_id=456)
        state.set_day(0, "Lunes")
        state.set_edit_field("day")

        state.reset()

        assert state.user_id == 123
        assert state.training_id == 456
        assert state.day_of_week is None
        assert state.edit_field is None


class TestConversationStateConstants:
    """Tests para las constantes de ConversationState."""

    def test_constantes_existen(self):
        """Deben existir todas las constantes de estado."""
        assert hasattr(ConversationState, "REGISTRATION_ENTERING_NAME")
        assert hasattr(ConversationState, "TRAINING_SELECTING_STUDENT")
        assert hasattr(ConversationState, "EDIT_SELECTING_TRAINING")
        assert hasattr(ConversationState, "END")

    def test_constantes_son_strings(self):
        """Deben ser strings las constantes."""
        assert isinstance(ConversationState.REGISTRATION_ENTERING_NAME, str)
        assert isinstance(ConversationState.TRAINING_SELECTING_STUDENT, str)


class TestContextStateManagement:
    """Tests para funciones de gestión de estado en context."""

    def test_guardar_y_cargar_estado(self):
        """Debe guardar y cargar un estado correctamente."""
        context_data = {}
        state = TrainingState(user_id=123)
        state.set_student(1, "Juan Pérez")

        save_state_to_context(context_data, "training", state)
        loaded_state = load_state_from_context(context_data, "training", TrainingState)

        assert loaded_state.user_id == 123
        assert loaded_state.student_id == 1
        assert loaded_state.student_name == "Juan Pérez"

    def test_cargar_estado_inexistente(self):
        """Debe retornar None al cargar estado inexistente."""
        context_data = {}
        loaded_state = load_state_from_context(context_data, "nonexistent", TrainingState)

        assert loaded_state is None

    def test_guardar_estado_none(self):
        """Debe eliminar el estado al guardar None."""
        context_data = {"training": {"user_id": 123}}
        save_state_to_context(context_data, "training", None)

        assert "training" not in context_data

    def test_limpiar_estado(self):
        """Debe limpiar un estado del context."""
        context_data = {"training": {"user_id": 123}}
        clear_state(context_data, "training")

        assert "training" not in context_data

    def test_limpiar_estado_inexistente(self):
        """Debe manejar limpieza de estado inexistente sin errores."""
        context_data = {}
        clear_state(context_data, "nonexistent")  # No debe lanzar error

        assert len(context_data) == 0
