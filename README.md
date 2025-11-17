# 🏋️ EntrenaSmart - Gestión de Entrenamientos

**EntrenaSmart** es una aplicación full-stack moderna para gestionar tu programación de entrenamientos personalizados.

## 🚀 Inicio Rápido

### Requisitos Previos
- **Docker Desktop**: v20.10+
- **Docker Compose**: v1.29+ (incluido en Docker Desktop)
- **Windows 11** (o Linux/macOS con scripts `.sh`)

### Instalación en Un Comando

#### Windows 11 (Opción 1: PowerShell)
```powershell
.\setup.ps1
```

#### Windows 11 (Opción 2: Batch/CMD)
```batch
setup.bat
```

#### Linux/macOS
```bash
./setup.sh
```

Esto hará automáticamente:
1. ✅ Verifica Docker y Docker Compose
2. ✅ Crea archivo `.env` con variables de entorno
3. ✅ Construye las imágenes Docker
4. ✅ Inicia todos los servicios
5. ✅ Verifica la salud de los servicios

### Acceso a Servicios

Después de ejecutar el script de instalación, accede a:

- **Frontend (React)**: http://localhost:5173
- **API Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📦 Arquitectura

```
Frontend          Backend           Database
React/Vite    →   FastAPI      →   PostgreSQL
Nginx             Uvicorn          Port 5432
Port 5173         Port 8000
```

**Stack Tecnológico**:
- **Frontend**: React 18, Vite, Tailwind CSS, shadcn/ui, Framer Motion
- **Backend**: FastAPI, Python 3.11, Uvicorn
- **Database**: PostgreSQL 16
- **Bot**: Python Telegram Bot (opcional)

## 🛠️ Comandos Útiles

### PowerShell (Windows 11)
```powershell
# Ver logs en tiempo real
docker-compose logs -f

# Ver estado de servicios
docker-compose ps

# Detener servicios
.\docker-stop.ps1

# Usar utilidades (backup, restore, etc)
.\docker-utils.ps1
```

### Terminal (Linux/macOS)
```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver estado de servicios
docker-compose ps

# Detener servicios
./docker-stop.sh

# Usar utilidades (backup, restore, etc)
./docker-utils.sh
```

Para más detalles, ver [DOCKER.md](DOCKER.md)

## 📁 Estructura del Proyecto

```
EntrenaSmart/
├── backend/              # API FastAPI
├── frontend/             # App React/Vite
│
├── docker-compose.yml    # Configuración de servicios
├── Dockerfile            # Frontend
├── Dockerfile.api        # Backend API
├── Dockerfile.bot        # Bot de Telegram
│
├── Windows 11 (PowerShell & Batch)
│   ├── setup.ps1         # Setup maestro (PowerShell)
│   ├── setup.bat         # Setup maestro (Batch)
│   ├── docker-start.ps1  # Iniciar servicios
│   ├── docker-stop.ps1   # Detener servicios
│   └── docker-utils.ps1  # Utilidades Docker
│
├── Linux/macOS (Bash)
│   ├── setup.sh          # Setup maestro
│   ├── docker-start.sh   # Iniciar servicios
│   ├── docker-stop.sh    # Detener servicios
│   └── docker-utils.sh   # Utilidades Docker
│
├── .env.docker           # Template de variables
├── DOCKER.md             # Documentación Docker
└── README.md             # Este archivo
```

## 🔧 Configuración

El archivo `.env.docker` contiene:
- Credenciales de PostgreSQL
- URLs de base de datos
- CORS origins
- Tokens de Telegram (opcional)

Para cambiar valores, edita `.env` después del primer setup.

## 📚 Documentación Completa

- **[WINDOWS.md](WINDOWS.md)** - Guía completa para Windows 11 (PowerShell, Batch, troubleshooting)
- **[DOCKER.md](DOCKER.md)** - Guía completa de Docker, operaciones, troubleshooting

## 🔐 Seguridad

- ✅ Base de datos en contenedor aislado
- ✅ Variables de entorno segregadas
- ✅ Volúmenes Docker para persistencia
- ✅ Health checks en todos los servicios

## 📝 Licencia

MIT License

---

**Versión**: 1.0.0
**Status**: ✅ Docker-Ready & Production-Focused
