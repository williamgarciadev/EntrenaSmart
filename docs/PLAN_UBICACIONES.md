# 📋 PLAN: Vincular Ubicaciones con Entrenamientos

**Objetivo:** Que cada sesión de entrenamiento muestre correctamente la ubicación (ej: "2do piso") y la zona (ej: "zona pierna").

**Estado:** Pendiente de aprobación

---

## 🎯 Problema Actual

Cuando Geovanny hace `/mis_sesiones`, ve:
```
📅 *Tus Entrenamientos:*
*Lunes:* • 05:00
*Miércoles:* • 17:30
```

Debería ver:
```
📅 *Tus Entrenamientos:*
*Lunes (Pierna):*
  • 05:00 en 2do Piso
*Miércoles (Funcional):*
  • 17:30 en 4to Piso
```

---

## 🔍 Raíz del Problema

1. **Training** NO almacena la ubicación
2. **Training** NO tiene referencia a **TrainingDayConfig**
3. El handler `/set` no obtiene la ubicación al crear entrenamientos
4. Los métodos que muestran entrenamientos no consultan la ubicación

---

## 📐 Solución Propuesta

### **Opción A: Copiar ubicación a Training (Más Simple)**

Agregar 2 campos a `Training`:
- `location: str` (ej: "2do Piso")
- `training_day_config_id: int` (referencia FK a TrainingDayConfig)

**Ventajas:**
- Más rápido (sin JOIN)
- No hay duplicación de consultas
- Ubicación guardada con la sesión

**Desventajas:**
- Pequeña duplicación de datos
- Si ubicación cambia en config, las sesiones antiguas quedan con ubicación vieja

### **Opción B: Siempre consultar TrainingDayConfig (Más Dinámmica)**

Cuando se necesita mostrar una sesión, JOINear con TrainingDayConfig por `weekday`.

**Ventajas:**
- Cambios de ubicación se reflejan automáticamente
- Una sola fuente de verdad

**Desventajas:**
- Más consultas a BD
- Si se elimina config de un día, las sesiones pierden ubicación
- Más lento

---

## ✅ **RECOMENDACIÓN: Opción A**

Usar **Opción A** porque:
1. Es más simple
2. Mantiene histórico (si ubicación cambió, queda registrado)
3. No hay riesgo de que sesiones queden sin ubicación
4. Mejor desempeño

---

## 📝 Tareas Específicas

### **Fase 1: Modificar Modelo**

#### Tarea 1.1: Actualizar modelo `Training`
**Archivo:** `src/models/training.py`

```python
# Agregar campos:
location: Optional[str] = None           # Ubicación (ej: "2do Piso")
training_day_config_id: Optional[int] = None  # FK a TrainingDayConfig
session_type: str = ""                   # Tipo (ej: "Pierna")

# Agregar relación:
training_day_config = relationship("TrainingDayConfig", foreign_keys=[training_day_config_id])
```

**Cambios:**
- 3 nuevos campos
- 1 nueva relación
- Sin cambios en métodos existentes

---

### **Fase 2: Actualizar Base de Datos**

#### Tarea 2.1: Crear migración
**Archivo:** `migrations/versions/[timestamp]_add_location_to_training.py`

```sql
-- Agregar columnas a tabla trainings
ALTER TABLE trainings ADD COLUMN location VARCHAR(255) NULL;
ALTER TABLE trainings ADD COLUMN training_day_config_id INTEGER NULL;
ALTER TABLE trainings ADD FOREIGN KEY (training_day_config_id)
    REFERENCES training_day_configs(id);
```

**Cambios:**
- 1 archivo nuevo
- 2 columnas nuevas
- 1 restricción FK

---

### **Fase 3: Actualizar Servicios**

#### Tarea 3.1: Actualizar `TrainingService`
**Archivo:** `src/services/training_service.py`

Modificar método `add_training()`:
```python
def add_training(self, student_id, weekday, weekday_name, time_str,
                 session_type, location=None, training_day_config_id=None):
    # Si no se pasa location, intentar obtenerla de config
    if location is None and training_day_config_id is None:
        config = ConfigTrainingService.get_day_config(weekday)
        if config:
            location = config.location
            session_type = config.session_type
            training_day_config_id = config.id

    training = Training(...)
    training.location = location
    training.training_day_config_id = training_day_config_id
    # ... resto del código
```

Agregar/actualizar métodos:
- `get_training_with_location(training_id)` - Retorna Training con ubicación
- `get_schedule_with_locations(student_id)` - Retorna agenda completa con ubicaciones

**Cambios:**
- Actualizar `add_training()` (línea ~145)
- 1 método nuevo
- 1 método actualizado

---

#### Tarea 3.2: Integrar `ConfigTrainingService`
**Archivo:** `src/services/training_service.py`

En el constructor:
```python
def __init__(self, db_session):
    self.db = db_session
    self.config_service = ConfigTrainingService(db_session)
```

**Cambios:**
- 1 línea (inyectar servicio)

---

### **Fase 4: Actualizar Handlers**

#### Tarea 4.1: Actualizar `training_handler.py`
**Archivo:** `src/handlers/training_handler.py`

En función `build_training_conv_handler()`, línea ~375:

De:
```python
training_service.add_training(
    student_id=training['student_id'],
    weekday=training['day_number'],
    weekday_name=training['day_name'],
    time_str=training['time']
)
```

