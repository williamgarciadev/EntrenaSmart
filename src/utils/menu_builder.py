"""
Módulo de Construcción de Menús Interactivos
==============================================

Construye menús dinámicos con InlineKeyboardMarkup para Telegram.

Ejemplo:
    >>> from src.utils.menu_builder import build_student_menu
    >>> students = [Student(...), Student(...), ...]
    >>> keyboard, pagination = build_student_menu(students, page=0)
    >>> # keyboard es un InlineKeyboardMarkup listo para usar
    >>> # pagination es {"current": 0, "total": 1, "has_prev": False, "has_next": False}
"""
from typing import List, Tuple, Dict, Any, Optional, Callable
from dataclasses import dataclass

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.core.constants import (
    SESSION_TYPES,
    WEEKDAY_NAMES,
    WEEKDAY_NAME_TO_NUMBER
)


@dataclass
class PaginationInfo:
    """Información de paginación para menús grandes."""
    current_page: int
    total_pages: int
    has_previous: bool
    has_next: bool
    total_items: int


def paginate_items(
    items: List[Any],
    page: int = 0,
    per_page: int = 5
) -> Tuple[List[Any], PaginationInfo]:
    """
    Pagina una lista de items.

    Args:
        items: Lista de items a paginar
        page: Número de página (0-indexed)
        per_page: Items por página (default: 5)

    Returns:
        Tuple con items de la página y información de paginación

    Example:
        >>> items = list(range(12))
        >>> page_items, pagination = paginate_items(items, page=0, per_page=5)
        >>> page_items
        [0, 1, 2, 3, 4]
        >>> pagination.total_pages
        3
        >>> pagination.has_next
        True
    """
    total = len(items)
    total_pages = (total + per_page - 1) // per_page  # Redondear hacia arriba

    # Validar página
    if page >= total_pages and total_pages > 0:
        page = total_pages - 1
    if page < 0:
        page = 0

    # Extraer items de la página
    start = page * per_page
    end = min(start + per_page, total)
    page_items = items[start:end]

    # Crear info de paginación
    pagination = PaginationInfo(
        current_page=page,
        total_pages=total_pages,
        has_previous=page > 0,
        has_next=(page + 1) < total_pages,
        total_items=total
    )

    return page_items, pagination


def build_student_menu(
    students: List,
    page: int = 0,
    per_page: int = 5
) -> Tuple[InlineKeyboardMarkup, PaginationInfo]:
    """
    Construye menú de selección de alumnos.

    Crea un menú con botones para cada alumno, con paginación si hay >per_page.

    Args:
        students: Lista de objetos Student
        page: Página a mostrar (default: 0)
        per_page: Alumnos por página (default: 5)

    Returns:
        Tuple con (InlineKeyboardMarkup, PaginationInfo)

    Example:
        >>> from src.models.student import Student
        >>> students = [
        ...     Student(id=1, name="Juan Pérez", chat_id=123),
        ...     Student(id=2, name="Pedro García", chat_id=456),
        ...     Student(id=3, name="María López", chat_id=789)
        ... ]
        >>> keyboard, pagination = build_student_menu(students)
        >>> pagination.total_pages
        1
        >>> len(keyboard.inline_keyboard)  # 3 botones + sin paginación = 3 filas
        3
    """
    if not students:
        # Retornar menú vacío si no hay estudiantes
        buttons = [[InlineKeyboardButton("❌ No hay alumnos", callback_data="no_students")]]
        return InlineKeyboardMarkup(buttons), PaginationInfo(0, 0, False, False, 0)

    # Paginar estudiantes
    page_students, pagination = paginate_items(students, page, per_page)

    # Crear botones para cada alumno
    buttons = []
    for student in page_students:
        button = InlineKeyboardButton(
            text=f"👤 {student.name}",
            callback_data=f"student_{student.id}"
        )
        buttons.append([button])

    # Agregar botones de paginación si es necesario
    if pagination.total_pages > 1:
        pagination_buttons = []

        if pagination.has_previous:
            pagination_buttons.append(
                InlineKeyboardButton("⬅️ Anterior", callback_data=f"page_students_{page - 1}")
            )

        pagination_buttons.append(
            InlineKeyboardButton(
                f"{page + 1}/{pagination.total_pages}",
                callback_data="pagination_info"
            )
        )

        if pagination.has_next:
            pagination_buttons.append(
                InlineKeyboardButton("Siguiente ➡️", callback_data=f"page_students_{page + 1}")
            )

        buttons.append(pagination_buttons)

    return InlineKeyboardMarkup(buttons), pagination


