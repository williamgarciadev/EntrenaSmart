# 🔍 Guía de Debug - Sistema de Recordatorios de EntrenaSmart

## 📋 Flujo Esperado de Logs

Cuando programas un recordatorio, deberías ver esta secuencia de logs:

### 1️⃣ **Inicialización del Bot** (al iniciar main.py)

```
================================================== ===========
🚀 [POST_INIT] INICIALIZANDO SCHEDULER DE RECORDATORIOS
================================================== ===========
📦 [POST_INIT] Obteniendo sesión de BD...
✅ [POST_INIT] Sesión obtenida
📦 [POST_INIT] Creando SchedulerService...
✅ [POST_INIT] SchedulerService creado: <SchedulerService object>
📦 [POST_INIT] Inicializando scheduler...
🔧 [SCHEDULER] Inicializando SchedulerService...
🔧 [SCHEDULER] Intentando obtener event loop...
✅ [SCHEDULER] Event loop corriendo: <_WindowsSelectorEventLoop>
✅ [SCHEDULER] Job store configurado
🔧 [SCHEDULER] Creando BackgroundScheduler...
✅ [SCHEDULER] BackgroundScheduler creado
✅ [SCHEDULER] SchedulerService inicializado con timezone: America/Bogota
   - Bot: <telegram.ext._application.Application>
   - Event loop: <_WindowsSelectorEventLoop>
   - Event loop running: True
✅ [POST_INIT] Scheduler inicializado
📦 [POST_INIT] Iniciando scheduler...
✅ [SCHEDULER] Scheduler iniciado correctamente
📦 [POST_INIT] Iniciando scheduler...
✅ [POST_INIT] Scheduler almacenado
================================================== ===========
✅ [POST_INIT] BOT INICIALIZADO CORRECTAMENTE
================================================== ===========
```

**Lo más importante**:
- ✅ `Event loop running: True` - El event loop está activo
- ✅ `Event loop corriendo: <_WindowsSelectorEventLoop>` - Hay un loop disponible

---

### 2️⃣ **Programación de Recordatorio** (cuando dices /set)

```
📅 [REMINDER] Programando recordatorio:
   - training_id=13
   - student_chat_id=432391645
   - weekday=5
   - training_time=12:21
   - session_type=Sábado
🔑 [REMINDER] Job ID: reminder_training_13
🔄 [REMINDER] Cancelando job anterior si existe...
⏱️ [REMINDER] Calculando hora de recordatorio...
   - training_time=12:21
   - reminder_minutes_before=5
   - reminder_time=12:16
📆 [REMINDER] Día: 5 (sat)
📅 [REMINDER] Hora actual: 2025-11-15 12:14:58 America/Bogota
   - today_weekday=5
✅ [REMINDER] ¡Hoy es el día del entrenamiento!
⏰ [REMINDER] Hora recordatorio hoy: 12:16:00
✅ [REMINDER] Hora no ha pasado - agregando DateTrigger para hoy
✅ [REMINDER] Recordatorio programado para HOY: 12:16
📅 [REMINDER] Agregando CronTrigger semanal para sat
🔀 [REMINDER] Total triggers: 2
🔀 [REMINDER] Combinando triggers con OR
✅ [REMINDER] Trigger configurado: <OrTrigger...>
📌 [REMINDER] Agregando job al scheduler...
   - Function: ReminderTask.send_reminder_sync
   - Args: bot=<Application>, chat_id=432391645, session_type=Sábado, training_time=12:21
   - Event loop: <_WindowsSelectorEventLoop>
   - Event loop running: True
✅ [REMINDER] Job agregado exitosamente
✅ [REMINDER] Recordatorio programado completo: training_id=13, chat_id=432391645, dia=sat, hora_recordatorio=12:16
```

**Lo más importante**:
- ✅ `Event loop running: True` - El loop está disponible al agregar el job
- ✅ `Recordatorio programado para HOY: 12:16` - Se programó para hoy
- ✅ `Job agregado exitosamente` - No hubo error de serialización

---

### 3️⃣ **Ejecución del Recordatorio** (cuando llega la hora)

```
🔔 [SEND_REMINDER] ===== INICIANDO ENVÍO DE RECORDATORIO =====
🔔 [SEND_REMINDER] Parámetros recibidos:
   - bot: <telegram.ext._application.Application>
   - bot.bot: <telegram.Bot>
   - student_chat_id: 432391645
   - session_type: Sábado
   - training_time: 12:21
   - event_loop (parámetro): <_WindowsSelectorEventLoop>
   - event_loop running: True
📝 [SEND_REMINDER] Construyendo mensaje de recordatorio...
✅ [SEND_REMINDER] Mensaje construido: 450 caracteres
📄 [SEND_REMINDER] Preview: 🔔 *RECORDATORIO DE ENTRENAMIENTO* 🔔...
🔄 [SEND_REMINDER] Verificando event_loop...
✅ [SEND_REMINDER] event_loop ya disponible: <_WindowsSelectorEventLoop>
🔍 [SEND_REMINDER] Estado del event_loop:
   - event_loop: <_WindowsSelectorEventLoop>
   - is_running(): True
   - is_closed(): False
✅ [SEND_REMINDER] Event loop está corriendo - usando run_coroutine_threadsafe
📤 [SEND_REMINDER] Enviando mensaje con run_coroutine_threadsafe...
   - chat_id: 432391645
   - text_length: 450
   - parse_mode: HTML
✅ [SEND_REMINDER] Future creado: <Future pending>
⏳ [SEND_REMINDER] Esperando resultado (timeout=5s)...
✅ [SEND_REMINDER] Resultado obtenido: <Message object>
✅ [SEND_REMINDER] ===== RECORDATORIO ENVIADO EXITOSAMENTE =====
   - chat_id: 432391645
   - session_type: Sábado
   - training_time: 12:21
```

