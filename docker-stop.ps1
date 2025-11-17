# EntrenaSmart - Detener Servicios (Windows PowerShell)
# Uso: .\docker-stop.ps1

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗"
Write-Host "║          🛑 Deteniendo EntrenaSmart                        ║"
Write-Host "╚════════════════════════════════════════════════════════════════╝"
Write-Host ""

# Preguntar si desea eliminar datos
Write-Host "¿Deseas eliminar también los volúmenes (datos de BD)?"
Write-Host "Opciones:"
Write-Host "  1) Detener servicios (mantener datos)"
Write-Host "  2) Detener y eliminar todo (borrar BD)"
Write-Host ""
$option = Read-Host "Selecciona opción (1 o 2)"

switch ($option) {
    "1" {
        Write-Host ""
        Write-Host "Deteniendo servicios..." -ForegroundColor Yellow
        docker-compose stop
        Write-Host "✓ Servicios detenidos (datos preservados)" -ForegroundColor Green
        Write-Host ""
        Write-Host "Para iniciar nuevamente:" -ForegroundColor Cyan
        Write-Host "  PS> docker-compose up -d"
        break
    }
    "2" {
        Write-Host ""
        Write-Host "⚠️  Eliminando contenedores y volúmenes..." -ForegroundColor Red
        docker-compose down -v
        Write-Host "✓ Servicios eliminados (incluye BD)" -ForegroundColor Green
        Write-Host ""
        Write-Host "Para iniciar nuevamente:" -ForegroundColor Cyan
        Write-Host "  PS> .\setup.ps1"
        break
    }
    default {
        Write-Host "❌ Opción no válida" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Estado de servicios:" -ForegroundColor Cyan
docker-compose ps 2>$null | Write-Host
if ($LASTEXITCODE -ne 0) {
    Write-Host "Sin servicios activos" -ForegroundColor Yellow
}
Write-Host ""
