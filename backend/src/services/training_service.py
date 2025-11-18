# -*- coding: utf-8 -*-
"""
Servicio de Entrenamientos
==========================

Gestiona la lógica de negocio para entrenamientos (sesiones de entrenamiento).
Integración con SchedulerService para recordatorios automáticos.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.src.models.training import Training
from backend.src.repositories.training_repository import TrainingRepository
from backend.src.core.exceptions import ValidationError, RecordNotFoundError
from backend.src.utils.logger import logger


class TrainingService:
    """Servicio para gestionar entrenamientos."""

    def __init__(self, db: Session, scheduler_service=None):
        """
        Inicializa el servicio.

        Args:
            db: Sesión de SQLAlchemy
            scheduler_service: SchedulerService para gestionar recordatorios (opcional)
        """
        self.db = db
        self.repository = TrainingRepository(db)
        self.scheduler = scheduler_service

    def add_training(
        self,
        student_id: int,
        weekday: int,
        weekday_name: str,
        time_str: str,
        session_type: Optional[str] = None,
        location: Optional[str] = None,
        training_day_config_id: Optional[int] = None
    ) -> Training:
        """
        Agrega un nuevo entrenamiento para un alumno y programa recordatorio.

        Args:
            student_id: ID del alumno
            weekday: Día de la semana (0=Lunes, 6=Domingo)
            weekday_name: Nombre del día ("Lunes", "Martes", etc.)
            time_str: Hora en formato HH:MM
            session_type: Tipo de sesión (opcional)
            location: Ubicación del entrenamiento (opcional)
            training_day_config_id: ID de configuración del día (opcional)

        Returns:
            Training: Entrenamiento creado

        Raises:
            ValidationError: Si los datos no son válidos
        """
        # Validar
        if not isinstance(weekday, int) or weekday < 0 or weekday > 6:
            raise ValidationError("Día de la semana inválido (debe ser 0-6)")

        if not time_str or not isinstance(time_str, str):
            raise ValidationError("Hora inválida")

        # Crear entrenamiento
        training = Training(
            student_id=student_id,
            weekday=weekday,
            weekday_name=weekday_name,
            time_str=time_str,
            session_type=session_type or "",
            location=location,
            training_day_config_id=training_day_config_id
        )

        self.db.add(training)
        self.db.commit()
        self.db.refresh(training)

        # Programar recordatorio si scheduler está disponible
        if self.scheduler:
            try:
                from backend.src.models.student import Student
                student = self.db.query(Student).filter(Student.id == student_id).first()

                if student and student.chat_id:
                    self.scheduler.schedule_training_reminder(
                        training_id=training.id,
                        student_chat_id=student.chat_id,
                        weekday=weekday,
                        training_time=time_str,
                        session_type=session_type or "Entrenamiento",
                        location=location or ""
                    )
                    logger.info(f"Recordatorio programado para entrenamiento {training.id}")
            except Exception as e:
                logger.warning(f"No se pudo programar recordatorio: {str(e)}")

        logger.info(f"Entrenamiento creado: {training.id} - {weekday_name} {time_str}")
        return training

    def get_training_schedule_summary(self, student_id: int) -> Dict[str, Any]:
        """
        Obtiene un resumen del horario de entrenamientos de un alumno.

        Retorna los entrenamientos ordenados por día de la semana.

        Args:
            student_id: ID del alumno

        Returns:
            dict: Diccionario {día: [horarios]}
        """
        trainings = self.repository.get_by_student_id(student_id)

        schedule = {}
        for training in trainings:
            day = training.weekday_name
            if day not in schedule:
                schedule[day] = []
            schedule[day].append(training.time_str)

        return schedule

    def get_all_trainings(self, student_id: int) -> List[Training]:
        """
        Obtiene todos los entrenamientos de un alumno.

        Args:
            student_id: ID del alumno

        Returns:
            List[Training]: Lista de entrenamientos
        """
        return self.repository.get_by_student_id(student_id)

    def get_training_by_id(self, training_id: int) -> Optional[Training]:
        """
        Obtiene un entrenamiento por ID.

        Args:
            training_id: ID del entrenamiento

        Returns:
            Training: Entrenamiento o None si no existe
        """
        return self.repository.get_by_id(training_id)

    def update_training(
        self,
        training_id: int,
        weekday: Optional[int] = None,
        weekday_name: Optional[str] = None,
        time_str: Optional[str] = None,
        session_type: Optional[str] = None,
        location: Optional[str] = None,
        training_day_config_id: Optional[int] = None
    ) -> Training:
        """
        Actualiza un entrenamiento existente y reprograma recordatorio si cambia hora/día.

        Args:
            training_id: ID del entrenamiento
            weekday: Nuevo día (opcional)
            weekday_name: Nuevo nombre del día (opcional)
            time_str: Nueva hora (opcional)
            session_type: Nuevo tipo de sesión (opcional)
            location: Nueva ubicación (opcional)
            training_day_config_id: Nuevo ID de configuración (opcional)

        Returns:
            Training: Entrenamiento actualizado

        Raises:
            RecordNotFoundError: Si el entrenamiento no existe
        """
        training = self.repository.get_by_id(training_id)
        if not training:
            raise RecordNotFoundError(f"Entrenamiento {training_id} no encontrado")

        # Detectar cambios en hora o día para reprogramar recordatorio
        time_changed = time_str is not None and time_str != training.time_str
        day_changed = weekday is not None and weekday != training.weekday

        # Actualizar campos
        if weekday is not None:
            training.weekday = weekday
        if weekday_name is not None:
            training.weekday_name = weekday_name
        if time_str is not None:
            training.time_str = time_str
        if session_type is not None:
            training.session_type = session_type
        if location is not None:
            training.location = location
        if training_day_config_id is not None:
            training.training_day_config_id = training_day_config_id

        self.db.commit()
        self.db.refresh(training)

        # Reprogramar recordatorio si cambió hora o día
        if (time_changed or day_changed) and self.scheduler:
            try:
                from backend.src.models.student import Student
                student = self.db.query(Student).filter(Student.id == training.student_id).first()

                if student and student.chat_id:
                    # Cancelar recordatorio anterior y programar uno nuevo
                    self.scheduler.cancel_training_reminder(training_id)
                    self.scheduler.schedule_training_reminder(
                        training_id=training_id,
                        student_chat_id=student.chat_id,
                        weekday=training.weekday,
                        training_time=training.time_str,
                        session_type=training.session_type or "Entrenamiento",
                        location=training.location or ""
                    )
                    logger.info(f"Recordatorio reprogramado para entrenamiento {training_id}")
            except Exception as e:
                logger.warning(f"No se pudo reprogramar recordatorio: {str(e)}")

        logger.info(f"Entrenamiento actualizado: {training.id}")
        return training

    def delete_training(self, training_id: int) -> None:
        """
        Elimina un entrenamiento y cancela su recordatorio.

        Args:
            training_id: ID del entrenamiento

        Raises:
            RecordNotFoundError: Si el entrenamiento no existe
        """
        training = self.repository.get_by_id(training_id)
        if not training:
            raise RecordNotFoundError(f"Entrenamiento {training_id} no encontrado")

        # Cancelar recordatorio si scheduler está disponible
        if self.scheduler:
            try:
                self.scheduler.cancel_training_reminder(training_id)
                logger.info(f"Recordatorio cancelado para entrenamiento {training_id}")
            except Exception as e:
                logger.warning(f"No se pudo cancelar recordatorio: {str(e)}")

        self.db.delete(training)
        self.db.commit()

        logger.info(f"Entrenamiento eliminado: {training_id}")

    def set_session_type(self, training_id: int, session_type: str) -> Training:
        """
        Asigna un tipo de sesión a un entrenamiento.

        Útil cuando el entrenamiento se crea sin tipo y se asigna después.

        Args:
            training_id: ID del entrenamiento
            session_type: Tipo de sesión

        Returns:
            Training: Entrenamiento actualizado
        """
        return self.update_training(training_id, session_type=session_type)