def build_day_menu(exclude_days: List[int] = None) -> InlineKeyboardMarkup:
    """
    Construye menú de selección de días de la semana.

    Retorna un menú con todos los días de semana, opcionalmente excluyendo algunos.

    Args:
        exclude_days: Lista de índices de días a excluir (0=Lunes, 6=Domingo)

    Returns:
        InlineKeyboardMarkup con opciones de días

    Example:
        >>> keyboard = build_day_menu()
        >>> len(keyboard.inline_keyboard)  # 7 botones organizados
        4  # 2 filas de 2, 1 fila de 3
        >>> keyboard = build_day_menu(exclude_days=[0, 2])  # Excluir Lunes y Miércoles
    """
    if exclude_days is None:
        exclude_days = []

    buttons = []
    days_row = []

    # WEEKDAY_NAMES es {0: "Lunes", 1: "Martes", ...}
    for day_index in sorted(WEEKDAY_NAMES.keys()):
        # Saltar días excluidos
        if day_index in exclude_days:
            continue

        day_name = WEEKDAY_NAMES[day_index]
        emoji = "🏋️" if day_name.lower() in ["viernes", "sábado"] else "📅"

        button = InlineKeyboardButton(
            text=f"{emoji} {day_name}",
            callback_data=f"day_{day_index}"
        )
        days_row.append(button)

        # Agrupar en filas de 3 botones
        if len(days_row) == 3:
            buttons.append(days_row)
            days_row = []

    # Agregar últimos botones si quedan
    if days_row:
        buttons.append(days_row)

    return InlineKeyboardMarkup(buttons)


def build_session_type_menu() -> InlineKeyboardMarkup:
    """
    Construye menú de selección de tipos de sesión.

    Retorna un menú con todos los tipos de sesión disponibles.

    Returns:
        InlineKeyboardMarkup con opciones de tipos de sesión

    Example:
        >>> keyboard = build_session_type_menu()
        >>> len(keyboard.inline_keyboard)  # Depende de SESSION_TYPES
        3  # Una fila por cada tipo
    """
    buttons = []

    for session_type in SESSION_TYPES:
        emoji_map = {
            "Funcional": "💪",
            "Técnica": "⚙️",
            "Pesas": "🏋️",
            "Cardio": "🏃",
            "Flexibilidad": "🧘",
            "Otro": "❓"
        }

        emoji = emoji_map.get(session_type, "✨")

        button = InlineKeyboardButton(
            text=f"{emoji} {session_type}",
            callback_data=f"session_type_{session_type.lower()}"
        )
        buttons.append([button])

    return InlineKeyboardMarkup(buttons)


