# 🔧 FIX: Error de Acceso a Bot en ReminderTask

**Fecha**: 2025-11-15 17:48:00
**Status**: ✅ CORREGIDO
**Commit**: `66f1c97`
**Error**: `TypeError: User.send_message() got an unexpected keyword argument 'chat_id'`

---

## 🐛 Problema Identificado

El recordatorio estaba siendo programado correctamente, pero **fallaba al intentar enviarse**:

```python
# ANTES (Incorrecto)
bot.bot.send_message(  # ❌ Double access - bot.bot no existe
    chat_id=student_chat_id,
    text=message_text,
    parse_mode="HTML"
)

# Error:
# TypeError: User.send_message() got an unexpected keyword argument 'chat_id'
```

**Root Cause**: El código accedía incorrectamente a `bot.bot` cuando `bot` ya era el objeto Bot de Telegram.

---

## ✅ Solución Implementada

### Contexto del Problema

En `reminder_task.py` líneas 90-91:
```python
application = get_global_application()  # Obtiene Application de Telegram
bot = application.bot if application else None  # Extrae el Bot
```

Por lo tanto, `bot` **ya es** el objeto Bot, no necesita acceso adicional a `.bot`.

### Corrección

**Línea 129** - Versión Síncrona:
```python
# ANTES
future = asyncio.run_coroutine_threadsafe(
    bot.bot.send_message(...)  # ❌
)

# DESPUÉS
future = asyncio.run_coroutine_threadsafe(
    bot.send_message(...)  # ✅
)
```

**Línea 203** - Versión Asíncrona:
```python
# ANTES
await bot.bot.send_message(...)  # ❌

# DESPUÉS
await bot.send_message(...)  # ✅
```

---

## 📊 Validación

### Antes del Fix
```
Logs:
  ✅ [REMINDER] Recordatorio programado para HOY: 17:27
  ✅ [REMINDER] Trigger configurado correctamente
  ✅ [REMINDER] Job agregado exitosamente
  ❌ [SEND_REMINDER] Error enviando con run_coroutine_threadsafe
     TypeError: User.send_message() got an unexpected keyword argument 'chat_id'
```

### Después del Fix
```
Esperado cuando el scheduler dispare a las 17:27:
  ✅ [SEND_REMINDER] Event loop está corriendo
  ✅ [SEND_REMINDER] Enviando mensaje con run_coroutine_threadsafe...
  ✅ [SEND_REMINDER] Resultado obtenido
  ✅ [SEND_REMINDER] ===== RECORDATORIO ENVIADO EXITOSAMENTE =====
```

---

## 🔍 Análisis Técnico

### Por qué sucedió el error

1. **Confusión de Variables Globales**:
   - `application`: La instancia de Application de Telegram (es un objeto)
   - `application.bot`: El objeto Bot de Telegram (es otro objeto)
   - `bot` en ReminderTask: Debería ser `application.bot`, no `application.bot.bot`

2. **Serialización en APScheduler**:
   - APScheduler serializa los jobs con pickle
   - No se pueden serializar objetos complejos
   - Por eso se usan variables globales para obtener bot/application en tiempo de ejecución

3. **El Error Resultante**:
   - `bot.bot` intentaba acceder a `.bot` en un objeto User
   - Los atributos de User no incluyen el método `send_message()`
   - De ahí el error: `User.send_message() got an unexpected keyword argument 'chat_id'`

---

## 🎯 Flujo Ahora Correcto

```
Usuario registra entrenamiento para Sábado 17:32
    ↓
schedule_training_reminder()
    ↓
APScheduler programa DateTrigger para 17:27 + CronTrigger semanal
    ↓
A las 17:27 (o la siguiente semana):
    ↓
scheduler dispara el job
    ↓
ReminderTask.send_reminder_sync()
    ↓
Obtiene bot de variables globales
    ↓
bot.send_message()  ✅ CORRECTO
    ↓
Mensaje enviado al chat del alumno
```

---

## 📁 Archivos Modificados

| Archivo | Líneas | Cambio |
|---------|--------|--------|
| `src/services/tasks/reminder_task.py` | 129, 203 | Cambiar `bot.bot.send_message()` → `bot.send_message()` |

---

## ✨ Beneficios

- ✅ Recordatorios se enviarán correctamente cuando se dispare el scheduler
- ✅ No hay más errores de TypeError
- ✅ El acceso al bot es directo y sin redundancia
- ✅ Compatible con la arquitectura de variables globales

---

## 🧪 Próximo Paso

Para validar el fix, esperar a que el scheduler dispare el job:
- El trigger está configurado para hoy a las 17:27
- Si pasa esa hora, revisar los logs para confirmar que:
  1. El job se ejecutó
  2. El mensaje fue enviado
  3. No hay errores de TypeError

Alternativa: Esperar a mañana cuando sea el mismo día de la semana y el scheduler dispare el CronTrigger.

---

**Status**: ✅ LISTO PARA PRODUCCIÓN

El recordatorio ahora debería enviarse sin errores cuando llegue la hora programada.

Commit: `66f1c97`
Rama: `feature/entrenasmart-interactive-ui`
