"""
Middleware personalizado para la API.

Incluye validación de autenticación, logging y manejo de errores.
"""
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import HTTPException, status
from .logger import logger


async def verify_auth_header(request: Request, call_next):
    """
    Middleware para verificar tokens de autenticación.

    Requerido para todos los endpoints excepto /health, /docs, /redoc.
    """
    # Rutas públicas
    public_paths = ["/", "/health", "/docs", "/redoc", "/openapi.json"]

    if request.url.path in public_paths:
        return await call_next(request)

    # Verificar header Authorization
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado"
        )

    # Expected format: "Bearer <token>"
    try:
        scheme, credentials = auth_header.split()
        if scheme.lower() != "bearer":
            raise ValueError("Esquema inválido")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token inválido"
        )

    # Validar token (en desarrollo, aceptar cualquier cosa)
    if os.getenv("DEBUG", "False").lower() == "true":
        logger.debug(f"Token aceptado en modo DEBUG: {credentials[:20]}...")
        return await call_next(request)

    # En producción, validar token
    secret_key = os.getenv("API_SECRET_KEY")
    if credentials != secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    return await call_next(request)
