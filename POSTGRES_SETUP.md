# Configuración de PostgreSQL para EntrenaSmart

Los scripts de inicio ahora están configurados para usar **PostgreSQL** en lugar de SQLite para un mejor rendimiento y escalabilidad.

## Opción 1: Usar Docker (Recomendado - Más Fácil)

### Windows con Docker Desktop

1. **Instalar Docker Desktop**:
   - Descargar de: https://www.docker.com/products/docker-desktop/
   - Instalar y reiniciar si es necesario

2. **Iniciar solo PostgreSQL**:
   ```powershell
   # En la carpeta del proyecto
   docker-compose up -d postgres
   ```

3. **Verificar que está corriendo**:
   ```powershell
   docker ps
   ```

   Deberías ver `entrenasmart-db` en la lista.

4. **Iniciar el backend**:
   ```powershell
   .\start-backend.ps1
   ```

### Detener PostgreSQL cuando termines:
```powershell
docker-compose down
```

## Opción 2: Instalar PostgreSQL localmente en Windows

### 1. Descargar e Instalar PostgreSQL

1. Descargar desde: https://www.postgresql.org/download/windows/
2. Ejecutar el instalador
3. Durante la instalación:
   - Puerto: **5432** (dejar por defecto)
   - Contraseña del superusuario (postgres): Anotar esta contraseña
   - Locale: Dejar por defecto

### 2. Crear la base de datos y usuario

Abrir **pgAdmin** o usar **psql** desde PowerShell:

```powershell
# Conectar a PostgreSQL
psql -U postgres

# Crear usuario
CREATE USER entrenasmart WITH PASSWORD 'entrenasmart123';

# Crear base de datos
CREATE DATABASE entrenasmart OWNER entrenasmart;

# Dar permisos
GRANT ALL PRIVILEGES ON DATABASE entrenasmart TO entrenasmart;

# Salir
\q
```

### 3. Configurar el .env

El script crea automáticamente el `.env` con esta configuración:

```env
DATABASE_URL=postgresql://entrenasmart:entrenasmart123@localhost:5432/entrenasmart
```

Si usaste una contraseña diferente, edita el archivo `.env` y cambia la URL.

### 4. Iniciar el backend

```powershell
.\start-backend.ps1
```

## Opción 3: Usar PostgreSQL en la nube (Gratis)

### Supabase (Recomendado para pruebas)

1. Crear cuenta en: https://supabase.com
2. Crear un nuevo proyecto
3. En Settings > Database, copiar la **Connection String**
4. Editar `.env` y reemplazar `DATABASE_URL` con tu connection string:
   ```env
   DATABASE_URL=postgresql://postgres:[TU-PASSWORD]@[TU-HOST]:[PUERTO]/postgres
   ```

### Otras opciones gratuitas:
- **Neon**: https://neon.tech (Postgres serverless)
- **ElephantSQL**: https://www.elephantsql.com (20MB gratis)
- **Railway**: https://railway.app (500 horas/mes gratis)

## Verificar la conexión

Después de iniciar el backend, deberías ver:

```
Inicializando tablas de la base de datos PostgreSQL...
2025-11-17 - entrenasmart - INFO - Inicializando base de datos (postgresql://...)
2025-11-17 - entrenasmart - INFO - Base de datos inicializada correctamente (PostgreSQL)
```

## Problemas comunes

### Error: "could not connect to server"

**Solución**:
1. Verificar que PostgreSQL está corriendo:
   ```powershell
   # Con Docker
   docker ps

   # Instalación local - verificar servicio
   Get-Service postgresql*
   ```

2. Si está detenido, iniciarlo:
   ```powershell
   # Docker
   docker-compose up -d postgres

   # Local
   Start-Service postgresql-x64-16  # Ajustar nombre del servicio
   ```

### Error: "password authentication failed"

**Solución**: Verificar que las credenciales en `.env` coinciden con las de PostgreSQL:
```env
DATABASE_URL=postgresql://USUARIO:CONTRASEÑA@localhost:5432/entrenasmart
```

### Error: "database does not exist"

**Solución**: Crear la base de datos manualmente:
```sql
CREATE DATABASE entrenasmart;
```

## Migrar de SQLite a PostgreSQL (si ya tenías datos)

Si ya tenías datos en SQLite y quieres migrarlos:

```powershell
# Exportar datos de SQLite (requiere instalar pgloader)
pgloader storage/entrenasmart.db postgresql://entrenasmart:entrenasmart123@localhost:5432/entrenasmart
```

O simplemente recrear los datos manualmente desde la interfaz web.

## Comparación: SQLite vs PostgreSQL

| Característica | SQLite | PostgreSQL |
|---------------|---------|------------|
| Instalación | No requiere | Requiere servidor |
| Concurrencia | Limitada | Excelente |
| Rendimiento | Bueno para desarrollo | Mejor para producción |
| Tamaño | Archivo único | Servidor completo |
| Recomendado para | Desarrollo local simple | Producción y desarrollo |

## Configuración actual

Los scripts están configurados para usar PostgreSQL por defecto con:
- Usuario: `entrenasmart`
- Contraseña: `entrenasmart123`
- Base de datos: `entrenasmart`
- Puerto: `5432`
- Host: `localhost`

**Para cambiar a SQLite**: Edita `.env` y reemplaza:
```env
# Comentar o eliminar DATABASE_URL
# DATABASE_URL=postgresql://...

# Agregar DATABASE_PATH
DATABASE_PATH=storage/entrenasmart.db
```
