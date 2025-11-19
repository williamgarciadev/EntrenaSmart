# EntrenaSmart - Docker Compose Deployment

Esta carpeta contiene todos los archivos necesarios para desplegar EntrenaSmart localmente con Docker Compose.

## Archivos

- `Dockerfile.bot` - Dockerfile para el Bot de Telegram
- `Dockerfile.api` - Dockerfile para la API FastAPI
- `Dockerfile.frontend` - Dockerfile para el Frontend React/Vite
- `docker-compose.yml` - Orquestación de todos los servicios

## Prerequisitos

1. Docker instalado: https://docs.docker.com/get-docker/
2. Docker Compose instalado (incluido con Docker Desktop)
3. Archivo `.env` en la raíz del proyecto con las variables necesarias

## Configuración

### 1. Crear archivo .env en la raíz del proyecto

```bash
# Copiar desde la raíz del proyecto
cp ../../.env.example ../../.env
```

### 2. Editar .env con tus valores

```bash
# Bot de Telegram
TELEGRAM_BOT_TOKEN=tu_bot_token_de_@BotFather
TRAINER_TELEGRAM_ID=tu_id_numerico_de_telegram

# Base de Datos
POSTGRES_PASSWORD=entrenasmart123

# Seguridad
SECRET_KEY=genera_una_clave_secreta_de_minimo_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Configuración
DEBUG=False
ENVIRONMENT=development
TZ=America/Bogota
LOG_LEVEL=INFO

# Recordatorios
REMINDER_MINUTES_BEFORE=5
WEEKLY_REPORT_DAY=6
WEEKLY_REPORT_TIME=20:00

# CORS (no necesario para Docker local)
CORS_ORIGINS=http://localhost:5173
```

## Uso

### Iniciar todos los servicios

```bash
cd deployment/docker
docker-compose up -d
```

### Ver logs

```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f bot
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Detener servicios

```bash
docker-compose down
```

### Detener y eliminar volúmenes (cuidado: borra la BD)

```bash
docker-compose down -v
```

### Reconstruir después de cambios en el código

```bash
docker-compose up -d --build
```

### Reconstruir un servicio específico

```bash
docker-compose up -d --build api
```

## Servicios y Puertos

Una vez iniciados, los servicios están disponibles en:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Bot** | N/A | Bot de Telegram (sin interfaz web) |
| **API** | http://localhost:8000 | API FastAPI |
| **API Docs** | http://localhost:8000/docs | Documentación interactiva (Swagger) |
| **Frontend** | http://localhost:5173 | Aplicación web React |
| **PostgreSQL** | localhost:5432 | Base de datos |
| **pgAdmin** | http://localhost:5050 | Administrador de PostgreSQL |
| **Adminer** | http://localhost:8080 | Administrador universal de BD |

### Credenciales de pgAdmin

- **Email**: admin@entrenasmart.com
- **Password**: admin123

### Conectar a PostgreSQL desde pgAdmin

- **Host**: postgres
- **Port**: 5432
- **Database**: entrenasmart
- **Username**: entrenasmart
- **Password**: (valor de POSTGRES_PASSWORD en .env)

## Troubleshooting

### Error: "Port already in use"

Otro servicio está usando el puerto. Detén el servicio o cambia el puerto en docker-compose.yml:

```yaml
ports:
  - "8001:8000"  # Cambiar 8000 por otro puerto
```

### Error: "Cannot connect to database"

1. Verifica que PostgreSQL esté corriendo:
   ```bash
   docker-compose ps
   ```

2. Verifica los logs de PostgreSQL:
   ```bash
   docker-compose logs postgres
   ```

3. Espera a que PostgreSQL esté "healthy":
   ```bash
   docker-compose ps | grep healthy
   ```

### Error: "No such file or directory: .env"

Crea el archivo .env en la raíz del proyecto (dos niveles arriba):

```bash
cd ../..
cp .env.example .env
# Edita .env con tus valores
```

### Reconstruir todo desde cero

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Ver uso de recursos

```bash
docker stats
```

### Limpiar imágenes antiguas

```bash
docker system prune -a
```

## Comandos Útiles

```bash
# Ejecutar comando en contenedor
docker-compose exec api python --version
docker-compose exec bot python backend/main.py

# Ver redes
docker network ls

# Ver volúmenes
docker volume ls

# Inspeccionar contenedor
docker-compose exec api /bin/bash

# Ver logs de inicio únicamente
docker-compose logs --tail=100 api

# Seguir logs en tiempo real
docker-compose logs -f --tail=100 bot
```

## Desarrollo

Para desarrollo, puedes montar volúmenes adicionales para hot-reload:

```yaml
# Agregar en docker-compose.yml
api:
  volumes:
    - ../../backend:/app/backend  # Hot reload
```

Luego:

```bash
docker-compose up -d --build api
```

## Migración de Datos

### Backup de PostgreSQL

```bash
docker-compose exec postgres pg_dump -U entrenasmart entrenasmart > backup.sql
```

### Restore de PostgreSQL

```bash
cat backup.sql | docker-compose exec -T postgres psql -U entrenasmart entrenasmart
```

## Performance

Para producción local, considera:

1. **Limitar recursos**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```

2. **Habilitar health checks** (ya incluidos)

3. **Configurar restart policies** (ya incluido: `unless-stopped`)

## Actualización

```bash
# Detener servicios
docker-compose down

# Hacer git pull
cd ../..
git pull origin main

# Reconstruir y reiniciar
cd deployment/docker
docker-compose up -d --build
```
