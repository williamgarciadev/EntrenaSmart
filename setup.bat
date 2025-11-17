@echo off
REM EntrenaSmart - Setup Completo con Docker (Windows Batch)
REM Uso: setup.bat

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          🚀 EntrenaSmart - Setup Completo con Docker          ║
echo ║                                                                ║
echo ║  Este script automatiza todo el proceso de instalacion        ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Verificar Docker
echo ▶ Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Docker no está instalado
    echo.
    echo Descárgalo en: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
for /f "tokens=3" %%i in ('docker --version') do set DOCKER_VERSION=%%i
echo ✓ Docker v%DOCKER_VERSION% instalado

REM Verificar Docker Compose
echo ▶ Verificando Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Docker Compose no está instalado
    echo.
    echo Instálalo en: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)
for /f "tokens=3" %%i in ('docker-compose --version') do set COMPOSE_VERSION=%%i
echo ✓ Docker Compose v%COMPOSE_VERSION% instalado

REM Verificar Git
echo ▶ Verificando Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Git no está instalado
    pause
    exit /b 1
)
echo ✓ Git instalado

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          Preparando Entorno                                    ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Crear .env si no existe
echo ▶ Configurando variables de entorno...
if not exist .env (
    echo ℹ .env no existe, creando desde .env.docker
    copy .env.docker .env >nul
    echo ✓ .env creado
    echo.
    echo ⚠️  IMPORTANTE:
    echo    Revisa el archivo .env y actualiza:
    echo    - POSTGRES_PASSWORD
    echo    - TELEGRAM_BOT_TOKEN (si usas el bot)
    echo    - API_CORS_ORIGINS (si cambias puertos)
    echo.
    pause
) else (
    echo ✓ .env ya existe (sin cambios)
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          Construyendo e Iniciando Servicios                   ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo ▶ Construyendo imágenes Docker...
echo.
docker-compose build
echo.
echo ✓ Imágenes construidas

echo ▶ Iniciando servicios...
docker-compose up -d
echo ✓ Servicios iniciados

echo ▶ Esperando que los servicios se estabilicen (30 segundos)...
timeout /t 30 /nobreak

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          Verificando Salud de Servicios                       ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo ▶ Verificando PostgreSQL...
docker-compose exec -T postgres pg_isready -U entrenasmart >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ PostgreSQL disponible
) else (
    echo ✗ PostgreSQL aún iniciando (puede tomar más tiempo)
)

echo ▶ Verificando API Backend...
timeout /t 2 /nobreak >nul
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -ErrorAction SilentlyContinue; if ($response.StatusCode -eq 200) { Write-Host '✓ API Backend disponible' -ForegroundColor Green } } catch { Write-Host '✗ API Backend aún iniciando' -ForegroundColor Red }"

echo ▶ Verificando Frontend...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5173' -ErrorAction SilentlyContinue; if ($response.StatusCode -eq 200) { Write-Host '✓ Frontend disponible' -ForegroundColor Green } } catch { Write-Host 'ℹ Frontend aún iniciando (es normal)' -ForegroundColor Yellow }"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          Estado de Servicios                                  ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
docker-compose ps

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║                  ✅ SETUP COMPLETADO EXITOSAMENTE             ║
echo ║                                                                ║
echo ╠════════════════════════════════════════════════════════════════╣
echo ║                                                                ║
echo ║  🌐 ACCESO A SERVICIOS:                                        ║
echo ║                                                                ║
echo ║     Frontend (React/Vite):                                     ║
echo ║     🔗 http://localhost:5173                                    ║
echo ║                                                                ║
echo ║     API Backend (FastAPI):                                     ║
echo ║     🔗 http://localhost:8000                                    ║
echo ║     📖 Documentación: http://localhost:8000/docs               ║
echo ║     📋 ReDoc: http://localhost:8000/redoc                      ║
echo ║                                                                ║
echo ║     Base de Datos PostgreSQL:                                  ║
echo ║     🔗 localhost:5432                                           ║
echo ║     👤 Usuario: entrenasmart                                    ║
echo ║     📊 Base de Datos: entrenasmart                              ║
echo ║                                                                ║
echo ╠════════════════════════════════════════════════════════════════╣
echo ║  📋 COMANDOS ÚTILES:                                           ║
echo ║                                                                ║
echo ║     Ver logs en tiempo real:                                   ║
echo ║     PS> docker-compose logs -f                                 ║
echo ║                                                                ║
echo ║     Detener servicios:                                         ║
echo ║     PS> docker-compose stop                                    ║
echo ║                                                                ║
echo ║     Reiniciar servicios:                                       ║
echo ║     PS> docker-compose restart                                 ║
echo ║                                                                ║
echo ║     Ver utilidades:                                            ║
echo ║     PS> .\docker-utils.ps1                                     ║
echo ║                                                                ║
echo ╠════════════════════════════════════════════════════════════════╣
echo ║  📚 DOCUMENTACIÓN:                                             ║
echo ║                                                                ║
echo ║     Lee DOCKER.md para:                                        ║
echo ║     • Configuración avanzada                                   ║
echo ║     • Backups y restauración                                   ║
echo ║     • Solución de problemas                                    ║
echo ║     • Deploy a producción                                      ║
echo ║                                                                ║
echo ║     Lee README.md para:                                        ║
echo ║     • Descripción general del proyecto                         ║
echo ║     • Características principales                              ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo ⚠️  NOTA:
echo    Si algún servicio muestra 'Exit' o 'Restarting', revisa los logs:
echo    PS> docker-compose logs [servicio]
echo.
echo 📝 PRÓXIMOS PASOS:
echo    1. Abre http://localhost:5173 en tu navegador
echo    2. Revisa que todo funcione correctamente
echo    3. Si hay problemas, consulta DOCKER.md
echo.
pause
