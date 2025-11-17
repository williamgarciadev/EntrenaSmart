"""
Router de gestión de estudiantes.

Endpoints para crear, actualizar, listar y eliminar estudiantes
del sistema de entrenamientos.
Persiste datos en PostgreSQL a través de StudentService.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from ..schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentListResponse,
    SuccessResponse
)
from ..dependencies import get_current_trainer
from ..logger import logger
from src.models.base import get_db_context
from src.services.student_service import StudentService
from src.core.exceptions import (
    ValidationError,
    DuplicateRecordError,
    RecordNotFoundError
)

router = APIRouter()


@router.get("", response_model=StudentListResponse)
async def list_students(
    active_only: bool = False,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Listar todos los estudiantes desde la BD.

    Args:
        active_only: Si es True, solo retorna estudiantes activos
    """
    logger.info(f"Listando estudiantes desde BD (active_only={active_only})")

    try:
        with get_db_context() as db:
            service = StudentService(db)
            db_students = service.list_all_students(active_only=active_only)

        # Convertir objetos ORM a response models
        students = [
            StudentResponse(
                id=student.id,
                name=student.name,
                telegram_username=student.telegram_username,
                chat_id=student.chat_id,
                is_active=student.is_active,
                created_at=student.created_at,
                updated_at=student.updated_at
            )
            for student in db_students
        ]

        logger.info(f"✅ Obtenidos {len(students)} estudiantes de la BD")

        return StudentListResponse(
            students=students,
            total=len(students)
        )

    except Exception as e:
        logger.error(f"Error listando estudiantes: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar estudiantes"
        )


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Obtener un estudiante específico desde la BD.

    Args:
        student_id: ID del estudiante
    """
    try:
        with get_db_context() as db:
            service = StudentService(db)
            student = service.get_student_by_id_or_fail(student_id)

        logger.info(f"Obtenido estudiante desde BD: {student.name}")

        return StudentResponse(
            id=student.id,
            name=student.name,
            telegram_username=student.telegram_username,
            chat_id=student.chat_id,
            is_active=student.is_active,
            created_at=student.created_at,
            updated_at=student.updated_at
        )

    except RecordNotFoundError:
        logger.warning(f"Estudiante {student_id} no encontrado en BD")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante {student_id} no encontrado"
        )
    except Exception as e:
        logger.error(f"Error obteniendo estudiante {student_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estudiante"
        )


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student: StudentCreate,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Crear un nuevo estudiante en la BD.

    Args:
        student: Datos del estudiante a crear
    """
    try:
        with get_db_context() as db:
            service = StudentService(db)
            new_student = service.register_student(
                name=student.name,
                telegram_username=student.telegram_username,
                chat_id=None  # Se asigna cuando el alumno hace /start
            )
            # Auto-commit al salir del contexto

        logger.info(f"✅ Estudiante creado en BD: {new_student.name}")

        return StudentResponse(
            id=new_student.id,
            name=new_student.name,
            telegram_username=new_student.telegram_username,
            chat_id=new_student.chat_id,
            is_active=new_student.is_active,
            created_at=new_student.created_at,
            updated_at=new_student.updated_at
        )

    except ValidationError as e:
        logger.warning(f"Error de validación: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DuplicateRecordError as e:
        logger.warning(f"Estudiante duplicado: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creando estudiante: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear estudiante"
        )


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_update: StudentUpdate,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Actualizar un estudiante existente en la BD.

    Args:
        student_id: ID del estudiante
        student_update: Datos a actualizar
    """
    try:
        with get_db_context() as db:
            service = StudentService(db)

            # Verificar que el estudiante existe
            student = service.get_student_by_id_or_fail(student_id)

            # Actualizar nombre si se proporciona
            if student_update.name:
                student = service.update_student_name(student_id, student_update.name)

            # Actualizar telegram_username si se proporciona
            if student_update.telegram_username is not None:
                student.telegram_username = student_update.telegram_username

            # Actualizar is_active
            if student_update.is_active is not None:
                if student_update.is_active != student.is_active:
                    if student_update.is_active:
                        student = service.activate_student(student_id)
                    else:
                        student = service.deactivate_student(student_id)

            db.commit()
            db.refresh(student)
            # Auto-commit al salir del contexto

        logger.info(f"✅ Estudiante actualizado en BD: {student.name}")

        return StudentResponse(
            id=student.id,
            name=student.name,
            telegram_username=student.telegram_username,
            chat_id=student.chat_id,
            is_active=student.is_active,
            created_at=student.created_at,
            updated_at=student.updated_at
        )

    except RecordNotFoundError:
        logger.warning(f"Estudiante {student_id} no encontrado en BD")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante {student_id} no encontrado"
        )
    except ValidationError as e:
        logger.warning(f"Error de validación: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DuplicateRecordError as e:
        logger.warning(f"Estudiante duplicado: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error actualizando estudiante: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar estudiante"
        )


@router.delete("/{student_id}", response_model=SuccessResponse)
async def delete_student(
    student_id: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Eliminar un estudiante de la BD (soft delete - inactiva).

    Args:
        student_id: ID del estudiante a eliminar
    """
    try:
        with get_db_context() as db:
            service = StudentService(db)
            student = service.deactivate_student(student_id)
            # Auto-commit al salir del contexto

        logger.info(f"✅ Estudiante inactivado en BD: {student.name}")

        return SuccessResponse(
            message=f"Estudiante '{student.name}' eliminado exitosamente"
        )

    except RecordNotFoundError:
        logger.warning(f"Estudiante {student_id} no encontrado en BD")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante {student_id} no encontrado"
        )
    except Exception as e:
        logger.error(f"Error eliminando estudiante: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar estudiante"
        )
