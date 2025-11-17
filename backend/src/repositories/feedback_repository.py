# -*- coding: utf-8 -*-
"""
Repositorio de Feedback
========================
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.src.models.feedback import Feedback
from backend.src.repositories.base_repository import BaseRepository


class FeedbackRepository(BaseRepository[Feedback]):
    """Repositorio para operaciones de feedback."""

    def __init__(self, db: Session):
        """Inicializa con sesion de BD."""
        super().__init__(db, Feedback)

    def get_by_training_id(self, training_id: int) -> Optional[Feedback]:
        """Obtiene feedback de un entrenamiento."""
        return self.db.query(Feedback).filter(
            Feedback.training_id == training_id
        ).first()
