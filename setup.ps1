# EntrenaSmart - Setup Completo con Docker (Windows PowerShell)
# Uso: .\setup.ps1

$ErrorActionPreference = "Stop"

# Colores
$colors = @{
    'Red'    = [System.Console]::ForegroundColor = 'Red'
    'Green'  = [System.Console]::ForegroundColor = 'Green'
    'Yellow' = [System.Console]::ForegroundColor = 'Yellow'
    'Blue'   = [System.Console]::ForegroundColor = 'Blue'
    'Default' = [System.Console]::ResetColor()
}

function Print-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
    Write-Host "║ $Text" -ForegroundColor Blue
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
    Write-Host ""
}

function Print-Step {
    param([string]$Text)
    Write-Host "▶ $Text" -ForegroundColor Yellow
}

function Print-Success {
    param([string]$Text)
    Write-Host "✓ $Text" -ForegroundColor Green
}

function Print-Error {
    param([string]$Text)
    Write-Host "✗ $Text" -ForegroundColor Red
}

function Print-Info {
    param([string]$Text)
    Write-Host "ℹ $Text" -ForegroundColor Blue
}

# ============================================================================
# Verificaciones Preliminares
# ============================================================================

Print-Header "Verificando Requisitos Previos"

# Verificar Docker
Print-Step "Verificando Docker..."
try {
    $dockerVersion = docker --version
    if ($dockerVersion) {
        Print-Success $dockerVersion
    }
} catch {
    Print-Error "Docker no está instalado"
    Write-Host ""
    Write-Host "Descárgalo en: https://www.docker.com/products/docker-desktop"
    exit 1
}

# Verificar Docker Compose
Print-Step "Verificando Docker Compose..."
try {
    $composeVersion = docker-compose --version
    if ($composeVersion) {
        Print-Success $composeVersion
    }
} catch {
    Print-Error "Docker Compose no está instalado"
    Write-Host ""
    Write-Host "Instálalo siguiendo: https://docs.docker.com/compose/install/"
    exit 1
}

# Verificar Git
Print-Step "Verificando Git..."
try {
    $gitVersion = git --version
    if ($gitVersion) {
        Print-Success $gitVersion
    }
} catch {
    Print-Error "Git no está instalado"
    exit 1
}

# ============================================================================
# Preparar Entorno
# ============================================================================

Print-Header "Preparando Entorno"

# Crear .env desde .env.docker si no existe
Print-Step "Configurando variables de entorno..."
if (-not (Test-Path ".env")) {
    Print-Info ".env no existe, creando desde .env.docker"
    Copy-Item ".env.docker" ".env"
    Print-Success ".env creado"
    Write-Host ""
    Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Yellow
    Write-Host "   Revisa el archivo .env y actualiza:"
    Write-Host "   - POSTGRES_PASSWORD"
    Write-Host "   - TELEGRAM_BOT_TOKEN (si usas el bot)"
    Write-Host "   - API_CORS_ORIGINS (si cambias puertos)"
    Write-Host ""
    Read-Host "   Presiona Enter cuando hayas revisado .env"
} else {
    Print-Success ".env ya existe (sin cambios)"
}

# ============================================================================
# Construcción e Inicio
# ============================================================================

Print-Header "Construyendo e Iniciando Servicios"

Print-Step "Construyendo imágenes Docker..."
Write-Host ""
docker-compose build
Write-Host ""
Print-Success "Imágenes construidas"

Print-Step "Iniciando servicios..."
docker-compose up -d
Print-Success "Servicios iniciados"

# Esperar a que los servicios se estabilicen
Print-Step "Esperando que los servicios se estabilicen (30 segundos)..."
for ($i = 30; $i -gt 0; $i--) {
    Write-Host "`r   Esperando: ${i}s  " -NoNewline
    Start-Sleep -Seconds 1
}
Write-Host ""
Print-Success "Servicios estabilizados"

# ============================================================================
# Verificación de Salud
# ============================================================================

Print-Header "Verificando Salud de Servicios"

