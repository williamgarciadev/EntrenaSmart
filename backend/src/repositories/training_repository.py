# -*- coding: utf-8 -*-
"""
Repositorio de Entrenamientos
==============================
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.src.models.training import Training
from backend.src.repositories.base_repository import BaseRepository


class TrainingRepository(BaseRepository[Training]):
    """Repositorio para operaciones de entrenamientos."""

    def __init__(self, db: Session):
        """Inicializa con sesion de BD."""
        super().__init__(db, Training)

    def get_by_student_id(self, student_id: int) -> List[Training]:
        """Obtiene entrenamientos de un alumno."""
        return self.db.query(Training).filter(
            Training.student_id == student_id
        ).all()

    def get_active_by_student_id(self, student_id: int) -> List[Training]:
        """Obtiene entrenamientos activos de un alumno."""
        return self.db.query(Training).filter(
            Training.student_id == student_id,
            Training.is_active == True
        ).all()

    def deactivate_training(self, training_id: int) -> Training:
        """Desactiva un entrenamiento."""
        training = self.get_by_id(training_id)
        if training:
            training.deactivate()
            self.update(training)
        return training

    def activate_training(self, training_id: int) -> Training:
        """Activa un entrenamiento."""
        training = self.get_by_id(training_id)
        if training:
            training.activate()
            self.update(training)
        return training