A:
```python
config = config_service.get_day_config(training['day_number'])
training_service.add_training(
    student_id=training['student_id'],
    weekday=training['day_number'],
    weekday_name=training['day_name'],
    time_str=training['time'],
    session_type=config.session_type if config else "",
    location=config.location if config else None,
    training_day_config_id=config.id if config else None
)
```

**Cambios:**
- 1 bloque (1-5 líneas)
- Obtener config del día antes de crear training

---

#### Tarea 4.2: Actualizar `edit_training_handler.py`
**Archivo:** `src/handlers/edit_training_handler.py`

Cuando se actualiza un training, también actualizar ubicación:
```python
# Al actualizar, obtener config actualizada
config = config_service.get_day_config(new_weekday)
training.location = config.location if config else training.location
training.training_day_config_id = config.id if config else None
```

**Cambios:**
- 1 bloque (2-3 líneas) en método de actualización

---

### **Fase 5: Actualizar Visualización**

#### Tarea 5.1: Actualizar `student_handlers.py` - `/mis_sesiones`
**Archivo:** `src/handlers/student_handlers.py`

De:
```python
schedule = training_service.get_training_schedule_summary(student.id)
message = Messages.training_schedule(schedule)
```

A:
```python
trainings = training_service.get_all_trainings(student.id)
message = Messages.training_schedule_with_locations(trainings)
```

**Cambios:**
- 2 líneas (usar método diferente)

---

#### Tarea 5.2: Crear nuevo método en `messages.py`
**Archivo:** `src/utils/messages.py`

Agregar:
```python
@staticmethod
def training_schedule_with_locations(trainings: List[Training]) -> str:
    """
    Formatea entrenamientos con ubicación
    Agrupa por día
    """
    grouped = {}
    for training in trainings:
        day = training.weekday_name
        if day not in grouped:
            grouped[day] = []

        time_str = training.time_str
        location = training.location or "Sin ubicación"
        session_type = training.session_type or "General"

        grouped[day].append(f"  • {time_str} en {location} ({session_type})")

    message = "📅 *Tus Entrenamientos:*\n\n"
    for day in grouped:
        message += f"*{day}:*\n" + "\n".join(grouped[day]) + "\n\n"

    return message
```

**Cambios:**
- 1 método nuevo
- ~20 líneas

---

#### Tarea 5.3: Actualizar recordatorios
**Archivo:** `src/utils/messages.py`

Método `training_reminder()` ya acepta `location`:
```python
def training_reminder(session_type, training_time, location="Zona de Entrenamiento"):
```

Ahora hay que pasarla desde `scheduler_service.py`.

**Cambios en `src/services/scheduler_service.py`:**
- Obtener `training.location` al enviar recordatorio
- Pasar a `training_reminder()`

---

### **Fase 6: Validación**

#### Tarea 6.1: Pruebas manuales
1. Configurar día (ej: Lunes → Pierna, 2do Piso)
2. Asignar sesión a alumno (Lunes 05:00)
3. Ver `/mis_sesiones` → Debe mostrar ubicación ✓
4. Editar sesión → Ubicación se actualiza ✓
5. Recordatorio automático → Muestra ubicación ✓

---

## 📊 Resumen de Cambios

| Archivo | Cambios | Líneas |
|---------|---------|--------|
| `src/models/training.py` | Agregar 3 campos | +10 |
| `src/services/training_service.py` | Actualizar método + 1 nuevo | +15 |
| `src/handlers/training_handler.py` | Actualizar 1 bloque | +3 |
| `src/handlers/edit_training_handler.py` | Actualizar 1 bloque | +3 |
| `src/handlers/student_handlers.py` | 2 líneas | +2 |
| `src/utils/messages.py` | 1 método nuevo | +20 |
| `src/services/scheduler_service.py` | Pasar location | +2 |
| `migrations/versions/[...]_add_location.py` | Migración SQL | +10 |
| **TOTAL** | | **~65 líneas** |

---

## ⚙️ Flujo de Ejecución

```
1. Entrenador ejecuta /set ubicacion
   ↓
2. Sistema pide configurar ubicación global (TrainingDayConfig)
   ↓
3. Entrenador asigna sesión a alumno
   ↓
4. Sistema obtiene configuración del día
   ↓
5. Copia location + session_type + training_day_config_id a Training
   ↓
6. Alumno ve /mis_sesiones con ubicación
   ↓
7. Recordatorio automático incluye ubicación
```

---

## ✨ Resultado Esperado

**Comando:**
```
/mis_sesiones
```

**Respuesta actual:**
```
📅 *Tus Entrenamientos:*

*Lunes:*
  • 05:00

*Miércoles:*
  • 17:30
```

**Respuesta después:**
```
📅 *Tus Entrenamientos:*

*Lunes:*
  • 05:00 en 2do Piso (Pierna)

*Miércoles:*
  • 17:30 en 4to Piso (Funcional)
```

---

## ❓ Preguntas de Confirmación

1. ¿Estás de acuerdo con la **Opción A** (copiar ubicación)?
2. ¿Las ubicaciones configuradas son como "2do Piso", "4to Piso", etc.?
3. ¿Necesitas que se ejecute alguna migración de BD?
4. ¿El flujo de `training_handler.py` está correcto?

---

## 📍 Siguiente Paso

Una vez apruebes este plan, iré marcando tareas como completadas y te explicaré cada cambio.
