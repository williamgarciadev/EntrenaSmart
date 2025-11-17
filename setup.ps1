<#
.SYNOPSIS
    Script de configuración automática para EntrenaSmart en Windows

.DESCRIPTION
    Configura el entorno de desarrollo completo:
    - Verifica requisitos (Python, Node.js, Git)
    - Crea entorno virtual de Python
    - Instala dependencias de backend y frontend
    - Configura variables de entorno
    - Inicializa la base de datos
    - Opcionalmente ejecuta el proyecto

.PARAMETER SkipChecks
    Omite la verificación de requisitos

.PARAMETER RunAfterSetup
    Ejecuta el proyecto después de la configuración

.EXAMPLE
    .\setup.ps1
    .\setup.ps1 -RunAfterSetup
    .\setup.ps1 -SkipChecks -RunAfterSetup

.NOTES
    Versión: 1.0.0
    Autor: EntrenaSmart Team
    Requiere: PowerShell 5.1 o superior
#>

param(
    [switch]$SkipChecks,
    [switch]$RunAfterSetup
)

# Configuración
$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"
$VenvDir = Join-Path $ProjectRoot ".venv"
$EnvFile = Join-Path $ProjectRoot ".env"
$EnvExample = Join-Path $ProjectRoot ".env.example"

# Colores para output
function Write-ColorOutput {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success { Write-ColorOutput $args[0] "Green" }
function Write-Info { Write-ColorOutput $args[0] "Cyan" }
function Write-Warning { Write-ColorOutput $args[0] "Yellow" }
function Write-Error { Write-ColorOutput $args[0] "Red" }
function Write-Step { Write-ColorOutput "`n==> $($args[0])" "Magenta" }

# Banner
Write-Host @"

    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║     💪 ENTRENA SMART - SETUP WIZARD       ║
    ║                                           ║
    ║     Configuración Automática v1.0.0       ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# ==============================================================================
# PASO 1: VERIFICAR REQUISITOS
# ==============================================================================

if (-not $SkipChecks) {
    Write-Step "Verificando requisitos del sistema..."

    # Verificar Python
    Write-Info "Verificando Python 3.11+..."
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]

            if ($major -eq 3 -and $minor -ge 11) {
                Write-Success "✓ Python $major.$minor encontrado"
            } else {
                Write-Error "✗ Python 3.11+ requerido, encontrado: $major.$minor"
                Write-Warning "Descarga Python 3.11+ desde: https://www.python.org/downloads/"
                exit 1
            }
        }
    } catch {
        Write-Error "✗ Python no encontrado en PATH"
        Write-Warning "Instala Python 3.11+ desde: https://www.python.org/downloads/"
        exit 1
    }

    # Verificar Node.js
    Write-Info "Verificando Node.js..."
    try {
        $nodeVersion = node --version 2>&1
        if ($nodeVersion -match "v(\d+)") {
            $major = [int]$matches[1]
            if ($major -ge 18) {
                Write-Success "✓ Node.js $nodeVersion encontrado"
            } else {
                Write-Error "✗ Node.js 18+ requerido, encontrado: $nodeVersion"
                Write-Warning "Descarga Node.js desde: https://nodejs.org/"
                exit 1
            }
        }
    } catch {
        Write-Error "✗ Node.js no encontrado en PATH"
        Write-Warning "Instala Node.js 18+ desde: https://nodejs.org/"
        exit 1
    }

    # Verificar npm
    Write-Info "Verificando npm..."
    try {
        $npmVersion = npm --version 2>&1
        Write-Success "✓ npm $npmVersion encontrado"
    } catch {
        Write-Error "✗ npm no encontrado"
        exit 1
    }

    # Verificar Git
    Write-Info "Verificando Git..."
    try {
        $gitVersion = git --version 2>&1
        Write-Success "✓ $gitVersion encontrado"
    } catch {
        Write-Warning "⚠ Git no encontrado (opcional pero recomendado)"
    }

    Write-Success "`n✓ Todos los requisitos cumplidos"
}

