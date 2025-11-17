# EntrenaSmart - Utilidades Docker (Windows PowerShell)
# Uso: .\docker-utils.ps1 [comando] [opciones]

param(
    [string]$Command = "",
    [string]$Service = "",
    [string]$File = ""
)

function Show-Help {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗"
    Write-Host "║          📋 Utilidades de Docker para EntrenaSmart         ║"
    Write-Host "╚════════════════════════════════════════════════════════════╝"
    Write-Host ""
    Write-Host "Comandos disponibles:"
    Write-Host ""
    Write-Host "  .\docker-utils.ps1 logs [servicio]"
    Write-Host "      Ver logs (servicio: api, frontend, postgres, bot)"
    Write-Host ""
    Write-Host "  .\docker-utils.ps1 restart [servicio]"
    Write-Host "      Reiniciar servicio"
    Write-Host ""
    Write-Host "  .\docker-utils.ps1 bash api"
    Write-Host "      Entrar a bash en el contenedor de API"
    Write-Host ""
    Write-Host "  .\docker-utils.ps1 bash postgres"
    Write-Host "      Entrar a bash en el contenedor de PostgreSQL"
    Write-Host ""
    Write-Host "  .\docker-utils.ps1 db-backup"
    Write-Host "      Hacer backup de la base de datos"
    Write-Host ""
    Write-Host "  .\docker-utils.ps1 db-restore archivo.sql"
    Write-Host "      Restaurar base de datos desde backup"
    Write-Host ""
    Write-Host "  .\docker-utils.ps1 status"
    Write-Host "      Ver estado de todos los servicios"
    Write-Host ""
    Write-Host "  .\docker-utils.ps1 rebuild [servicio]"
    Write-Host "      Reconstruir imagen de un servicio"
    Write-Host ""
    Write-Host "  .\docker-utils.ps1 clean"
    Write-Host "      Limpiar imágenes y volúmenes no usados"
    Write-Host ""
}

if ([string]::IsNullOrWhiteSpace($Command)) {
    Show-Help
    exit 0
}

switch ($Command.ToLower()) {
    "logs" {
        if ([string]::IsNullOrWhiteSpace($Service)) {
            Write-Host "Ver logs de todos los servicios..." -ForegroundColor Cyan
            docker-compose logs -f
        } else {
            Write-Host "Ver logs de $Service..." -ForegroundColor Cyan
            docker-compose logs -f $Service
        }
    }

    "restart" {
        if ([string]::IsNullOrWhiteSpace($Service)) {
            Write-Host "Reiniciando todos los servicios..." -ForegroundColor Yellow
            docker-compose restart
        } else {
            Write-Host "Reiniciando $Service..." -ForegroundColor Yellow
            docker-compose restart $Service
        }
        Write-Host "✓ Servicios reiniciados" -ForegroundColor Green
    }

    "bash" {
        $targetService = if ([string]::IsNullOrWhiteSpace($Service)) { "api" } else { $Service }
        Write-Host "Entrando a bash en $targetService..." -ForegroundColor Cyan
        docker-compose exec $targetService bash
    }

    "status" {
        Write-Host "Estado de los servicios:" -ForegroundColor Cyan
        docker-compose ps
    }

    "db-backup" {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupFile = "backup_${timestamp}.sql"
        Write-Host "Creando backup de la base de datos..." -ForegroundColor Yellow
        docker-compose exec -T postgres pg_dump -U entrenasmart entrenasmart | Out-File -FilePath $backupFile -Encoding ASCII

        if (Test-Path $backupFile) {
            $size = (Get-Item $backupFile).Length / 1MB
            Write-Host "✓ Backup creado: $backupFile (${size:F2} MB)" -ForegroundColor Green
        } else {
            Write-Host "❌ Error al crear el backup" -ForegroundColor Red
            exit 1
        }
    }

    "db-restore" {
        if ([string]::IsNullOrWhiteSpace($File)) {
            Write-Host "❌ Especifica el archivo a restaurar" -ForegroundColor Red
            Write-Host "   Uso: .\docker-utils.ps1 db-restore archivo.sql"
            exit 1
        }

        if (-not (Test-Path $File)) {
            Write-Host "❌ Archivo no encontrado: $File" -ForegroundColor Red
            exit 1
        }

        Write-Host "⚠️  Restaurando base de datos desde $File..." -ForegroundColor Red
        $confirm = Read-Host "¿Estás seguro? (escribe 'si' para confirmar)"

        if ($confirm -eq "si") {
            Get-Content $File | docker-compose exec -T postgres psql -U entrenasmart entrenasmart
            Write-Host "✓ Base de datos restaurada" -ForegroundColor Green
        } else {
            Write-Host "Cancelado" -ForegroundColor Yellow
        }
    }

    "rebuild" {
        $targetService = if ([string]::IsNullOrWhiteSpace($Service)) { "api" } else { $Service }
        Write-Host "Reconstruyendo imagen de $targetService..." -ForegroundColor Yellow
        docker-compose build --no-cache $targetService
        Write-Host "Relanzando $targetService..." -ForegroundColor Yellow
        docker-compose up -d $targetService
        Write-Host "✓ $targetService reconstruido y relanzado" -ForegroundColor Green
    }

    "clean" {
        Write-Host "⚠️  Limpiando recursos no usados de Docker..." -ForegroundColor Red
        docker-compose down
        docker system prune -f
        Write-Host "✓ Limpieza completada" -ForegroundColor Green
        Write-Host "   Para iniciar nuevamente: .\setup.ps1"
    }

    default {
        Write-Host "❌ Comando no reconocido: $Command" -ForegroundColor Red
        Write-Host "Usa: .\docker-utils.ps1 sin argumentos para ver la ayuda"
        exit 1
    }
}

Write-Host ""
