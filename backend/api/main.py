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

from backend.api.routers import auth, training_config
from backend.api.middleware import verify_auth_header

# Configuración CORS
CORS_ORIGINS = os.getenv("API_CORS_ORIGINS", "http://localhost:5173").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Contexto de ciclo de vida de la aplicación.

    Se ejecuta al iniciar (yield) y al detener.
    """
    # Startup
    print("🚀 API EntrenaSmart iniciada")
    yield
    # Shutdown
    print("🛑 API EntrenaSmart detenida")


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
