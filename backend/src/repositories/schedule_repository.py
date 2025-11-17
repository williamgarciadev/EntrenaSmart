# -*- coding: utf-8 -*-
"""
Repositorio de Programaciones de Mensajes
==========================================
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.src.models.message_schedule import MessageSchedule
from backend.src.repositories.base_repository import BaseRepository


class ScheduleRepository(BaseRepository[MessageSchedule]):
    """Repositorio para operaciones de programaciones de mensajes."""

    def __init__(self, db: Session):
        """Inicializa con sesion de BD."""
        super().__init__(db, MessageSchedule)

    def get_by_template_and_student(
        self,
        template_id: int,
        student_id: int
    ) -> List[MessageSchedule]:
        """
        Obtiene programaciones por plantilla y estudiante.

        Args:
            template_id: ID de la plantilla
            student_id: ID del estudiante

        Returns:
            Lista de programaciones
        """
        return self.db.query(MessageSchedule).filter(
            MessageSchedule.template_id == template_id,
            MessageSchedule.student_id == student_id
        ).all()

    def get_active_schedules(self) -> List[MessageSchedule]:
        """
        Obtiene todas las programaciones activas.

        Returns:
            Lista de programaciones activas
        """
        return self.db.query(MessageSchedule).filter(
            MessageSchedule.is_active == True
        ).all()

    def get_by_student_id(self, student_id: int) -> List[MessageSchedule]:
        """
        Obtiene programaciones de un estudiante.

        Args:
            student_id: ID del estudiante

        Returns:
            Lista de programaciones
        """
        return self.db.query(MessageSchedule).filter(
            MessageSchedule.student_id == student_id
        ).all()

    def get_active_by_student_id(self, student_id: int) -> List[MessageSchedule]:
        """
        Obtiene programaciones activas de un estudiante.

        Args:
            student_id: ID del estudiante

        Returns:
            Lista de programaciones activas
        """
        return self.db.query(MessageSchedule).filter(
            MessageSchedule.student_id == student_id,
            MessageSchedule.is_active == True
        ).all()

    def deactivate_schedule(self, schedule_id: int) -> Optional[MessageSchedule]:
        """
        Desactiva una programación.

        Args:
            schedule_id: ID de la programación

        Returns:
            Programación desactivada o None
        """
        schedule = self.get_by_id(schedule_id)
        if schedule:
            schedule.deactivate()
            self.update(schedule)
        return schedule

    def activate_schedule(self, schedule_id: int) -> Optional[MessageSchedule]:
        """
        Activa una programación.

        Args:
            schedule_id: ID de la programación

        Returns:
            Programación activada o None
        """
        schedule = self.get_by_id(schedule_id)
        if schedule:
            schedule.activate()
            self.update(schedule)
        return schedule

    def exists_duplicate(
        self,
        template_id: int,
        student_id: int,
        hour: int,
        minute: int,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si existe una programación duplicada.

        Args:
            template_id: ID de la plantilla
            student_id: ID del estudiante
            hour: Hora
            minute: Minuto
            exclude_id: ID a excluir de la búsqueda (para updates)

        Returns:
            True si existe duplicado, False en caso contrario
        """
        query = self.db.query(MessageSchedule).filter(
            MessageSchedule.template_id == template_id,
            MessageSchedule.student_id == student_id,
            MessageSchedule.hour == hour,
            MessageSchedule.minute == minute
        )

        if exclude_id:
            query = query.filter(MessageSchedule.id != exclude_id)

        return query.first() is not None
