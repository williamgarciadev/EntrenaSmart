# 🚂 Guía de Despliegue en Railway - EntrenaSmart

Esta guía te llevará paso a paso para desplegar EntrenaSmart en Railway.

## 📋 Pre-requisitos

- [ ] Cuenta en [Railway.app](https://railway.app)
- [ ] Repositorio de GitHub con EntrenaSmart
- [ ] Token de Bot de Telegram (obtener de [@BotFather](https://t.me/BotFather))
- [ ] Tu Telegram ID (obtener de [@userinfobot](https://t.me/userinfobot))

## 🎯 Arquitectura en Railway

Railway creará **4 servicios**:

1. **PostgreSQL** - Base de datos (provisto por Railway)
2. **API Backend** - FastAPI (Dockerfile.api)
3. **Bot** - Telegram Bot (Dockerfile.bot)
4. **Frontend** - React/Vite (frontend/Dockerfile)

---

## 📦 Paso 1: Crear Proyecto en Railway

1. Ve a [railway.app](https://railway.app) y haz login
2. Click en **"New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Autoriza Railway a acceder a tu GitHub
5. Selecciona el repositorio **EntrenaSmart**
6. Railway detectará automáticamente los Dockerfiles

---

## 🗄️ Paso 2: Agregar PostgreSQL

1. En tu proyecto Railway, click en **"+ New"**
2. Selecciona **"Database"** → **"Add PostgreSQL"**
3. Railway creará automáticamente el servicio y las variables:
   - `DATABASE_URL`
   - `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`

**✅ PostgreSQL está listo**

---

## 🔧 Paso 3: Configurar Servicio API (Backend)

### 3.1 Crear el servicio

1. Click en **"+ New"** → **"Empty Service"**
2. Nombra el servicio: **"api"**
3. En Settings → **"Source"**, conecta con el repositorio
4. En Settings → **"Build"**:
   - **Builder**: Docker
   - **Dockerfile Path**: `Dockerfile.api`
   - **Docker Build Context**: `.` (raíz del proyecto)

### 3.2 Configurar Variables de Entorno

Click en el servicio **"api"** → **"Variables"** → **"New Variable"**:

```bash
# Database (referencia al servicio PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Telegram
TELEGRAM_BOT_TOKEN=tu_bot_token_de_botfather
TRAINER_TELEGRAM_ID=tu_telegram_id_numerico

# Security
SECRET_KEY=genera_clave_secreta_aqui_min_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# App Config
DEBUG=False
ENVIRONMENT=production
TZ=America/Bogota
PYTHONUNBUFFERED=1

# CORS (actualizar después con URL del frontend)
CORS_ORIGINS=http://localhost:5173
```

### 3.3 Configurar Port

Railway asigna `$PORT` automáticamente. Asegúrate que `Dockerfile.api` use:

```dockerfile
CMD uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### 3.4 Generar Dominio Público

1. En el servicio **"api"** → **"Settings"** → **"Networking"**
2. Click **"Generate Domain"**
3. Railway creará una URL como: `https://entrenasmart-api-production.up.railway.app`
4. **Copia esta URL** (la necesitarás para el frontend)

**✅ API configurado**

---

## 🤖 Paso 4: Configurar Servicio Bot

### 4.1 Crear el servicio

1. Click en **"+ New"** → **"Empty Service"**
2. Nombra el servicio: **"bot"**
3. En Settings → **"Source"**, conecta con el repositorio
4. En Settings → **"Build"**:
   - **Builder**: Docker
   - **Dockerfile Path**: `Dockerfile.bot`
   - **Docker Build Context**: `.` (raíz del proyecto)

### 4.2 Configurar Variables de Entorno

Click en el servicio **"bot"** → **"Variables"**:

```bash
# Database (referencia al servicio PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Telegram (mismos valores que en API)
TELEGRAM_BOT_TOKEN=tu_bot_token_de_botfather
TRAINER_TELEGRAM_ID=tu_telegram_id_numerico

# Security (mismos valores que en API)
SECRET_KEY=la_misma_clave_secreta_que_en_api
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# App Config
DEBUG=False
ENVIRONMENT=production
TZ=America/Bogota
PYTHONUNBUFFERED=1
```

### 4.3 NO generar dominio público

El bot **NO necesita** dominio público, solo conecta con Telegram via polling.

**✅ Bot configurado**

---

## 🎨 Paso 5: Configurar Servicio Frontend

### 5.1 Crear el servicio

1. Click en **"+ New"** → **"Empty Service"**
2. Nombra el servicio: **"frontend"**
3. En Settings → **"Source"**, conecta con el repositorio
4. En Settings → **"Build"**:
   - **Builder**: Docker
   - **Dockerfile Path**: `frontend/Dockerfile`
   - **Docker Build Context**: `frontend`
   - **Build Args**: Agregar `VITE_API_URL`

### 5.2 Configurar Variables de Entorno

Click en el servicio **"frontend"** → **"Variables"**:

```bash
# API URL (usa la URL que generaste en el Paso 3.4)
VITE_API_URL=https://entrenasmart-api-production.up.railway.app
```

### 5.3 Verificar Dockerfile del Frontend

Asegúrate que `frontend/Dockerfile` use el ARG correctamente:

```dockerfile
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
```

### 5.4 Generar Dominio Público

1. En el servicio **"frontend"** → **"Settings"** → **"Networking"**
2. Click **"Generate Domain"**
3. Railway creará una URL como: `https://entrenasmart-frontend-production.up.railway.app`
4. **Esta es tu aplicación web pública** 🎉

**✅ Frontend configurado**

---

## 🔄 Paso 6: Actualizar CORS en API

Ahora que tienes la URL del frontend, actualiza la variable CORS en el servicio API:

1. Ve al servicio **"api"** → **"Variables"**
2. Edita `CORS_ORIGINS`:

```bash
CORS_ORIGINS=https://entrenasmart-frontend-production.up.railway.app
```

3. Railway re-desplegará automáticamente la API

---

## 🗃️ Paso 7: Migrar Base de Datos

### 7.1 Acceder a la base de datos

Railway provee varias formas de acceder:

**Opción A: Railway CLI**

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Seleccionar proyecto
railway link

# Conectar a PostgreSQL
railway connect postgres
```

**Opción B: Variables de conexión directa**

1. Ve al servicio **"Postgres"** → **"Variables"**
2. Copia las credenciales: `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`
3. Usa un cliente PostgreSQL local (DBeaver, pgAdmin, psql)

### 7.2 Ejecutar migración de timestamps

**Método 1: Desde Railway CLI**

```bash
# Conectar al servicio API
railway run bash

# Dentro del contenedor
python backend/migrations/migrate_timestamps_to_timezone.py
exit
```

**Método 2: Ejecutar manualmente en PostgreSQL**

Conecta a la base de datos y ejecuta las queries del archivo:
`backend/migrations/migrate_timestamps_to_timezone.py`

**✅ Base de datos migrada**

---

## 📊 Paso 8: Verificar Deployment

### 8.1 Verificar Logs

Para cada servicio, ve a la pestaña **"Deployments"** y verifica los logs:

**API:**
```
✓ Database connection successful
✓ Uvicorn running on 0.0.0.0:$PORT
✓ Health check endpoint: /health
```

**Bot:**
```
✓ Database connection successful
✓ Bot started successfully
✓ APScheduler running
✓ Listening for messages...
```

**Frontend:**
```
✓ Nginx started
✓ Serving on port 80
```

### 8.2 Probar la aplicación

1. **API Health Check**:
   ```
   https://tu-api-url.up.railway.app/health
   ```
   Debe devolver: `{"status": "healthy"}`

2. **Frontend**:
   ```
   https://tu-frontend-url.up.railway.app
   ```
   Debe cargar la página de login

3. **Bot de Telegram**:
   - Abre tu bot en Telegram
   - Envía `/start`
   - Debe responder con el menú

**✅ Deployment exitoso** 🎉

---

## 🔐 Paso 9: Crear Usuario Admin

Necesitas crear un trainer/admin en la base de datos:

### Opción A: Via Railway CLI

```bash
railway connect postgres

-- Dentro de psql
INSERT INTO trainers (email, password_hash, name)
VALUES (
  'admin@entrenasmart.com',
  '$2b$12$...', -- Genera hash con bcrypt
  'Admin'
);
```

### Opción B: Via API

Usa el endpoint de registro si existe, o crea uno temporal.

---

## 🚀 Paso 10: Configuración Post-Deployment

### 10.1 Configurar Auto-Deploy

Railway auto-deploya en cada push a main por defecto. Para configurar:

1. Ve a **Settings** → **"Triggers"**
2. Configura la rama: `main` o `production`
3. Habilita **"Auto-deploys"**

### 10.2 Configurar Health Checks

Railway monitorea automáticamente, pero puedes configurar:

1. **Settings** → **"Health Check"**
2. **Path**: `/health`
3. **Timeout**: 100 segundos
4. **Interval**: 300 segundos

### 10.3 Configurar Recursos

Railway asigna recursos automáticamente. Para planes Pro:

- **Memory**: 512MB - 8GB
- **CPU**: 1-8 vCPUs
- **Storage**: hasta 100GB

---

## 💰 Costos Estimados

### Plan Free (Starter)

- **$5 USD** de crédito gratis al mes
- 4 servicios × ~$1.25 = ~$5/mes
- PostgreSQL incluido (500MB gratis)
- **Costo mensual**: GRATIS (con créditos)

### Plan Pro ($20/mes)

- **$20 USD** de crédito incluido
- Sin límite de servicios
- PostgreSQL hasta 8GB incluido
- Más memoria y CPU
- **Costo mensual**: ~$20-30/mes

---

## 🔧 Troubleshooting

### Error: "DATABASE_URL not found"

**Solución**: Verifica que estés usando la referencia correcta:
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### Error: "Port already in use"

**Solución**: Asegúrate que tus Dockerfiles usen `$PORT`:
```dockerfile
CMD uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### Error: "CORS policy blocked"

**Solución**: Actualiza `CORS_ORIGINS` en la API con la URL exacta del frontend.

### Bot no responde

**Solución**:
1. Verifica logs del servicio bot
2. Confirma que `TELEGRAM_BOT_TOKEN` sea correcto
3. Verifica que el bot esté arrancado correctamente

### Frontend muestra error de conexión

**Solución**:
1. Verifica que `VITE_API_URL` apunte a la URL correcta de la API
2. Verifica que el servicio API esté corriendo
3. Verifica CORS en la API

---

## 📚 Recursos Adicionales

- [Railway Docs](https://docs.railway.app)
- [Railway CLI](https://docs.railway.app/develop/cli)
- [Railway Templates](https://railway.app/templates)
- [Railway Discord](https://discord.gg/railway)

---

## ✅ Checklist Final

- [ ] Proyecto creado en Railway
- [ ] PostgreSQL agregado y conectado
- [ ] Servicio API desplegado con variables configuradas
- [ ] Servicio Bot desplegado y corriendo
- [ ] Servicio Frontend desplegado con dominio público
- [ ] CORS actualizado en API
- [ ] Base de datos migrada (timestamps timezone-aware)
- [ ] Usuario admin creado
- [ ] Health checks verificados
- [ ] Bot de Telegram respondiendo
- [ ] Frontend accesible públicamente
- [ ] Auto-deploy configurado

---

## 🎉 ¡Listo!

Tu aplicación EntrenaSmart está ahora desplegada en Railway y accesible desde:

- **Frontend**: `https://tu-frontend.up.railway.app`
- **API**: `https://tu-api.up.railway.app`
- **Bot**: Corriendo en background, accesible via Telegram

**¡Felicidades por tu deployment!** 🚀
