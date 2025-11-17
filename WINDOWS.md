# 🪟 EntrenaSmart en Windows 11

Guía completa para ejecutar EntrenaSmart en Windows 11 usando Docker Desktop.

## Requisitos Previos

### 1. Docker Desktop
**Descargar e instalar desde**: https://www.docker.com/products/docker-desktop

**Pasos instalación**:
1. Descarga Docker Desktop para Windows
2. Ejecuta el instalador
3. Reinicia tu PC
4. Abre PowerShell y verifica: `docker --version`

### 2. Verificar Instalación
```powershell
PS> docker --version
Docker version 24.x.x, build xxxxx

PS> docker-compose --version
Docker Compose version 2.x.x, build xxxxx
```

Si Docker no aparece en PATH:
1. Reinicia PowerShell/CMD
2. Reinicia el PC si es necesario

## Ejecución en Windows 11

### Opción 1: PowerShell (Recomendado)

#### Paso 1: Abre PowerShell
- Presiona `Win + X` → Selecciona "Terminal (Administrador)"
- O presiona `Win` → Escribe "PowerShell" → Click derecho → "Ejecutar como administrador"

#### Paso 2: Navega al proyecto
```powershell
cd "ruta\al\EntrenaSmart"
```

#### Paso 3: Ejecuta el setup
```powershell
.\setup.ps1
```

**Nota**: Si obtienes error de "permisos", ejecuta primero:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Opción 2: Batch (CMD)

#### Paso 1: Abre CMD
- Presiona `Win + R` → Escribe `cmd` → Presiona Enter
- O presiona `Win + X` → Selecciona "Símbolo de sistema (Administrador)"

#### Paso 2: Navega al proyecto
```batch
cd ruta\al\EntrenaSmart
```

#### Paso 3: Ejecuta el setup
```batch
setup.bat
```

## Scripts Disponibles

### Setup (Instalación Inicial)
```powershell
# PowerShell
.\setup.ps1

# Batch
setup.bat
```

**Qué hace**:
- ✅ Verifica Docker y Docker Compose
- ✅ Crea `.env` desde `.env.docker`
- ✅ Construye imágenes Docker
- ✅ Inicia servicios
- ✅ Verifica salud de servicios

### Iniciar Servicios
```powershell
# PowerShell
.\docker-start.ps1
```

### Detener Servicios
```powershell
# PowerShell
.\docker-stop.ps1

# Selecciona opción:
# 1) Detener servicios (mantener datos)
# 2) Detener y eliminar todo (borrar BD)
```

### Utilidades
```powershell
# PowerShell
.\docker-utils.ps1           # Ver ayuda
.\docker-utils.ps1 logs      # Ver logs
.\docker-utils.ps1 logs api  # Logs específicos
.\docker-utils.ps1 status    # Estado de servicios
.\docker-utils.ps1 db-backup # Backup de BD
.\docker-utils.ps1 bash api  # Bash en contenedor
```

## Comandos Docker Nativos

Estos comandos funcionan en PowerShell/CMD sin scripts:

```powershell
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f postgres

# Ver estado de servicios
docker-compose ps

# Detener servicios (mantiene datos)
docker-compose stop

# Iniciar servicios detenidos
docker-compose start

# Reiniciar servicios
docker-compose restart

# Entrar a bash en API
docker-compose exec api bash

# Entrar a bash en PostgreSQL
docker-compose exec postgres bash

# Ejecutar comando en contenedor
docker-compose exec api python script.py

# Ver variables de entorno
docker-compose config
```

## Acceso a Servicios

Después de ejecutar `setup.ps1` o `setup.bat`, accede a:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Frontend | http://localhost:5173 | Aplicación React |
| API | http://localhost:8000 | Backend FastAPI |
| API Docs | http://localhost:8000/docs | Documentación Swagger |
| ReDoc | http://localhost:8000/redoc | Documentación alternativa |
| PostgreSQL | localhost:5432 | Base de datos |

**Credenciales BD**:
- Usuario: `entrenasmart`
- Contraseña: Ver `.env`
- Base de datos: `entrenasmart`

## Solución de Problemas

### ❌ "Docker not found"

**Problema**: Docker no está en PATH

**Soluciones**:
1. Reinicia PowerShell/CMD
2. Reinicia el PC
3. Reinstala Docker Desktop
4. Verifica que Docker Desktop está ejecutándose (busca icono en bandeja)

### ❌ "Cannot connect to Docker daemon"

**Problema**: Docker Desktop no está corriendo

**Solución**: Abre Docker Desktop y espera a que esté listo (verá "Docker Engine running")

### ❌ "Port already in use"

**Problema**: Puerto 5173, 8000 o 5432 ocupados

**Soluciones**:
```powershell
# Ver qué proceso usa puerto 5173
netstat -ano | findstr :5173

# Matar proceso por PID (ej: 1234)
taskkill /PID 1234 /F

# O cambiar puertos en docker-compose.yml
```

### ❌ "Permission denied" al ejecutar scripts

**Solución 1** (Recomendado - Una sola vez):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Solución 2** (Temporal):
```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

### ❌ Servicios no inician

**Verificar logs**:
```powershell
docker-compose logs api
docker-compose logs postgres
docker-compose logs frontend
```

**Reconstruir servicios**:
```powershell
docker-compose down -v
.\setup.ps1
```

### ❌ Base de datos vacía después de setup

**Esperado**: La BD necesita migraciones

**Solución**: Ejecutar migraciones (ver documentación backend)

## Rendimiento en Windows 11

### WSL2 vs Hyper-V

Docker Desktop en Windows 11 usa **WSL2** (recomendado) por defecto.

**Verificar**:
```powershell
docker info | findstr WSL
```

### Optimizar Rendimiento

**Aumentar recursos asignados a Docker**:
1. Abre Docker Desktop
2. Settings → Resources
3. Aumenta CPU, Memory, Disk
4. Click "Apply & Restart"

**Recomendaciones**:
- CPU: 4+ cores
- Memory: 4GB+ (6-8GB ideal)
- Disk: 50GB+

## Backup y Restauración

### Crear Backup
```powershell
.\docker-utils.ps1 db-backup
# Genera: backup_YYYYMMDD_HHMMSS.sql
```

### Restaurar Backup
```powershell
.\docker-utils.ps1 db-restore backup_20251116_120000.sql
# Confirma con 'si'
```

## Logs y Debugging

### Ver Logs Completos
```powershell
docker-compose logs > logs.txt
notepad logs.txt
```

### Ver Logs en Tiempo Real
```powershell
docker-compose logs -f
```

### Detener y Limpiar Todo
```powershell
docker-compose down -v
docker system prune -f
```

## Desarrollo en Windows 11

### Editar Código
- Frontend: `frontend/src/` (se recarga automáticamente)
- Backend: `backend/` (requiere restart)

### Reiniciar Backend
```powershell
docker-compose restart api
```

### Ver Cambios en Frontend
```powershell
docker-compose logs -f frontend
```

## Recursos Útiles

- [Docker Desktop Docs](https://docs.docker.com/desktop/install/windows-install/)
- [Docker Compose CLI](https://docs.docker.com/engine/reference/commandline/compose/)
- [WSL2 Documentation](https://docs.microsoft.com/windows/wsl/)

---

**Última Actualización**: 2025-11-16
**Versión Windows**: Windows 11 (21H2+)
**Docker Desktop**: 24.0+
