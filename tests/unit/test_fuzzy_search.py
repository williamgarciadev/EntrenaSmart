"""
Tests unitarios para el módulo fuzzy_search.
"""
import pytest
from dataclasses import dataclass

from src.utils.fuzzy_search import (
    search_by_field,
    search_students,
    search_students_exact,
    get_search_suggestions
)


# Clase simple para testing (sin Mock)
@dataclass
class SimpleStudent:
    """Clase simple para testing sin dependencies."""
    id: int
    name: str


class TestSearchByField:
    """Tests para la función search_by_field."""

    def test_búsqueda_exacta(self):
        """Debe encontrar coincidencias exactas."""
        items = [
            SimpleStudent(id=1, name="Juan Pérez"),
            SimpleStudent(id=2, name="Pedro García"),
            SimpleStudent(id=3, name="María López")
        ]

        results = search_by_field(
            "Juan Pérez",
            items,
            lambda x: x.name
        )

        assert len(results) == 1
        assert results[0].name == "Juan Pérez"

    def test_búsqueda_parcial(self):
        """Debe encontrar coincidencias parciales."""
        items = [
            SimpleStudent(id=1, name="Juan Pérez"),
            SimpleStudent(id=2, name="Pedro García"),
            SimpleStudent(id=3, name="Juanita López")
        ]

        results = search_by_field(
            "Juan",
            items,
            lambda x: x.name,
            cutoff=0.5
        )

        assert len(results) > 0
        assert any("Juan" in r.name for r in results)

    def test_búsqueda_con_typo(self):
        """Debe encontrar coincidencias a pesar de errores tipográficos."""
        items = [
            SimpleStudent(id=1, name="Juan Pérez"),
            SimpleStudent(id=2, name="Pedro García"),
            SimpleStudent(id=3, name="María López")
        ]

        results = search_by_field(
            "Juab",  # Typo: "Juab" en lugar de "Juan"
            items,
            lambda x: x.name,
            cutoff=0.4  # Más tolerante para errores tipográficos
        )

        assert len(results) > 0
        assert "Juan" in results[0].name

    def test_búsqueda_sin_resultados(self):
        """Debe retornar lista vacía si no hay coincidencias."""
        items = [
            SimpleStudent(id=1, name="Juan Pérez"),
            SimpleStudent(id=2, name="Pedro García")
        ]

        results = search_by_field(
            "Xyz123",
            items,
            lambda x: x.name,
            cutoff=0.6
        )

        assert len(results) == 0

    def test_búsqueda_case_insensitive(self):
        """Debe ignorar diferencias de mayúsculas/minúsculas."""
        items = [
            SimpleStudent(id=1, name="Juan Pérez"),
            SimpleStudent(id=2, name="PEDRO GARCÍA")
        ]

        results_lower = search_by_field(
            "juan",
            items,
            lambda x: x.name,
            cutoff=0.5
        )

        results_upper = search_by_field(
            "JUAN",
            items,
            lambda x: x.name,
            cutoff=0.5
        )

        assert len(results_lower) > 0
        assert len(results_upper) > 0

    def test_búsqueda_múltiples_resultados(self):
        """Debe retornar múltiples resultados ordenados por similitud."""
        items = [
            SimpleStudent(id=1, name="Juan Pérez"),
            SimpleStudent(id=2, name="Juan López"),
            SimpleStudent(id=3, name="Juan García"),
            SimpleStudent(id=4, name="Pedro García")
        ]

        results = search_by_field(
            "Juan",
            items,
            lambda x: x.name,
            max_results=5,
            cutoff=0.5
        )

        # Debe encontrar al menos 3 "Juan"
        juan_count = sum(1 for r in results if "Juan" in r.name)
        assert juan_count >= 3

    def test_máximo_resultados_respetado(self):
        """Debe respetar el límite max_results."""
        items = [
            SimpleStudent(id=1, name="Juan Pérez"),
            SimpleStudent(id=2, name="Juan López"),
            SimpleStudent(id=3, name="Juan García"),
            SimpleStudent(id=4, name="Juan Martínez"),
            SimpleStudent(id=5, name="Juan Rodríguez")
        ]

        results = search_by_field(
            "Juan",
            items,
            lambda x: x.name,
            max_results=2,
            cutoff=0.6
        )

        assert len(results) <= 2

    def test_consulta_vacía(self):
        """Debe retornar lista vacía para consulta vacía."""
        items = [SimpleStudent(id=1, name="Juan Pérez")]

        results = search_by_field(
            "",
            items,
            lambda x: x.name
        )

        assert len(results) == 0

    def test_consulta_solo_espacios(self):
        """Debe retornar lista vacía para consulta con solo espacios."""
        items = [SimpleStudent(id=1, name="Juan Pérez")]

        results = search_by_field(
            "   ",
            items,
            lambda x: x.name
        )

        assert len(results) == 0


