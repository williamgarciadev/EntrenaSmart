# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Descripción del Proyecto

**EntrenaSmart** es un bot inteligente de Telegram que gestiona programaciones de entrenamientos personalizados con recordatorios automáticos y seguimiento de sesiones.

**Versión Actual**: 1.0.0
**Estado**: ✅ Estable y Listo para Producción
**Stack Principal**: Python 3.11+ | SQLAlchemy 2.0 | APScheduler | python-telegram-bot 20.7

---

## Arquitectura de Alto Nivel

### Patrón: Layered Architecture + Clean Code

La aplicación sigue una arquitectura en capas con clara separación de responsabilidades:

```
┌─────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER (handlers/)                         │
│  - Conversational handlers (registration, training)     │
│  - Command handlers (start, help, mi_semana)            │
│  - Callback handlers (button interactions)              │
├─────────────────────────────────────────────────────────┤
│  SERVICE LAYER (services/)                              │
│  - StudentService: CRUD y gestión de estudiantes        │
│  - TrainingService: Lógica de entrenamientos            │
│  - SchedulerService: Orquestación de tareas en segundo  │
│  - ReportService: Reportes y analytics                  │
│  - FeedbackService: Retroalimentación de sesiones       │
├─────────────────────────────────────────────────────────┤
│  REPOSITORY LAYER (repositories/)                       │
│  - BaseRepository: Operaciones CRUD genéricas           │
│  - StudentRepository, TrainingRepository, etc.          │
│  - Abstracción de acceso a datos con SQLAlchemy ORM    │
├─────────────────────────────────────────────────────────┤
│  DATA LAYER (models/)                                   │
│  - SQLAlchemy ORM models para DB                        │
│  - Modelos: Student, Training, TrainingDayConfig, etc.  │
│  - Validación con Pydantic en requests/responses        │
├─────────────────────────────────────────────────────────┤
│  CROSS-CUTTING (core/, utils/)                          │
│  - Configuración, constantes, excepciones               │
│  - Logging, validación, state management                │
│  - Menu builder y fuzzy search utilities                │
└─────────────────────────────────────────────────────────┘
```

### Flujos Principales

**1. Registro de Estudiante:**
```
/registrarme → RegistrationHandler → StudentService.create()
→ DB (Student) → Confirmación al usuario
```

**2. Configuración de Entrenamientos:**
```
/config_semana → ConfigTrainingHandler → ConversationState
→ TrainingService.create_week_config() → DB (Training + Config)
→ SchedulerService.register_reminders() → APScheduler
```

**3. Recordatorios Automáticos:**
```
APScheduler (5 min antes) → ReminderTask.execute()
→ SchedulerService.send_reminder() → Telegram API
```

**4. Reportes:**
```
ReportService.generate_report() → TrainingRepository.get_user_stats()
→ ReportTask (background) → envío de PDF
```

---

## Estructura de Directorios