# PostgreSQL
Print-Step "Verificando PostgreSQL..."
try {
    docker-compose exec -T postgres pg_isready -U entrenasmart *> $null
    Print-Success "PostgreSQL disponible"
} catch {
    Print-Error "PostgreSQL aún iniciando (puede tomar más tiempo)"
}

# API Backend
Print-Step "Verificando API Backend..."
$maxAttempts = 10
$attempt = 0
while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Print-Success "API Backend disponible"
            break
        }
    } catch {
        $attempt++
        if ($attempt -lt $maxAttempts) {
            Start-Sleep -Seconds 2
        }
    }
}
if ($attempt -eq $maxAttempts) {
    Print-Error "API Backend aún iniciando (puede tomar más tiempo)"
}

# Frontend
Print-Step "Verificando Frontend..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Print-Success "Frontend disponible"
    }
} catch {
    Print-Info "Frontend aún iniciando (es normal, puede tomar 30-60 segundos)"
}

# ============================================================================
# Estado Final
# ============================================================================

Print-Header "Estado de Servicios"
docker-compose ps

# ============================================================================
# Instrucciones Finales
# ============================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║                  ✅ SETUP COMPLETADO EXITOSAMENTE             ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "╠════════════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║  🌐 ACCESO A SERVICIOS:                                        ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║     Frontend (React/Vite):                                     ║" -ForegroundColor Green
Write-Host "║     🔗 http://localhost:5173                                    ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║     API Backend (FastAPI):                                     ║" -ForegroundColor Green
Write-Host "║     🔗 http://localhost:8000                                    ║" -ForegroundColor Green
Write-Host "║     📖 Documentación: http://localhost:8000/docs               ║" -ForegroundColor Green
Write-Host "║     📋 ReDoc: http://localhost:8000/redoc                      ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║     Base de Datos PostgreSQL:                                  ║" -ForegroundColor Green
Write-Host "║     🔗 localhost:5432                                           ║" -ForegroundColor Green
Write-Host "║     👤 Usuario: entrenasmart                                    ║" -ForegroundColor Green
Write-Host "║     📊 Base de Datos: entrenasmart                              ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "╠════════════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  📋 COMANDOS ÚTILES:                                           ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║     Ver logs en tiempo real:                                   ║" -ForegroundColor Green
Write-Host "║     PS> docker-compose logs -f                                 ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║     Detener servicios:                                         ║" -ForegroundColor Green
Write-Host "║     PS> docker-compose stop                                    ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║     Reiniciar servicios:                                       ║" -ForegroundColor Green
Write-Host "║     PS> docker-compose restart                                 ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║     Entrar a bash en API:                                      ║" -ForegroundColor Green
Write-Host "║     PS> docker-compose exec api bash                           ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║     Acceder a PostgreSQL:                                      ║" -ForegroundColor Green
Write-Host "║     PS> docker-compose exec postgres psql -U entrenasmart      ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║     Ver utilidades:                                            ║" -ForegroundColor Green
Write-Host "║     PS> .\docker-utils.ps1                                     ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "╠════════════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  📚 DOCUMENTACIÓN:                                             ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║     Lee DOCKER.md para:                                        ║" -ForegroundColor Green
Write-Host "║     • Configuración avanzada                                   ║" -ForegroundColor Green
Write-Host "║     • Backups y restauración                                   ║" -ForegroundColor Green
Write-Host "║     • Solución de problemas                                    ║" -ForegroundColor Green
Write-Host "║     • Deploy a producción                                      ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║     Lee README.md para:                                        ║" -ForegroundColor Green
Write-Host "║     • Descripción general del proyecto                         ║" -ForegroundColor Green
Write-Host "║     • Características principales                              ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  NOTA:" -ForegroundColor Yellow
Write-Host "   Si algún servicio muestra 'Exit' o 'Restarting', revisa los logs:"
Write-Host "   PS> docker-compose logs [servicio]"
Write-Host ""
Write-Host "📝 PRÓXIMOS PASOS:" -ForegroundColor Yellow
Write-Host "   1. Abre http://localhost:5173 en tu navegador"
Write-Host "   2. Revisa que todo funcione correctamente"
Write-Host "   3. Si hay problemas, consulta DOCKER.md"
Write-Host ""
