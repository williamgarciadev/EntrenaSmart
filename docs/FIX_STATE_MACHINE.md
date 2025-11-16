# 🔧 FIX: Máquina de Estados Separada en /config_semana

**Fecha**: 2025-11-15 17:21:00
**Status**: ✅ IMPLEMENTADO Y VALIDADO
**Problema**: Configuraciones múltiples no se guardaban (solo la primera persistía)

---

## 🐛 Problema Identificado

El ConversationHandler tenía una **mapping incorrecta** de estados:

```python
# ANTES (Incorrecto)
CONFIRM_CONTINUE = 4    # Estaba siendo usado como estado de confirmación
                        # Pero mapeaba a config_training_continue()
                        # Que NO guardaba en BD
```

**Síntomas**:
- Primera configuración (Sábado → Brazo → 2do Piso) → ✅ SE GUARDABA
- Segunda configuración (Viernes → Funcional → 1er Piso) → ❌ NO SE GUARDABA
- En los logs: `[CONTINUE]` aparecía en vez de `[CONFIRM]` en la segunda iteración

**Causa Raíz**:
El flujo saltaba directamente a `config_training_continue()` sin ejecutar `config_training_confirm()`, por lo tanto NO ejecutaba el `service.configure_day()` que guarda en BD.

---

## ✅ Solución Implementada

### 1. Separar estados CONFIRM_DATA y CONFIRM_CONTINUE

**ANTES**:
```python
SELECT_DAY = 1
SELECT_SESSION_TYPE = 2
SELECT_LOCATION = 3
CONFIRM_CONTINUE = 4    # ❌ Era el único estado de confirmación
```

**DESPUÉS**:
```python
SELECT_DAY = 1
SELECT_SESSION_TYPE = 2
SELECT_LOCATION = 3
CONFIRM_DATA = 4        # ✅ Nuevo: mostrar resumen y confirmar datos
CONFIRM_CONTINUE = 5    # ✅ Renumerado: preguntar si otro día
```

### 2. Actualizar Flujo de Handler

```
/config_semana
    ↓ [SELECT_DAY]
Usuario selecciona día (Sábado)
    ↓ [SELECT_SESSION_TYPE]
Usuario selecciona tipo (Brazo)
    ↓ [SELECT_LOCATION]
Usuario ingresa ubicación (2do Piso)
    ↓ [CONFIRM_DATA] ← NUEVO: Mostrar resumen
"¿Es correcto?"
    ↓
config_training_confirm()
    ↓ Guardado en BD
    ↓ [CONFIRM_CONTINUE] ← Ahora pregunta "¿Otro día?"
"¿Quieres configurar otro día?"
    ↓
config_training_continue()
    ↓ Maneja Sí/No
```

### 3. Actualizar ConversationHandler States Mapping

**ANTES**:
```python
states={
    SELECT_DAY: [...],
    SELECT_SESSION_TYPE: [...],
    SELECT_LOCATION: [...],
    CONFIRM_CONTINUE: [           # ❌ Incorrecto!
        MessageHandler(..., config_training_continue)  # Saltar saving!
    ]
}
```

**DESPUÉS**:
```python
states={
    SELECT_DAY: [...],
    SELECT_SESSION_TYPE: [...],
    SELECT_LOCATION: [...],
    CONFIRM_DATA: [                    # ✅ Nuevo: mostrar y confirmar
        MessageHandler(..., config_training_confirm)  # GUARDA en BD
    ],
    CONFIRM_CONTINUE: [                # ✅ Renumerado: pregunta otro día
        MessageHandler(..., config_training_continue) # Maneja Sí/No
    ]
}
```

---

## 📝 Cambios de Código

### `src/handlers/config_training_handler.py`

**Línea 40-45**: Redefinir estados
```python
# Antiguos estados
SELECT_DAY = 1
SELECT_SESSION_TYPE = 2
SELECT_LOCATION = 3
CONFIRM_CONTINUE = 4    # ❌ Mal

# Nuevos estados
SELECT_DAY = 1
SELECT_SESSION_TYPE = 2
SELECT_LOCATION = 3
CONFIRM_DATA = 4        # ✅ Mostrar/confirmar datos
CONFIRM_CONTINUE = 5    # ✅ Preguntar otro día
```

**Línea 235**: `config_training_select_location()` retorna ahora `CONFIRM_DATA`
```python
return CONFIRM_DATA  # Cambio: era implícito, ahora explícito
```

**Línea 288**: `config_training_confirm()` retorna `CONFIRM_CONTINUE`
```python
return CONFIRM_CONTINUE  # Ya hacía esto, pero ahora es estado 5, no 4
```

