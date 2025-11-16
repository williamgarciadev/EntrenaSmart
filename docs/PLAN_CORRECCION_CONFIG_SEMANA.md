# Plan Exhaustivo de Corrección: /config_semana

**Fecha**: 2025-11-15
**Status**: ANÁLISIS → IMPLEMENTACIÓN
**Prioridad**: CRÍTICA
**Enfoque**: Soluciones de fondo, no parches temporales

---

## 📊 RESUMEN EJECUTIVO

El flujo `/config_semana` presenta **7 problemas arquitectónicos** que generan errores persistentes:

| # | Problema | Severidad | Causa Raíz | Impacto |
|---|----------|-----------|-----------|--------|
| 1 | Inconsistencia estado conversacional | MEDIA | Uso de dict plano sin validación | Typos, type-safety baja |
| 2 | Gestión deficiente de conexiones BD | ALTA | No uso de context managers | Fugas, recursos sin liberar |
| 3 | Limpieza parcial de estado | MEDIA | Clear manual incompleto | Estado inconsistente entre ciclos |
| 4 | Validación ubicación incompleta | BAJA | Sin límites upper/sanitización | Datos inválidos, potencial SQL injection |
| 5 | Race condition en duplicados | MEDIA | Búsqueda+inserción no atómica | UNIQUE constraint errors |
| 6 | Transacciones inconsistentes | MEDIA | Commits explícitos dispersos | Confusion responsabilidad transaccional |
| 7 | Excepciones genéricas | MEDIA | Captura de todo como Exception | Experiencia usuario pobre, difícil debuggear |

---

## 🎯 SOLUCIONES ARQUITECTÓNICAS

### SOLUCIÓN 1: Estandarizar Gestión de Estado

**Actual** (Problemático):
```python
context.user_data["weekday_name"] = day_text       # String key
context.user_data["weekday"] = DAYS_SPANISH[day_text]
context.user_data["session_type"] = session_type
context.user_data["location"] = location
```

**Problema**: Sin type-safety, propenso a typos

**SOLUCIÓN**: Usar dataclass + helper functions (patrón existente en training_handler.py)

```python
@dataclass
class ConfigTrainingState:
    weekday: int
    weekday_name: str
    session_type: str
    location: str

# En handler:
state = ConfigTrainingState(weekday=0, weekday_name="Lunes", ...)
save_state_to_context_simple(context, state)  # Automático

# En confirm:
state = load_state_from_context_simple(context, ConfigTrainingState)
# Si hay typo en atributo → error de compilación inmediato
```

**Impacto**:
- Type-safety en todos los atributos
- IDE autocomplete funciona
- Refactorización segura con rename
- Limpieza automática con clear_state_simple()

**Archivos a modificar**:
- `config_training_handler.py` (usar dataclass + helpers)
- `training_state.py` (agregar ConfigTrainingState)

---

### SOLUCIÓN 2: Context Manager para Conexiones BD

**Actual** (Problemático):
```python
db = None
try:
    db = get_db()
    service = ConfigTrainingService(db)
    # ... uso ...
finally:
    if db:
        db.close()
```

**Problemas**:
- Variable `db = None` innecesaria
- Pattern verboso y propenso a olvidos
- No garantiza commit en caso de error

**SOLUCIÓN**: Crear context manager en `models/base.py`

```python
@contextmanager
def get_db_context():
    """Context manager para DB sessions con commit automático."""
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Auto-commit si no hay excepción
    except Exception:
        db.rollback()  # Rollback automático en error
        raise
    finally:
        db.close()

# Uso en handler:
async def config_training_confirm(update, context):
    with get_db_context() as db:
        service = ConfigTrainingService(db)
        service.configure_day(weekday, session_type, location)
        # Auto-commit al salir del bloque
```

**Impacto**:
- ✅ Commit/rollback automático
- ✅ Cierre garantizado
- ✅ 2 líneas en vez de 9
- ✅ Pattern reutilizable en todos handlers

**Archivos a modificar**:
- `src/models/base.py` (agregar context manager)
- `config_training_handler.py` (usar context manager)

---

### SOLUCIÓN 3: Limpieza Automática con State Machine

**Actual** (Problemático):
```python
# En confirm()
for key in ["weekday", "weekday_name", "session_type", "location"]:
    context.user_data.pop(key, None)  # Manual, incompleto

return CONFIRM_CONTINUE  # Vuelve al menú
```

**Problema**:
- Si exception entre clear y menu, estado queda sucio
- Manual y propenso a olvidos
- No hay garantía de limpieza completa

**SOLUCIÓN**: Hacer clear automático en transición de estado

