#!/bin/bash

# Script para iniciar EntrenaSmart con Docker
# Uso: ./docker-start.sh

set -e  # Salir si hay error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🚀 Iniciando EntrenaSmart con Docker              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Verificar que Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado o no está en el PATH"
    echo "   Descárgalo en: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Verificar que Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    echo "   Instálalo siguiendo las instrucciones en: https://docs.docker.com/compose/install/"
    exit 1
fi

# Crear .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env desde .env.docker..."
    cp .env.docker .env
    echo "   ✓ Archivo .env creado"
    echo "   ⚠️  Revisa .env y actualiza los valores según sea necesario"
fi

echo ""
echo "📦 Levantando servicios con docker-compose..."
echo ""

# Levantar servicios
docker-compose up -d

# Esperar a que los servicios se inicien
echo ""
echo "⏳ Esperando que los servicios se inicien (20 segundos)..."
sleep 20

# Verificar estado
echo ""
echo "📊 Estado de los servicios:"
docker-compose ps

echo ""
echo "✅ Verificación final:"

# Verificar que la API está disponible
echo -n "   API Backend... "
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓"
else
    echo "⚠️  (aún iniciando, revisa con 'docker-compose logs api')"
fi

# Verificar que el frontend está disponible
echo -n "   Frontend... "
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✓"
else
    echo "⚠️  (aún iniciando, revisa con 'docker-compose logs frontend')"
fi

# Verificar que PostgreSQL está disponible
echo -n "   PostgreSQL... "
if docker-compose exec -T postgres pg_isready -U entrenasmart > /dev/null 2>&1; then
    echo "✓"
else
    echo "⚠️  (aún iniciando)"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║             🎉 EntrenaSmart iniciada correctamente!        ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                            ║"
echo "║  🌐 Frontend (React):                                      ║"
echo "║     http://localhost:5173                                  ║"
echo "║                                                            ║"
echo "║  🔌 API Backend (FastAPI):                                 ║"
echo "║     http://localhost:8000                                  ║"
echo "║     Documentación: http://localhost:8000/docs              ║"
echo "║     ReDoc: http://localhost:8000/redoc                     ║"
echo "║                                                            ║"
echo "║  🗄️  Base de Datos (PostgreSQL):                          ║"
echo "║     localhost:5432                                         ║"
echo "║     Usuario: entrenasmart                                  ║"
echo "║     BD: entrenasmart                                       ║"
echo "║                                                            ║"
echo "║  📋 Comandos útiles:                                       ║"
echo "║     Ver logs:        docker-compose logs -f                ║"
echo "║     Parar:           docker-compose stop                   ║"
echo "║     Detener todo:    docker-compose down                   ║"
echo "║     Bash en API:     docker-compose exec api bash          ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
