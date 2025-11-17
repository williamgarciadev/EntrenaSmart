#!/bin/bash

# Script para detener EntrenaSmart
# Uso: ./docker-stop.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🛑 Deteniendo EntrenaSmart                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Preguntar si desea eliminar datos
echo "¿Deseas eliminar también los volúmenes (datos de BD)?"
echo "Opciones:"
echo "  1) Detener servicios (mantener datos)"
echo "  2) Detener y eliminar todo (borrar BD)"
echo ""
read -p "Selecciona opción (1 o 2): " option

case $option in
    1)
        echo ""
        echo "Deteniendo servicios..."
        docker-compose stop
        echo "✓ Servicios detenidos (datos preservados)"
        echo ""
        echo "Para iniciar nuevamente:"
        echo "  docker-compose up -d"
        ;;
    2)
        echo ""
        echo "⚠️  Eliminando contenedores y volúmenes..."
        docker-compose down -v
        echo "✓ Servicios eliminados (incluye BD)"
        echo ""
        echo "Para iniciar nuevamente:"
        echo "  ./docker-start.sh"
        ;;
    *)
        echo "❌ Opción no válida"
        exit 1
        ;;
esac

echo ""
echo "Estado de servicios:"
docker-compose ps 2>/dev/null || echo "Sin servicios activos"
