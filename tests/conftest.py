"""
Configuración de fixtures para pytest
======================================

Este archivo contiene fixtures compartidas para todos los tests.
"""
import pytest
from typing import Generator


@pytest.fixture
def sample_student_data() -> dict:
    """Datos de ejemplo para un alumno."""
    return {
        "chat_id": 123456789,
        "name": "Test User",
        "telegram_username": "testuser"
    }


@pytest.fixture
def sample_training_data() -> dict:
    """Datos de ejemplo para un entrenamiento."""
    return {
        "student_id": 1,
        "weekday": 0,  # Lunes
        "time": "05:00",
        "session_type": "Funcional"
    }


@pytest.fixture
def sample_feedback_data() -> dict:
    """Datos de ejemplo para feedback."""
    return {
        "training_id": 1,
        "intensity": 3,
        "pain_level": 1,
        "comments": "Todo bien, sin molestias"
    }

