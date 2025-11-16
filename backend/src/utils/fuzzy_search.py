"""
Módulo de Búsqueda Fuzzy (Búsqueda Inteligente)
================================================

Implementa búsqueda tolerante a errores tipográficos
usando difflib de la librería estándar de Python.

Ejemplo:
    >>> students = [Student(name="Juan Pérez"), Student(name="Pedro García")]
    >>> search_students("Jua", students)
    [Student(name="Juan Pérez")]
    >>> search_students("Pedr", students)
    [Student(name="Pedro García")]
    >>> search_students("Xyz", students)
    []
"""
from difflib import get_close_matches
from typing import List, TypeVar, Callable

# TypeVar para búsqueda genérica
T = TypeVar('T')


def search_by_field(
    query: str,
    items: List[T],
    field_getter: Callable[[T], str],
    max_results: int = 3,
    cutoff: float = 0.6
) -> List[T]:
    """
    Búsqueda fuzzy genérica en una lista de objetos.

    Encuentra elementos cuyo campo coincida aproximadamente con la consulta,
    incluso si hay errores tipográficos.

    Args:
        query: Texto a buscar (ej: "Jua")
        items: Lista de objetos a buscar
        field_getter: Función que extrae el campo a buscar (ej: lambda s: s.name)
        max_results: Número máximo de resultados (default: 3)
        cutoff: Umbral de similitud 0.0-1.0 (default: 0.6 = 60%)

    Returns:
        List[T]: Objetos que coinciden ordenados por similitud

    Example:
        >>> from src.models.student import Student
        >>> students = [
        ...     Student(name="Juan Pérez", chat_id=1),
        ...     Student(name="Pedro García", chat_id=2),
        ...     Student(name="Juanita López", chat_id=3)
        ... ]
        >>> results = search_by_field("Juan", students, lambda s: s.name)
        >>> len(results)
        2  # Juan Pérez y Juanita López
    """
    if not query.strip():
        return []

    # Normalizar consulta
    query_normalized = query.strip().lower()

    # Extraer campos y mantener mapping
    field_values = [field_getter(item).lower() for item in items]

    # Encontrar coincidencias
    matches = get_close_matches(
        query_normalized,
        field_values,
        n=max_results,
        cutoff=cutoff
    )

    # Retornar objetos correspondientes en orden
    result = []
    for match in matches:
        # Encontrar índice original
        for idx, field_val in enumerate(field_values):
            if field_val == match and items[idx] not in result:
                result.append(items[idx])
                break

    return result


def search_students(
    query: str,
    students: List,
    max_results: int = 5,
    cutoff: float = 0.6
) -> List:
    """
    Búsqueda fuzzy de alumnos por nombre.

    Encuentra alumnos cuyo nombre coincida aproximadamente con la consulta,
    tolerando errores tipográficos comunes.

    Args:
        query: Texto a buscar (ej: "Jua", "pedri", "juan perez")
        students: Lista de objetos Student
        max_results: Número máximo de resultados (default: 5)
        cutoff: Umbral de similitud 0.0-1.0 (default: 0.6)

    Returns:
        List: Lista de Student que coinciden, ordenados por similitud

    Example:
        >>> from src.models.student import Student
        >>> students = [
        ...     Student(name="Juan Pérez", chat_id=123),
        ...     Student(name="Juan López", chat_id=456),
        ...     Student(name="Pedro García", chat_id=789)
        ... ]
        >>> # Búsqueda exacta
        >>> results = search_students("Juan Pérez", students)
        >>> results[0].name
        'Juan Pérez'
        >>> # Búsqueda parcial (tolerante a errores)
        >>> results = search_students("Jua", students)
        >>> len(results)
        2  # Encuentra Juan Pérez y Juan López
        >>> # Búsqueda con typo
        >>> results = search_students("Pedr", students)
        >>> results[0].name
        'Pedro García'
        >>> # Sin resultados
        >>> results = search_students("Xyz", students)
        >>> len(results)
        0
    """
    return search_by_field(
        query=query,
        items=students,
        field_getter=lambda s: s.name,
        max_results=max_results,
        cutoff=cutoff
    )


def search_students_exact(
    query: str,
    students: List
) -> List:
    """
    Búsqueda exacta (case-insensitive) de alumnos.

    Encuentra alumnos cuyo nombre coincida exactamente (pero sin diferenciar mayúsculas).
    Más restrictivo que search_students.

    Args:
        query: Texto a buscar exacto
        students: Lista de objetos Student

    Returns:
        List: Lista de Student que coinciden exactamente

    Example:
        >>> students = [
        ...     Student(name="Juan Pérez", chat_id=123),
        ...     Student(name="juan pérez", chat_id=456),  # Mismo nombre, distinto caso
        ...     Student(name="Juan", chat_id=789)
        ... ]
        >>> results = search_students_exact("juan pérez", students)
        >>> len(results)
        2  # Encuentra ambos registros
        >>> results = search_students_exact("Juan", students)
        >>> len(results)
        1  # Solo el que es exactamente "Juan"
    """
    if not query.strip():
        return []

    query_normalized = query.strip().lower()
    return [s for s in students if s.name.lower() == query_normalized]


def get_search_suggestions(
    query: str,
    students: List,
    max_suggestions: int = 5,
    cutoff: float = 0.5
) -> List[str]:
    """
    Obtiene sugerencias de nombres basadas en búsqueda fuzzy.

    Útil para mostrar sugerencias al usuario cuando no encuentra lo que busca.

    Args:
        query: Texto inicial del usuario
        students: Lista de objetos Student
        max_suggestions: Número de sugerencias (default: 5)
        cutoff: Umbral mínimo de similitud (default: 0.5)

    Returns:
        List[str]: Lista de nombres sugeridos

    Example:
        >>> students = [
        ...     Student(name="Juan Pérez", chat_id=123),
        ...     Student(name="Pedro García", chat_id=456),
        ...     Student(name="Juanita López", chat_id=789)
        ... ]
        >>> suggestions = get_search_suggestions("Jua", students)
        >>> "Juan Pérez" in suggestions
        True
        >>> "Juanita López" in suggestions
        True
    """
    if not query.strip():
        return []

    query_normalized = query.strip().lower()
    names = [s.name for s in students]

    suggestions = get_close_matches(
        query_normalized,
        names,
        n=max_suggestions,
        cutoff=cutoff
    )

    return suggestions