```
entrenasmart/
├── main.py                          # Punto de entrada, configuración del bot
├── pyproject.toml                   # Configuración del proyecto
├── requirements.txt                 # Dependencias de producción
├── requirements-dev.txt             # Dependencias de desarrollo
├── .env.example                     # Template de variables de entorno
├── Dockerfile                       # Containerización
├── docker-compose.yml               # Orquestación local
│
├── src/                             # Código principal
│   ├── __init__.py
│   ├── __version__.py               # Versión central del app
│   ├── core/                        # Configuración y constantes
│   │   ├── config.py                # Settings con Pydantic (DB, Telegram, etc)
│   │   ├── constants.py             # Constantes del negocio
│   │   └── exceptions.py            # Excepciones custom (DatabaseError, etc)
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── base.py                  # Base class + init_db(), get_db()
│   │   ├── student.py               # Model: Usuario/Estudiante
│   │   ├── training.py              # Model: Sesión de entrenamiento
│   │   ├── training_day_config.py   # Model: Config semanal de entrenamiento
│   │   └── feedback.py              # Model: Feedback de sesiones
│   ├── repositories/                # Data access layer (Repository pattern)
│   │   ├── base_repository.py       # CRUD genérico (create, read, update, delete)
│   │   ├── student_repository.py    # Queries específicas de Student
│   │   ├── training_repository.py   # Queries específicas de Training
│   │   ├── feedback_repository.py   # Queries específicas de Feedback
│   │   └── config_training_repository.py # Queries de configuración
│   ├── services/                    # Business logic layer
│   │   ├── student_service.py       # Lógica de estudiantes
│   │   ├── training_service.py      # Lógica de entrenamientos
│   │   ├── config_training_service.py # Configuración de entrenamientos
│   │   ├── feedback_service.py      # Lógica de feedback
│   │   ├── report_service.py        # Generación de reportes
│   │   ├── scheduler_service.py     # Orquestación con APScheduler
│   │   └── tasks/                   # Background tasks
│   │       ├── reminder_task.py     # Envío de recordatorios
│   │       ├── report_task.py       # Generación de reportes
│   │       └── feedback_task.py     # Procesamiento de feedback
│   ├── handlers/                    # Presentation layer (Telegram handlers)
│   │   ├── trainer_handlers.py      # Comandos del entrenador (/start, /help, /reporte)
│   │   ├── registration_handler.py  # Flujo conversacional de registro
│   │   ├── training_handler.py      # Flujo conversacional de entrenamientos
│   │   ├── config_training_handler.py # Flujo /config_semana
│   │   ├── edit_training_handler.py # Flujo de edición de sesiones
│   │   ├── student_handlers.py      # Comandos de estudiante (/mis_sesiones)
│   │   ├── student_schedule_handler.py # Comando /mi_semana
│   │   └── training_state_manager.py # Gestión de estado conversacional
│   └── utils/                       # Utilidades transversales
│       ├── logger.py                # Configuración de logging con loguru
│       ├── conversation_state.py    # State machine para conversaciones
│       ├── menu_builder.py          # Construcción dinámica de menús
│       ├── fuzzy_search.py          # Búsqueda difusa de locaciones
│       ├── messages.py              # Templates de mensajes
│       ├── validation_helpers.py    # Validadores de negocio
│       └── validators.py            # Validadores de input
│
├── tests/                           # Suite de testing
│   ├── conftest.py                  # Fixtures compartidas
│   ├── test_config_semana.py        # Tests de flujo de configuración
│   ├── test_config_semana_persistence.py # Tests de persistencia
│   ├── unit/                        # Unit tests
│   │   ├── test_fuzzy_search.py
│   │   ├── test_menu_builder.py
│   │   └── test_conversation_state.py
│   └── integration/                 # Integration tests
│
├── scripts/                         # Scripts utilitarios
│   ├── db/
│   │   └── init_db.py               # Script para inicializar BD
│   └── test_*.py                    # Scripts de prueba y debug
│
├── docs/                            # Documentación del proyecto
│   ├── architecture.md              # Detalles de arquitectura
│   ├── database-schema.md           # Schema de BD
│   ├── fase*.md                     # Resúmenes de fases de desarrollo
│   ├── CHANGELOG.md                 # Historial de cambios
│   ├── RELEASE_NOTES.md             # Notas de versión
│   └── FIX_*.md                     # Documentación de fixes
│
├── tasks/                           # Planificación y documentación
│   ├── todo.md                      # Plan general del proyecto
│   └── PLAN_*.md                    # Planes específicos
│
├── storage/                         # Almacenamiento local
│   ├── backups/                     # Backups de base de datos
│   └── .gitkeep
│
├── .github/                         # Configuración de GitHub y instrucciones
│   ├── copilot-instructions.md      # Instrucciones para agentes IA
│   └── docs/                        # Documentación modular
│       ├── python-best-practices.md
│       ├── project-structure.md
│       ├── solid-principles.md
│       └── version-control.md
│
└── .gitignore                       # Control de versiones
```

---

## Comandos Esenciales para Desarrollo

### Configuración Inicial

```bash
# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env y añadir: TELEGRAM_TOKEN, DATABASE_URL, etc.
```

### Desarrollo

