# 🚀 Guía de Desarrollo Local - EntrenaSmart

Este documento proporciona instrucciones para ejecutar EntrenaSmart en **modo desarrollo local** sin Docker.

---

## ✅ Requisitos Previos

- **Python 3.11+** instalado
- **Node.js 20+** y npm instalados
- **Git** configurado

Verifica:
```bash
python --version  # >= 3.11
npm --version     # >= 20
node --version    # >= 20
```

---

## 🎯 Opción 1: Ejecución Rápida (Recomendado)

### Terminal 1: Ejecutar API Backend

```bash
cd backend
uvicorn api.main:app --reload --port 8000
```

Verás:
```
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete [Uvicorn]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**API disponible en:**
- `http://localhost:8000`
- Documentación: `http://localhost:8000/docs` ← ¡ABRE ESTO EN EL NAVEGADOR!

### Terminal 2: Ejecutar Frontend React

```bash
cd frontend
npm install  # Solo la primera vez
npm run dev
```

Verás:
```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  press h + enter to show help
```

**Frontend disponible en:**
- `http://localhost:5173`
- Página de configuración: `http://localhost:5173/config`

---

## 🧪 Testing - Opción 2: Probar API Automáticamente

### Terminal 3 (Después de iniciar API):

```bash
python test_api.py
```

Esto ejecutará 4 tests:
1. ✅ Health check
2. ✅ Obtener configuración semanal
3. ✅ Actualizar configuración
4. ✅ Verificar cambios

**Ejemplo de output:**
```
======================================================================
🧪 PRUEBAS DE API - EntrenaSmart
======================================================================

🧪 TEST 1: Health Check
   Status: 200
   Response: {'status': 'healthy'}

🧪 TEST 2: Obtener Configuración Semanal
   Status: 200
   Días configurados: 7
     - Lunes: Pierna
     - Martes: Funcional
...

✅ TODOS LOS TESTS PASARON
```

---

## 🌐 Testing Manual en el Navegador

### 1. API Swagger UI (Documentación Interactiva)

Abre: `http://localhost:8000/docs`

Aquí puedes:
- Ver todos los endpoints disponibles
- Hacer requests sin escribir código
- Ver schemas de request/response

**Prueba esto:**
```
GET /api/training-config (con Authorization: Bearer dev-token)
```

### 2. Frontend Web

Abre: `http://localhost:5173/config`

Aquí puedes:
- Ver calendario de 7 días
- Hacer clic en "Editar" en cualquier día
- Seleccionar tipo de entrenamiento
- Ingresar ubicación
- Guardar cambios
- Ver confirmación en tiempo real

---

## 📝 Flujo de Desarrollo Típico

```bash
# Terminal 1 - Backend
cd backend
uvicorn api.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev

# Terminal 3 - Testing (opcional)
python test_api.py

# Terminal 4 - Git (opcional)
git status
git add .
git commit -m "feat: descripción del cambio"
git push
```

---

## 🔧 Estructura de Carpetas para Desarrollo

```
EntrenaSmart/
├── backend/
│   ├── api/
│   │   ├── main.py          ← Edita aquí para endpoints
│   │   ├── routers/
│   │   │   └── training_config.py  ← Edita aquí para lógica
│   │   └── schemas.py       ← Edita aquí para modelos
│   ├── src/                 ← Código del bot (no tocar)
│   └── main.py              ← Bot principal (no tocar)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── features/
│   │   │   │   └── ConfigWeekCalendar.tsx  ← Edita aquí para UI
│   │   │   └── ui/
│   │   │       └── Button.tsx
│   │   ├── hooks/
│   │   │   └── useTrainingConfig.ts  ← Edita aquí para queries
│   │   ├── pages/
│   │   │   └── ConfigPage.tsx
│   │   ├── lib/
│   │   │   └── api.ts  ← Edita aquí para cliente HTTP
│   │   └── App.tsx
│   └── vite.config.ts
│
└── test_api.py  ← Script de testing
```

---

## 🐛 Troubleshooting

### Error: "Connection refused" en el frontend

**Causa:** API no está ejecutándose

**Solución:**
```bash
# Terminal 1
cd backend
uvicorn api.main:app --reload --port 8000
```

### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Causa:** Dependencias no instaladas

**Solución:**
```bash
pip install -r requirements.txt
```

### Error: "npm: command not found"

**Causa:** Node.js no está instalado

**Solución:** Descargar desde https://nodejs.org/

### Error: "Port 8000 already in use"

**Causa:** Otra aplicación usa el puerto

**Solución:**
```bash
# Cambiar puerto
uvicorn api.main:app --reload --port 8001
```

### El frontend no se conecta a la API

**Verificar:**
1. API está en `http://localhost:8000/health` ✅
2. Frontend está en `http://localhost:5173` ✅
3. Browser Console no muestra errores CORS (debería haber 0)

---

## 📊 Variables de Entorno (Desarrollo)

**backend/.env** (ya debería existir):
```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
TRAINER_TELEGRAM_ID=tu_id_aqui
DATABASE_URL=sqlite:///./storage/entrenasmart.db
DEBUG=True
```

**frontend/.env** (ya debería existir):
```env
VITE_API_URL=http://localhost:8000
VITE_DEV_TOKEN=dev-token
```

---

## 🚀 Próximos Pasos

### Después de que todo funcione:

1. **FASE 3: Plantillas de Mensajes**
   ```bash
   # Nuevos archivos a crear
   backend/api/routers/templates.py
   frontend/src/pages/TemplatesPage.tsx
   ```

2. **Hacer cambios y probar en vivo:**
   - API recarga automáticamente (uvicorn --reload)
   - Frontend recarga automáticamente (Vite HMR)

3. **Commit y push:**
   ```bash
   git add .
   git commit -m "feat: descripción"
   git push origin main
   ```

---

## 🎓 Comandos Útiles

```bash
# Listar procesos en puertos
lsof -i :8000  # API
lsof -i :5173  # Frontend

# Matar proceso en puerto (si está atrapado)
kill -9 <PID>

# Ver logs en tiempo real
uvicorn api.main:app --reload --port 8000 --log-level=debug

# Validar tipos TypeScript
cd frontend && npx tsc --noEmit

# Formatear código (opcional)
black backend/  # Python
npx prettier --write frontend/src  # JavaScript/TypeScript
```

---

## ✅ Checklist antes de continuar

- [ ] API ejecutándose en `http://localhost:8000`
- [ ] Swagger UI visible en `http://localhost:8000/docs`
- [ ] Frontend ejecutándose en `http://localhost:5173`
- [ ] Página `/config` carga sin errores
- [ ] `python test_api.py` pasa todos los tests
- [ ] Puedo actualizar un día de entrenamiento desde la UI
- [ ] Los cambios se guardan (se ven en Swagger UI)

---

## 🎉 ¿Todo funcionando?

**Perfecto, estás listo para:**
- Continuar con FASE 3 (Plantillas)
- Hacer cambios iterativos
- Commitear al repositorio

¡Gracias por usar EntrenaSmart! 💪
