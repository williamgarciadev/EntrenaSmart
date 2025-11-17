@echo off
REM Start the EntrenaSmart backend API server - Windows version

echo [92mIniciando Backend API de EntrenaSmart...[0m

REM Check if .env file exists
if not exist .env (
    echo [93mCreando archivo .env desde .env.example...[0m
    (
        echo # Development configuration
        echo TELEGRAM_BOT_TOKEN=dev_token_placeholder
        echo TRAINER_TELEGRAM_ID=123456789
        echo.
        echo # PostgreSQL Database ^(usar PostgreSQL en lugar de SQLite^)
        echo DATABASE_URL=postgresql://entrenasmart:entrenasmart123@localhost:5432/entrenasmart
        echo.
        echo # API Configuration
        echo API_SECRET_KEY=dev-secret-key
        echo API_CORS_ORIGINS=http://localhost:5173
        echo.
        echo # Logging
        echo LOG_LEVEL=INFO
        echo LOG_FILE=logs/bot.log
        echo.
        echo # Timezone
        echo TIMEZONE=America/Bogota
        echo.
        echo # Development mode
        echo DEBUG=true
        echo ENVIRONMENT=development
    ) > .env
    echo [92mArchivo .env creado[0m
)

REM Create required directories
echo [93mCreando directorios requeridos...[0m
if not exist storage mkdir storage
if not exist logs mkdir logs

REM Initialize database tables
echo [93mInicializando tablas de la base de datos PostgreSQL...[0m
set PYTHONPATH=backend;%PYTHONPATH%
python -c "from src.models.base import init_db; init_db()"
if errorlevel 1 (
    echo [91mError al inicializar la base de datos[0m
    echo [93mAsegurate de que PostgreSQL este corriendo y accesible en localhost:5432[0m
    exit /b 1
)
echo [92mBase de datos inicializada[0m

REM Check if dependencies are installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo [93mInstalando dependencias de Python...[0m
    pip install -q -r requirements.txt
    if errorlevel 1 (
        echo [91mError al instalar dependencias[0m
        exit /b 1
    )
    echo [92mDependencias instaladas[0m
)

REM Start the server
echo [92mIniciando servidor API en http://localhost:8000[0m
echo [93mPresiona Ctrl+C para detener el servidor[0m
echo.

set PYTHONPATH=backend;%PYTHONPATH%
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
