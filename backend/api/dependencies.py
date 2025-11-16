"""
Dependencias compartidas para la API.

Incluye autenticación, validación y acceso a servicios.
"""
import os
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

# Simulación de usuario autenticado
# En producción, usar JWT tokens y verificar contra base de datos


def verify_trainer_access(credentials: HTTPAuthCredentials = Depends(HTTPBearer())):
    """
    Verifica que el token corresponde al entrenador autorizado.

    En producción, validar JWT y verificar contra TRAINER_TELEGRAM_ID.
    """
    secret_key = os.getenv("API_SECRET_KEY", "dev-secret-key")

    if credentials.credentials != secret_key and credentials.credentials != "dev-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

    return {"user_id": 1, "role": "trainer"}


async def get_current_trainer(
    trainer: dict = Depends(verify_trainer_access)
):
    """Obtiene el entrenador actual validado."""
    return trainer
