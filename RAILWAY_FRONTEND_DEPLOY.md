# Despliegue de Frontend en Railway - Guía Rápida

## Prerequisito

**IMPORTANTE**: Antes de desplegar el Frontend, necesitas tener la URL de la API.

Si aún no has desplegado la API, sigue primero: `RAILWAY_API_DEPLOY.md`

---

## Paso 1: Crear el servicio Frontend

1. Ve a Railway Dashboard: https://railway.app/dashboard
2. Abre tu proyecto "sparkling-amazement"
3. Click en **"+ New"** → **"GitHub Repo"**
4. Selecciona tu repositorio EntrenaSmart
5. Nombra el servicio: **"Frontend"**

---

## Paso 2: Configurar el Build

1. En el servicio Frontend, ve a **Settings** → **Build**
2. Configura:
   - **Dockerfile Path**: `frontend/Dockerfile`
   - **Build Command**: (dejar vacío)

---

## Paso 3: Configurar Variables de Entorno

En **Variables**, agrega:

```bash
# URL de la API (CRÍTICO - reemplaza con tu URL real)
VITE_API_URL=https://api-production-xxxx.up.railway.app

# Puerto (Railway lo asigna automáticamente, pero Nginx usa 80)
PORT=80
```

**⚠️ IMPORTANTE**:
- Reemplaza `https://api-production-xxxx.up.railway.app` con la URL real de tu API
- NO agregues `/` al final de la URL
- NO uses `http`, debe ser `https`

---

## Paso 4: Configurar Build Args

Railway necesita pasar `VITE_API_URL` como build argument para que Vite lo incluya en el build.

### Opción A: En Railway Dashboard

1. Ve a **Settings** → **Build**
2. En **Build Arguments**, agrega:
   ```
   VITE_API_URL=https://api-production-xxxx.up.railway.app
   ```

### Opción B: railway.toml

Crea o actualiza `railway.toml` en la raíz del proyecto:

```toml
[build]
builder = "dockerfile"
dockerfilePath = "frontend/Dockerfile"

[build.buildArgs]
VITE_API_URL = "https://api-production-xxxx.up.railway.app"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 10
```

---

## Paso 5: Generar Dominio Público

1. En el servicio Frontend, ve a **Settings** → **Networking**
2. Click en **"Generate Domain"**
3. Copia la URL generada (será algo como: `https://frontend-production-xxxx.up.railway.app`)

---

## Paso 6: Actualizar CORS en la API

Una vez que tengas la URL del Frontend, actualiza las variables de la API:

1. Ve al servicio **API**
2. En **Variables**, actualiza:
   ```bash
   CORS_ORIGINS=https://frontend-production-xxxx.up.railway.app
   ```
3. Railway redesplegará automáticamente la API

---

## Paso 7: Desplegar

1. Click en **"Deploy"** o espera el auto-deploy
2. Monitorea los logs en tiempo real
3. El build puede tardar 2-3 minutos (compilando React + Vite)

---

## Paso 8: Verificar Frontend funcionando

Abre en el navegador:
```
https://tu-frontend-url.up.railway.app
```

Deberías ver:
- ✅ Página de login de EntrenaSmart
- ✅ Sin errores en la consola del navegador (F12)
- ✅ Puede hacer login (probar con credenciales)

---

## Verificar Conexión API ↔ Frontend

### En la consola del navegador (F12):

1. Abre la pestaña **Network**
2. Intenta hacer login
3. Verifica que los requests vayan a: `https://api-production-xxxx.up.railway.app/api/...`
4. Deberían devolver código 200 (OK) o 401 (Unauthorized - credenciales incorrectas)

### Errores comunes:

**CORS Error**:
```
Access to fetch at 'https://api...' from origin 'https://frontend...' has been blocked by CORS policy
```
**Solución**: Actualiza `CORS_ORIGINS` en la API con la URL del Frontend

**API URL incorrecta**:
```
Failed to fetch
```
**Solución**: Verifica que `VITE_API_URL` esté correcto en las variables del Frontend

---

## Estructura Final en Railway

Deberías tener 3 servicios:

```
📦 sparkling-amazement (Proyecto)
├── 🤖 EntrenaSmart (Bot) - Sin URL pública
├── 🗄️  Postgres (Database) - Sin URL pública
├── 🚀 API (FastAPI) - https://api-production-xxxx.up.railway.app
└── 🌐 Frontend (React) - https://frontend-production-xxxx.up.railway.app
```

---

## Troubleshooting

### Error: "VITE_API_URL is undefined"

La variable no se pasó correctamente durante el build.

**Solución**:
1. Asegúrate de configurar `VITE_API_URL` como **Build Argument** (no solo variable de entorno)
2. Redeploy del servicio

### Error: Build falla en "npm ci"

**Síntoma**:
```
npm ERR! The package-lock.json lockfile is corrupt
```

**Solución**:
1. Asegúrate de que `frontend/package-lock.json` esté en el repositorio
2. Verifica que `frontend/Dockerfile` use `npm ci` (no `npm install`)

### Error: Nginx no inicia

**Síntoma**:
```
nginx: [emerg] bind() to 0.0.0.0:80 failed
```

**Solución**:
- Railway asigna un puerto dinámico, pero Nginx usa 80 internamente
- El Dockerfile ya está configurado correctamente para exponer puerto 80
- Railway hace el mapeo automáticamente

### Página en blanco (White Screen of Death)

**Solución**:
1. Abre la consola del navegador (F12)
2. Busca errores en la pestaña **Console**
3. Verifica que `VITE_API_URL` esté correcto
4. Verifica que la API esté respondiendo: `https://api-url/health`

---

## URLs Finales

Guarda estas URLs para uso futuro:

```bash
# Bot de Telegram (sin URL pública - usa Telegram API)
Bot: Conectado vía Telegram polling

# PostgreSQL (sin URL pública - solo interno)
Database: postgres.railway.internal:5432

# API FastAPI
API: https://api-production-xxxx.up.railway.app
API Docs: https://api-production-xxxx.up.railway.app/docs
API Health: https://api-production-xxxx.up.railway.app/health

# Frontend React
Frontend: https://frontend-production-xxxx.up.railway.app
Frontend Health: https://frontend-production-xxxx.up.railway.app/health
```

---

## Siguiente Paso: Configurar Dominio Personalizado (Opcional)

Si quieres usar un dominio propio (ej: `entrenasmart.com`):

1. Ve a **Settings** → **Networking** en cada servicio
2. Click en **"Custom Domain"**
3. Configura los registros DNS según las instrucciones de Railway

**Recomendación**:
- API: `api.tudominio.com`
- Frontend: `tudominio.com` o `app.tudominio.com`