# ==============================================================================
# PASO 2: CONFIGURAR ENTORNO VIRTUAL DE PYTHON
# ==============================================================================

Write-Step "Configurando entorno virtual de Python..."

if (Test-Path $VenvDir) {
    Write-Warning "Entorno virtual ya existe. ¿Desea recrearlo? (S/N)"
    $response = Read-Host
    if ($response -eq "S" -or $response -eq "s") {
        Write-Info "Eliminando entorno virtual existente..."
        Remove-Item -Recurse -Force $VenvDir
    } else {
        Write-Info "Usando entorno virtual existente"
    }
}

if (-not (Test-Path $VenvDir)) {
    Write-Info "Creando entorno virtual..."
    python -m venv $VenvDir
    Write-Success "✓ Entorno virtual creado"
}

# Activar entorno virtual
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    Write-Info "Activando entorno virtual..."
    & $ActivateScript
    Write-Success "✓ Entorno virtual activado"
} else {
    Write-Error "✗ No se pudo encontrar el script de activación"
    exit 1
}

# ==============================================================================
# PASO 3: INSTALAR DEPENDENCIAS DE PYTHON
# ==============================================================================

Write-Step "Instalando dependencias de Python..."

# Actualizar pip
Write-Info "Actualizando pip..."
python -m pip install --upgrade pip --quiet

# Instalar dependencias de producción
$RequirementsFile = Join-Path $ProjectRoot "requirements.txt"
if (Test-Path $RequirementsFile) {
    Write-Info "Instalando requirements.txt..."
    pip install -r $RequirementsFile --quiet
    Write-Success "✓ Dependencias de producción instaladas"
} else {
    Write-Warning "⚠ No se encontró requirements.txt"
}

# Instalar dependencias de desarrollo
$RequirementsDevFile = Join-Path $ProjectRoot "requirements-dev.txt"
if (Test-Path $RequirementsDevFile) {
    Write-Info "Instalando requirements-dev.txt..."
    pip install -r $RequirementsDevFile --quiet
    Write-Success "✓ Dependencias de desarrollo instaladas"
} else {
    Write-Warning "⚠ No se encontró requirements-dev.txt"
}

# ==============================================================================
# PASO 4: INSTALAR DEPENDENCIAS DE NODE.JS
# ==============================================================================

Write-Step "Instalando dependencias de Node.js..."

if (Test-Path $FrontendDir) {
    Push-Location $FrontendDir

    Write-Info "Ejecutando npm install en frontend..."
    npm install
    Write-Success "✓ Dependencias de frontend instaladas"

    Pop-Location
} else {
    Write-Warning "⚠ Directorio frontend no encontrado"
}

# ==============================================================================
# PASO 5: CONFIGURAR VARIABLES DE ENTORNO
# ==============================================================================

Write-Step "Configurando variables de entorno..."

if (-not (Test-Path $EnvFile)) {
    if (Test-Path $EnvExample) {
        Write-Info "Copiando .env.example a .env..."
        Copy-Item $EnvExample $EnvFile
        Write-Success "✓ Archivo .env creado"

        Write-Warning "`n⚠ IMPORTANTE: Edita el archivo .env con tus credenciales:"
        Write-Info "   - TELEGRAM_TOKEN: Token del bot de Telegram"
        Write-Info "   - DATABASE_URL: URL de la base de datos"
        Write-Info ""
        Write-Warning "¿Deseas editar el archivo .env ahora? (S/N)"
        $response = Read-Host

        if ($response -eq "S" -or $response -eq "s") {
            notepad $EnvFile
        }
    } else {
        Write-Warning "⚠ No se encontró .env.example"
        Write-Info "Creando .env básico..."

        @"
# Telegram
TELEGRAM_TOKEN=your_token_here

# Base de datos
DATABASE_URL=sqlite:///./storage/entrenasmart.db

# API
API_CORS_ORIGINS=http://localhost:5173

# Modo
DEBUG=True

# Huso horario
TIMEZONE=America/Bogota
"@ | Out-File -FilePath $EnvFile -Encoding UTF8

        Write-Success "✓ Archivo .env creado (configúralo manualmente)"
    }
} else {
    Write-Info ".env ya existe, omitiendo..."
}

