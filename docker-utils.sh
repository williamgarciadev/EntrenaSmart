#!/bin/bash

# Script de utilidades para EntrenaSmart con Docker
# Uso: ./docker-utils.sh [comando]

if [ -z "$1" ]; then
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║          📋 Utilidades de Docker para EntrenaSmart         ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Comandos disponibles:"
    echo ""
    echo "  ./docker-utils.sh logs [servicio]"
    echo "      Ver logs (servicio: api, frontend, postgres, bot)"
    echo ""
    echo "  ./docker-utils.sh restart [servicio]"
    echo "      Reiniciar servicio"
    echo ""
    echo "  ./docker-utils.sh bash api"
    echo "      Entrar a bash en el contenedor de API"
    echo ""
    echo "  ./docker-utils.sh bash postgres"
    echo "      Entrar a bash en el contenedor de PostgreSQL"
    echo ""
    echo "  ./docker-utils.sh db-backup"
    echo "      Hacer backup de la base de datos"
    echo ""
    echo "  ./docker-utils.sh db-restore [archivo.sql]"
    echo "      Restaurar base de datos desde backup"
    echo ""
    echo "  ./docker-utils.sh status"
    echo "      Ver estado de todos los servicios"
    echo ""
    echo "  ./docker-utils.sh rebuild [servicio]"
    echo "      Reconstruir imagen de un servicio"
    echo ""
    echo "  ./docker-utils.sh clean"
    echo "      Limpiar imágenes y volúmenes no usados"
    echo ""
    exit 0
fi

case "$1" in
    logs)
        service=${2:-""}
        if [ -z "$service" ]; then
            echo "Ver logs de todos los servicios..."
            docker-compose logs -f
        else
            echo "Ver logs de $service..."
            docker-compose logs -f "$service"
        fi
        ;;

    restart)
        service=${2:-""}
        if [ -z "$service" ]; then
            echo "Reiniciando todos los servicios..."
            docker-compose restart
        else
            echo "Reiniciando $service..."
            docker-compose restart "$service"
        fi
        ;;

    bash)
        service=${2:-"api"}
        echo "Entrando a bash en $service..."
        docker-compose exec "$service" bash
        ;;

    status)
        echo "Estado de los servicios:"
        docker-compose ps
        ;;

    db-backup)
        timestamp=$(date +%Y%m%d_%H%M%S)
        backup_file="backup_${timestamp}.sql"
        echo "Creando backup de la base de datos..."
        docker-compose exec -T postgres pg_dump -U entrenasmart entrenasmart > "$backup_file"
        if [ -f "$backup_file" ]; then
            size=$(du -h "$backup_file" | cut -f1)
            echo "✓ Backup creado: $backup_file ($size)"
        else
            echo "❌ Error al crear el backup"
            exit 1
        fi
        ;;

    db-restore)
        if [ -z "$2" ]; then
            echo "❌ Especifica el archivo a restaurar"
            echo "   Uso: ./docker-utils.sh db-restore archivo.sql"
            exit 1
        fi

        if [ ! -f "$2" ]; then
            echo "❌ Archivo no encontrado: $2"
            exit 1
        fi

        echo "⚠️  Restaurando base de datos desde $2..."
        read -p "¿Estás seguro? (escribe 'si' para confirmar): " confirm
        if [ "$confirm" = "si" ]; then
            docker-compose exec -T postgres psql -U entrenasmart entrenasmart < "$2"
            echo "✓ Base de datos restaurada"
        else
            echo "Cancelado"
        fi
        ;;

    rebuild)
        service=${2:-"api"}
        echo "Reconstruyendo imagen de $service..."
        docker-compose build --no-cache "$service"
        echo "Relanzando $service..."
        docker-compose up -d "$service"
        echo "✓ $service reconstruido y relanzado"
        ;;

    clean)
        echo "⚠️  Limpiando recursos no usados de Docker..."
        docker-compose down
        docker system prune -f
        echo "✓ Limpieza completada"
        echo "   Para iniciar nuevamente: ./docker-start.sh"
        ;;

    *)
        echo "❌ Comando no reconocido: $1"
        echo "Usa: ./docker-utils.sh sin argumentos para ver la ayuda"
        exit 1
        ;;
esac