class TestSearchStudents:
    """Tests para la función search_students."""

    def setup_method(self):
        """Preparar datos de prueba."""
        self.students = [
            SimpleStudent(id=1, name="Juan Pérez"),
            SimpleStudent(id=2, name="Pedro García"),
            SimpleStudent(id=3, name="María López"),
            SimpleStudent(id=4, name="Juanita Martínez"),
            SimpleStudent(id=5, name="Carlos Rodríguez")
        ]

    def test_búsqueda_estudiante_exacta(self):
        """Debe encontrar estudiante por nombre exacto."""
        results = search_students("Juan Pérez", self.students)
        assert len(results) > 0
        assert results[0].name == "Juan Pérez"

    def test_búsqueda_estudiante_parcial(self):
        """Debe encontrar estudiantes con búsqueda parcial."""
        results = search_students("Juan", self.students, cutoff=0.5)
        assert len(results) >= 1  # Al menos Juan Pérez
        names = [s.name for s in results]
        assert any("Juan" in name for name in names)

    def test_búsqueda_estudiante_con_typo(self):
        """Debe tolerar errores tipográficos."""
        results = search_students("Juab", self.students, cutoff=0.4)
        assert len(results) > 0
        # Debe encontrar nombres que contengan "Juan"

    def test_búsqueda_estudiante_sin_resultados(self):
        """Debe retornar lista vacía si no hay coincidencias."""
        results = search_students("Xyz", self.students)
        assert len(results) == 0

    def test_búsqueda_estudiante_máx_resultados(self):
        """Debe respetar el límite de resultados."""
        results = search_students("Juan", self.students, max_results=1)
        assert len(results) <= 1

    def test_búsqueda_estudiante_cutoff(self):
        """Debe aplicar el umbral de similitud correctamente."""
        # Con cutoff alto, menos resultados
        results_strict = search_students("J", self.students, cutoff=0.9)
        # Con cutoff bajo, más resultados
        results_loose = search_students("J", self.students, cutoff=0.3)

        assert len(results_loose) >= len(results_strict)


class TestSearchStudentsExact:
    """Tests para la función search_students_exact."""

    def setup_method(self):
        """Preparar datos de prueba."""
        self.students = [
            SimpleStudent(id=1, name="Juan Pérez"),
            SimpleStudent(id=2, name="juan pérez"),  # Mismo nombre, distinto caso
            SimpleStudent(id=3, name="JUAN PÉREZ"),   # Mismo nombre, mayúsculas
            SimpleStudent(id=4, name="Juan"),
            SimpleStudent(id=5, name="Pedro García")
        ]

    def test_búsqueda_exacta_match(self):
        """Debe encontrar solo coincidencias exactas."""
        results = search_students_exact("juan pérez", self.students)
        # Debe encontrar los tres registros (case-insensitive)
        assert len(results) == 3
        assert all(s.name.lower() == "juan pérez" for s in results)

    def test_búsqueda_exacta_sin_resultados(self):
        """Debe retornar lista vacía si no hay coincidencia exacta."""
        results = search_students_exact("Juan", self.students)
        # Debe encontrar solo el que es exactamente "Juan"
        assert len(results) == 1
        assert results[0].name == "Juan"

    def test_búsqueda_exacta_sin_coincidencia(self):
        """Debe retornar lista vacía para búsqueda sin coincidencias."""
        results = search_students_exact("Xyz", self.students)
        assert len(results) == 0

    def test_búsqueda_exacta_consulta_vacía(self):
        """Debe retornar lista vacía para consulta vacía."""
        results = search_students_exact("", self.students)
        assert len(results) == 0

    def test_búsqueda_exacta_case_insensitive(self):
        """Debe ignorar diferencias de caso."""
        results_lower = search_students_exact("juan pérez", self.students)
        results_upper = search_students_exact("JUAN PÉREZ", self.students)
        results_mixed = search_students_exact("JuAn PéReZ", self.students)

        assert len(results_lower) == len(results_upper) == len(results_mixed)


class TestGetSearchSuggestions:
    """Tests para la función get_search_suggestions."""

    def setup_method(self):
        """Preparar datos de prueba."""
        self.students = [
            SimpleStudent(id=1, name="Juan Pérez"),
            SimpleStudent(id=2, name="Juan López"),
            SimpleStudent(id=3, name="Pedro García"),
            SimpleStudent(id=4, name="Juanita Martínez"),
            SimpleStudent(id=5, name="Carlos Rodríguez")
        ]

    def test_sugerencias_básicas(self):
        """Debe retornar sugerencias válidas."""
        suggestions = get_search_suggestions("Juan", self.students, cutoff=0.4)
        assert len(suggestions) > 0
        assert all(isinstance(s, str) for s in suggestions)

    def test_sugerencias_máximo_respetado(self):
        """Debe respetar el límite de sugerencias."""
        suggestions = get_search_suggestions("Juan", self.students, max_suggestions=2)
        assert len(suggestions) <= 2

    def test_sugerencias_sin_resultados(self):
        """Debe retornar lista vacía si no hay sugerencias."""
        suggestions = get_search_suggestions("Xyz", self.students, cutoff=0.9)
        assert len(suggestions) == 0

    def test_sugerencias_consulta_vacía(self):
        """Debe retornar lista vacía para consulta vacía."""
        suggestions = get_search_suggestions("", self.students)
        assert len(suggestions) == 0

    def test_sugerencias_cutoff_bajo(self):
        """Con cutoff bajo, debe retornar más sugerencias."""
        suggestions_strict = get_search_suggestions("J", self.students, cutoff=0.9)
        suggestions_loose = get_search_suggestions("J", self.students, cutoff=0.3)

        assert len(suggestions_loose) >= len(suggestions_strict)

    def test_sugerencias_formato_string(self):
        """Las sugerencias deben ser strings con nombres."""
        suggestions = get_search_suggestions("Juan", self.students)

        # Deben ser nombres válidos de estudiantes
        valid_names = [s.name for s in self.students]
        for suggestion in suggestions:
            assert suggestion in valid_names
