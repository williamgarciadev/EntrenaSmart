# Plan de Corrección: Persistencia de Datos en PostgreSQL

## 🔴 PROBLEMA IDENTIFICADO

**Ubicación**: `backend/api/routers/training_config.py` (líneas 19-29, 125-131, 165-171)

**Síntoma**:
- Frontend muestra datos correctamente
- Base de datos PostgreSQL está vacía
- Datos se pierden al reiniciar la aplicación

**Causa Raíz**:
El router usa un diccionario `MOCK_CONFIG` en memoria en lugar de conectarse a la base de datos real.

---

## ✅ SOLUCIÓN

Conectar el router directamente a `ConfigTrainingService` que ya existe y está totalmente implementado.

### Cambios Necesarios en `training_config.py`:

1. **Eliminar MOCK_CONFIG** (líneas 19-29)
   - Diccionario temporal no será necesario
   - Toda persistencia se hará vía BD

2. **Reemplazar `get_weekly_config()` endpoint (línea 32)**
   - Usar `ConfigTrainingService.get_all_configs()`
   - Consultar datos de BD en lugar de MOCK_CONFIG

3. **Reemplazar `get_day_config()` endpoint (línea 63)**
   - Usar `ConfigTrainingService.get_day_config(weekday)`
   - Obtener un día específico de BD

4. **Reemplazar `update_day_config()` endpoint (línea 97)**
   - Usar `ConfigTrainingService.configure_day()`
   - Guardar cambios en BD (PERSIST automáticamente)

5. **Reemplazar `delete_day_config()` endpoint (línea 145)**
   - Usar `ConfigTrainingService.delete_day_config()`
   - Eliminar de BD correctamente

### Pasos Específicos:

#### Paso 1: Imports (línea 15 actual)
```python
# AGREGAR estas importaciones:
from src.models.base import get_db_context
from src.services.config_training_service import ConfigTrainingService
from src.core.exceptions import RecordNotFoundError, ValidationError
```

#### Paso 2: Eliminar MOCK_CONFIG (líneas 19-29)
```python
# ❌ ELIMINAR TODO ESTO:
MOCK_CONFIG = {
    0: {...},
    1: {...},
    # etc
}
```

#### Paso 3: GET /training-config (obtener semanal)
**Cambio**: De leer MOCK_CONFIG → Consultar BD
```python
@router.get("", response_model=WeeklyConfigResponse)
async def get_weekly_config(trainer: dict = Depends(get_current_trainer)):
    """Obtener configuración semanal completa."""
    logger.info("Obteniendo configuración semanal")

    with get_db_context() as db:
        service = ConfigTrainingService(db)
        configs = service.get_all_configs()

    # Convertir a response model
    response_configs = [
        TrainingDayConfigResponse(
            id=config.id,
            weekday=config.weekday,
            weekday_name=config.weekday_name,
            session_type=config.session_type,
            location=config.location,
            is_active=config.is_active,
            created_at=config.created_at,
            updated_at=config.updated_at
        )
        for config in configs
    ]

    return WeeklyConfigResponse(configs=response_configs)
```

#### Paso 4: GET /training-config/{weekday} (obtener un día)
**Cambio**: De leer MOCK_CONFIG → Consultar BD
```python
@router.get("/{weekday}", response_model=TrainingDayConfigResponse)
async def get_day_config(
    weekday: int,
    trainer: dict = Depends(get_current_trainer)
):
    """Obtener configuración de un día específico."""
    if not 0 <= weekday <= 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El día debe estar entre 0 (Lunes) y 6 (Domingo)"
        )

    with get_db_context() as db:
        service = ConfigTrainingService(db)
        config = service.get_day_config(weekday)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuración no encontrada para el día {weekday}"
        )

    return TrainingDayConfigResponse(
        id=config.id,
        weekday=config.weekday,
        weekday_name=config.weekday_name,
        session_type=config.session_type,
        location=config.location,
        is_active=config.is_active,
        created_at=config.created_at,
        updated_at=config.updated_at
    )
```

