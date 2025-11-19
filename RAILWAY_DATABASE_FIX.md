# Railway PostgreSQL Connection Fix

## Problema Actual

Tu bot está usando SQLite en lugar de PostgreSQL, causando errores de tipo ARRAY:

```
Inicializando base de datos (sqlite:///storage/entrenasmart.db)...
ERROR: Compiler can't render element of type ARRAY
```

## Solución: 3 Pasos Sencillos

### Paso 1: Crear Servicio PostgreSQL en Railway

Si aún **NO** has creado el servicio PostgreSQL:

1. Ve a tu proyecto en Railway Dashboard
2. Click en **"+ New"** (botón superior derecho)
3. Selecciona **"Database"**
4. Elige **"Add PostgreSQL"**
5. Railway creará automáticamente el servicio con el nombre **"Postgres"**

**IMPORTANTE**: Anota el nombre exacto que Railway le da al servicio (generalmente es "Postgres")

### Paso 2: Verificar el Nombre del Servicio PostgreSQL

En Railway Dashboard:

1. Ve a tu proyecto
2. Mira todos los servicios desplegados
3. Identifica el servicio de base de datos PostgreSQL
4. **Anota el nombre exacto** (puede ser "Postgres", "PostgreSQL", "database", etc.)

### Paso 3: Actualizar la Variable DATABASE_URL

Una vez que sepas el nombre exacto del servicio PostgreSQL, actualiza la variable en el servicio **Bot**:

#### Opción A: Si el servicio se llama "Postgres"
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

#### Opción B: Si el servicio tiene otro nombre (ejemplo: "PostgreSQL")
```bash
DATABASE_URL=${{PostgreSQL.DATABASE_URL}}
```

#### Opción C: Si el servicio tiene otro nombre (ejemplo: "database")
```bash
DATABASE_URL=${{database.DATABASE_URL}}
```

**Nota**: NO uses comillas dobles. La sintaxis correcta es `${{ServiceName.DATABASE_URL}}` sin comillas.

## Cómo Actualizar Variables en Railway

### En el Servicio Bot:

1. Click en el servicio **Bot** en Railway Dashboard
2. Ve a la pestaña **"Variables"**
3. Encuentra la variable **DATABASE_URL**
4. Edita su valor a: `${{NombreServicioPostgres.DATABASE_URL}}`
5. Click **"Save"**
6. Railway redesplegará automáticamente el servicio

## Verificación del Fix

Después de actualizar la variable, ve a los logs del servicio Bot:

### ✅ Logs Correctos (PostgreSQL funcionando):
```
Inicializando base de datos (postgresql://...)...
✓ Base de datos inicializada correctamente
✓ Bot iniciado exitosamente
```

### ❌ Logs Incorrectos (aún usando SQLite):
```
Inicializando base de datos (sqlite:///storage/entrenasmart.db)...
ERROR: Compiler can't render element of type ARRAY
```

## Pasos Siguientes (Después del Fix)

Una vez que el bot esté conectado a PostgreSQL:

### 1. Verificar que el Bot Inicia Correctamente

Revisa los logs del servicio Bot. Deberías ver:
```
✓ Base de datos inicializada correctamente
✓ Tablas verificadas/creadas
✓ Bot iniciado exitosamente
✓ Programador de tareas iniciado
```

### 2. Ejecutar Migración de Timestamps (IMPORTANTE)

La base de datos necesita una migración para manejar correctamente las zonas horarias.

**Opción 1: Ejecutar desde Railway CLI**

Si tienes Railway CLI instalado:

```bash
# Instalar Railway CLI (si no lo tienes)
npm i -g @railway/cli

# Login
railway login

# Link a tu proyecto
railway link

# Ejecutar la migración en el servicio Bot
railway run -s Bot python backend/migrations/migrate_timestamps_to_timezone.py
```

**Opción 2: Ejecutar manualmente conectándote a la BD**

1. Ve al servicio PostgreSQL en Railway
2. Copia la variable **DATABASE_URL**
3. Ejecuta el script de migración localmente:

```bash
# En tu máquina local
export DATABASE_URL="postgresql://usuario:password@host:port/database"
python backend/migrations/migrate_timestamps_to_timezone.py
```

**Opción 3: Agregar comando de migración al startup**

Puedes modificar el Dockerfile para ejecutar la migración automáticamente:

