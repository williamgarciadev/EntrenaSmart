"""
Tests unitarios para el módulo menu_builder.
"""
import pytest
from dataclasses import dataclass

from telegram import InlineKeyboardMarkup

from src.utils.menu_builder import (
    paginate_items,
    build_student_menu,
    build_day_menu,
    build_session_type_menu,
    build_confirmation_menu,
    build_edit_session_menu,
    build_edit_options_menu,
    build_yesno_menu,
    build_cancel_menu,
    PaginationInfo
)


@dataclass
class SimpleStudent:
    """Clase simple para testing."""
    id: int
    name: str


@dataclass
class SimpleTraining:
    """Clase simple para testing."""
    id: int
    weekday_name: str
    time_str: str
    session_type: str


class TestPaginateItems:
    """Tests para la función paginate_items."""

    def test_paginación_sin_exceso(self):
        """Debe manejar listas sin necesidad de paginación."""
        items = [1, 2, 3]
        page_items, pagination = paginate_items(items, page=0, per_page=5)

        assert page_items == [1, 2, 3]
        assert pagination.current_page == 0
        assert pagination.total_pages == 1
        assert not pagination.has_previous
        assert not pagination.has_next

    def test_paginación_múltiples_páginas(self):
        """Debe paginar correctamente con múltiples páginas."""
        items = list(range(12))

        page_0, pag_0 = paginate_items(items, page=0, per_page=5)
        page_1, pag_1 = paginate_items(items, page=1, per_page=5)
        page_2, pag_2 = paginate_items(items, page=2, per_page=5)

        assert page_0 == [0, 1, 2, 3, 4]
        assert page_1 == [5, 6, 7, 8, 9]
        assert page_2 == [10, 11]

        assert pag_0.has_next
        assert pag_1.has_previous and pag_1.has_next
        assert pag_2.has_previous and not pag_2.has_next

    def test_paginación_página_inválida(self):
        """Debe ajustarse a página válida si se proporciona inválida."""
        items = [1, 2, 3]

        page_items, pagination = paginate_items(items, page=10, per_page=5)

        assert page_items == [1, 2, 3]
        assert pagination.current_page == 0  # Se ajusta a la última página válida

    def test_paginación_items_totales(self):
        """Debe reportar el total de items correctamente."""
        items = list(range(25))
        _, pagination = paginate_items(items, page=0, per_page=10)

        assert pagination.total_items == 25
        assert pagination.total_pages == 3


class TestBuildStudentMenu:
    """Tests para build_student_menu."""

    def test_menú_estudiantes_vacío(self):
        """Debe manejar lista vacía de estudiantes."""
        keyboard, pagination = build_student_menu([])

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1  # Un botón "No hay alumnos"
        assert pagination.total_items == 0

    def test_menú_estudiantes_simple(self):
        """Debe construir menú con pocos estudiantes."""
        students = [
            SimpleStudent(id=1, name="Juan Pérez"),
            SimpleStudent(id=2, name="Pedro García")
        ]

        keyboard, pagination = build_student_menu(students)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2  # 2 botones de estudiantes
        assert pagination.total_pages == 1
        assert not pagination.has_next

    def test_menú_estudiantes_con_paginación(self):
        """Debe agregar paginación si hay más de per_page."""
        students = [SimpleStudent(id=i, name=f"Estudiante {i}") for i in range(10)]

        keyboard, pagination = build_student_menu(students, per_page=5)

        # 5 botones de estudiantes + 1 fila de paginación
        assert len(keyboard.inline_keyboard) == 6
        assert pagination.has_next
        assert not pagination.has_previous


class TestBuildDayMenu:
    """Tests para build_day_menu."""

    def test_menú_días_existe(self):
        """Debe crear menú de días."""
        keyboard = build_day_menu()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Debe tener varios botones de días
        total_buttons = sum(len(row) for row in keyboard.inline_keyboard)
        assert total_buttons == 7  # 7 días de la semana


class TestBuildSessionTypeMenu:
    """Tests para build_session_type_menu."""

    def test_menú_tipos_sesión_existe(self):
        """Debe crear menú de tipos de sesión."""
        keyboard = build_session_type_menu()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Debe tener botones para cada tipo de sesión
        assert len(keyboard.inline_keyboard) > 0


class TestBuildConfirmationMenu:
    """Tests para build_confirmation_menu."""

    def test_menú_confirmación_existe(self):
        """Debe crear menú de confirmación."""
        details = {"student": "Juan", "day": "Lunes"}
        keyboard = build_confirmation_menu(details)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1  # Una fila
        assert len(keyboard.inline_keyboard[0]) == 2  # Dos botones (confirmar/cancelar)


class TestBuildEditSessionMenu:
    """Tests para build_edit_session_menu."""

    def test_menú_editar_sesión_vacío(self):
        """Debe manejar lista vacía de entrenamientos."""
        keyboard = build_edit_session_menu([])

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1  # Botón "No hay sesiones"

    def test_menú_editar_sesión_con_datos(self):
        """Debe mostrar entrenamientos disponibles."""
        trainings = [
            SimpleTraining(id=1, weekday_name="Lunes", time_str="05:00", session_type="Funcional"),
            SimpleTraining(id=2, weekday_name="Miércoles", time_str="19:00", session_type="Pesas")
        ]

        keyboard = build_edit_session_menu(trainings)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2  # Un botón por entrenamiento


class TestBuildEditOptionsMenu:
    """Tests para build_edit_options_menu."""

    def test_menú_opciones_edición_existe(self):
        """Debe crear menú de opciones de edición."""
        keyboard = build_edit_options_menu()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 4  # 4 opciones


class TestBuildYesNoMenu:
    """Tests para build_yesno_menu."""

    def test_menú_sí_no_default(self):
        """Debe crear menú Sí/No con defaults."""
        keyboard = build_yesno_menu()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 2

    def test_menú_sí_no_personalizado(self):
        """Debe permitir personalizar textos y callbacks."""
        keyboard = build_yesno_menu(
            affirmative_text="✅ Aceptar",
            negative_text="❌ Rechazar",
            affirmative_callback="accept_action",
            negative_callback="reject_action"
        )

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard[0]) == 2


class TestBuildCancelMenu:
    """Tests para build_cancel_menu."""

    def test_menú_cancelar_default(self):
        """Debe crear menú con botón de cancelación."""
        keyboard = build_cancel_menu()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 1

    def test_menú_cancelar_personalizado(self):
        """Debe permitir personalizar callback."""
        keyboard = build_cancel_menu("custom_cancel")

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard[0]) == 1


class TestMenuIntegration:
    """Tests de integración entre menús."""

    def test_menús_retornan_inlinekeyboard(self):
        """Todos los menús deben retornar InlineKeyboardMarkup."""
        students = [SimpleStudent(id=1, name="Test")]
        trainings = [SimpleTraining(id=1, weekday_name="Lunes", time_str="05:00", session_type="Funcional")]

        assert isinstance(build_day_menu(), InlineKeyboardMarkup)
        assert isinstance(build_session_type_menu(), InlineKeyboardMarkup)
        assert isinstance(build_confirmation_menu({}), InlineKeyboardMarkup)
        assert isinstance(build_edit_session_menu(trainings), InlineKeyboardMarkup)
        assert isinstance(build_edit_options_menu(), InlineKeyboardMarkup)
        assert isinstance(build_yesno_menu(), InlineKeyboardMarkup)
        assert isinstance(build_cancel_menu(), InlineKeyboardMarkup)

        keyboard, _ = build_student_menu(students)
        assert isinstance(keyboard, InlineKeyboardMarkup)
