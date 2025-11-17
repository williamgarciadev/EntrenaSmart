"""
EntrenaSmart API - Backend FastAPI
==================================

API REST para gestionar el backoffice del bot de entrenamientos.
Punto de entrada principal de la aplicación FastAPI.

Se ejecuta independientemente del bot de Telegram pero comparte la misma base de datos.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routers import auth, training_config, templates, schedules, students
from .middleware import verify_auth_header

# Configuración CORS
CORS_ORIGINS = os.getenv("API_CORS_ORIGINS", "http://localhost:5173").split(",")


# Variable global para la instancia del bot de Telegram
_telegram_bot = None


def get_telegram_bot():
    """
    Obtiene la instancia singleton del bot de Telegram.

    Returns:
        Bot: Instancia del bot o None si no está configurado
    """
    return _telegram_bot


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Contexto de ciclo de vida de la aplicación.

    Se ejecuta al iniciar (yield) y al detener.
    """
    global _telegram_bot

    # Startup
    print("[STARTUP] API EntrenaSmart iniciada")
    print("[STARTUP] Inicializando base de datos...")

    # Importar init_db y todos los modelos para que se registren
    from backend.src.models.base import init_db
    from backend.src.models import (
        Student,
        Training,
        TrainingDayConfig,
        Feedback,
        MessageSchedule,
        MessageTemplate
    )

    # Inicializar base de datos
    init_db()
    print("[STARTUP] Base de datos inicializada")

    # Inicializar bot de Telegram (singleton)
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if telegram_token:
        print("[STARTUP] Inicializando bot de Telegram...")
        from telegram import Bot
        _telegram_bot = Bot(token=telegram_token)
        print("[STARTUP] ✅ Bot de Telegram inicializado")
    else:
        print("[STARTUP] ⚠️  TELEGRAM_BOT_TOKEN no configurado - funciones de mensajería deshabilitadas")

    yield

    # Shutdown
    print("[SHUTDOWN] API EntrenaSmart detenida")


# Crear aplicación FastAPI
app = FastAPI(
    title="EntrenaSmart API",
    description="API REST para gestionar entrenamientos personalizados",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rutas
@app.get("/", tags=["Health"])
async def root():
    """Verificar que la API está funcionando."""
    return {
        "status": "ok",
        "message": "EntrenaSmart API v1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(training_config.router, prefix="/api/training-config", tags=["Training Config"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(schedules.router, prefix="/api/schedules", tags=["Schedules"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])


# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador centralizado de excepciones."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
