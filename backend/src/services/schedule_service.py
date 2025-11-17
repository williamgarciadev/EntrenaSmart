# -*- coding: utf-8 -*-
"""
Servicio de Programaciones de Mensajes
=======================================

Gestiona la lógica de negocio para programaciones de envío
automático de mensajes a estudiantes.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.src.models.message_schedule import MessageSchedule
from backend.src.repositories.schedule_repository import ScheduleRepository
from backend.src.core.exceptions import (
    ValidationError,
    DuplicateRecordError,
    RecordNotFoundError
)
from backend.src.utils.logger import logger


class ScheduleService:
    """Servicio para gestionar programaciones de mensajes."""

    def __init__(self, db: Session):
        """
        Inicializa el servicio.

        Args:
            db: Sesión de SQLAlchemy
        """
        self.db = db
        self.repository = ScheduleRepository(db)

    def create_schedule(
        self,
        template_id: int,
        student_id: int,
        hour: int,
        minute: int,
        days_of_week: List[int],
        is_active: bool = True
    ) -> MessageSchedule:
        """
        Crea una nueva programación de mensaje.

        Args:
            template_id: ID de la plantilla
            student_id: ID del estudiante
            hour: Hora (0-23)
            minute: Minuto (0-59)
            days_of_week: Lista de días de la semana (0=Lunes, 6=Domingo)
            is_active: Si está activa

        Returns:
            MessageSchedule creada

        Raises:
            ValidationError: Si los datos no son válidos
            DuplicateRecordError: Si ya existe una programación idéntica
        """
        # Validar hora
        if not 0 <= hour <= 23:
            raise ValidationError("La hora debe estar entre 0 y 23")

        # Validar minuto
        if not 0 <= minute <= 59:
            raise ValidationError("El minuto debe estar entre 0 y 59")

        # Validar días de la semana
        if not days_of_week or len(days_of_week) == 0:
            raise ValidationError("Debe seleccionar al menos un día de la semana")

        for day in days_of_week:
            if not 0 <= day <= 6:
                raise ValidationError(f"Día inválido: {day}. Debe estar entre 0 (Lunes) y 6 (Domingo)")

        # Verificar duplicados
        if self.repository.exists_duplicate(template_id, student_id, hour, minute):
            raise DuplicateRecordError(
                "MessageSchedule",
                f"Ya existe una programación con los mismos datos"
            )

        # Crear programación
        schedule = MessageSchedule(
            template_id=template_id,
            student_id=student_id,
            hour=hour,
            minute=minute,
            days_of_week=sorted(days_of_week),
            is_active=is_active
        )

        created = self.repository.create(schedule)
        logger.info(f"Programación creada: {created.id}")

        return created

    def update_schedule(
        self,
        schedule_id: int,
        template_id: Optional[int] = None,
        student_id: Optional[int] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        days_of_week: Optional[List[int]] = None,
        is_active: Optional[bool] = None
    ) -> MessageSchedule:
        """
        Actualiza una programación existente.

        Args:
            schedule_id: ID de la programación
            template_id: Nuevo ID de plantilla (opcional)
            student_id: Nuevo ID de estudiante (opcional)
            hour: Nueva hora (opcional)
            minute: Nuevo minuto (opcional)
            days_of_week: Nuevos días (opcional)
            is_active: Nuevo estado (opcional)

        Returns:
            MessageSchedule actualizada

        Raises:
            RecordNotFoundError: Si la programación no existe
            ValidationError: Si los datos no son válidos
        """
        schedule = self.repository.get_by_id(schedule_id)
        if not schedule:
            raise RecordNotFoundError("MessageSchedule", {"id": schedule_id})

        # Actualizar campos
        if template_id is not None:
            schedule.template_id = template_id

        if student_id is not None:
            schedule.student_id = student_id

        if hour is not None:
            if not 0 <= hour <= 23:
                raise ValidationError("La hora debe estar entre 0 y 23")
            schedule.hour = hour

        if minute is not None:
            if not 0 <= minute <= 59:
                raise ValidationError("El minuto debe estar entre 0 y 59")
            schedule.minute = minute

        if days_of_week is not None:
            if len(days_of_week) == 0:
                raise ValidationError("Debe seleccionar al menos un día de la semana")
            for day in days_of_week:
                if not 0 <= day <= 6:
                    raise ValidationError(f"Día inválido: {day}")
            schedule.days_of_week = sorted(days_of_week)

        if is_active is not None:
            schedule.is_active = is_active

        updated = self.repository.update(schedule)
        logger.info(f"Programación actualizada: {schedule_id}")

        return updated

    def delete_schedule(self, schedule_id: int) -> None:
        """
        Elimina una programación.

        Args:
            schedule_id: ID de la programación

        Raises:
            RecordNotFoundError: Si la programación no existe
        """
        schedule = self.repository.get_by_id(schedule_id)
        if not schedule:
            raise RecordNotFoundError("MessageSchedule", {"id": schedule_id})

        self.repository.delete(schedule)
        logger.info(f"Programación eliminada: {schedule_id}")

    def get_schedule_by_id(self, schedule_id: int) -> Optional[MessageSchedule]:
        """
        Obtiene una programación por ID.

        Args:
            schedule_id: ID de la programación

        Returns:
            MessageSchedule o None
        """
        return self.repository.get_by_id(schedule_id)

    def get_schedule_by_id_or_fail(self, schedule_id: int) -> MessageSchedule:
        """
        Obtiene una programación por ID o lanza excepción.

        Args:
            schedule_id: ID de la programación

        Returns:
            MessageSchedule

        Raises:
            RecordNotFoundError: Si no existe
        """
        schedule = self.repository.get_by_id(schedule_id)
        if not schedule:
            raise RecordNotFoundError("MessageSchedule", {"id": schedule_id})
        return schedule

    def list_all_schedules(self, active_only: bool = False) -> List[MessageSchedule]:
        """
        Lista todas las programaciones.

        Args:
            active_only: Si es True, solo retorna activas

        Returns:
            Lista de programaciones
        """
        if active_only:
            return self.repository.get_active_schedules()
        return self.repository.get_all()

    def get_schedules_by_student(
        self,
        student_id: int,
        active_only: bool = False
    ) -> List[MessageSchedule]:
        """
        Obtiene programaciones de un estudiante.

        Args:
            student_id: ID del estudiante
            active_only: Si es True, solo retorna activas

        Returns:
            Lista de programaciones
        """
        if active_only:
            return self.repository.get_active_by_student_id(student_id)
        return self.repository.get_by_student_id(student_id)

    def activate_schedule(self, schedule_id: int) -> MessageSchedule:
        """
        Activa una programación.

        Args:
            schedule_id: ID de la programación

        Returns:
            MessageSchedule activada

        Raises:
            RecordNotFoundError: Si no existe
        """
        schedule = self.repository.activate_schedule(schedule_id)
        if not schedule:
            raise RecordNotFoundError("MessageSchedule", {"id": schedule_id})
        logger.info(f"Programación activada: {schedule_id}")
        return schedule

    def deactivate_schedule(self, schedule_id: int) -> MessageSchedule:
        """
        Desactiva una programación.

        Args:
            schedule_id: ID de la programación

        Returns:
            MessageSchedule desactivada

        Raises:
            RecordNotFoundError: Si no existe
        """
        schedule = self.repository.deactivate_schedule(schedule_id)
        if not schedule:
            raise RecordNotFoundError("MessageSchedule", {"id": schedule_id})
        logger.info(f"Programación desactivada: {schedule_id}")
        return schedule
