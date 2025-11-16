# Arquitectura de EntrenaSmart

## Visión General

EntrenaSmart sigue una **arquitectura limpia** con separación clara de responsabilidades, implementando principios SOLID y patrones de diseño probados.

## Capas de la Arquitectura

### 1. Capa de Presentación (Handlers)
- **Responsabilidad**: Interactuar con usuarios de Telegram
- **Ubicación**: `src/handlers/`
- **Componentes**:
  - `trainer_handlers.py`: Comandos del entrenador
  - `student_handlers.py`: Respuestas de alumnos

### 2. Capa de Lógica de Negocio (Services)
- **Responsabilidad**: Implementar reglas de negocio
- **Ubicación**: `src/services/`
- **Componentes**:
  - `student_service.py`: Gestión de alumnos
  - `training_service.py`: Gestión de entrenamientos
  - `feedback_service.py`: Gestión de feedback
  - `report_service.py`: Generación de reportes
  - `scheduler_service.py`: Programación de tareas

### 3. Capa de Acceso a Datos (Repositories)
- **Responsabilidad**: Abstracción de persistencia
- **Ubicación**: `src/repositories/`
- **Patrón**: Repository Pattern
- **Componentes**:
  - `base_repository.py`: Operaciones CRUD genéricas
  - `student_repository.py`: Operaciones de alumnos
  - `training_repository.py`: Operaciones de entrenamientos
  - `feedback_repository.py`: Operaciones de feedback

### 4. Capa de Dominio (Models)
- **Responsabilidad**: Definir entidades de negocio
- **Ubicación**: `src/models/`
- **ORM**: SQLAlchemy
- **Componentes**:
  - `student.py`: Entidad Alumno
  - `training.py`: Entidad Entrenamiento
  - `feedback.py`: Entidad Feedback

### 5. Capa de Infraestructura (Core + Utils)
- **Responsabilidad**: Configuración y utilidades
- **Ubicación**: `src/core/` y `src/utils/`
- **Componentes**:
  - `config.py`: Configuración con Pydantic
  - `logger.py`: Sistema de logging
  - `validators.py`: Validadores
  - `formatters.py`: Formateadores

## Flujo de Datos

```
Usuario Telegram
     ↓
Handlers (Presentación)
     ↓
Services (Lógica de Negocio)
     ↓
Repositories (Acceso a Datos)
     ↓
Models (SQLAlchemy)
     ↓
Base de Datos (SQLite)
```

## Principios SOLID Aplicados

### Single Responsibility Principle (SRP)
- Cada módulo tiene una única razón para cambiar
- Handlers solo manejan interacción con Telegram
- Services solo implementan lógica de negocio
- Repositories solo acceden a datos

### Open/Closed Principle (OCP)
- Extensible mediante herencia y composición
- BaseRepository permite crear nuevos repositorios sin modificar código existente

### Liskov Substitution Principle (LSP)
- Los repositorios específicos pueden sustituir a BaseRepository
- Las implementaciones respetan los contratos de las interfaces

### Interface Segregation Principle (ISP)
- Interfaces específicas para cada tipo de repositorio
- Servicios dependen solo de las operaciones que necesitan

### Dependency Inversion Principle (DIP)
- Services dependen de abstracciones (repositorios), no de implementaciones concretas
- Facilita testing con mocks

## Patrones de Diseño

### Repository Pattern
- Abstrae el acceso a datos
- Facilita cambiar de SQLite a PostgreSQL sin afectar servicios

### Service Layer
- Centraliza lógica de negocio
- Facilita reutilización y testing

### Dependency Injection
- Los servicios reciben repositorios como dependencias
- Facilita testing y mantenibilidad

## Testing

### Tests Unitarios
- Prueban componentes individuales aisladamente
- Usan mocks para dependencias
- Cobertura: Services, Repositories, Models, Utils

### Tests de Integración
- Prueban flujos completos
- Usan base de datos en memoria
- Cobertura: Handlers, Workflows completos

## Consideraciones de Escalabilidad

1. **Separación de responsabilidades**: Facilita mantenimiento
2. **Abstracción de datos**: Permite migrar a PostgreSQL si crece
3. **Service Layer**: Permite agregar nuevas funcionalidades sin modificar handlers
4. **Testing robusto**: Detecta regresiones temprano