```python
class TrainingStateManager:
    @staticmethod
    def save_config_state(context, weekday, weekday_name, session_type, location):
        """Guarda estado de forma atómica."""
        state = ConfigTrainingState(
            weekday=weekday,
            weekday_name=weekday_name,
            session_type=session_type,
            location=location
        )
        save_state_to_context_simple(context, state)

    @staticmethod
    def clear_config_state(context):
        """Limpia estado de forma atómica."""
        clear_state_simple(context)

    @staticmethod
    def get_config_state(context) -> ConfigTrainingState:
        """Obtiene estado con validación."""
        try:
            return load_state_from_context_simple(context, ConfigTrainingState)
        except KeyError:
            raise StateNotFoundError("Estado de configuración no encontrado")

# En handler:
async def config_training_confirm(update, context):
    state = TrainingStateManager.get_config_state(context)

    with get_db_context() as db:
        service = ConfigTrainingService(db)
        service.configure_day(state.weekday, state.session_type, state.location)

    # Clear automático al cambiar de estado
    TrainingStateManager.clear_config_state(context)

    return CONFIRM_CONTINUE  # Pregunta "¿Otro día?"
```

**Impacto**:
- ✅ Clear garantizado antes de siguiente ciclo
- ✅ Validación de estado automática
- ✅ Responsabilidades claras
- ✅ Reutilizable en otros handlers

**Archivos a modificar**:
- `src/handlers/training_state_manager.py` (crear)
- `config_training_handler.py` (usar manager)

---

### SOLUCIÓN 4: Validación Completa de Ubicación

**Actual** (Problemático):
```python
if not location or len(location) < 3:
    return SELECT_LOCATION
```

**Problemas**:
- Sin límite superior (location > 100 chars → BD error)
- Sin sanitización (potencial SQL injection)
- Sin validación de caracteres

**SOLUCIÓN**: Crear validador reutilizable

```python
# src/utils/validators.py
class LocationValidator:
    MIN_LENGTH = 3
    MAX_LENGTH = 100
    ALLOWED_CHARS_PATTERN = r'^[a-zA-Z0-9\s\-./()áéíóúñ]+$'  # Ej español

    @classmethod
    def validate(cls, location: str) -> None:
        """Valida ubicación, lanza LocationValidationError si inválida."""
        if not location or not isinstance(location, str):
            raise LocationValidationError("Ubicación no puede estar vacía")

        location = location.strip()

        if len(location) < cls.MIN_LENGTH:
            raise LocationValidationError(
                f"Ubicación muy corta (mínimo {cls.MIN_LENGTH} caracteres)"
            )

        if len(location) > cls.MAX_LENGTH:
            raise LocationValidationError(
                f"Ubicación muy larga (máximo {cls.MAX_LENGTH} caracteres)"
            )

        if not re.match(cls.ALLOWED_CHARS_PATTERN, location):
            raise LocationValidationError(
                "Ubicación contiene caracteres no permitidos"
            )

        return location.strip()

# En handler:
async def config_training_select_location(update, context):
    try:
        location = LocationValidator.validate(update.message.text)
        TrainingStateManager.save_config_state(context, ..., location=location)
        return CONFIRM_CONTINUE
    except LocationValidationError as e:
        await update.message.reply_text(f"❌ {e.message}")
        return SELECT_LOCATION
```

**Impacto**:
- ✅ Validación estricta (min/max/chars)
- ✅ Mensajes claros al usuario
- ✅ Reutilizable en otros handlers
- ✅ Sin SQL injection

**Archivos a modificar**:
- `src/utils/validators.py` (agregar LocationValidator)
- `config_training_handler.py` (usar validador)
- `src/core/exceptions.py` (agregar LocationValidationError)

---

### SOLUCIÓN 5: UPSERT Atómico para Evitar Race Conditions

**Actual** (Problemático):
```python
config = self.get_by_weekday(weekday)  # SELECT 1
if config:
    # UPDATE 2
    self.db.commit()
else:
    # INSERT 3
    self.db.commit()
```

**Problema**:
Entre SELECT y INSERT, otro proceso puede crear el mismo weekday → UNIQUE constraint error

**SOLUCIÓN**: Usar UPSERT en BD (ON CONFLICT / ON DUPLICATE KEY)

```python
# En ConfigTrainingRepository
def update_by_weekday(
    self,
    weekday: int,
    session_type: str,
    location: str
) -> TrainingDayConfig:
    """UPSERT atómico: inserta o actualiza sin race condition."""

    days_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    weekday_name = days_names[weekday]

    # Busca existente (con lock explícito si SQLite lo soporta)
    config = self.db.query(TrainingDayConfig).filter(
        TrainingDayConfig.weekday == weekday
    ).with_for_update().first()  # ← Lock para evitar race condition

    if config:
        # UPDATE
        config.session_type = session_type
        config.location = location
        config.updated_at = datetime.now()
    else:
        # INSERT
        config = TrainingDayConfig(
            weekday=weekday,
            weekday_name=weekday_name,
            session_type=session_type,
            location=location
        )
        self.db.add(config)

    self.db.flush()  # Detecta UNIQUE violation aquí
    self.db.commit()
    self.db.refresh(config)

    return config
```

