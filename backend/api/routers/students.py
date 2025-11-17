"""
Router de gestión de estudiantes.

Endpoints para crear, actualizar, listar y eliminar estudiantes
del sistema de entrenamientos.
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

router = APIRouter()

# Simulación de datos en memoria para desarrollo
MOCK_STUDENTS = {
    1: {
        "id": 1,
        "name": "Juan García",
        "telegram_username": "juangarcia",
        "chat_id": 123456789,
        "is_active": True,
        "created_at": "2025-11-16T00:00:00",
        "updated_at": "2025-11-16T00:00:00"
    },
    2: {
        "id": 2,
        "name": "María López",
        "telegram_username": "marialopez",
        "chat_id": 987654321,
        "is_active": True,
        "created_at": "2025-11-16T00:00:00",
        "updated_at": "2025-11-16T00:00:00"
    },
    3: {
        "id": 3,
        "name": "Carlos Rodríguez",
        "telegram_username": "carlosrod",
        "chat_id": 555666777,
        "is_active": True,
        "created_at": "2025-11-16T00:00:00",
        "updated_at": "2025-11-16T00:00:00"
    },
    4: {
        "id": 4,
        "name": "Ana Martínez",
        "telegram_username": "anamartinez",
        "chat_id": None,
        "is_active": True,
        "created_at": "2025-11-16T00:00:00",
        "updated_at": "2025-11-16T00:00:00"
    },
}

_next_id = 5


@router.get("", response_model=StudentListResponse)
async def list_students(
    active_only: bool = False,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Listar todos los estudiantes.

    Args:
        active_only: Si es True, solo retorna estudiantes activos
    """
    logger.info("Listando estudiantes")

    students = list(MOCK_STUDENTS.values())

    if active_only:
        students = [s for s in students if s["is_active"]]

    return StudentListResponse(
        students=[StudentResponse(**s) for s in students],
        total=len(students)
    )


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Obtener un estudiante específico.

    Args:
        student_id: ID del estudiante
    """
    if student_id not in MOCK_STUDENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante {student_id} no encontrado"
        )

    student = MOCK_STUDENTS[student_id]
    logger.info(f"Obteniendo estudiante: {student['name']}")

    return StudentResponse(**student)


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student: StudentCreate,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Crear un nuevo estudiante.

    Args:
        student: Datos del estudiante a crear
    """
    global _next_id

    # Validar que el nombre sea único
    for s in MOCK_STUDENTS.values():
        if s["name"].lower() == student.name.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un estudiante con el nombre '{student.name}'"
            )

    # Validar que telegram_username sea único si se proporciona
    if student.telegram_username:
        for s in MOCK_STUDENTS.values():
            if s["telegram_username"] and s["telegram_username"].lower() == student.telegram_username.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un estudiante con el usuario Telegram '{student.telegram_username}'"
                )

    now = datetime.now().isoformat()
    new_student = {
        "id": _next_id,
        "name": student.name,
        "telegram_username": student.telegram_username,
        "chat_id": None,
        "is_active": student.is_active,
        "created_at": now,
        "updated_at": now
    }

    MOCK_STUDENTS[_next_id] = new_student
    _next_id += 1

    logger.info(f"Estudiante creado: {student.name}")

    return StudentResponse(**new_student)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_update: StudentUpdate,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Actualizar un estudiante existente.

    Args:
        student_id: ID del estudiante
        student_update: Datos a actualizar
    """
    if student_id not in MOCK_STUDENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante {student_id} no encontrado"
        )

    student = MOCK_STUDENTS[student_id]

    # Actualizar campos si se proporcionan
    if student_update.name is not None:
        # Validar que el nuevo nombre sea único
        for s in MOCK_STUDENTS.values():
            if s["id"] != student_id and s["name"].lower() == student_update.name.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un estudiante con el nombre '{student_update.name}'"
                )
        student["name"] = student_update.name

    if student_update.telegram_username is not None:
        # Validar que el nuevo username sea único
        if student_update.telegram_username:
            for s in MOCK_STUDENTS.values():
                if s["id"] != student_id and s["telegram_username"] and \
                   s["telegram_username"].lower() == student_update.telegram_username.lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ya existe un estudiante con el usuario Telegram '{student_update.telegram_username}'"
                    )
        student["telegram_username"] = student_update.telegram_username

    if student_update.is_active is not None:
        student["is_active"] = student_update.is_active

    student["updated_at"] = datetime.now().isoformat()

    logger.info(f"Estudiante actualizado: {student['name']}")

    return StudentResponse(**student)


@router.delete("/{student_id}", response_model=SuccessResponse)
async def delete_student(
    student_id: int,
    trainer: dict = Depends(get_current_trainer)
):
    """
    Eliminar un estudiante (soft delete - inactiva).

    Args:
        student_id: ID del estudiante a eliminar
    """
    if student_id not in MOCK_STUDENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante {student_id} no encontrado"
        )

    student = MOCK_STUDENTS[student_id]
    student["is_active"] = False
    student["updated_at"] = datetime.now().isoformat()

    logger.info(f"Estudiante inactivado: {student['name']}")

    return SuccessResponse(
        message=f"Estudiante '{student['name']}' eliminado exitosamente"
    )