def build_confirmation_menu(details: Dict[str, Any]) -> InlineKeyboardMarkup:
    """
    Construye menú de confirmación con opciones Confirmar/Cancelar.

    Args:
        details: Dict con detalles a confirmar (no se usa en el botón, solo informativo)

    Returns:
        InlineKeyboardMarkup con botones Confirmar y Cancelar

    Example:
        >>> details = {"student": "Juan", "day": "Lunes", "time": "05:00"}
        >>> keyboard = build_confirmation_menu(details)
        >>> len(keyboard.inline_keyboard)  # 1 fila con 2 botones
        1
    """
    buttons = [
        [
            InlineKeyboardButton("✅ Confirmar", callback_data="confirm_action"),
            InlineKeyboardButton("❌ Cancelar", callback_data="cancel_action")
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def build_search_results_menu(
    items: List[Any],
    item_formatter: Callable[[Any, int], str],
    callback_prefix: str,
    page: int = 0,
    per_page: int = 5
) -> Tuple[str, InlineKeyboardMarkup, PaginationInfo]:
    """
    Construye un menú con resultados de búsqueda paginados.

    Útil para mostrar resultados de búsqueda fuzzy con paginación.

    Args:
        items: Lista de items a mostrar
        item_formatter: Función que formatea cada item (recibe item e índice, retorna string)
        callback_prefix: Prefijo para el callback (ej: "student" → "student_<id>")
        page: Número de página (0-indexed)
        per_page: Items por página

    Returns:
        Tuple con (texto del mensaje, keyboard, pagination info)

    Example:
        >>> students = [Student(...), Student(...), ...]
        >>> text, keyboard, pagination = build_search_results_menu(
        ...     students,
        ...     lambda s, i: f"{i+1}. {s.name}",
        ...     "student"
        ... )
    """
    # Paginar items
    page_items, pagination = paginate_items(items, page, per_page)

    # Formatear texto
    lines = []
    for i, item in enumerate(page_items):
        # Calcular índice real (no relativo a la página)
        real_idx = page * per_page + i
        text = item_formatter(item, real_idx)
        lines.append(text)

    # Agregar info de paginación si hay varias páginas
    if pagination.total_pages > 1:
        lines.append(f"\n📄 Página {pagination.current_page + 1}/{pagination.total_pages}")

    message_text = "\n".join(lines)

    # Construir botones
    buttons = []
    for i, item in enumerate(page_items):
        real_idx = page * per_page + i
        # Asumir que item tiene un atributo id
        item_id = getattr(item, 'id', real_idx)
        button = InlineKeyboardButton(
            text=f"👤 {getattr(item, 'name', str(item))}",
            callback_data=f"{callback_prefix}_{item_id}"
        )
        buttons.append([button])

    # Agregar botones de paginación si es necesario
    if pagination.total_pages > 1:
        pagination_buttons = []

        if pagination.has_previous:
            pagination_buttons.append(
                InlineKeyboardButton("⬅️ Anterior", callback_data=f"page_{callback_prefix}_{page - 1}")
            )

        pagination_buttons.append(
            InlineKeyboardButton(
                f"{page + 1}/{pagination.total_pages}",
                callback_data="pagination_info"
            )
        )

        if pagination.has_next:
            pagination_buttons.append(
                InlineKeyboardButton("Siguiente ➡️", callback_data=f"page_{callback_prefix}_{page + 1}")
            )

        buttons.append(pagination_buttons)

    return message_text, InlineKeyboardMarkup(buttons), pagination


def build_edit_session_menu(trainings: List) -> InlineKeyboardMarkup:
    """
    Construye menú para editar sesión existente.

    Muestra lista de entrenamientos configurados para seleccionar cuál editar.

    Args:
        trainings: Lista de objetos Training

    Returns:
        InlineKeyboardMarkup con opciones de entrenamientos a editar

    Example:
        >>> from src.models.training import Training
        >>> trainings = [Training(...), Training(...)]
        >>> keyboard = build_edit_session_menu(trainings)
    """
    if not trainings:
        buttons = [[InlineKeyboardButton("❌ No hay sesiones", callback_data="no_trainings")]]
        return InlineKeyboardMarkup(buttons)

    buttons = []
    for training in trainings:
        # Mostrar: Día - Hora - Tipo
        text = f"📋 {training.weekday_name} {training.time_str} ({training.session_type})"
        button = InlineKeyboardButton(
            text=text,
            callback_data=f"edit_training_{training.id}"
        )
        buttons.append([button])

    return InlineKeyboardMarkup(buttons)


def build_edit_options_menu() -> InlineKeyboardMarkup:
    """
    Construye menú de opciones para editar una sesión.

    Permite elegir qué aspecto editar (día, hora, tipo, o eliminar).

    Returns:
        InlineKeyboardMarkup con opciones de edición

    Example:
        >>> keyboard = build_edit_options_menu()
        >>> len(keyboard.inline_keyboard)  # 4 opciones
        4
    """
    buttons = [
        [InlineKeyboardButton("📅 Cambiar Día", callback_data="edit_day")],
        [InlineKeyboardButton("⏰ Cambiar Hora", callback_data="edit_time")],
        [InlineKeyboardButton("💪 Cambiar Tipo", callback_data="edit_type")],
        [InlineKeyboardButton("🗑️ Eliminar Sesión", callback_data="delete_training")]
    ]

    return InlineKeyboardMarkup(buttons)


def build_yesno_menu(
    affirmative_text: str = "✅ Sí",
    negative_text: str = "❌ No",
    affirmative_callback: str = "yes",
    negative_callback: str = "no"
) -> InlineKeyboardMarkup:
    """
    Construye menú simple Sí/No.

    Útil para confirmaciones simples.

    Args:
        affirmative_text: Texto del botón afirmativo
        negative_text: Texto del botón negativo
        affirmative_callback: Callback para botón afirmativo
        negative_callback: Callback para botón negativo

    Returns:
        InlineKeyboardMarkup con opciones Sí/No

    Example:
        >>> keyboard = build_yesno_menu(
        ...     affirmative_text="✅ Eliminar",
        ...     negative_text="❌ Cancelar",
        ...     affirmative_callback="confirm_delete",
        ...     negative_callback="cancel_delete"
        ... )
    """
    buttons = [
        [
            InlineKeyboardButton(affirmative_text, callback_data=affirmative_callback),
            InlineKeyboardButton(negative_text, callback_data=negative_callback)
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def build_cancel_menu(callback_data: str = "cancel") -> InlineKeyboardMarkup:
    """
    Construye menú con un solo botón de cancelación.

    Args:
        callback_data: Callback a ejecutar al presionar cancelar

    Returns:
        InlineKeyboardMarkup con botón de cancelación

    Example:
        >>> keyboard = build_cancel_menu("cancel_registration")
    """
    buttons = [[InlineKeyboardButton("❌ Cancelar", callback_data=callback_data)]]
    return InlineKeyboardMarkup(buttons)


def build_trainer_commands_menu() -> InlineKeyboardMarkup:
    """
    Construye menú de comandos disponibles para el entrenador.

    Retorna un menú con los principales comandos que puede ejecutar.

    Returns:
        InlineKeyboardMarkup con botones de comandos

    Example:
        >>> keyboard = build_trainer_commands_menu()
        >>> len(keyboard.inline_keyboard)  # Múltiples filas de comandos
    """
    buttons = [
        [InlineKeyboardButton("👤 Registrar Alumno", callback_data="cmd_registrarme")],
        [InlineKeyboardButton("⏱️ Configurar Entrenamiento", callback_data="cmd_set")],
        [InlineKeyboardButton("📋 Listar Alumnos", callback_data="cmd_listar_alumnos")],
        [InlineKeyboardButton("📊 Generar Reporte", callback_data="cmd_reporte")],
        [InlineKeyboardButton("📖 Ayuda", callback_data="cmd_help")]
    ]

    return InlineKeyboardMarkup(buttons)


def build_student_commands_menu() -> InlineKeyboardMarkup:
    """
    Construye menú de comandos disponibles para alumnos.

    Retorna un menú con los comandos que puede ejecutar un alumno.

    Returns:
        InlineKeyboardMarkup con botones de comandos

    Example:
        >>> keyboard = build_student_commands_menu()
        >>> len(keyboard.inline_keyboard)  # 2 comandos principales
    """
    buttons = [
        [InlineKeyboardButton("📅 Mis Sesiones", callback_data="cmd_mis_sesiones")],
        [InlineKeyboardButton("📖 Ayuda", callback_data="cmd_help")]
    ]

    return InlineKeyboardMarkup(buttons)
