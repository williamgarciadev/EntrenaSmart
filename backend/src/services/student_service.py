"""
Servicio de Gestión de Alumnos
================================

Implementa la lógica de negocio para operaciones relacionadas
con alumnos, validaciones y reglas de negocio.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from backend.src.models.student import Student
from backend.src.repositories.student_repository import StudentRepository
from backend.src.core.exceptions import (
    ValidationError,
    StudentNotActiveError,
    RecordNotFoundError
)
from backend.src.core.constants import MAX_STUDENT_NAME_LENGTH


class StudentService:
    """
    Servicio de gestión de alumnos.

    Encapsula la lógica de negocio relacionada con alumnos.
    """

    def __init__(self, db: Session):
        """
        Inicializa el servicio de alumnos.

        Args:
            db: Sesión de base de datos
        """
        self.db = db
        self.repository = StudentRepository(db)

    def register_student(
        self,
        name: str,
        telegram_username: Optional[str] = None,
        chat_id: Optional[int] = None
    ) -> Student:
        """
        Registra un nuevo alumno en el sistema.

        Args:
            name: Nombre del alumno
            telegram_username: Username de Telegram (opcional)
            chat_id: ID del chat de Telegram (opcional, se asigna cuando el alumno inicia sesión)

        Returns:
            Student: Alumno registrado

        Raises:
            ValidationError: Si el nombre es inválido
            DuplicateRecordError: Si el alumno ya está registrado
        """
        # Validar nombre
        name = name.strip()
        if not name:
            raise ValidationError(
                "El nombre del alumno no puede estar vacío",
                {"name": name}
            )

        if len(name) > MAX_STUDENT_NAME_LENGTH:
            raise ValidationError(
                f"El nombre no puede exceder {MAX_STUDENT_NAME_LENGTH} caracteres",
                {"name": name, "length": len(name)}
            )

        # Limpiar username (remover @ si existe)
        if telegram_username:
            telegram_username = telegram_username.lstrip("@").strip()

        # Crear alumno
        return self.repository.create_student(
            chat_id=chat_id,
            name=name,
            telegram_username=telegram_username
        )

    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """
        Obtiene un alumno por su ID (primary key).

        Args:
            student_id: ID del alumno

        Returns:
            Optional[Student]: Alumno encontrado o None
        """
        return self.repository.get_by_id(student_id)

    def get_student_by_id_or_fail(self, student_id: int) -> Student:
        """
        Obtiene un alumno por su ID o lanza excepción.

        Args:
            student_id: ID del alumno

        Returns:
            Student: Alumno encontrado

        Raises:
            RecordNotFoundError: Si el alumno no existe
        """
        return self.repository.get_by_id_or_fail(student_id)

    def get_student_by_chat_id(self, chat_id: int) -> Optional[Student]:
        """
        Obtiene un alumno por su chat_id de Telegram.

        Args:
            chat_id: ID del chat de Telegram

        Returns:
            Optional[Student]: Alumno encontrado o None
        """
        return self.repository.get_by_chat_id(chat_id)

    def get_student_by_chat_id_or_fail(self, chat_id: int) -> Student:
        """
        Obtiene un alumno por su chat_id o lanza excepción.

        Args:
            chat_id: ID del chat de Telegram

        Returns:
            Student: Alumno encontrado

        Raises:
            RecordNotFoundError: Si el alumno no existe
        """
        return self.repository.get_by_chat_id_or_fail(chat_id)

    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """
        Obtiene un alumno por su ID.

        Args:
            student_id: ID del alumno

        Returns:
            Optional[Student]: Alumno encontrado o None
        """
        return self.repository.get_by_id(student_id)

    def get_student_by_id_or_fail(self, student_id: int) -> Student:
        """
        Obtiene un alumno por su ID o lanza excepción.

        Args:
            student_id: ID del alumno

        Returns:
            Student: Alumno encontrado

        Raises:
            RecordNotFoundError: Si el alumno no existe
        """
        return self.repository.get_by_id_or_fail(student_id)

    def is_student_registered(self, chat_id: int) -> bool:
        """
        Verifica si un alumno está registrado.

        Args:
            chat_id: ID del chat de Telegram

        Returns:
            bool: True si está registrado, False en caso contrario
        """
        return self.repository.exists_by_chat_id(chat_id)

    def list_all_students(self, active_only: bool = True) -> List[Student]:
        """
        Lista todos los alumnos.

        Args:
            active_only: Si True, solo lista alumnos activos

        Returns:
            List[Student]: Lista de alumnos
        """
        if active_only:
            return self.repository.get_active_students()
        return self.repository.get_all()

    def deactivate_student(self, student_id: int) -> Student:
        """
        Desactiva un alumno.

        Args:
            student_id: ID del alumno

        Returns:
            Student: Alumno desactivado

        Raises:
            RecordNotFoundError: Si el alumno no existe
        """
        return self.repository.deactivate_student(student_id)

    def activate_student(self, student_id: int) -> Student:
        """
        Activa un alumno.

        Args:
            student_id: ID del alumno

        Returns:
            Student: Alumno activado

        Raises:
            RecordNotFoundError: Si el alumno no existe
        """
        return self.repository.activate_student(student_id)

    def update_student_name(self, student_id: int, new_name: str) -> Student:
        """
        Actualiza el nombre de un alumno.

        Args:
            student_id: ID del alumno
            new_name: Nuevo nombre

        Returns:
            Student: Alumno actualizado

        Raises:
            ValidationError: Si el nombre es inválido
            RecordNotFoundError: Si el alumno no existe
        """
        # Validar nombre
        new_name = new_name.strip()
        if not new_name:
            raise ValidationError(
                "El nombre del alumno no puede estar vacío",
                {"name": new_name}
            )

        if len(new_name) > MAX_STUDENT_NAME_LENGTH:
            raise ValidationError(
                f"El nombre no puede exceder {MAX_STUDENT_NAME_LENGTH} caracteres",
                {"name": new_name, "length": len(new_name)}
            )

        return self.repository.update_name(student_id, new_name)

    def get_active_students_count(self) -> int:
        """
        Obtiene el número de alumnos activos.

        Returns:
            int: Número de alumnos activos
        """
        return len(self.repository.get_active_students())

    def validate_student_is_active(self, student_id: int) -> None:
        """
        Valida que un alumno esté activo.

        Args:
            student_id: ID del alumno

        Raises:
            RecordNotFoundError: Si el alumno no existe
            StudentNotActiveError: Si el alumno está inactivo
        """
        student = self.repository.get_by_id_or_fail(student_id)
        if not student.is_active:
            raise StudentNotActiveError(student_id)

    def update_student_chat_id(self, student_id: int, chat_id: int) -> Student:
        """
        Actualiza el chat_id de un alumno.

        Se utiliza cuando un alumno hace /start en el bot y ya está registrado
        pero sin chat_id asignado.

        Args:
            student_id: ID del alumno
            chat_id: ID del chat de Telegram

        Returns:
            Student: Alumno actualizado

        Raises:
            RecordNotFoundError: Si el alumno no existe
        """
        return self.repository.update_chat_id(student_id, chat_id)

