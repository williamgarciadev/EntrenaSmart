# EntrenaSmart - Railway Deployment

Esta carpeta contiene todos los archivos necesarios para desplegar EntrenaSmart en Railway.

## Archivos

- `Dockerfile.bot` - Dockerfile para el Bot de Telegram
- `Dockerfile.api` - Dockerfile para la API FastAPI
- `Dockerfile.frontend` - Dockerfile para el Frontend React/Vite
- `railway.toml` - Configuración de Railway (opcional)

## Despliegue Rápido

### Prerequisitos

1. Cuenta en [Railway](https://railway.app)
2. Railway CLI instalado: `npm i -g @railway/cli`
3. Repositorio conectado a Railway

### Paso 1: Crear servicios en Railway Dashboard

Ve a https://railway.app/dashboard y crea estos servicios:

1. **PostgreSQL**
   - Servicio → New → Database → PostgreSQL
   - Nombre: `Postgres`

2. **Bot**
   - Servicio → New → GitHub Repo → EntrenaSmart
   - Nombre: `EntrenaSmart`
   - Dockerfile Path: `deployment/railway/Dockerfile.bot`

3. **API**
   - Servicio → New → GitHub Repo → EntrenaSmart
   - Nombre: `API`
   - Dockerfile Path: `deployment/railway/Dockerfile.api`

4. **Frontend**
   - Servicio → New → GitHub Repo → EntrenaSmart
   - Nombre: `Frontend`
   - Dockerfile Path: `deployment/railway/Dockerfile.frontend`

### Paso 2: Configurar Variables de Entorno

#### Bot (EntrenaSmart)

```bash
TELEGRAM_BOT_TOKEN=tu_bot_token
TRAINER_TELEGRAM_ID=tu_id
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=tu_clave_secreta_minimo_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
DEBUG=False
ENVIRONMENT=production
TZ=America/Bogota
REMINDER_MINUTES_BEFORE=5
WEEKLY_REPORT_DAY=6
WEEKLY_REPORT_TIME=20:00
```

#### API

```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=tu_clave_secreta_minimo_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
TELEGRAM_BOT_TOKEN=tu_bot_token
TRAINER_TELEGRAM_ID=tu_id
ENVIRONMENT=production
DEBUG=False
TZ=America/Bogota
LOG_LEVEL=INFO
CORS_ORIGINS=https://tu-frontend-url.up.railway.app
```

#### Frontend

```bash
VITE_API_URL=https://tu-api-url.up.railway.app
```

**IMPORTANTE**: También agrega `VITE_API_URL` como **Build Argument** en Settings → Build.

### Paso 3: Generar Dominios Públicos

Para cada servicio (API y Frontend):
1. Settings → Networking
2. Click "Generate Domain"
3. Copia la URL generada

### Paso 4: Actualizar CORS

Una vez que tengas la URL del Frontend, actualiza `CORS_ORIGINS` en el servicio API:

```bash
railway variables -s API --set CORS_ORIGINS='https://tu-frontend-url.up.railway.app'
```

### Paso 5: Verificar Despliegue

```bash
# Ver logs del Bot
railway logs -s EntrenaSmart

# Ver logs de la API
railway logs -s API

# Ver logs del Frontend
railway logs -s Frontend
```

## URLs Finales

Después del despliegue tendrás:

- **Bot**: Sin URL pública (usa Telegram API)
- **API**: `https://api-production-xxxx.up.railway.app`
- **API Docs**: `https://api-production-xxxx.up.railway.app/docs`
- **Frontend**: `https://frontend-production-xxxx.up.railway.app`

## Troubleshooting

Ver documentación completa en `/RAILWAY_DEPLOY.md` en la raíz del proyecto.

## Costos Estimados

Railway cobra por uso:
- **Postgres**: ~$5/mes (siempre activo)
- **Bot**: ~$0-5/mes (siempre activo, bajo uso de CPU)
- **API**: ~$0-5/mes (activo bajo demanda)
- **Frontend**: ~$0-5/mes (activo bajo demanda)

**Total estimado**: $5-15/mes

## Comandos Útiles

```bash
# Ver status
railway status

# Ver variables
railway variables -s <servicio>

# Ver logs en tiempo real
railway logs -s <servicio> -f

# Ejecutar comando en servicio
railway run -s <servicio> <comando>

# Redesplegar servicio
railway up -s <servicio>
```