```bash
# Ejecutar el bot
python main.py

# Ejecutar linting y formateo
black src/ tests/
isort src/ tests/
flake8 src/ tests/

# Verificar tipos
mypy src/

# Ejecutar tests
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html

# Ejecutar un test específico
pytest tests/unit/test_fuzzy_search.py -v
pytest tests/test_config_semana.py::TestConfigSemana::test_validacion_horarios -v

# Ejecutar solo tests unitarios
pytest tests/unit/ -v

# Ver reporte de cobertura
pytest --cov=src --cov-report=term-missing tests/
```

### Seguridad y Calidad

```bash
# Análisis de seguridad
bandit -r src/

# Verificar todo antes de commit
black --check src/ tests/
isort --check-only src/ tests/
flake8 src/ tests/
mypy src/
pytest tests/ --cov=src

# Inicializar base de datos
python scripts/db/init_db.py
```

### Base de Datos

```bash
# Inicializar BD con esquema
python scripts/db/init_db.py

# Conectarse a SQLite (desarrollo)
sqlite3 storage/entrenasmart.db

# Ver estructura
.schema

# Salir
.quit
```

### Docker

```bash
# Build y run con Docker Compose
docker-compose up --build

# Stop containers
docker-compose down
```

---

## Guía de Desarrollo

### 1. Patrones de Código

**Principios SOLID aplicados:**
- **Single Responsibility**: Cada servicio/repositorio tiene UNA responsabilidad
- **Open/Closed**: Extensible sin modificar código existente (base_repository.py)
- **Liskov Substitution**: Los repositories heredan de BaseRepository
- **Interface Segregation**: Servicios solo implementan métodos necesarios
- **Dependency Inversion**: Services dependen de abstracciones (repositories)

**Type Hints Obligatorios:**
```python
from typing import List, Optional
from src.models.student import Student

def get_student_trainings(student_id: int) -> List[Training]:
    """Obtiene entrenamientos del estudiante."""
    # Implementación...
```

**Docstrings en Español:**
```python
def create_training(self, student_id: int, day: str) -> Training:
    """
    Crea un nuevo entrenamiento para un estudiante.

    Args:
        student_id: ID del estudiante
        day: Día de la semana (lunes-domingo)

    Returns:
        Objeto Training creado

    Raises:
        StudentNotFound: Si el estudiante no existe
        InvalidDayError: Si el día es inválido
    """
```

### 2. Workflow de Nuevas Funcionalidades

1. **Análisis**: Leer documentación en `.github/docs/` relevante
2. **Planificación**: Crear plan en `tasks/todo.md`
3. **Implementación**:
   - Model (datos) → Repository (acceso) → Service (lógica) → Handler (presentación)
   - Mínimo: 2 test cases por funcionalidad (happy path + error case)
4. **Testing**: `pytest` con cobertura >80%
5. **Commit**: Mensaje descriptivo en español

### 3. Manejo de Estado Conversacional

El bot usa `ConversationState` para mantener estado entre mensajes:

```python
from src.utils.conversation_state import ConversationState

state = ConversationState()
state.set_value("training_day", "lunes")
day = state.get_value("training_day")  # "lunes"
state.reset()  # Limpiar estado
```

### 4. Manejo de Errores

Usar excepciones custom en `src/core/exceptions.py`:

```python
from src.core.exceptions import StudentNotFound, ValidationError

try:
    student = StudentRepository().find_by_id(999)
    if not student:
        raise StudentNotFound("Estudiante no encontrado")
except StudentNotFound as e:
    logger.error(f"Error: {e}")
```

### 5. Logging

Usar `logger` desde `src.utils.logger`:

```python
from src.utils.logger import logger

logger.info("Entrenamiento creado para estudiante 123")
logger.error(f"Error procesando feedback: {str(e)}")
logger.debug("Detalles de debugging aquí")
```

---

## Puntos Clave de la Arquitectura

### ConversationState (Máquina de Estados)
- **Ubicación**: `src/utils/conversation_state.py`
- **Propósito**: Mantener contexto entre mensajes de usuario
- **Uso**: Registration, Training, Config handlers
- **Riesgo**: Sin sincronización de threads = bugs concurrentes
- **Mitigación**: APScheduler maneja threads adecuadamente

