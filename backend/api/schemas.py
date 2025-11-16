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
