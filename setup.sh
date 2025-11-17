#!/bin/bash

#
# Script de configuración automática para EntrenaSmart en Linux/Mac
#
# Configura el entorno de desarrollo completo:
# - Verifica requisitos (Python, Node.js, Git)
# - Crea entorno virtual de Python
# - Instala dependencias de backend y frontend
# - Configura variables de entorno
# - Inicializa la base de datos
# - Opcionalmente ejecuta el proyecto
#
# Uso:
#   ./setup.sh
#   ./setup.sh --run
#   ./setup.sh --skip-checks --run
#
# Versión: 1.0.0
# Autor: EntrenaSmart Team
#

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funciones de output
print_success() { echo -e "${GREEN}$1${NC}"; }
print_info() { echo -e "${CYAN}$1${NC}"; }
print_warning() { echo -e "${YELLOW}$1${NC}"; }
print_error() { echo -e "${RED}$1${NC}"; }
print_step() { echo -e "\n${MAGENTA}==> $1${NC}"; }

# Configuración
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
VENV_DIR="$PROJECT_ROOT/.venv"
ENV_FILE="$PROJECT_ROOT/.env"
ENV_EXAMPLE="$PROJECT_ROOT/.env.example"

SKIP_CHECKS=false
RUN_AFTER_SETUP=false

# Parsear argumentos
for arg in "$@"; do
    case $arg in
        --skip-checks)
            SKIP_CHECKS=true
            shift
            ;;
        --run)
            RUN_AFTER_SETUP=true
            shift
            ;;
        --help|-h)
            echo "Uso: ./setup.sh [opciones]"
            echo ""
            echo "Opciones:"
            echo "  --skip-checks    Omitir verificación de requisitos"
            echo "  --run            Ejecutar proyecto después de setup"
            echo "  --help, -h       Mostrar esta ayuda"
            exit 0
            ;;
    esac
done

# Banner
cat << "EOF"

    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║     💪 ENTRENA SMART - SETUP WIZARD       ║
    ║                                           ║
    ║     Configuración Automática v1.0.0       ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝

EOF

# ==============================================================================
# PASO 1: VERIFICAR REQUISITOS
# ==============================================================================

if [ "$SKIP_CHECKS" = false ]; then
    print_step "Verificando requisitos del sistema..."

    # Verificar Python
    print_info "Verificando Python 3.11+..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
            print_success "✓ Python $PYTHON_VERSION encontrado"
        else
            print_error "✗ Python 3.11+ requerido, encontrado: $PYTHON_VERSION"
            print_warning "Instala Python 3.11+ desde tu gestor de paquetes"
            exit 1
        fi
    else
        print_error "✗ Python no encontrado"
        print_warning "Instala Python 3.11+ (Debian/Ubuntu: sudo apt install python3.11)"
        exit 1
    fi

    # Verificar Node.js
    print_info "Verificando Node.js..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        NODE_MAJOR=$(echo $NODE_VERSION | grep -oP '(?<=v)\d+')

        if [ "$NODE_MAJOR" -ge 18 ]; then
            print_success "✓ Node.js $NODE_VERSION encontrado"
        else
            print_error "✗ Node.js 18+ requerido, encontrado: $NODE_VERSION"
            print_warning "Actualiza Node.js desde: https://nodejs.org/"
            exit 1
        fi
    else
        print_error "✗ Node.js no encontrado"
        print_warning "Instala Node.js 18+ desde: https://nodejs.org/"
        exit 1
    fi

    # Verificar npm
    print_info "Verificando npm..."
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "✓ npm $NPM_VERSION encontrado"
    else
        print_error "✗ npm no encontrado"
        exit 1
    fi

    # Verificar Git
    print_info "Verificando Git..."
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        print_success "✓ $GIT_VERSION encontrado"
    else
        print_warning "⚠ Git no encontrado (opcional pero recomendado)"
    fi

    print_success "\n✓ Todos los requisitos cumplidos"
fi

# ==============================================================================
# PASO 2: CONFIGURAR ENTORNO VIRTUAL DE PYTHON
# ==============================================================================

print_step "Configurando entorno virtual de Python..."

if [ -d "$VENV_DIR" ]; then
    print_warning "Entorno virtual ya existe."
    read -p "¿Desea recrearlo? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        print_info "Eliminando entorno virtual existente..."
        rm -rf "$VENV_DIR"
    else
        print_info "Usando entorno virtual existente"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    print_info "Creando entorno virtual..."
    python3 -m venv "$VENV_DIR"
    print_success "✓ Entorno virtual creado"
fi

# Activar entorno virtual
print_info "Activando entorno virtual..."
source "$VENV_DIR/bin/activate"
print_success "✓ Entorno virtual activado"

# ==============================================================================
# PASO 3: INSTALAR DEPENDENCIAS DE PYTHON
# ==============================================================================

print_step "Instalando dependencias de Python..."

# Actualizar pip
print_info "Actualizando pip..."
pip install --upgrade pip --quiet

# Instalar dependencias de producción
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    print_info "Instalando requirements.txt..."
    pip install -r "$PROJECT_ROOT/requirements.txt" --quiet
    print_success "✓ Dependencias de producción instaladas"
