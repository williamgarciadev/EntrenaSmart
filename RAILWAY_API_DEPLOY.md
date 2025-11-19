# Despliegue de API en Railway - Guía Rápida

## Opción 1: Desde Railway Dashboard (Recomendado)

### Paso 1: Crear el servicio API

1. Ve a Railway Dashboard: https://railway.app/dashboard
2. Abre tu proyecto "sparkling-amazement"
3. Click en **"+ New"** → **"GitHub Repo"**
4. Selecciona tu repositorio EntrenaSmart
5. Nombra el servicio: **"API"**

### Paso 2: Configurar el Build

1. En el servicio API, ve a **Settings** → **Build**
2. Configura:
   - **Dockerfile Path**: `Dockerfile.api`
   - **Build Command**: (dejar vacío)

### Paso 3: Configurar Variables de Entorno

En **Variables**, agrega las siguientes:

```bash
# Base de datos
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Seguridad
SECRET_KEY=genera_una_clave_secreta_muy_segura_minimo_32_caracteres_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Telegram (para verificar que requests vienen del bot autorizado)
TELEGRAM_BOT_TOKEN=8537850989:AAHQGHnpTe_odVCl0qN5QsQ-lX-T6jbROmE
TRAINER_TELEGRAM_ID=432391645

# Ambiente
ENVIRONMENT=production
DEBUG=False
TZ=America/Bogota
LOG_LEVEL=INFO

# CORS - Permitir frontend (actualizar después con URL real)
CORS_ORIGINS=*
```

### Paso 4: Generar Dominio Público

1. En el servicio API, ve a **Settings** → **Networking**
2. Click en **"Generate Domain"**
3. Copia la URL generada (será algo como: `https://api-production-xxxx.up.railway.app`)

### Paso 5: Desplegar

1. Click en **"Deploy"** o espera el auto-deploy
2. Monitorea los logs en tiempo real
3. Verifica que muestre:
   ```
   ✓ Base de datos inicializada (PostgreSQL)
   ✓ API iniciada en puerto $PORT
   ```

### Paso 6: Verificar API funcionando

Abre en el navegador:
```
https://tu-api-url.up.railway.app/docs
```

Deberías ver la documentación Swagger de FastAPI.

---

## Opción 2: Desde Railway CLI

Lamentablemente, Railway CLI no tiene comando directo para crear servicios nuevos.
Debes usar Railway Dashboard para crear el servicio, y luego usar CLI para:

```bash
# Ver logs de la API
railway logs -s API

# Ver variables
railway variables -s API

# Ejecutar comandos
railway run -s API python --version
```

---

## Variables de Entorno Explicadas

| Variable | Descripción | Valor |
|----------|-------------|-------|
| `DATABASE_URL` | Conexión a PostgreSQL | `${{Postgres.DATABASE_URL}}` |
| `SECRET_KEY` | Clave para JWT tokens | Mínimo 32 caracteres aleatorios |
| `ALGORITHM` | Algoritmo de encriptación | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tiempo de expiración tokens | `43200` (30 días) |
| `TELEGRAM_BOT_TOKEN` | Token del bot | Tu token de @BotFather |
| `TRAINER_TELEGRAM_ID` | ID del entrenador | Tu ID numérico |
| `ENVIRONMENT` | Entorno | `production` |
| `DEBUG` | Modo debug | `False` |
| `TZ` | Zona horaria | `America/Bogota` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `CORS_ORIGINS` | Orígenes permitidos | `*` (o URL específica del frontend) |

---

## Troubleshooting

### Error: "Port already in use"
- Railway asigna el puerto automáticamente vía variable `$PORT`
- Dockerfile.api ya está configurado para usar `${PORT:-8000}`

### Error: "Module not found"
- Verifica que Dockerfile.api copie correctamente `backend/`
- Verifica que `PYTHONPATH=/app/backend` esté configurado

### Error: "Database connection failed"
- Verifica que `DATABASE_URL=${{Postgres.DATABASE_URL}}` esté sin comillas
- Verifica que servicios API y Postgres estén en el mismo proyecto

### API no responde en /health
- Verifica logs: `railway logs -s API`
- Verifica que el puerto sea el correcto (Railway usa `$PORT`)
- Health check está en: `/health`

---

## Siguiente Paso: Desplegar Frontend

Una vez que la API esté funcionando y tengas su URL pública:

1. Copia la URL de la API (ej: `https://api-production-xxxx.up.railway.app`)
2. Úsala para desplegar el Frontend con `VITE_API_URL`

Ver: `RAILWAY_FRONTEND_DEPLOY.md` (próximo paso)
