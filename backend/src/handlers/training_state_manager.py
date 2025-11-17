# -*- coding: utf-8 -*-
"""
Gestor de Estado para Configuración de Entrenamientos Semanales
================================================================

Manager para manejar el estado conversacional del flujo /config_semana
de forma segura y type-safe.
"""
from telegram.ext import ContextTypes

from backend.src.utils.conversation_state import (
    ConfigTrainingState,
    save_state_to_context_simple,
    load_state_from_context_simple,
    clear_state_simple
)
from backend.src.core.exceptions import StateNotFoundError
from backend.src.utils.logger import logger


class TrainingStateManager:
    """
    Gestor de estado para configuración semanal de entrenamientos.

    Proporciona métodos para guardar, cargar y limpiar estado de manera segura.
    Abstrae los detalles de cómo se almacena el estado en context.user_data.
    """

    @staticmethod
    def save_config_state(
        context: ContextTypes.DEFAULT_TYPE,
        weekday: int,
        weekday_name: str,
        session_type: str,
        location: str
    ) -> None:
        """
        Guarda el estado de configuración actual.

        Args:
            context: ContextTypes.DEFAULT_TYPE del handler
            weekday: Número de día (0-6)
            weekday_name: Nombre del día en español
            session_type: Tipo de entrenamiento
            location: Ubicación

        Ejemplo:
            >>> TrainingStateManager.save_config_state(
            ...     context,
            ...     weekday=0,
            ...     weekday_name="Lunes",
            ...     session_type="Pierna",
            ...     location="2do Piso"
            ... )
        """
        state = ConfigTrainingState(
            weekday=weekday,
            weekday_name=weekday_name,
            session_type=session_type,
            location=location
        )
        save_state_to_context_simple(context, state)
        logger.debug(
            f"[STATE] Guardado: weekday={weekday}, type={session_type}, loc={location}"
        )

    @staticmethod
    def get_config_state(context: ContextTypes.DEFAULT_TYPE) -> ConfigTrainingState:
        """
        Obtiene el estado de configuración guardado.

        Args:
            context: ContextTypes.DEFAULT_TYPE del handler

        Returns:
            ConfigTrainingState con los datos guardados

        Raises:
            StateNotFoundError: Si el estado no existe o fue perdido

        Ejemplo:
            >>> state = TrainingStateManager.get_config_state(context)
            >>> print(state.session_type)  # "Pierna"
        """
        state = load_state_from_context_simple(context, ConfigTrainingState)

        if state is None:
            logger.warning("[STATE] Estado no encontrado")
            raise StateNotFoundError()

        logger.debug(f"[STATE] Cargado: {state.weekday_name} - {state.session_type}")
        return state

    @staticmethod
    def clear_config_state(context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Limpia el estado de configuración.

        Esta función debe ser llamada después de guardar en BD para
        limpiar el estado temporal y preparar para el siguiente ciclo.

        Args:
            context: ContextTypes.DEFAULT_TYPE del handler

        Ejemplo:
            >>> TrainingStateManager.clear_config_state(context)
        """
        clear_state_simple(context, ConfigTrainingState)
        logger.debug("[STATE] Limpiado")

    @staticmethod
    def partial_state_exists(context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Verifica si existe un estado parcial de configuración.

        Útil para determinar si debemos reintentar o empezar desde cero.

        Args:
            context: ContextTypes.DEFAULT_TYPE del handler

        Returns:
            True si existe estado, False si no
        """
        state = load_state_from_context_simple(context, ConfigTrainingState)
        return state is not None
