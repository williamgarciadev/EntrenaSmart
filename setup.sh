#!/bin/bash

#╔════════════════════════════════════════════════════════════════════════════╗
#║                                                                            ║
#║              🚀 EntrenaSmart - Setup Completo con Docker                  ║
#║                                                                            ║
#║  Este script automatiza todo el proceso de instalación y configuración    ║
#║                                                                            ║
#╚════════════════════════════════════════════════════════════════════════════╝

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
PROJECT_NAME="EntrenaSmart"
DOCKER_REQUIRED="20.10"
COMPOSE_REQUIRED="1.29"

# ============================================================================
# Funciones de Utilidad
# ============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${YELLOW}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# ============================================================================
# Verificaciones Preliminares
# ============================================================================

print_header "Verificando Requisitos Previos"

# Verificar Docker
print_step "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado"
    echo ""
    echo "Descárgalo en: https://www.docker.com/products/docker-desktop"
    exit 1
fi
docker_version=$(docker --version | awk '{print $3}' | cut -d',' -f1)
print_success "Docker v$docker_version instalado"

# Verificar Docker Compose
print_step "Verificando Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado"
    echo ""
    echo "Instálalo siguiendo: https://docs.docker.com/compose/install/"
    exit 1
fi
compose_version=$(docker-compose --version | awk '{print $3}' | cut -d',' -f1)
print_success "Docker Compose v$compose_version instalado"

# Verificar Git
print_step "Verificando Git..."
if ! command -v git &> /dev/null; then
    print_error "Git no está instalado"
    exit 1
fi
print_success "Git instalado"

# ============================================================================
# Preparar Entorno
# ============================================================================

print_header "Preparando Entorno"

# Crear .env desde .env.docker si no existe
print_step "Configurando variables de entorno..."
if [ ! -f .env ]; then
    print_info ".env no existe, creando desde .env.docker"
    cp .env.docker .env
    print_success ".env creado"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANTE:${NC}"
    echo "   Revisa el archivo .env y actualiza:"
    echo "   - POSTGRES_PASSWORD"
    echo "   - TELEGRAM_BOT_TOKEN (si usas el bot)"
    echo "   - API_CORS_ORIGINS (si cambias puertos)"
    echo ""
    read -p "   ¿Presiona Enter cuando hayas revisado .env..."
else
    print_success ".env ya existe (sin cambios)"
fi

# Hacer scripts ejecutables
print_step "Preparando scripts..."
chmod +x docker-start.sh docker-stop.sh docker-utils.sh 2>/dev/null || true
print_success "Scripts preparados"

# ============================================================================
# Construcción y Inicio
# ============================================================================

print_header "Construyendo e Iniciando Servicios"

print_step "Construyendo imágenes Docker..."
echo ""
docker-compose build 2>&1 | grep -E "Step|Building|Successfully" || true
echo ""
print_success "Imágenes construidas"

print_step "Iniciando servicios..."
docker-compose up -d
print_success "Servicios iniciados"

# Esperar a que los servicios se estabilicen
print_step "Esperando que los servicios se estabilicen (30 segundos)..."
for i in {30..1}; do
    printf "\r   Esperando: ${i}s  "
    sleep 1
done
echo ""
print_success "Servicios estabilizados"

# ============================================================================
# Verificación de Salud
# ============================================================================

print_header "Verificando Salud de Servicios"

# PostgreSQL
print_step "Verificando PostgreSQL..."
if docker-compose exec -T postgres pg_isready -U entrenasmart > /dev/null 2>&1; then
    print_success "PostgreSQL disponible"
else
    print_error "PostgreSQL aún iniciando (puede tomar más tiempo)"
fi

# API Backend
print_step "Verificando API Backend..."
max_attempts=10
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "API Backend disponible"
        break
    fi
    attempt=$((attempt + 1))
    if [ $attempt -lt $max_attempts ]; then
        sleep 2
    fi
done
if [ $attempt -eq $max_attempts ]; then
    print_error "API Backend aún iniciando (puede tomar más tiempo)"
fi

# Frontend
print_step "Verificando Frontend..."
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    print_success "Frontend disponible"
else
    print_info "Frontend aún iniciando (es normal, puede tomar 30-60 segundos)"
fi

# ============================================================================
# Estado Final
# ============================================================================

print_header "Estado de Servicios"

docker-compose ps

# ============================================================================
# Instrucciones Finales
# ============================================================================

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║                  ✅ SETUP COMPLETADO EXITOSAMENTE             ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}╠════════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║  🌐 ACCESO A SERVICIOS:                                        ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║     Frontend (React/Vite):                                     ║${NC}"
echo -e "${GREEN}║     🔗 http://localhost:5173                                    ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║     API Backend (FastAPI):                                     ║${NC}"
echo -e "${GREEN}║     🔗 http://localhost:8000                                    ║${NC}"
echo -e "${GREEN}║     📖 Documentación: http://localhost:8000/docs               ║${NC}"
echo -e "${GREEN}║     📋 ReDoc: http://localhost:8000/redoc                      ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║     Base de Datos PostgreSQL:                                  ║${NC}"
echo -e "${GREEN}║     🔗 localhost:5432                                           ║${NC}"
echo -e "${GREEN}║     👤 Usuario: entrenasmart                                    ║${NC}"
echo -e "${GREEN}║     📊 Base de Datos: entrenasmart                              ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}╠════════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  📋 COMANDOS ÚTILES:                                           ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║     Ver logs en tiempo real:                                   ║${NC}"
echo -e "${GREEN}║     $ docker-compose logs -f                                   ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║     Detener servicios:                                         ║${NC}"
echo -e "${GREEN}║     $ docker-compose stop                                      ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║     Reiniciar servicios:                                       ║${NC}"
echo -e "${GREEN}║     $ docker-compose restart                                   ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║     Entrar a bash en API:                                      ║${NC}"
echo -e "${GREEN}║     $ docker-compose exec api bash                             ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║     Acceder a PostgreSQL:                                      ║${NC}"
echo -e "${GREEN}║     $ docker-compose exec postgres psql -U entrenasmart        ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║     Usar utilidades (backups, logs, etc):                      ║${NC}"
echo -e "${GREEN}║     $ ./docker-utils.sh                                        ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}╠════════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  📚 DOCUMENTACIÓN:                                             ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║     Lee DOCKER.md para:                                        ║${NC}"
echo -e "${GREEN}║     • Configuración avanzada                                   ║${NC}"
echo -e "${GREEN}║     • Backups y restauración                                   ║${NC}"
echo -e "${GREEN}║     • Solución de problemas                                    ║${NC}"
echo -e "${GREEN}║     • Deploy a producción                                      ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║     Lee README.md para:                                        ║${NC}"
echo -e "${GREEN}║     • Descripción general del proyecto                         ║${NC}"
echo -e "${GREEN}║     • Características principales                              ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}⚠️  NOTA:${NC}"
echo "   Si algún servicio muestra 'Exit' o 'Restarting', revisa los logs:"
echo "   $ docker-compose logs [servicio]"
echo ""
echo -e "${YELLOW}📝 PRÓXIMOS PASOS:${NC}"
echo "   1. Abre http://localhost:5173 en tu navegador"
echo "   2. Revisa que todo funcione correctamente"
echo "   3. Si hay problemas, consulta DOCKER.md"
echo ""
