# Start the EntrenaSmart backend API server - PowerShell version

Write-Host "Iniciando Backend API de EntrenaSmart..." -ForegroundColor Green

# Check if .env file exists
if (-Not (Test-Path .env)) {
    Write-Host "Creando archivo .env desde .env.example..." -ForegroundColor Yellow

    @"
# Development configuration
TELEGRAM_BOT_TOKEN=dev_token_placeholder
TRAINER_TELEGRAM_ID=123456789
DATABASE_PATH=storage/entrenasmart.db
API_SECRET_KEY=dev-secret-key
API_CORS_ORIGINS=http://localhost:5173
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
TIMEZONE=America/Bogota
DEBUG=true
ENVIRONMENT=development
"@ | Out-File -FilePath .env -Encoding UTF8

    Write-Host "Archivo .env creado" -ForegroundColor Green
}

# Create required directories
Write-Host "Creando directorios requeridos..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path storage | Out-Null
New-Item -ItemType Directory -Force -Path logs | Out-Null

# Initialize database if it doesn't exist
if (-Not (Test-Path storage\entrenasmart.db)) {
    Write-Host "Inicializando base de datos..." -ForegroundColor Yellow
    $env:PYTHONPATH = "backend;$env:PYTHONPATH"
    python -c "from src.models.base import init_db; init_db()"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error al inicializar la base de datos" -ForegroundColor Red
        exit 1
    }
    Write-Host "Base de datos inicializada" -ForegroundColor Green
}

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