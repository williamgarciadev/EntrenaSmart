"""
Router de autenticación.

Endpoints para login y obtener información del usuario actual.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from ..schemas import AuthLoginRequest, AuthTokenResponse, AuthMeResponse
from ..dependencies import get_current_trainer

router = APIRouter()

# Token de prueba para desarrollo
DEV_TOKEN = "dev-token"
DEV_USERNAME = "admin"
DEV_PASSWORD = "admin123"


@router.post("/login", response_model=AuthTokenResponse)
async def login(credentials: AuthLoginRequest):
    """
    Login del entrenador.

    En desarrollo, aceptar username=admin y password=admin123.
    En producción, validar contra base de datos con hash bcrypt.
    """
    # Validación simple para desarrollo
    if (credentials.username != DEV_USERNAME or
        credentials.password != DEV_PASSWORD):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    return AuthTokenResponse(
        access_token=DEV_TOKEN,
        message="Login exitoso"
    )


@router.get("/me", response_model=AuthMeResponse)
async def get_me(trainer: dict = Depends(get_current_trainer)):
    """
    Obtener información del usuario autenticado.
    """
    return AuthMeResponse(
        user_id=trainer["user_id"],
        username=DEV_USERNAME,
        role=trainer["role"]
    )


@router.post("/logout")
async def logout(trainer: dict = Depends(get_current_trainer)):
    """
    Logout del usuario.

    En producción, invalidar el token.
    """
    return {"message": "Logout exitoso"}