### Scheduler Service (APScheduler)
- **Ubicación**: `src/services/scheduler_service.py`
- **Responsabilidad**:
  - Registrar recordatorios 5 min antes de cada entrenamiento
  - Ejecutar tasks en background (reminder_task, report_task, etc)
  - Limpiar jobs al eliminar entrenamientos
- **Crítico**: Sin este servicio, NO HAY RECORDATORIOS

### Repository Pattern (Data Abstraction)
- **BaseRepository**: Operaciones CRUD genéricas
- **Ventaja**: Cambiar BD sin tocar services
- **Implementación**: SQLAlchemy ORM + SQLite

### Handler Conversacionales
- **Flujo**: Python-telegram-bot ConversationHandler
- **Estados**: ESTADOS_* definidos en cada handler
- **Pattern**: entry → conversation → end
- **Cuidado**: Orden de handlers en main.py importa (conflictos)

---

## Convenciones Importantes

### Nomenclatura
- **Models**: Singulares, PascalCase (`Student`, `Training`)
- **Servicios**: `*Service` (`StudentService`, `TrainingService`)
- **Repositorios**: `*Repository` (`StudentRepository`)
- **Handlers**: descriptivo + `_handler` o `*_handlers`
- **Tasks**: descriptivo + `_task` (`reminder_task.py`)

### Base de Datos
- **ORM**: SQLAlchemy 2.0 con declarative models
- **BD**: SQLite por defecto (cambiar en config.py para prod)
- **Migraciones**: Manual (crear scripts en `scripts/db/`)
- **Timestamps**: Todos los models tienen `created_at`, `updated_at`

### Testing
- **Framework**: pytest + pytest-asyncio
- **Fixtures**: En `conftest.py`
- **Cobertura**: Mínimo 80% (configurado en pyproject.toml)
- **Async**: Soportado nativamente

---

## Archivos Críticos a NO Modificar sin Análisis Profundo

1. **main.py**: Punto de entrada, orden de handlers es CRÍTICO
2. **src/models/base.py**: Inicialización de BD, cambios afectan toda la app
3. **src/services/scheduler_service.py**: Recordatorios dependen 100% de esto
4. **src/utils/conversation_state.py**: Estado conversacional es frágil sin cuidado
5. **pyproject.toml**: Cambios pueden romper tests, formateo, types

---

## Resolución de Problemas Comunes

### Bot no envía recordatorios
1. Verificar `SchedulerService` está inicializado en `main.py`
2. Revisar `reminder_task.py` y logs
3. Chequear horarios en BD (table `training_day_config`)
4. Verificar zona horaria (pytz en settings)

### Tests fallan por async
- Usar `@pytest.mark.asyncio` en test functions
- O conftest.py con fixture async

### Conflictos de handlers en Telegram
- Revisar orden en `main.py` (ConversationHandlers deben ir primero)
- Verificar que `ConversationState` se reinicia

### Import errors
- Asegurar `.venv` está activado
- Reinstalar con `pip install -r requirements.txt`
- Limpiar `__pycache__` y `.pytest_cache`

---

## Próximos Pasos Sugeridos

Para futuras sesiones:
1. Revisar `docs/architecture.md` para detalles técnicos
2. Leer tests en `tests/` para entender flujos
3. Ejecutar `pytest -v` para ver estado actual
4. Revisar logs en `storage/` si hay issues

---

## Variables de Entorno Requeridas

```bash
# Telegram
TELEGRAM_TOKEN=xxxxx  # Token del bot

# Base de datos
DATABASE_URL=sqlite:///./storage/entrenasmart.db

# Modo
DEBUG=False

# Huso horario
TIMEZONE=America/Bogota
```

---

## Recursos Adicionales

- Documentación oficial: `.github/docs/`
- Instrucciones para agentes IA: `.github/copilot-instructions.md`
- Notas de versión: `docs/RELEASE_NOTES.md`
- Historial de cambios: `docs/CHANGELOG.md`

---

**Última actualización**: 2025-11-16
**Versión**: 1.0.0
**Mantenedor**: EntrenaSmart Team