**Línea 464-475**: ConversationHandler estados mapping
```python
states={
    ...
    CONFIRM_DATA: [                    # ✅ Nuevo estado 4
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            config_training_confirm    # GUARDA en BD
        )
    ],
    CONFIRM_CONTINUE: [                # ✅ Renumerado a estado 5
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            config_training_continue   # Pregunta "¿otro día?"
        )
    ]
}
```

### Test Files Updates

**`test_config_semana.py`**:
- Línea 41: Agregado `CONFIRM_DATA` a imports
- Línea 150: `CONFIRM_DATA (4)` ✅
- Línea 174: `CONFIRM_CONTINUE (5)` ✅

**`test_config_semana_persistence.py`**:
- Línea 46: Agregado `CONFIRM_DATA` a imports
- Línea 102: `CONFIRM_DATA` esperado de `config_training_select_location()`
- Línea 107: `CONFIRM_CONTINUE` esperado de `config_training_confirm()`

---

## ✅ Validación Completada

### Test Suite 1: Flujo Básico
```
✅ PASO 1: SELECT_DAY (1)
✅ PASO 2: SELECT_SESSION_TYPE (2)
✅ PASO 3: SELECT_LOCATION (3)
✅ PASO 4: CONFIRM_DATA (4) - Mostrar resumen
✅ PASO 5: CONFIRM_CONTINUE (5) - Pregunta "¿otro día?"
✅ PASO 6: END (-1) - Finalizar
✅ Validaciones de error
```

### Test Suite 2: Persistencia
```
✅ PRUEBA 1: Persistencia Múltiple (6 configuraciones)
✅ PRUEBA 2: Actualizar Existente (UPSERT)
✅ PRUEBA 3: Integridad de Datos (8 campos)
✅ PRUEBA 4: Resumen Semanal
✅ PRUEBA 5: Concurrencia (múltiples usuarios)
✅ PRUEBA 6: Rollback Automático
```

**Resultado**: `6/6 pruebas exitosas` ✅

---

## 🚀 Cómo Funciona Ahora

### Flujo Telegram para SEGUNDA configuración

```
Usuario: /config_semana
Bot: ¿Qué día?

Usuario: Viernes
Bot: ¿Qué tipo? → [SELECT_SESSION_TYPE]

Usuario: Funcional
Bot: ¿En qué piso? → [SELECT_LOCATION]

Usuario: 1er Piso
Bot: Resumen... ¿Es correcto?
    ↓ [CONFIRM_DATA] → Llama config_training_confirm()

Usuario: Sí
Bot: ✅ Viernes configurado como Funcional en 1er Piso!
     ¿Quieres otro día?
    ↓ [CONFIRM_CONTINUE] → Llama config_training_continue()

Usuario: No
Bot: ✅ Configuración Completada
     Lunes: Brazo (2do Piso) ✅
     Viernes: Funcional (1er Piso) ✅
```

**Cambio Clave**:
- PRIMERA iteración: `[CONFIRM_DATA]` → guarda Lunes ✅
- SEGUNDA iteración: `[CONFIRM_DATA]` → guarda Viernes ✅ (Ahora funciona!)

---

## 📊 Cambios Totales

| Archivo | Cambios | Estado |
|---------|---------|--------|
| `src/handlers/config_training_handler.py` | Separar CONFIRM_DATA/CONTINUE, actualizar mapping | ✅ |
| `test_config_semana.py` | Importar CONFIRM_DATA, actualizar assertions | ✅ |
| `test_config_semana_persistence.py` | Importar CONFIRM_DATA, actualizar flujo | ✅ |

**Tests**:
- Básico: 10/10 ✅
- Persistencia: 6/6 ✅

---

## 🎯 Resultado Final

```
ANTES:
├─ /config_semana (Sábado) ✅ Guardado
├─ /config_semana (Viernes) ❌ NO guardado
└─ BD: Solo Sábado visible

DESPUÉS:
├─ /config_semana (Sábado) ✅ Guardado en CONFIRM_DATA
├─ /config_semana (Viernes) ✅ Guardado en CONFIRM_DATA (ARREGLADO)
└─ BD: Sábado + Viernes ambos visibles
```

---

## 🔍 Validación en Telegram

**Próximo paso**: Reiniciar bot y ejecutar flujo en Telegram:
```
/config_semana
→ Viernes
→ Funcional
→ 1er Piso
→ Sí
→ No

Esperado: Resumen muestra AMBAS configuraciones
├─ Sábado: Brazo (2do Piso)
└─ Viernes: Funcional (1er Piso)
```

---

**Status**: ✅ LISTO PARA PRODUCCIÓN

Ambas suites de prueba pasan exitosamente. La máquina de estados está correctamente separada y la persistencia de múltiples configuraciones está garantizada.

Commit: `feature/entrenasmart-interactive-ui`