**Lo más importante**:
- ✅ `INICIANDO ENVÍO DE RECORDATORIO` - Se ejecutó en la hora correcta
- ✅ `event_loop running: True` - El loop estaba disponible
- ✅ `RECORDATORIO ENVIADO EXITOSAMENTE` - Se envió el mensaje

---

## 🐛 Problemas Comunes y Soluciones

### ❌ Problema 1: `Event loop running: False` en post_init

**Error esperado:**
```
🔧 [SCHEDULER] Event loop corriendo: False
✅ [SCHEDULER] Event loop obtenido (no corriendo): <_WindowsSelectorEventLoop>
```

**Causa**: El event loop no estaba corriendo en el momento de `initialize_scheduler()`

**Solución**: El código está diseñado para manejar esto. Cuando `send_reminder_sync` se ejecuta, intenta obtenerlo dinámicamente. Verifica que en **Paso 3** veas `event_loop running: True`.

---

### ❌ Problema 2: `Event loop: None` en reminder_task

**Error esperado:**
```
❌ [SEND_REMINDER] No se pudo obtener event_loop
❌ [SEND_REMINDER] ===== FALLO: NO HAY EVENT LOOP DISPONIBLE O NO ESTÁ CORRIENDO =====
```

**Causa**: El BackgroundScheduler se ejecuta en un thread separado sin acceso al event loop

**Solución**: Debe pasarse explícitamente como argumento. Verifica que en **Paso 2** veas `Event loop running: True` cuando se agrega el job.

---

### ❌ Problema 3: No aparecen logs de ejecución (Paso 3)

**Posibles causas**:
1. El recordatorio nunca se dispara (check los tiempos en Paso 2)
2. El scheduler no está corriendo
3. El bot no está recibiendo las tareas

**Verificación**:
- ✅ En **Paso 1**: ¿Aparece `✅ [SCHEDULER] Scheduler iniciado correctamente`?
- ✅ En **Paso 2**: ¿Aparece `✅ [REMINDER] Recordatorio programado completo`?
- 🕐 ¿Pasó la hora del recordatorio? (check `Recordatorio programado para HOY: XX:XX`)

---

### ❌ Problema 4: `Timeout esperando resultado (>5s)`

**Error esperado:**
```
❌ [SEND_REMINDER] Timeout esperando resultado (>5s): did not complete within 5 seconds
```

**Causa**: El mensaje tardó más de 5 segundos en enviarse (problema de red)

**Solución**: Aumentar timeout de 5s a 10s en `reminder_task.py` línea 125:
```python
result = future.result(timeout=10)  # Cambiar de 5 a 10
```

---

### ❌ Problema 5: `Error enviando con run_coroutine_threadsafe`

**Error esperado**:
```
❌ [SEND_REMINDER] Error enviando con run_coroutine_threadsafe: ...
```

**Causa**: Error específico al enviar el mensaje. Revisa el mensaje completo en los logs.

**Verificación**:
- ¿El bot tiene permiso para enviar mensajes al chat?
- ¿El chat_id es correcto?
- ¿El token de Telegram es válido?

---

## 📊 Cómo Leer los Logs

### Estructura de cada línea:

```
TIMESTAMP - LOGGER - LEVEL - [PREFIJO] MENSAJE
2025-11-15 12:15:00 - entrenasmart - INFO - ✅ [REMINDER] Recordatorio programado para HOY: 12:16
```

- **TIMESTAMP**: Hora exacta
- **LOGGER**: `entrenasmart` (nuestro logger)
- **LEVEL**: `INFO`, `DEBUG`, `ERROR`, etc.
- **[PREFIJO]**: Dónde ocurre (POST_INIT, SCHEDULER, REMINDER, SEND_REMINDER)
- **MENSAJE**: Qué está sucediendo

### Emojis y su significado:

| Emoji | Significado |
|-------|-------------|
| 🚀 | Inicio importante |
| ✅ | Éxito |
| ❌ | Error |
| ⚠️ | Advertencia |
| 📦 | Preparación/Setup |
| 🔧 | Configuración |
| 📅 | Información sobre recordatorio |
| 🔔 | Envío de recordatorio |
| ⏰ | Hora/Tiempo |
| 🔄 | Proceso en progreso |
| 📝 | Creación de contenido |
| 📤 | Envío |
| ⏳ | Espera |
| 🔍 | Verificación/Inspection |

---

## 🧪 Test Rápido

Ejecuta el test de debug:
```bash
python test_reminder_corrected.py
```

Deberías ver en los logs:
```
✅ [SEND_REMINDER] ===== RECORDATORIO ENVIADO EXITOSAMENTE =====
```

---

## 📝 Resumen: Qué Buscar

✅ **Bot inicia correctamente**:
- Línea: `Event loop running: True` en POST_INIT

✅ **Recordatorio se programa**:
- Línea: `Recordatorio programado para HOY` (si es hoy)
- Línea: `Job agregado exitosamente`

✅ **Recordatorio se envía**:
- Línea: `RECORDATORIO ENVIADO EXITOSAMENTE`

Si no ves estas tres líneas, ahí está el problema. Los logs te mostrarán exactamente dónde falla.