#### Paso 5: POST /training-config/{weekday} (actualizar/crear)
**Cambio**: De guardar en MOCK_CONFIG → Persistir en BD
```python
@router.post("/{weekday}", response_model=SuccessResponse)
async def update_day_config(
    weekday: int,
    config: TrainingDayConfigCreate,
    trainer: dict = Depends(get_current_trainer)
):
    """Actualizar configuración de un día específico."""
    if not 0 <= weekday <= 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El día debe estar entre 0 (Lunes) y 6 (Domingo)"
        )

    # Validar tipos de entrenamiento permitidos
    VALID_TYPES = ["Pierna", "Funcional", "Brazo", "Espalda", "Pecho", "Hombros"]
    if config.session_type and config.session_type not in VALID_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de entrenamiento inválido. Debe ser uno de: {', '.join(VALID_TYPES)}"
        )

    try:
        with get_db_context() as db:
            service = ConfigTrainingService(db)
            config_obj = service.configure_day(
                weekday=weekday,
                session_type=config.session_type,
                location=config.location
            )
            # Auto-commit al salir del contexto

        logger.info(f"Configuración actualizada para el día {config.weekday_name}")

        return SuccessResponse(
            message=f"Configuración actualizada para {config.weekday_name}",
            data={
                "weekday": weekday,
                "session_type": config.session_type,
                "location": config.location
            }
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error actualizando configuración: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar configuración"
        )
```

#### Paso 6: DELETE /training-config/{weekday} (eliminar)
**Cambio**: De limpiar en MOCK_CONFIG → Eliminar de BD
```python
@router.delete("/{weekday}", response_model=SuccessResponse)
async def delete_day_config(
    weekday: int,
    trainer: dict = Depends(get_current_trainer)
):
    """Eliminar configuración de un día específico."""
    if not 0 <= weekday <= 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El día debe estar entre 0 (Lunes) y 6 (Domingo)"
        )

    day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    day_name = day_names[weekday]

    try:
        with get_db_context() as db:
            service = ConfigTrainingService(db)
            service.delete_day_config(weekday)
            # Auto-commit al salir del contexto

        logger.info(f"Configuración eliminada para {day_name}")

        return SuccessResponse(
            message=f"Configuración eliminada para {day_name}"
        )
    except RecordNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay configuración para {day_name}"
        )
    except Exception as e:
        logger.error(f"Error eliminando configuración: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar configuración"
        )
```

---

## 📊 RESUMEN DE CAMBIOS

| Elemento | Antes | Después |
|----------|-------|---------|
| **Almacenamiento** | MOCK_CONFIG (memoria) | PostgreSQL (persistente) |
| **GET semanal** | Lee MOCK_CONFIG dict | Consulta BD via servicio |
| **GET un día** | Lee MOCK_CONFIG dict | Consulta BD via servicio |
| **POST/UPDATE** | Modifica MOCK_CONFIG | Guarda en BD (auto-commit) |
| **DELETE** | Limpia MOCK_CONFIG | Elimina de BD |
| **Persistencia** | ❌ NO persiste | ✅ SI persiste |
| **Durabilidad** | Datos se pierden al reiniciar | ✅ Datos permanecen |
| **Código a cambiar** | ~180 líneas | ~15 líneas efectivas |
| **Riesgo de regresión** | Bajo (API interface igual) | ✅ Bajo |

---

## ✨ BENEFICIOS

- ✅ **Datos persistentes** en PostgreSQL
- ✅ **Coherencia** entre frontend y BD
- ✅ **Durabilidad** entre reinicios
- ✅ **Escalabilidad** para múltiples usuarios
- ✅ **Auditoría** (created_at, updated_at automáticos)
- ✅ **Transacciones ACID** garantizadas
- ✅ **Código limpio** sin MOCK_CONFIG

---

## 🧪 VALIDACIÓN DESPUÉS DE CAMBIOS

1. Guardar configuración desde UI → Verificar en BD
   ```bash
   psql -U postgres -d entrenasmart
   SELECT * FROM training_day_configs;
   ```

2. Reiniciar backend → Datos deben persistir
3. GET endpoint debe devolver datos de BD
4. Eliminar desde UI → Debe desaparecer de BD

---

## 📝 NOTAS IMPORTANTES

- **No afecta otros routers** (students, templates, schedules)
- **Compatible con frontend** (API interface no cambia)
- **Rollback automático** si hay error (transacciones)
- **Logging integrado** para auditoría
- **Validación mantiene tipos permitidos**

---

## 🚀 SIGUIENTE PASO

**Espera mi aprobación para empezar.**

Iré reemplazando cada endpoint de forma **SIMPLE Y ENFOCADA** sin cambios masivos.
