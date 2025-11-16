# -*- coding: utf-8 -*-
"""
Repositorio Base Generico
==========================

Proporciona operaciones CRUD basicas para todos los repositorios.
"""
from typing import TypeVar, Generic, List, Optional

from sqlalchemy.orm import Session

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Repositorio base generico con operaciones CRUD.
    """

    def __init__(self, db: Session, model_class: type[T]):
        """
        Inicializa el repositorio.

        Args:
            db: Sesion de SQLAlchemy
            model_class: Clase del modelo
        """
        self.db = db
        self.model_class = model_class

    def create(self, obj: T) -> T:
        """Crea un nuevo registro."""
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(self, id: int) -> Optional[T]:
        """Obtiene un registro por ID."""
        return self.db.query(self.model_class).filter(
            self.model_class.id == id
        ).first()

    def get_all(self) -> List[T]:
        """Obtiene todos los registros."""
        return self.db.query(self.model_class).all()

    def update(self, obj: T) -> T:
        """Actualiza un registro."""
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: T) -> None:
        """Elimina un registro."""
        self.db.delete(obj)
        self.db.commit()