**Impacto**:
- ✅ Operación atómica (sin race condition)
- ✅ SQLAlchemy detects UNIQUE violation antes de commit
- ✅ Comportamiento consistente update/insert

**Archivos a modificar**:
- `src/repositories/config_training_repository.py` (agregar lock)

---

### SOLUCIÓN 6: Transacciones con Patrón Single Responsibility

**Actual** (Problemático):
```python
# En config_training_confirm()
db = get_db()
service = ConfigTrainingService(db)
service.configure_day(weekday, session_type, location)  # ¿Quién hace commit?
# Handler limpia estado
# Handler pregunta al usuario
# Handler retorna estado
```

**Problema**:
Responsabilidades dispersas (handler → service → repository)

**SOLUCIÓN**: Cada capa responsable de SU parte

```python
# HANDLER (interfaz usuario + flujo)
async def config_training_confirm(update, context):
    state = TrainingStateManager.get_config_state(context)

    try:
        with get_db_context() as db:
            service = ConfigTrainingService(db)
            service.configure_day(state.weekday, state.session_type, state.location)
        # Auto-commit aquí por context manager

        # Handler solo controla flujo
        TrainingStateManager.clear_config_state(context)
        await update.message.reply_text("✅ Guardado")
        return CONFIRM_CONTINUE

    except ConfigurationError as e:
        await update.message.reply_text(f"❌ Error: {e.user_message}")
        return CONFIRM_CONTINUE

# SERVICE (lógica negocio + validación)
def configure_day(self, weekday, session_type, location):
    # Validar datos
    if not isinstance(weekday, int) or weekday < 0 or weekday > 6:
        raise ValidationError("Día inválido")

    # Delegar persistencia
    config = self.repository.update_by_weekday(weekday, session_type, location)
    # ← Service NO hace commit (lo hace context manager del handler)

    return config

# REPOSITORY (solo CRUD)
def update_by_weekday(self, weekday, session_type, location):
    # Solo inserta/actualiza, NO commit
    config = self.db.query(TrainingDayConfig).filter(...).first()
    if config:
        config.session_type = session_type
        config.location = location
    else:
        config = TrainingDayConfig(...)
        self.db.add(config)

    return config
    # ← Repository NO hace commit (lo hace el caller)
```

**Impacto**:
- ✅ Responsabilidades claras (handler → service → repository)
- ✅ Service sin efectos de BD
- ✅ Transacciones centralizadas en handler
- ✅ Testeable en capas

**Archivos a modificar**:
- `src/repositories/config_training_repository.py` (remover commits explícitos)
- `src/services/config_training_service.py` (remover lógica transaccional)
- `config_training_handler.py` (centralizar transacciones)

---

### SOLUCIÓN 7: Excepciones Específicas

**Actual** (Problemático):
```python
except Exception as e:  # ← Captura TODO
    logger.error(f"Error: {e}")
    await update.message.reply_text(f"❌ Error: {str(e)}")
    return ConversationHandler.END
```

**Problema**:
No diferencia entre user errors (validación) vs system errors (BD)

**SOLUCIÓN**: Custom exceptions en `src/core/exceptions.py`

```python
# exceptions.py
class ConfigurationError(Exception):
    """Base para errores de configuración."""
    def __init__(self, message: str, user_message: str = None):
        self.message = message
        self.user_message = user_message or message
        super().__init__(message)

class ValidationError(ConfigurationError):
    """Datos inválidos."""
    pass

class DatabaseError(ConfigurationError):
    """Error de base de datos."""
    pass

class StateNotFoundError(ConfigurationError):
    """Estado conversacional perdido."""
    pass

# En handler:
try:
    with get_db_context() as db:
        service = ConfigTrainingService(db)
        service.configure_day(state.weekday, state.session_type, state.location)

except ValidationError as e:
    # Usuario debe reintentar
    await update.message.reply_text(f"❌ {e.user_message}")
    return CONFIRM_CONTINUE

except StateNotFoundError as e:
    # Estado perdido, reiniciar flujo
    logger.warning(f"Estado perdido: {e.message}")
    await update.message.reply_text("❌ La sesión se interrumpió, volvamos a comenzar.")
    return ConversationHandler.END

except DatabaseError as e:
    # Error de sistema
    logger.error(f"Error de BD: {e.message}", exc_info=True)
    await update.message.reply_text("❌ Error de base de datos, intenta más tarde.")
    return ConversationHandler.END

except Exception as e:
    # Inesperado
    logger.critical(f"Error inesperado: {e}", exc_info=True)
    return ConversationHandler.END
```

