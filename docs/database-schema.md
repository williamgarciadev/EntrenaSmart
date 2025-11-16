# Esquema de Base de Datos - EntrenaSmart

## Visión General

La base de datos de EntrenaSmart utiliza **SQLite** para el MVP, con un diseño que facilita la migración a PostgreSQL si el proyecto escala.

## Tablas

### `students` - Alumnos

Almacena información de los alumnos registrados.

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| `id` | INTEGER | ID único del alumno | PRIMARY KEY, AUTOINCREMENT |
| `chat_id` | BIGINT | ID de chat de Telegram | UNIQUE, NOT NULL |
| `name` | VARCHAR(100) | Nombre del alumno | NOT NULL |
| `telegram_username` | VARCHAR(50) | Username de Telegram | NULLABLE |
| `is_active` | BOOLEAN | Estado del alumno | DEFAULT TRUE |
| `created_at` | DATETIME | Fecha de registro | DEFAULT CURRENT_TIMESTAMP |
| `updated_at` | DATETIME | Última actualización | DEFAULT CURRENT_TIMESTAMP |

**Índices:**
- `idx_students_chat_id` en `chat_id` (búsquedas frecuentes)
- `idx_students_active` en `is_active` (filtrado de activos)

---

### `trainings` - Entrenamientos Programados

Almacena las sesiones de entrenamiento configuradas semanalmente.

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| `id` | INTEGER | ID único del entrenamiento | PRIMARY KEY, AUTOINCREMENT |
| `student_id` | INTEGER | ID del alumno | FOREIGN KEY → students(id), NOT NULL |
| `weekday` | INTEGER | Día de la semana (0-6) | NOT NULL, CHECK (0 <= weekday <= 6) |
| `time` | TIME | Hora del entrenamiento | NOT NULL |
| `session_type` | VARCHAR(50) | Tipo de sesión | NOT NULL |
| `is_active` | BOOLEAN | Estado de la sesión | DEFAULT TRUE |
| `created_at` | DATETIME | Fecha de creación | DEFAULT CURRENT_TIMESTAMP |
| `updated_at` | DATETIME | Última actualización | DEFAULT CURRENT_TIMESTAMP |

**Índices:**
- `idx_trainings_student` en `student_id` (consultas por alumno)
- `idx_trainings_weekday_time` en `(weekday, time)` (búsqueda de sesiones)
- `idx_trainings_active` en `is_active` (filtrado de activas)

**Constraint adicional:**
- UNIQUE(`student_id`, `weekday`, `time`) - No duplicar sesiones

---

### `feedback` - Feedback Post-Entrenamiento

Almacena el feedback de los alumnos después de cada sesión.

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| `id` | INTEGER | ID único del feedback | PRIMARY KEY, AUTOINCREMENT |
| `training_id` | INTEGER | ID del entrenamiento | FOREIGN KEY → trainings(id), NOT NULL |
| `session_date` | DATE | Fecha de la sesión | NOT NULL |
| `intensity` | INTEGER | Intensidad percibida (1-4) | NOT NULL, CHECK (1 <= intensity <= 4) |
| `pain_level` | INTEGER | Nivel de dolor (0-5) | DEFAULT 0, CHECK (0 <= pain_level <= 5) |
| `comments` | TEXT | Comentarios del alumno | NULLABLE |
| `completed` | BOOLEAN | Sesión completada | DEFAULT TRUE |
| `created_at` | DATETIME | Fecha de registro | DEFAULT CURRENT_TIMESTAMP |

**Índices:**
- `idx_feedback_training` en `training_id` (consultas por entrenamiento)
- `idx_feedback_date` en `session_date` (consultas por fecha)

---

### `apscheduler_jobs` - Tareas Programadas

Tabla generada automáticamente por APScheduler para persistencia de jobs.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | VARCHAR(191) | ID único del job |
| `next_run_time` | FLOAT | Timestamp de próxima ejecución |
| `job_state` | BLOB | Estado serializado del job |

**Nota:** Esta tabla la maneja APScheduler automáticamente.

---

## Relaciones

```
students (1) ──────< (N) trainings
trainings (1) ──────< (N) feedback
```

### Relación: Student → Training
- **Tipo**: Uno a Muchos
- **Descripción**: Un alumno puede tener múltiples entrenamientos
- **Cascada**: ON DELETE CASCADE (si se elimina alumno, se eliminan sus entrenamientos)

### Relación: Training → Feedback
- **Tipo**: Uno a Muchos
- **Descripción**: Un entrenamiento puede tener múltiples registros de feedback
- **Cascada**: ON DELETE CASCADE (si se elimina entrenamiento, se elimina su feedback)

---

## Valores de Ejemplo

### Weekday (día de la semana)
```python
0 = Lunes
1 = Martes
2 = Miércoles
3 = Jueves
4 = Viernes
5 = Sábado
6 = Domingo
```

### Intensity (intensidad)
```
1 = Suave
2 = Moderado
3 = Intenso
4 = Muy intenso
```

### Pain Level (nivel de dolor)
```
0 = Sin dolor
1 = Leve molestia
2 = Dolor leve
3 = Dolor moderado
4 = Dolor fuerte
5 = Dolor muy fuerte
```

---

## Consideraciones de Diseño

### 1. Normalización
- Base de datos normalizada en 3FN
- Evita redundancia de datos
- Facilita mantenimiento

### 2. Índices
- Índices en columnas de búsqueda frecuente
- Mejora performance de consultas

### 3. Constraints
- Validaciones a nivel de BD
- Integridad referencial garantizada
- Checks para valores válidos

### 4. Timestamps
- `created_at` y `updated_at` en todas las tablas principales
- Facilita auditoría y debugging

### 5. Soft Deletes
- Campo `is_active` en lugar de DELETE físico
- Permite recuperar datos si es necesario
- Mantiene historial

---

## Migración Futura a PostgreSQL

El diseño actual facilita migración a PostgreSQL:

1. **Tipos compatibles**: Los tipos usados existen en PostgreSQL
2. **Índices**: La sintaxis de índices es compatible
3. **Constraints**: Foreign keys y checks funcionan igual
4. **SQLAlchemy**: Cambiar solo el connection string

```python
# SQLite (actual)
DATABASE_URL = "sqlite:///storage/entrenasmart.db"

# PostgreSQL (futuro)
DATABASE_URL = "postgresql://user:pass@host:5432/entrenasmart"
```