# ==============================================================================
# PASO 6: CREAR ESTRUCTURA DE DIRECTORIOS
# ==============================================================================

Write-Step "Verificando estructura de directorios..."

$Directories = @(
    "storage",
    "storage/backups",
    "logs"
)

foreach ($dir in $Directories) {
    $fullPath = Join-Path $ProjectRoot $dir
    if (-not (Test-Path $fullPath)) {
        Write-Info "Creando directorio: $dir"
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
    }
}

Write-Success "✓ Estructura de directorios verificada"

# ==============================================================================
# PASO 7: INICIALIZAR BASE DE DATOS
# ==============================================================================

Write-Step "Inicializando base de datos..."

$InitDbScript = Join-Path $ProjectRoot "scripts\db\init_db.py"
if (Test-Path $InitDbScript) {
    Write-Info "Ejecutando script de inicialización..."
    python $InitDbScript
    Write-Success "✓ Base de datos inicializada"
} else {
    Write-Warning "⚠ Script de inicialización no encontrado: $InitDbScript"
    Write-Info "La BD se creará automáticamente al ejecutar la aplicación"
}

# ==============================================================================
# PASO 8: RESUMEN Y COMANDOS ÚTILES
# ==============================================================================

Write-Step "Configuración completada exitosamente!"

Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║                    ✓ SETUP COMPLETADO                          ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

📋 COMANDOS ÚTILES:

  🔧 Desarrollo:
     • Activar entorno:   .\.venv\Scripts\Activate.ps1
     • Backend API:       python -m uvicorn backend.api.main:app --reload
     • Frontend:          cd frontend && npm run dev
     • Bot Telegram:      python backend\main.py

  🐳 Docker:
     • Iniciar todo:      docker-compose up --build
     • Detener:           docker-compose down

  🧪 Testing:
     • Ejecutar tests:    pytest tests/ -v
     • Cobertura:         pytest --cov=src tests/

  📝 Linting:
     • Formatear:         black src/ tests/
     • Ordenar imports:   isort src/ tests/
     • Verificar:         flake8 src/ tests/

  🌐 URLs:
     • Frontend:          http://localhost:5173
     • Backend API:       http://localhost:8000
     • API Docs:          http://localhost:8000/docs

"@ -ForegroundColor Green

if (-not (Test-Path $EnvFile) -or (Select-String -Path $EnvFile -Pattern "your_token_here" -Quiet)) {
    Write-Warning @"

⚠️  ACCIÓN REQUERIDA:
   Configura el archivo .env con tus credenciales antes de ejecutar.
   Edita: $EnvFile

"@
}

# ==============================================================================
# PASO 9: EJECUTAR PROYECTO (OPCIONAL)
# ==============================================================================

if ($RunAfterSetup) {
    Write-Step "Ejecutando proyecto..."

    Write-Info "Opción de ejecución:"
    Write-Host "1. Backend API (FastAPI)"
    Write-Host "2. Frontend (Vite)"
    Write-Host "3. Bot de Telegram"
    Write-Host "4. Docker Compose (Todo)"
    Write-Host "5. Omitir"

    $option = Read-Host "Selecciona una opción (1-5)"

    switch ($option) {
        "1" {
            Write-Info "Iniciando Backend API..."
            python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
        }
        "2" {
            Write-Info "Iniciando Frontend..."
            Push-Location $FrontendDir
            npm run dev
            Pop-Location
        }
        "3" {
            Write-Info "Iniciando Bot de Telegram..."
            python backend\main.py
        }
        "4" {
            Write-Info "Iniciando Docker Compose..."
            docker-compose up --build
        }
        default {
            Write-Info "Omitiendo ejecución automática"
        }
    }
}

Write-Success "`n¡Listo! El proyecto EntrenaSmart está configurado y listo para usar. 💪"