**Impacto**:
- ✅ Errores específicos por tipo
- ✅ Mensajes claros al usuario
- ✅ Recuperación inteligente
- ✅ Debugging más fácil

**Archivos a modificar**:
- `src/core/exceptions.py` (agregar excepciones específicas)
- `config_training_handler.py` (usar excepciones específicas)
- `config_training_service.py` (lanzar excepciones específicas)

---

## 📋 PLAN DE IMPLEMENTACIÓN

### Fase 1: Crear Infraestructura de Apoyo (Sin modificar flujo existente)

**Tareas**:
1. ✅ [T1.1] Agregar `ConfigTrainingState` dataclass a `training_state.py`
2. ✅ [T1.2] Agregar excepciones específicas a `core/exceptions.py`
3. ✅ [T1.3] Crear `LocationValidator` en `utils/validators.py`
4. ✅ [T1.4] Agregar context manager `get_db_context()` a `models/base.py`
5. ✅ [T1.5] Crear `TrainingStateManager` en nuevo archivo `handlers/training_state_manager.py`

**Impacto**: CERO en flujo existente

---

### Fase 2: Refactor Handler (Reemplazar implementación)

**Tareas**:
6. ✅ [T2.1] Reemplazar `context.user_data` por `ConfigTrainingState` + manager
7. ✅ [T2.2] Reemplazar try/finally manual por `get_db_context()`
8. ✅ [T2.3] Agregar validación usando `LocationValidator`
9. ✅ [T2.4] Agregar manejo específico de excepciones

**Impacto**: Funcionalidad idéntica, código más robusto

---

### Fase 3: Refactor Repository (Transacciones)

**Tareas**:
10. ✅ [T3.1] Remover commits explícitos de `update_by_weekday()`
11. ✅ [T3.2] Agregar lock con `with_for_update()` para atomicidad

**Impacto**: Responsabilidad transaccional en handler

---

### Fase 4: Refactor Service (Limpieza)

**Tareas**:
12. ✅ [T4.1] Verificar service no tiene lógica transaccional
13. ✅ [T4.2] Agregar validación de tipos en `configure_day()`

**Impacto**: Minimal, consolidar existente

---

### Fase 5: Testing y Validación

**Tareas**:
14. ✅ [T5.1] Prueba manual: Flujo completo `/config_semana` → guardado → resumen
15. ✅ [T5.2] Prueba: Duplicar requests simultáneos (race condition)
16. ✅ [T5.3] Prueba: Excepciones (ubicación inválida, BD offline)

---

## ✅ CRITERIOS DE ÉXITO

| Criterio | Validación |
|----------|-----------|
| Type-safety | `ConfigTrainingState` dataclass con IDE autocomplete |
| Transacciones | Commit/rollback automático, sin fugas de BD |
| Atomicidad | `with_for_update()` previene race conditions |
| Validación | Ubicación con límites y sanitización |
| Excepciones | Errores específicos, mensajes claros al usuario |
| Limpieza | Clear automático en cada ciclo de estado |
| Documentación | Cada cambio documentado con "por qué" |

---

## 🔍 VERIFICACIÓN POST-IMPLEMENTACIÓN

```python
# Test 1: Type-safety
state = ConfigTrainingState(weekday=0, ...)  # IDE autocomplete
state.weekday  # No typos posibles

# Test 2: Transacciones
with get_db_context() as db:
    service.configure_day(...)  # Auto-commit
# Connection cerrada garantizado

# Test 3: Atomicidad
# Ejecutar 2 requests simultáneamente → Sin UNIQUE constraint error

# Test 4: Validación
LocationValidator.validate("ab")  # Raise LocationValidationError
LocationValidator.validate("x" * 101)  # Raise LocationValidationError
LocationValidator.validate("2do'; DROP TABLE; --")  # Raise LocationValidationError

# Test 5: Excepciones
# ValidationError → return SELECT_LOCATION
# DatabaseError → return ConversationHandler.END
# Exception → log, return ConversationHandler.END
```

---

## 📝 NOTAS IMPORTANTES

1. **NO hacer commits en repository**: Responsabilidad del handler (context manager)
2. **Dataclass for state**: Type-safety garantizado
3. **Lock con `with_for_update()`**: Previene race conditions
4. **LocationValidator**: Reutilizable en otros handlers
5. **Excepciones específicas**: Cada error tipo tiene su handling

---

**Próximo paso**: Iniciar Fase 1 con T1.1
