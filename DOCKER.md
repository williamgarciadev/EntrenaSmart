# 🐳 EntrenaSmart - Guía de Ejecución con Docker

## Descripción

EntrenaSmart es una aplicación completa que se ejecuta con Docker Compose, incluyendo:

- **Frontend**: React/Vite (Nginx)
- **Backend API**: FastAPI (Python/Uvicorn)
- **Base de Datos**: PostgreSQL
- **Bot de Telegram**: Python (Opcional)

## Requisitos Previos

- **Docker**: v20.10 o superior
- **Docker Compose**: v1.29 o superior
- **Git**: Para clonar el repositorio

### Instalar Docker

#### Windows:
- Descargar [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Ejecutar el instalador
- Reiniciar la computadora

#### Linux:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# CentOS/RHEL
sudo yum install docker docker-compose
```

#### macOS:
- Descargar [Docker Desktop para Mac](https://www.docker.com/products/docker-desktop)
- Instalar siguiendo el asistente

## Configuración

### 1. Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.docker .env

# Editar .env con tus valores (opcional)
# nano .env
```

**Variables Importantes**:
- `POSTGRES_PASSWORD`: Contraseña de PostgreSQL
- `TELEGRAM_BOT_TOKEN`: Token del bot de Telegram (si usas el bot)
- `API_CORS_ORIGINS`: Orígenes permitidos para CORS

## Ejecución

### 1. Iniciar los Servicios

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f api      # Backend
docker-compose logs -f frontend # Frontend
docker-compose logs -f postgres # Base de datos
```

### 2. Verificar que Todo Está Funcionando

```bash
# Ver estado de los contenedores
docker-compose ps

# Debería mostrar algo como:
# NAME                 STATUS
# entrenasmart-db      Up (healthy)
# entrenasmart-api     Up (healthy)
# entrenasmart-frontend  Up (healthy)
```

### 3. Acceder a la Aplicación

| Servicio | URL | Propósito |
|----------|-----|----------|
| **Frontend** | http://localhost:5173 | Interfaz de usuario |
| **API** | http://localhost:8000 | Backend REST API |
| **API Docs** | http://localhost:8000/docs | Documentación interactiva |
| **PostgreSQL** | localhost:5432 | Base de datos |
| **pgAdmin** | http://localhost:5050 | Admin GUI para PostgreSQL |
| **Adminer** | http://localhost:8080 | Admin universal de BD |

## Administración de Base de Datos

### 🗄️ Credenciales de Acceso

**PostgreSQL**:
```
Host: postgres (desde Docker) o localhost:5432 (local)
Usuario: entrenasmart
Contraseña: entrenasmart123
Base de datos: entrenasmart
```

**pgAdmin 4** (Interfaz gráfica recomendada):
```
URL: http://localhost:5050
Email: admin@entrenasmart.com
Contraseña: admin123
```

**Adminer** (Herramienta universal):
```
URL: http://localhost:8080
Sistema: PostgreSQL
Servidor: postgres
Usuario: entrenasmart
Contraseña: entrenasmart123
Base de datos: entrenasmart
```

### Usando pgAdmin

1. Acceder a http://localhost:5050
2. Hacer login con:
   - Email: `admin@entrenasmart.com`
   - Contraseña: `admin123`
3. En la primera ejecución, registrar el servidor:
   - Click en "Add New Server"
   - Name: `entrenasmart`
   - Host: `postgres` (desde Docker) o `localhost` (local)
   - Username: `entrenasmart`
   - Password: `entrenasmart123`
   - Port: `5432`
4. Explorar bases de datos, tablas y ejecutar queries

### Usando Adminer

1. Acceder a http://localhost:8080
2. Seleccionar: **PostgreSQL**
3. Ingresar credenciales:
   - Sistema: PostgreSQL
   - Servidor: `postgres`
   - Usuario: `entrenasmart`
   - Contraseña: `entrenasmart123`
   - Base de datos: `entrenasmart`
4. Click en "Entrar"

**Ventaja de Adminer**: Una sola imagen, interfaz minimalista, sin instalación.

### Acceso por línea de comandos

```bash
# Conectar a PostgreSQL interactivamente
docker-compose exec postgres psql -U entrenasmart -d entrenasmart

# Comandos útiles dentro de psql:
\dt                    # Listar todas las tablas
\d students            # Describir estructura de tabla
\d+ students           # Describir con detalles adicionales
SELECT * FROM students;  # Consultar datos
\x                     # Toggle formato expandido (útil para datos anchos)
\q                     # Salir
```

## Operaciones Comunes

### Ver Logs
```bash
# Todos los servicios
docker-compose logs -f

# Especifico (últimas 100 líneas)
docker-compose logs --tail=100 api
```

### Detener Servicios
```bash
# Pausar sin eliminar contenedores
docker-compose stop

# Eliminar todo (incluye volúmenes de datos)
docker-compose down

# Eliminar todo incluyendo datos de la BD
docker-compose down -v
```

### Reiniciar Servicios
```bash
# Reiniciar todos
docker-compose restart

# Reiniciar específico
docker-compose restart api
```

### Reconstruir Imágenes
```bash
# Reconstruir sin cachéé
docker-compose build --no-cache

# Reconstruir y levantar
docker-compose up -d --build
```

### Ejecutar Comandos en Contenedores

```bash
# Bash en el contenedor de API
docker-compose exec api bash

# Bash en el contenedor de Base de Datos
docker-compose exec postgres bash

# Ejecutar comando único
docker-compose exec api python -m pytest
```

### Acceder a la Base de Datos

```bash
# Conectar a PostgreSQL
docker-compose exec postgres psql -U entrenasmart -d entrenasmart

# Desde la línea de comandos local (si tienes psql instalado)
psql -h localhost -U entrenasmart -d entrenasmart
```

## Solución de Problemas

### Puerto Ya en Uso

Si recibe el error `Port is already in use`:

```bash
# Encontrar qué está usando el puerto
lsof -i :5173  # Frontend
lsof -i :8000  # API
lsof -i :5432  # PostgreSQL

# Matar el proceso
kill -9 <PID>

# O cambiar el puerto en docker-compose.yml
```

### Base de Datos No Se Conecta

```bash
# Verificar que PostgreSQL está saludable
docker-compose ps

# Ver logs de PostgreSQL
docker-compose logs postgres

# Reintentar conexión
docker-compose restart api
```

### Frontend No Carga

```bash
# Verificar logs del frontend
docker-compose logs frontend

# Limpiar build y reintentar
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d
```

### Permisos Denegados

```bash
# En Linux, agregar usuario al grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### pgAdmin No Inicia o No Responde

```bash
# Ver logs de pgAdmin
docker-compose logs pgadmin

# Reiniciar solo pgAdmin
docker-compose restart pgadmin

# Reconstruir e iniciar pgAdmin
docker-compose up -d --build pgadmin
```

**Solución**: Esperar 30-60 segundos después de iniciar Docker, pgAdmin es lento en la primera ejecución.

### Adminer No Puede Conectar

Si ves "Cannot connect to server" en Adminer:

1. **Verificar servidor correcto**: Usar `postgres` (no `localhost`)
2. **Verificar puerto**: 5432 (por defecto)
3. **Verificar credenciales**: entrenasmart / entrenasmart123
4. **Ver logs**: `docker-compose logs postgres`

Si aún falla:
```bash
# Reiniciar postgres
docker-compose restart postgres

# Esperar health check
docker-compose ps postgres  # Debe mostrar "healthy"

# Reintentar en Adminer
```

### Base de Datos Vacía en pgAdmin/Adminer

Si las tablas no aparecen:

```bash
# Verificar que init_db() fue ejecutado
docker-compose logs api | grep -i "inicializ"

# Inicializar manualmente
docker-compose exec api python -c "from src.models.base import init_db; init_db()"

# Recargar pgAdmin/Adminer en navegador (F5)
```

## Variables de Entorno Importantes

```env
# PostgreSQL
POSTGRES_DB=entrenasmart
POSTGRES_USER=entrenasmart
POSTGRES_PASSWORD=entrenasmart123

# Base de Datos
DATABASE_URL=postgresql://entrenasmart:entrenasmart123@postgres:5432/entrenasmart

# API
API_CORS_ORIGINS=http://localhost:5173,http://localhost:80,http://frontend:80
DEBUG=False

# Telegram (Opcional)
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_WEBHOOK_URL=https://tudominio.com/webhook

# Almacenamiento
STORAGE_PATH=/app/storage
LOGS_PATH=/app/logs
```

## Volúmenes Persistentes

Los datos se almacenan en volúmenes de Docker:

- **postgres_data**: Base de datos PostgreSQL
- **storage**: Archivos y configuración
- **logs**: Logs de la aplicación

```bash
# Ver volúmenes
docker volume ls

# Ver detalles de un volumen
docker volume inspect entrenasmart_postgres_data

# Limpiar volúmenes no usados
docker volume prune
```

## Desarrollo vs Producción

### Desarrollo (Actual)
- DEBUG=True
- Recarga automática de código
- Logs detallados
- CORS abierto para localhost

### Producción
- DEBUG=False
- Sin recarga automática
- Logs limitados
- CORS restringido
- SSL/TLS habilitado
- Reverse proxy (Nginx)

Para pasar a producción:
1. Editar .env con valores de producción
2. Usar certificados SSL
3. Configurar dominio propio
4. Usar contraseñas seguras

## Backup y Restauración

### Backup de la Base de Datos

```bash
# Crear backup
docker-compose exec postgres pg_dump -U entrenasmart entrenasmart > backup.sql

# Backup con compresión
docker-compose exec postgres pg_dump -U entrenasmart entrenasmart | gzip > backup.sql.gz
```

### Restaurar Base de Datos

```bash
# Restaurar desde archivo
docker-compose exec -T postgres psql -U entrenasmart entrenasmart < backup.sql

# Restaurar desde archivo comprimido
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U entrenasmart entrenasmart
```

## Actualización

Para actualizar a una nueva versión:

```bash
# 1. Detener servicios
docker-compose down

# 2. Actualizar código (git pull)
git pull origin main

# 3. Reconstruir imágenes
docker-compose build --no-cache

# 4. Levantar nuevamente
docker-compose up -d

# 5. Ver logs
docker-compose logs -f
```

## Scripts Útiles

### Script de Inicio (start.sh)

```bash
#!/bin/bash
echo "Iniciando EntrenaSmart..."
docker-compose up -d
echo "Esperando que los servicios se inicien..."
sleep 10
docker-compose ps
echo "✓ EntrenaSmart iniciada correctamente"
echo "Frontend: http://localhost:5173"
echo "API: http://localhost:8000"
```

### Script de Parada (stop.sh)

```bash
#!/bin/bash
echo "Deteniendo EntrenaSmart..."
docker-compose down
echo "✓ EntrenaSmart detenida"
```

## Ayuda y Soporte

Para más información:
- Docs API: http://localhost:8000/docs
- GitHub Issues: [Crear issue](https://github.com/turepositorio/issues)
- Email: soporte@tudominio.com

---

## ✨ Novedades Recientes

- ✅ **pgAdmin 4**: Interfaz gráfica completa para administración de PostgreSQL
- ✅ **Adminer**: Herramienta universal para BD (MySQL, PostgreSQL, SQLite, etc.)
- ✅ **Soporte Dual de BD**: Configuración flexible para SQLite (desarrollo) y PostgreSQL (Docker)
- ✅ **Health Checks**: Todos los servicios con verificaciones de estado automáticas

**Última Actualización**: Noviembre 2024
**Versión**: 1.1.0
