# Start the EntrenaSmart backend API server - PowerShell version

Write-Host "Iniciando Backend API de EntrenaSmart..." -ForegroundColor Green

# Check if .env file exists
if (-Not (Test-Path .env)) {
    Write-Host "Creando archivo .env desde .env.example..." -ForegroundColor Yellow

    @"
# Development configuration
TELEGRAM_BOT_TOKEN=dev_token_placeholder
TRAINER_TELEGRAM_ID=123456789

# PostgreSQL Database (usar PostgreSQL en lugar de SQLite)
DATABASE_URL=postgresql://entrenasmart:entrenasmart123@localhost:5432/entrenasmart

# API Configuration
API_SECRET_KEY=dev-secret-key
API_CORS_ORIGINS=http://localhost:5173

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Timezone
TIMEZONE=America/Bogota

# Development mode
DEBUG=true
ENVIRONMENT=development
"@ | Out-File -FilePath .env -Encoding UTF8

    Write-Host "Archivo .env creado" -ForegroundColor Green
}

# Create required directories
Write-Host "Creando directorios requeridos..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path storage | Out-Null
New-Item -ItemType Directory -Force -Path logs | Out-Null

# Initialize database tables
Write-Host "Inicializando tablas de la base de datos PostgreSQL..." -ForegroundColor Yellow
$env:PYTHONPATH = "backend;$env:PYTHONPATH"
python -c "from src.models.base import init_db; init_db()"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error al inicializar la base de datos" -ForegroundColor Red
    Write-Host "Asegurate de que PostgreSQL este corriendo y accesible en localhost:5432" -ForegroundColor Yellow
    exit 1
}
Write-Host "Base de datos inicializada" -ForegroundColor Green

# Check if dependencies are installed
python -c "import fastapi" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Instalando dependencias de Python..." -ForegroundColor Yellow
    pip install -q -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error al instalar dependencias" -ForegroundColor Red
        exit 1
    }
    Write-Host "Dependencias instaladas" -ForegroundColor Green
}

# Start the server
Write-Host "Iniciando servidor API en http://localhost:8000" -ForegroundColor Green
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

$env:PYTHONPATH = "backend;$env:PYTHONPATH"
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
