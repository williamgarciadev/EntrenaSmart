# -*- coding: utf-8 -*-
"""
Validadores para EntrenaSmart
==============================

Módulo con validadores reutilizables para datos de la aplicación.
"""
import re
from src.core.exceptions import LocationValidationError


class LocationValidator:
    """Validador para ubicaciones de entrenamientos."""

    MIN_LENGTH = 3
    MAX_LENGTH = 100
    # Permite caracteres alfanuméricos, espacios, guiones, puntos, paréntesis, y caracteres acentuados
    ALLOWED_CHARS_PATTERN = r'^[a-zA-Z0-9\s\-./()áéíóúñÁÉÍÓÚÑ]+$'

    @classmethod
    def validate(cls, location: str) -> str:
        """
        Valida una ubicación de entrenamiento.

        Verifica:
        - No está vacía
        - Longitud mínima (3 caracteres)
        - Longitud máxima (100 caracteres)
        - Solo contiene caracteres permitidos

        Args:
            location: String con la ubicación

        Returns:
            Ubicación validada y limpiada (stripped)

        Raises:
            LocationValidationError: Si la ubicación no es válida
        """
        if not location or not isinstance(location, str):
            raise LocationValidationError("❌ Ubicación no puede estar vacía.")

        location = location.strip()

        if len(location) < cls.MIN_LENGTH:
            raise LocationValidationError(
                f"❌ Ubicación muy corta (mínimo {cls.MIN_LENGTH} caracteres)."
            )

        if len(location) > cls.MAX_LENGTH:
            raise LocationValidationError(
                f"❌ Ubicación muy larga (máximo {cls.MAX_LENGTH} caracteres)."
            )

        if not re.match(cls.ALLOWED_CHARS_PATTERN, location):
            raise LocationValidationError(
                "❌ Ubicación contiene caracteres no permitidos."
            )

        return location
