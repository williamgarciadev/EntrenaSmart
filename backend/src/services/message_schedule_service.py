"""
Servicio de Gestión de Programación de Mensajes
================================================

Implementa la lógica de negocio para operaciones relacionadas
con programación de envío automático de mensajes.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.src.models.message_schedule import MessageSchedule
from backend.src.core.exceptions import (
    ValidationError,
    RecordNotFoundError,
    DuplicateRecordError
)


class MessageScheduleService:
    """
    Servicio de gestión de programación de mensajes.

    Encapsula la lógica de negocio relacionada con programación de mensajes.
    """

    def __init__(self, db: Session):
        """
        Inicializa el servicio de programación de mensajes.

        Args:
            db: Sesión de base de datos
        """
        self.db = db

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
            template_id: ID de la plantilla de mensaje
            student_id: ID del estudiante destinatario
            hour: Hora de envío (0-23)
            minute: Minuto de envío (0-59)
            days_of_week: Lista de días de semana (0=lunes, 6=domingo)
            is_active: Si la programación está activa (default: True)

        Returns:
            MessageSchedule: Programación creada

        Raises:
            ValidationError: Si los datos son inválidos
            DuplicateRecordError: Si ya existe una programación similar
        """
        # Validaciones
        if hour < 0 or hour > 23:
            raise ValidationError(
                "La hora debe estar entre 0 y 23",
                {"hour": hour}
            )

        if minute < 0 or minute > 59:
            raise ValidationError(
                "El minuto debe estar entre 0 y 59",
                {"minute": minute}
            )

        if not days_of_week or len(days_of_week) == 0:
            raise ValidationError(
                "Debe especificar al menos un día de la semana",
                {"days_of_week": days_of_week}
            )

        for day in days_of_week:
            if day < 0 or day > 6:
                raise ValidationError(
                    "Los días de la semana deben estar entre 0 (lunes) y 6 (domingo)",
                    {"day": day}
                )

        # Verificar si ya existe una programación similar
        existing = self.db.query(MessageSchedule).filter(
            MessageSchedule.template_id == template_id,
            MessageSchedule.student_id == student_id,
            MessageSchedule.hour == hour,
            MessageSchedule.minute == minute,
            MessageSchedule.is_active == True
        ).first()

        if existing:
            raise DuplicateRecordError(
                f"Ya existe una programación activa para este estudiante con el mismo horario"
            )

        # Crear programación
        schedule = MessageSchedule(
            template_id=template_id,
            student_id=student_id,
            hour=hour,
            minute=minute,
            days_of_week=days_of_week,
            is_active=is_active
        )

        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)

        return schedule

    def get_schedule_by_id(self, schedule_id: int) -> Optional[MessageSchedule]:
        """
        Obtiene una programación por su ID.

        Args:
            schedule_id: ID de la programación

        Returns:
            Optional[MessageSchedule]: Programación encontrada o None
        """
        return self.db.query(MessageSchedule).filter(
            MessageSchedule.id == schedule_id
        ).first()

    def get_schedule_by_id_or_fail(self, schedule_id: int) -> MessageSchedule:
        """
        Obtiene una programación por su ID o lanza excepción.

        Args:
            schedule_id: ID de la programación

        Returns:
            MessageSchedule: Programación encontrada

        Raises:
            RecordNotFoundError: Si no se encuentra la programación
        """
        schedule = self.get_schedule_by_id(schedule_id)
        if not schedule:
            raise RecordNotFoundError(
                f"Programación con ID {schedule_id} no encontrada"
            )
        return schedule

    def list_all_schedules(self, active_only: bool = False) -> List[MessageSchedule]:
        """
        Lista todas las programaciones.

        Args:
            active_only: Si True, solo retorna programaciones activas

        Returns:
            List[MessageSchedule]: Lista de programaciones
        """
        query = self.db.query(MessageSchedule)

        if active_only:
            query = query.filter(MessageSchedule.is_active == True)

        return query.order_by(MessageSchedule.id.desc()).all()

    def list_schedules_by_student(
        self,
        student_id: int,
        active_only: bool = False
    ) -> List[MessageSchedule]:
        """
        Lista programaciones de un estudiante específico.

        Args:
            student_id: ID del estudiante
            active_only: Si True, solo retorna programaciones activas

        Returns:
            List[MessageSchedule]: Lista de programaciones
        """
        query = self.db.query(MessageSchedule).filter(
            MessageSchedule.student_id == student_id
        )

        if active_only:
            query = query.filter(MessageSchedule.is_active == True)

        return query.order_by(MessageSchedule.id.desc()).all()

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
            days_of_week: Nuevos días de semana (opcional)
            is_active: Nuevo estado (opcional)

        Returns:
            MessageSchedule: Programación actualizada

        Raises:
            RecordNotFoundError: Si no se encuentra la programación
            ValidationError: Si los datos son inválidos
        """
        schedule = self.get_schedule_by_id_or_fail(schedule_id)

        # Actualizar campos si se proporcionan
        if template_id is not None:
            schedule.template_id = template_id

        if student_id is not None:
            schedule.student_id = student_id

        if hour is not None:
            if hour < 0 or hour > 23:
                raise ValidationError(
                    "La hora debe estar entre 0 y 23",
                    {"hour": hour}
                )
            schedule.hour = hour

        if minute is not None:
            if minute < 0 or minute > 59:
                raise ValidationError(
                    "El minuto debe estar entre 0 y 59",
                    {"minute": minute}
                )
            schedule.minute = minute

        if days_of_week is not None:
            if not days_of_week or len(days_of_week) == 0:
                raise ValidationError(
                    "Debe especificar al menos un día de la semana",
                    {"days_of_week": days_of_week}
                )
            for day in days_of_week:
                if day < 0 or day > 6:
                    raise ValidationError(
                        "Los días de la semana deben estar entre 0 (lunes) y 6 (domingo)",
                        {"day": day}
                    )
            schedule.days_of_week = days_of_week

        if is_active is not None:
            schedule.is_active = is_active

        self.db.commit()
        self.db.refresh(schedule)

        return schedule

    def delete_schedule(self, schedule_id: int) -> MessageSchedule:
        """
        Elimina (desactiva) una programación.

        Args:
            schedule_id: ID de la programación

        Returns:
            MessageSchedule: Programación eliminada

        Raises:
            RecordNotFoundError: Si no se encuentra la programación
        """
        schedule = self.get_schedule_by_id_or_fail(schedule_id)
        schedule.deactivate()

        self.db.commit()
        self.db.refresh(schedule)

        return schedule

    def activate_schedule(self, schedule_id: int) -> MessageSchedule:
        """
        Activa una programación.

        Args:
            schedule_id: ID de la programación

        Returns:
            MessageSchedule: Programación activada

        Raises:
            RecordNotFoundError: Si no se encuentra la programación
        """
        schedule = self.get_schedule_by_id_or_fail(schedule_id)
        schedule.activate()

        self.db.commit()
        self.db.refresh(schedule)

        return schedule