```dockerfile
# Al final de Dockerfile (antes de CMD)
RUN echo '#!/bin/sh\n\
python backend/migrations/migrate_timestamps_to_timezone.py\n\
python backend/main.py' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
```

### 3. Configurar las Demás Variables de Entorno

Asegúrate de que TODAS estas variables estén configuradas en el servicio Bot:

```bash
# OBLIGATORIAS
TELEGRAM_BOT_TOKEN=tu_token_real_aqui
TRAINER_TELEGRAM_ID=tu_id_numerico
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=genera_clave_secreta_minimo_32_caracteres

# RECOMENDADAS
TZ=America/Bogota
LOG_LEVEL=INFO
ENVIRONMENT=production

# OPCIONALES (para backups automáticos)
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
MAX_BACKUPS=7
```

## Troubleshooting Adicional

### Problema: Railway no encuentra el servicio PostgreSQL

**Síntoma**: Railway muestra error "Service not found"

**Solución**:
1. Asegúrate de que ambos servicios (Bot y Postgres) están en el **mismo proyecto**
2. Verifica que el nombre del servicio es exacto (sensible a mayúsculas/minúsculas)
3. Intenta usar la referencia completa: `${{Postgres.DATABASE_PRIVATE_URL}}`

### Problema: La variable se ve correcta pero sigue usando SQLite

**Posibles causas**:

1. **Las comillas están mal**:
   - ❌ INCORRECTO: `DATABASE_URL="${{Postgres.DATABASE_URL}}"`
   - ✅ CORRECTO: `DATABASE_URL=${{Postgres.DATABASE_URL}}`

2. **El servicio PostgreSQL no está activo**:
   - Verifica en Railway Dashboard que el servicio Postgres tenga status "Active"
   - Revisa los logs del servicio Postgres para confirmar que inició correctamente

3. **Variable duplicada**:
   - Asegúrate de que no hay múltiples variables `DATABASE_URL`
   - Elimina cualquier variable duplicada

### Problema: Error de conexión a PostgreSQL

**Síntoma**: `could not connect to server` o `connection refused`

**Soluciones**:

1. **Espera a que PostgreSQL esté listo**:
   - PostgreSQL puede tardar 30-60 segundos en estar listo
   - Railway redesplegará automáticamente cuando esté disponible

2. **Verifica las credenciales**:
   - No modifiques manualmente DATABASE_URL
   - Usa siempre la referencia `${{Postgres.DATABASE_URL}}`

3. **Revisa el Health Check del servicio Postgres**:
   - Debe estar "Healthy" en Railway Dashboard

## Comandos Útiles de Railway CLI

```bash
# Ver variables de un servicio
railway variables -s Bot

# Ver logs en tiempo real
railway logs -s Bot

# Ejecutar comando en el servicio
railway run -s Bot python --version

# Redeploy manual
railway up -s Bot
```

## Contacto y Soporte

Si sigues teniendo problemas:

1. **Verifica los logs del Bot**: Busca mensajes de error específicos
2. **Verifica los logs de Postgres**: Confirma que está aceptando conexiones
3. **Captura de pantalla**: Toma screenshots de:
   - Variables del servicio Bot
   - Variables del servicio Postgres
   - Logs de ambos servicios
   - Lista de servicios en el proyecto

## Checklist Final

Antes de reportar un problema, verifica:

- [ ] Servicio PostgreSQL creado y activo en Railway
- [ ] Nombre del servicio PostgreSQL verificado
- [ ] Variable `DATABASE_URL=${{NombreCorrectoServicio.DATABASE_URL}}` sin comillas
- [ ] Servicio Bot redesplegado después de cambiar variables
- [ ] Logs del Bot revisados (buscar "postgresql://" en lugar de "sqlite://")
- [ ] PostgreSQL muestra status "Healthy" en Railway Dashboard
- [ ] Todas las variables obligatorias configuradas
- [ ] Migración de timestamps ejecutada (después de que PostgreSQL funcione)

## Próximos Pasos

Una vez que el Bot esté funcionando correctamente con PostgreSQL:

1. ✅ Desplegar servicio API (FastAPI)
2. ✅ Desplegar servicio Frontend (React + Nginx)
3. ✅ Configurar dominio personalizado (opcional)
4. ✅ Configurar backups automáticos
5. ✅ Monitorear uso de recursos y costos

---

**¿Todo listo?** Una vez que hagas los cambios, el bot debería iniciar correctamente en unos segundos.
