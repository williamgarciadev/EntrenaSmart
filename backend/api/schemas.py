"""
Modelos Pydantic para request/response de la API.

Define la estructura de datos que se envían y reciben en los endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============================================================================
# AUTENTICACIÓN
# ============================================================================

class AuthLoginRequest(BaseModel):
    """Request para login."""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class AuthTokenResponse(BaseModel):
    """Response con token de acceso."""
    access_token: str
    token_type: str = "bearer"
    message: str = "Login exitoso"


class AuthMeResponse(BaseModel):
    """Response con información del usuario actual."""
    user_id: int
    username: str
    role: str


# ============================================================================
# CONFIGURACIÓN SEMANAL
# ============================================================================

class TrainingDayConfigCreate(BaseModel):
    """Request para crear/actualizar configuración de un día."""
    weekday: int = Field(..., ge=0, le=6, description="0=Lunes, 6=Domingo")
    weekday_name: str = Field(..., description="Nombre del día (lunes-domingo)")
    session_type: str = Field(..., description="Tipo de entrenamiento")
    location: str = Field(..., description="Ubicación/piso")


class TrainingDayConfigResponse(BaseModel):
    """Response con configuración de un día."""
    id: int
    weekday: int
    weekday_name: str
    session_type: str
    location: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WeeklyConfigResponse(BaseModel):
    """Response con configuración completa de la semana."""
    configs: list[TrainingDayConfigResponse]
    message: str = "Configuración semanal obtenida"


# ============================================================================
# ESTUDIANTES
# ============================================================================

class StudentBase(BaseModel):
    """Datos base de un estudiante."""
    name: str = Field(..., min_length=1, max_length=100)
    telegram_username: Optional[str] = Field(None, max_length=50)
    is_active: bool = True


class StudentCreate(StudentBase):
    """Request para crear estudiante."""
    pass


class StudentUpdate(StudentBase):
    """Request para actualizar estudiante."""
    pass


class StudentResponse(StudentBase):
    """Response con datos del estudiante."""
    id: int
    chat_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StudentListResponse(BaseModel):
    """Response con lista de estudiantes."""
    students: list[StudentResponse]
    total: int
    message: str = "Estudiantes obtenidos"


# ============================================================================
# ENTRENAMIENTOS
# ============================================================================

class TrainingBase(BaseModel):
    """Datos base de un entrenamiento."""
    weekday: int = Field(..., ge=0, le=6)
    weekday_name: str
    time_str: str = Field(..., description="Hora en formato HH:MM")
    session_type: str
    location: Optional[str] = None


class TrainingCreate(TrainingBase):
    """Request para crear entrenamiento."""
    student_id: int


class TrainingResponse(TrainingBase):
    """Response con datos del entrenamiento."""
    id: int
    student_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StudentTrainingsResponse(BaseModel):
    """Response con entrenamientos de un estudiante."""
    student_id: int
    student_name: str
    trainings: list[TrainingResponse]
    total: int = 0
    message: str = "Entrenamientos obtenidos exitosamente"


# ============================================================================
# RESPUESTAS GENÉRICAS
# ============================================================================

class SuccessResponse(BaseModel):
    """Response genérico de éxito."""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Response genérico de error."""
    success: bool = False
    detail: str
    error_type: str = "GeneralError"


# ============================================================================
# DASHBOARD
# ============================================================================

class StatCard(BaseModel):
    """Datos para una tarjeta de estadística."""
    title: str
    value: int | str
    change: Optional[int] = None
    trend: Optional[str] = None  # "up", "down"


class DashboardStatsResponse(BaseModel):
    """Response con estadísticas del dashboard."""
    total_students: int
    active_students: int
    trainings_this_week: int
    response_rate: float
    timestamp: datetime


# ============================================================================
# PLANTILLAS DE MENSAJES
# ============================================================================

class TemplateCreate(BaseModel):
    """Request para crear plantilla de mensaje."""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre de la plantilla")
    content: str = Field(..., min_length=1, description="Contenido del mensaje con variables {var}")
    variables: list[str] = Field(default_factory=list, description="Variables disponibles")
    is_active: bool = True


class TemplateUpdate(BaseModel):
    """Request para actualizar plantilla."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1)
    variables: Optional[list[str]] = None
    is_active: Optional[bool] = None


class TemplateResponse(BaseModel):
    """Response con datos de plantilla."""
    id: int
    name: str
    content: str
    variables: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """Response con lista de plantillas."""
    templates: list[TemplateResponse]
    total: int
    message: str = "Plantillas obtenidas"


# ============================================================================
# PROGRAMACIÓN DE ENVÍOS
# ============================================================================

class MessageScheduleCreate(BaseModel):
    """Request para crear una programación de envío."""
    template_id: int = Field(..., description="ID de la plantilla a enviar")
    student_id: int = Field(..., description="ID del estudiante")
    hour: int = Field(..., ge=0, le=23, description="Hora (0-23)")
    minute: int = Field(..., ge=0, le=59, description="Minuto (0-59)")
    days_of_week: list[int] = Field(..., description="Días de semana (0=lunes, 6=domingo)")
    is_active: bool = True


class MessageScheduleUpdate(BaseModel):
    """Request para actualizar programación."""
    template_id: Optional[int] = None
    student_id: Optional[int] = None
    hour: Optional[int] = Field(None, ge=0, le=23)
    minute: Optional[int] = Field(None, ge=0, le=59)
    days_of_week: Optional[list[int]] = None
    is_active: Optional[bool] = None


class MessageScheduleResponse(BaseModel):
    """Response con datos de programación."""
    id: int
    template_id: int
    student_id: int
    hour: int
    minute: int
    days_of_week: list[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageScheduleListResponse(BaseModel):
    """Response con lista de programaciones."""
    schedules: list[MessageScheduleResponse]
    total: int
    message: str = "Programaciones obtenidas"
