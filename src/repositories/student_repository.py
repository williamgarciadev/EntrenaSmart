# -*- coding: utf-8 -*-
"""
Repositorio de Alumnos
======================
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.student import Student
from src.repositories.base_repository import BaseRepository
from src.core.exceptions import RecordNotFoundError


class StudentRepository(BaseRepository[Student]):
    """Repositorio para operaciones de alumnos."""

    def __init__(self, db: Session):
        """Inicializa con sesion de BD."""
        super().__init__(db, Student)

    def create_student(self, name: str, telegram_username: Optional[str] = None, chat_id: Optional[int] = None) -> Student:
        """
        Crea un nuevo alumno.

        Args:
            name: Nombre del alumno
            telegram_username: Username de Telegram (opcional)
            chat_id: ID del chat de Telegram (opcional, se asigna cuando alumno inicia sesión)

        Returns:
            Student: Alumno creado
        """
        student = Student(
            name=name,
            telegram_username=telegram_username,
            chat_id=chat_id
        )
        return self.create(student)

    def get_by_chat_id(self, chat_id: int) -> Optional[Student]:
        """Obtiene alumno por chat_id."""
        return self.db.query(Student).filter(Student.chat_id == chat_id).first()

    def get_by_chat_id_or_fail(self, chat_id: int) -> Student:
        """Obtiene alumno o lanza excepcion."""
        student = self.get_by_chat_id(chat_id)
        if not student:
            raise RecordNotFoundError("Student", {"chat_id": chat_id})
        return student

    def exists_by_chat_id(self, chat_id: int) -> bool:
        """Verifica si existe alumno con este chat_id."""
        return self.db.query(
            self.db.query(Student).filter(Student.chat_id == chat_id).exists()
        ).scalar()

    def get_active_students(self) -> List[Student]:
        """Obtiene todos los alumnos activos."""
        return self.db.query(Student).filter(Student.is_active == True).all()

    def deactivate_student(self, student_id: int) -> Student:
        """Desactiva un alumno."""
        student = self.get_by_id(student_id)
        if student:
            student.deactivate()
            self.update(student)
        return student

    def activate_student(self, student_id: int) -> Student:
        """Activa un alumno."""
        student = self.get_by_id(student_id)
        if student:
            student.activate()
            self.update(student)
        return student

    def get_by_id_or_fail(self, student_id: int) -> Student:
        """Obtiene alumno por ID o falla."""
        student = self.get_by_id(student_id)
        if not student:
            raise RecordNotFoundError("Student", {"id": student_id})
        return student

    def update_name(self, student_id: int, new_name: str) -> Student:
        """Actualiza nombre del alumno."""
        student = self.get_by_id(student_id)
        if student:
            student.name = new_name
            self.update(student)
        return student