else
    print_warning "⚠ No se encontró requirements.txt"
fi

# Instalar dependencias de desarrollo
if [ -f "$PROJECT_ROOT/requirements-dev.txt" ]; then
    print_info "Instalando requirements-dev.txt..."
    pip install -r "$PROJECT_ROOT/requirements-dev.txt" --quiet
    print_success "✓ Dependencias de desarrollo instaladas"
else
    print_warning "⚠ No se encontró requirements-dev.txt"
fi

# ==============================================================================
# PASO 4: INSTALAR DEPENDENCIAS DE NODE.JS
# ==============================================================================

print_step "Instalando dependencias de Node.js..."

if [ -d "$FRONTEND_DIR" ]; then
    cd "$FRONTEND_DIR"
    print_info "Ejecutando npm install en frontend..."
    npm install
    print_success "✓ Dependencias de frontend instaladas"
    cd "$PROJECT_ROOT"
else
    print_warning "⚠ Directorio frontend no encontrado"
fi

# ==============================================================================
# PASO 5: CONFIGURAR VARIABLES DE ENTORNO
# ==============================================================================

print_step "Configurando variables de entorno..."

if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$ENV_EXAMPLE" ]; then
        print_info "Copiando .env.example a .env..."
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        print_success "✓ Archivo .env creado"

        print_warning "\n⚠ IMPORTANTE: Edita el archivo .env con tus credenciales:"
        print_info "   - TELEGRAM_TOKEN: Token del bot de Telegram"
        print_info "   - DATABASE_URL: URL de la base de datos"
        echo ""
        read -p "¿Deseas editar el archivo .env ahora? (s/N): " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Ss]$ ]]; then
            ${EDITOR:-nano} "$ENV_FILE"
        fi
    else
        print_warning "⚠ No se encontró .env.example"
        print_info "Creando .env básico..."

        cat > "$ENV_FILE" << 'ENVEOF'
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
ENVEOF

        print_success "✓ Archivo .env creado (configúralo manualmente)"
    fi
else
    print_info ".env ya existe, omitiendo..."
fi

# ==============================================================================
# PASO 6: CREAR ESTRUCTURA DE DIRECTORIOS
# ==============================================================================

print_step "Verificando estructura de directorios..."

DIRECTORIES=(
    "storage"
    "storage/backups"
    "logs"
)

for dir in "${DIRECTORIES[@]}"; do
    if [ ! -d "$PROJECT_ROOT/$dir" ]; then
        print_info "Creando directorio: $dir"
        mkdir -p "$PROJECT_ROOT/$dir"
    fi
done

print_success "✓ Estructura de directorios verificada"

# ==============================================================================
# PASO 7: INICIALIZAR BASE DE DATOS
# ==============================================================================

print_step "Inicializando base de datos..."

INIT_DB_SCRIPT="$PROJECT_ROOT/scripts/db/init_db.py"
if [ -f "$INIT_DB_SCRIPT" ]; then
    print_info "Ejecutando script de inicialización..."
    python "$INIT_DB_SCRIPT"
    print_success "✓ Base de datos inicializada"
else
    print_warning "⚠ Script de inicialización no encontrado"
    print_info "La BD se creará automáticamente al ejecutar la aplicación"
fi

# ==============================================================================
# PASO 8: RESUMEN Y COMANDOS ÚTILES
# ==============================================================================

print_step "Configuración completada exitosamente!"

cat << EOF

╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║                    ✓ SETUP COMPLETADO                          ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

📋 COMANDOS ÚTILES:

  🔧 Desarrollo:
     • Activar entorno:   source .venv/bin/activate
     • Backend API:       python -m uvicorn backend.api.main:app --reload
     • Frontend:          cd frontend && npm run dev
     • Bot Telegram:      python backend/main.py

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

EOF

if [ ! -f "$ENV_FILE" ] || grep -q "your_token_here" "$ENV_FILE"; then
    print_warning "
⚠️  ACCIÓN REQUERIDA:
   Configura el archivo .env con tus credenciales antes de ejecutar.
   Edita: $ENV_FILE
"
fi

# ==============================================================================
# PASO 9: EJECUTAR PROYECTO (OPCIONAL)
# ==============================================================================

if [ "$RUN_AFTER_SETUP" = true ]; then
    print_step "Ejecutando proyecto..."

    echo "Opción de ejecución:"
    echo "1. Backend API (FastAPI)"
    echo "2. Frontend (Vite)"
    echo "3. Bot de Telegram"
    echo "4. Docker Compose (Todo)"
    echo "5. Omitir"

    read -p "Selecciona una opción (1-5): " option

    case $option in
        1)
            print_info "Iniciando Backend API..."
            python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
            ;;
        2)
            print_info "Iniciando Frontend..."
            cd "$FRONTEND_DIR"
            npm run dev
            ;;
        3)
            print_info "Iniciando Bot de Telegram..."
            python backend/main.py
            ;;
        4)
            print_info "Iniciando Docker Compose..."
            docker-compose up --build
            ;;
        *)
            print_info "Omitiendo ejecución automática"
            ;;
    esac
fi

print_success "\n¡Listo! El proyecto EntrenaSmart está configurado y listo para usar. 💪"
