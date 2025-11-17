# EntrenaSmart - Iniciar con Docker (Windows PowerShell)
# Uso: .\docker-start.ps1

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗"
Write-Host "║          🚀 Iniciando EntrenaSmart con Docker              ║"
Write-Host "╚════════════════════════════════════════════════════════════════╝"
Write-Host ""

# Verificar Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "   Descárgalo en: https://www.docker.com/products/docker-desktop"
    exit 1
}

# Verificar Docker Compose
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose no está instalado" -ForegroundColor Red
    Write-Host "   Instálalo siguiendo: https://docs.docker.com/compose/install/"
    exit 1
}

# Crear .env si no existe
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creando archivo .env desde .env.docker..." -ForegroundColor Yellow
    Copy-Item ".env.docker" ".env"
    Write-Host "   ✓ Archivo .env creado"
    Write-Host "   ⚠️  Revisa .env y actualiza los valores según sea necesario"
}

Write-Host ""
Write-Host "📦 Levantando servicios con docker-compose..." -ForegroundColor Cyan
Write-Host ""

# Levantar servicios
docker-compose up -d

# Esperar a que los servicios se inicien
Write-Host ""
Write-Host "⏳ Esperando que los servicios se inicien (20 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Verificar estado
Write-Host ""
Write-Host "📊 Estado de los servicios:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "✅ Verificación final:" -ForegroundColor Green

# Verificar API
Write-Host -NoNewline "   API Backend... " -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✓" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  (aún iniciando, revisa con 'docker-compose logs api')" -ForegroundColor Yellow
}

# Verificar Frontend
Write-Host -NoNewline "   Frontend... " -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✓" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  (aún iniciando, revisa con 'docker-compose logs frontend')" -ForegroundColor Yellow
}

# Verificar PostgreSQL
Write-Host -NoNewline "   PostgreSQL... " -ForegroundColor Cyan
try {
    docker-compose exec -T postgres pg_isready -U entrenasmart *> $null
    Write-Host "✓" -ForegroundColor Green
} catch {
    Write-Host "⚠️  (aún iniciando)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║             🎉 EntrenaSmart iniciada correctamente!        ║" -ForegroundColor Green
Write-Host "╠════════════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "║  🌐 Frontend (React):                                      ║" -ForegroundColor Green
Write-Host "║     http://localhost:5173                                  ║" -ForegroundColor Green
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "║  🔌 API Backend (FastAPI):                                 ║" -ForegroundColor Green
Write-Host "║     http://localhost:8000                                  ║" -ForegroundColor Green
Write-Host "║     Documentación: http://localhost:8000/docs              ║" -ForegroundColor Green
Write-Host "║     ReDoc: http://localhost:8000/redoc                     ║" -ForegroundColor Green
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "║  🗄️  Base de Datos (PostgreSQL):                          ║" -ForegroundColor Green
Write-Host "║     localhost:5432                                         ║" -ForegroundColor Green
Write-Host "║     Usuario: entrenasmart                                  ║" -ForegroundColor Green
Write-Host "║     BD: entrenasmart                                       ║" -ForegroundColor Green
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "║  📋 Comandos útiles:                                       ║" -ForegroundColor Green
Write-Host "║     Ver logs:        docker-compose logs -f                ║" -ForegroundColor Green
Write-Host "║     Parar:           docker-compose stop                   ║" -ForegroundColor Green
Write-Host "║     Detener todo:    docker-compose down                   ║" -ForegroundColor Green
Write-Host "║     Bash en API:     docker-compose exec api bash          ║" -ForegroundColor Green
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
