# -*- coding: utf-8 -*-
"""
Repositorio de Configuración de Entrenamientos
===============================================

Maneja operaciones CRUD para TrainingDayConfig (configuración semanal).
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.src.models.training_day_config import TrainingDayConfig
from backend.src.repositories.base_repository import BaseRepository


class ConfigTrainingRepository(BaseRepository[TrainingDayConfig]):
    """Repositorio para gestionar TrainingDayConfig."""

    def __init__(self, db: Session):
        """Inicializa el repositorio."""
        super().__init__(db, TrainingDayConfig)

    def get_by_weekday(self, weekday: int) -> Optional[TrainingDayConfig]:
        """
        Obtiene la configuración de un día específico.

        Args:
            weekday: Número de día (0=Lunes, 6=Domingo)

        Returns:
            TrainingDayConfig o None si no existe
        """
        return self.db.query(TrainingDayConfig).filter(
            TrainingDayConfig.weekday == weekday,
            TrainingDayConfig.is_active == True
        ).first()

    def get_all_active(self) -> List[TrainingDayConfig]:
        """
        Obtiene todas las configuraciones activas de la semana.

        Returns:
            Lista de TrainingDayConfig activas, ordenadas por weekday
        """
        return self.db.query(TrainingDayConfig).filter(
            TrainingDayConfig.is_active == True
        ).order_by(TrainingDayConfig.weekday).all()

    def get_all_by_session_type(self, session_type: str) -> List[TrainingDayConfig]:
        """
        Obtiene todas las configuraciones de un tipo de entrenamiento.

        Args:
            session_type: Tipo de entrenamiento (ej: "Pierna", "Funcional")

        Returns:
            Lista de TrainingDayConfig con ese tipo
        """
        return self.db.query(TrainingDayConfig).filter(
            TrainingDayConfig.session_type == session_type,
            TrainingDayConfig.is_active == True
        ).all()

    def weekday_exists(self, weekday: int) -> bool:
        """
        Verifica si ya existe configuración para un día.

        Args:
            weekday: Número de día

        Returns:
            True si existe, False en caso contrario
        """
        return self.db.query(TrainingDayConfig).filter(
            TrainingDayConfig.weekday == weekday
        ).first() is not None

    def update_by_weekday(
        self,
        weekday: int,
        session_type: str,
        location: str
    ) -> Optional[TrainingDayConfig]:
        """
        Actualiza (o inserta) la configuración de un día específico (UPSERT atómico).

        Utiliza `with_for_update()` para evitar race conditions en caso de
        solicitudes concurrentes. El commit es responsabilidad del caller
        (típicamente el handler que usa get_db_context()).

        Args:
            weekday: Número de día (0-6)
            session_type: Nuevo tipo de entrenamiento
            location: Nueva ubicación

        Returns:
            TrainingDayConfig actualizado o creado (pendiente de commit)

        Nota:
            - NO hace commit directamente
            - Caller debe hacer commit via context manager get_db_context()
            - with_for_update() previene race conditions en concurrencia
        """
        # Buscar existente CON LOCK para evitar race condition
        config = self.db.query(TrainingDayConfig).filter(
            TrainingDayConfig.weekday == weekday
        ).with_for_update().first()

        if config:
            # UPDATE
            config.session_type = session_type
            config.location = location
            # Marcar como activa si tiene valores configurados
            config.is_active = bool(session_type and location)
        else:
            # INSERT
            from datetime import datetime
            days_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            weekday_name = days_names[weekday]

            config = TrainingDayConfig(
                weekday=weekday,
                weekday_name=weekday_name,
                session_type=session_type,
                location=location,
                is_active=bool(session_type and location)  # Activa solo si tiene valores
            )
            self.db.add(config)

        # NO hacer commit aquí - es responsabilidad del caller
        # El context manager get_db_context() manejará commit/rollback
        return config
