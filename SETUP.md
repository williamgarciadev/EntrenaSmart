# 🚀 Guía de Configuración de EntrenaSmart

Esta guía te ayudará a configurar el proyecto EntrenaSmart en tu máquina local usando los scripts de configuración automática.

## 📋 Requisitos Previos

Antes de ejecutar los scripts de configuración, asegúrate de tener instalado:

### Requisitos Obligatorios

- **Python 3.11+** - [Descargar](https://www.python.org/downloads/)
- **Node.js 18+** - [Descargar](https://nodejs.org/)
- **npm** (incluido con Node.js)

### Requisitos Opcionales

- **Git** - [Descargar](https://git-scm.com/)
- **Docker Desktop** (para ejecución con Docker) - [Descargar](https://www.docker.com/products/docker-desktop/)

---

## 🪟 Windows - Usando PowerShell

### 1. Preparación

Abre PowerShell como **Administrador** y navega a la carpeta del proyecto:

```powershell
cd C:\ruta\a\tu\EntrenaSmart
```

### 2. Habilitar Ejecución de Scripts (Solo la primera vez)

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Ejecutar Setup

**Opción A: Configuración Básica**
```powershell
.\setup.ps1
```

**Opción B: Configuración y Ejecución Automática**
```powershell
.\setup.ps1 -RunAfterSetup
```

**Opción C: Omitir Verificación de Requisitos**
```powershell
.\setup.ps1 -SkipChecks
```

**Opción D: Todas las opciones**
```powershell
.\setup.ps1 -SkipChecks -RunAfterSetup
```

### 4. Configurar Variables de Entorno

El script creará un archivo `.env` desde `.env.example`. **Debes editar este archivo** con tus credenciales:

```powershell
notepad .env
```

Configura al menos:
- `TELEGRAM_TOKEN`: Token de tu bot de Telegram (obtenerlo desde [@BotFather](https://t.me/botfather))

### 5. Ejecutar el Proyecto

**Backend API:**
```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Ejecutar API
python -m uvicorn backend.api.main:app --reload
```

**Frontend:**
```powershell
cd frontend
npm run dev
```

**Bot de Telegram:**
```powershell
python backend\main.py
```

**Docker Compose (Todo junto):**
```powershell
docker-compose up --build
```

---

## 🐧 Linux / 🍎 macOS - Usando Bash

### 1. Preparación

Abre la terminal y navega a la carpeta del proyecto:

```bash
cd /ruta/a/tu/EntrenaSmart
```

### 2. Hacer el Script Ejecutable (Solo la primera vez)

```bash
chmod +x setup.sh
```

### 3. Ejecutar Setup

**Opción A: Configuración Básica**
```bash
./setup.sh
```

**Opción B: Configuración y Ejecución Automática**
```bash
./setup.sh --run
```

**Opción C: Omitir Verificación de Requisitos**
```bash
./setup.sh --skip-checks
```

**Opción D: Todas las opciones**
```bash
./setup.sh --skip-checks --run
```

### 4. Configurar Variables de Entorno

El script creará un archivo `.env` desde `.env.example`. **Debes editar este archivo** con tus credenciales:

```bash
nano .env
# O usando tu editor preferido: vim, gedit, vscode, etc.
```

Configura al menos:
- `TELEGRAM_TOKEN`: Token de tu bot de Telegram (obtenerlo desde [@BotFather](https://t.me/botfather))

### 5. Ejecutar el Proyecto

**Backend API:**
```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar API
python -m uvicorn backend.api.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

**Bot de Telegram:**
```bash
python backend/main.py
```

**Docker Compose (Todo junto):**
```bash
docker-compose up --build
```

---

## 📦 ¿Qué hace el Script de Setup?

El script de configuración automáticamente:

1. ✅ **Verifica requisitos** - Python, Node.js, npm, Git
2. ✅ **Crea entorno virtual** - `.venv` para aislar dependencias de Python
3. ✅ **Instala dependencias de Python** - `requirements.txt` y `requirements-dev.txt`
4. ✅ **Instala dependencias de Node.js** - `npm install` en `frontend/`
5. ✅ **Configura variables de entorno** - Copia `.env.example` a `.env`
6. ✅ **Crea directorios necesarios** - `storage/`, `logs/`, etc.
7. ✅ **Inicializa la base de datos** - Crea esquema SQLite
8. ✅ **Muestra comandos útiles** - Resumen de cómo ejecutar el proyecto

---

## 🌐 URLs de la Aplicación

Una vez ejecutado, accede a:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Dashboard** | http://localhost:5173/ | Panel principal del entrenador |
| **Estudiantes** | http://localhost:5173/students | Gestión de estudiantes |
| **Configuración** | http://localhost:5173/config | Configuración de entrenamientos |
| **API Docs** | http://localhost:8000/docs | Documentación interactiva de la API |
| **API ReDoc** | http://localhost:8000/redoc | Documentación alternativa de la API |
| **API Health** | http://localhost:8000/health | Health check del backend |

---

## 🔧 Comandos Útiles Post-Setup

### Python (Backend)

```bash
# Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\Activate.ps1  # Windows

# Ejecutar tests
pytest tests/ -v

# Ejecutar tests con cobertura
pytest --cov=src tests/

# Formatear código
black src/ tests/

# Ordenar imports
isort src/ tests/

# Verificar linting
flake8 src/ tests/

# Verificar tipos
mypy src/
```

### JavaScript (Frontend)

```bash
cd frontend

# Ejecutar en desarrollo
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview

# Linting
npm run lint
```

### Base de Datos

```bash
# Inicializar BD manualmente
python scripts/db/init_db.py

# Conectarse a SQLite (desde root del proyecto)
sqlite3 storage/entrenasmart.db

# Ver tablas
.schema

# Salir de SQLite
.quit
```

### Docker

```bash
# Iniciar todo
docker-compose up --build

# Iniciar en background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v
```

---

## 🐛 Solución de Problemas

### Error: "No se puede ejecutar scripts en este sistema"

**Windows PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: "python: command not found"

**Linux/Mac:**
```bash
# Verifica si tienes python3
python3 --version

# Crea un alias (temporal)
alias python=python3
```

### Error: "Access to the path ... is denied" al eliminar .venv

Este error ocurre cuando el entorno virtual está en uso por algún proceso.

**Windows PowerShell:**
```powershell
# 1. Desactivar entorno virtual si está activo
deactivate

# 2. Cerrar IDEs (VSCode, PyCharm, etc.)

# 3. Esperar y forzar eliminación
Start-Sleep -Seconds 2
Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue

# 4. Si persiste, renombrar y crear nuevo
if (Test-Path .venv) {
    Rename-Item .venv .venv_old
    Write-Host "Entorno renombrado. Elimina .venv_old manualmente después."
}

# 5. Ejecutar setup nuevamente
.\setup.ps1
```

**Nota:** El script `setup.ps1` v1.1+ maneja esto automáticamente renombrando el directorio.

### Error: "Module not found"

**Backend:**
```bash
source .venv/bin/activate  # Activa el entorno virtual primero
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Error 404 en `/api/students`

Asegúrate de que:
1. El backend esté corriendo en `http://localhost:8000`
2. El archivo `.env` tenga `API_CORS_ORIGINS=http://localhost:5173`
3. El router de students esté registrado en `backend/api/main.py`

Verifica que el backend esté funcionando:
```bash
curl http://localhost:8000/health
```

### Puerto 8000 o 5173 ya en uso

**Windows:**
```powershell
# Ver qué proceso usa el puerto
netstat -ano | findstr :8000

# Matar proceso (reemplaza PID)
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# Ver qué proceso usa el puerto
lsof -i :8000

# Matar proceso
kill -9 <PID>
```

### Base de datos corrupta

```bash
# Respaldar BD actual
cp storage/entrenasmart.db storage/backups/entrenasmart_backup.db

# Reinicializar BD
rm storage/entrenasmart.db
python scripts/db/init_db.py
```

---

## 📝 Configuración del Bot de Telegram

### 1. Crear Bot con BotFather

1. Abre Telegram y busca [@BotFather](https://t.me/botfather)
2. Envía `/newbot`
3. Sigue las instrucciones (nombre del bot, username)
4. Copia el **token** que te da BotFather

### 2. Configurar Token en `.env`

```env
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 3. Obtener tu Chat ID (Opcional)

Para recibir notificaciones como entrenador:

1. Busca [@userinfobot](https://t.me/userinfobot) en Telegram
2. Envía `/start`
3. Copia tu `Id` (es un número)
4. Agrégalo en `.env`:

```env
TRAINER_CHAT_ID=tu_chat_id_aqui
```

---

## 🎯 Próximos Pasos

Una vez configurado el proyecto:

1. **Explora el Dashboard** - http://localhost:5173/
2. **Registra estudiantes** - Desde la sección "Estudiantes"
3. **Configura entrenamientos** - Desde la sección "Configuración"
4. **Prueba el bot** - Envía `/start` a tu bot de Telegram
5. **Revisa logs** - Verifica que todo funcione correctamente

---

## 📚 Recursos Adicionales

- **Documentación completa**: Ver `CLAUDE.md` en la raíz del proyecto
- **Arquitectura**: Ver `docs/architecture.md`
- **Changelog**: Ver `docs/CHANGELOG.md`
- **API Docs**: http://localhost:8000/docs (cuando el backend esté corriendo)

---

## 💡 Consejos

- **Usa Docker** para evitar problemas de dependencias
- **Activa el entorno virtual** antes de ejecutar comandos de Python
- **Revisa los logs** si algo no funciona como esperado
- **Haz backups** de la base de datos antes de hacer cambios importantes

---

## 🆘 ¿Necesitas Ayuda?

Si tienes problemas que no se resuelven con esta guía:

1. Revisa los logs en `logs/`
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de que los puertos 8000 y 5173 no estén en uso
4. Consulta la documentación completa en `CLAUDE.md`

---

**¡Listo! Ahora puedes empezar a usar EntrenaSmart. 💪✨**
