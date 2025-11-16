# Plan de Trabajo: EntrenaSmart - Bot de Telegram para Entrenadores

## 📝 Resumen
Implementación de un bot de Telegram automatizado que ayuda a entrenadores personales a gestionar recordatorios de entrenamientos, recopilar feedback de alumnos y generar reportes semanales. El bot usará Python con python-telegram-bot, APScheduler para tareas programadas, y SQLite para persistencia de datos.

## 🎯 Objetivos
- [ ] Crear una estructura de proyecto profesional siguiendo principios SOLID y PEP 8
- [ ] Implementar sistema de comandos para el entrenador (/nuevo_alumno, /set)
- [ ] Automatizar recordatorios 30 minutos antes del entrenamiento
- [ ] Recopilar feedback post-entrenamiento de los alumnos
- [ ] Generar reportes semanales automáticos cada domingo
- [ ] Preparar el proyecto para deployment con Docker

## 📋 Tareas

### Fase 1: Preparación y Estructura Base ✅
- [x] 1.1 Crear estructura de directorios del proyecto
  - src/ con subdirectorios: core/, models/, repositories/, services/, handlers/, utils/
  - tests/ con subdirectorios: unit/, integration/
  - storage/backups/ para datos locales y respaldos
  - logs/ para archivos de log
  - docs/ para documentación adicional
  
- [x] 1.2 Configurar archivos base del proyecto
  - requirements.txt con dependencias de producción
  - requirements-dev.txt con dependencias de desarrollo
  - pyproject.toml para configuración de herramientas (black, isort, pytest, mypy, coverage)
  - .env.example con template completo de variables de entorno
  - .gitignore configurado para Python, IDEs, OS, y archivos del proyecto
  
- [x] 1.3 Crear archivos __init__.py en todos los paquetes Python
  - src/ y todos sus subdirectorios
  - tests/ y subdirectorios
  - Documentación inline en cada __init__.py
  
- [x] 1.4 Crear documentación inicial
  - docs/architecture.md - Arquitectura del proyecto
  - docs/database-schema.md - Esquema de base de datos
  - tests/conftest.py - Fixtures de pytest

### Fase 2: Configuración y Base de Datos ✅
- [x] 2.1 Implementar configuración centralizada
  - src/core/config.py con Pydantic Settings
  - src/core/exceptions.py con excepciones personalizadas
  - src/core/constants.py con constantes del proyecto
  
- [x] 2.2 Crear modelos de base de datos
  - src/models/base.py - Configuración base SQLAlchemy
  - src/models/student.py - Modelo de Alumno
  - src/models/training.py - Modelo de Entrenamiento
  - src/models/feedback.py - Modelo de Feedback
  
- [x] 2.3 Implementar repositorios (patrón Repository)
  - src/repositories/base_repository.py - Repositorio base genérico
  - src/repositories/student_repository.py - Operaciones de alumnos
  - src/repositories/training_repository.py - Operaciones de entrenamientos
  - src/repositories/feedback_repository.py - Operaciones de feedback

### Fase 3: Servicios de Negocio ✅
- [x] 3.1 Implementar servicio de gestión de alumnos
  - src/services/student_service.py
  - Lógica para crear/actualizar/eliminar alumnos
  - Validaciones de negocio
  
- [x] 3.2 Implementar servicio de entrenamientos
  - src/services/training_service.py
  - Configuración de semana de entrenamientos
  - Validación de horarios y duplicados
  
- [x] 3.3 Implementar servicio de feedback
  - src/services/feedback_service.py
  - Registro de feedback post-entrenamiento
  - Cálculo de estadísticas
  
- [x] 3.4 Implementar servicio de reportes
  - src/services/report_service.py
  - Generación de reportes semanales
  - Formateo de mensajes de reporte

### Fase 4: Sistema de Recordatorios ✅
- [x] 4.1 Implementar servicio de scheduler
  - src/services/scheduler_service.py
  - Configuración de APScheduler con SQLite jobstore
  - Manejo de zona horaria
  
- [x] 4.2 Implementar tareas programadas
  - src/services/tasks/reminder_task.py - Recordatorios pre-entrenamiento
  - src/services/tasks/feedback_task.py - Solicitud de feedback
  - src/services/tasks/report_task.py - Generación de reportes semanales
  
- [x] 4.3 Integrar scheduler con servicios de negocio
  - Programar recordatorios al crear entrenamientos
  - Cancelar tareas al modificar/eliminar entrenamientos
  - Reportes semanales automáticos

### Fase 5: Handlers del Bot de Telegram ✅
- [x] 5.1 Implementar handlers del entrenador
  - src/handlers/trainer_handlers.py
  - /start - Mensaje de bienvenida
  - /registrarme - Registrar nuevo alumno
  - /set - Configurar entrenamiento
  - /listar_alumnos - Listar alumnos
  - /reporte - Solicitar reporte manual
  - /help - Ayuda con comandos
  
- [x] 5.2 Implementar handlers de alumnos
  - src/handlers/student_handlers.py
  - /mis_sesiones - Ver entrenamientos
  - Callbacks de feedback (intensidad, completitud)
  - Manejo de respuestas de texto
  
- [x] 5.3 Implementar mensajes y templates
  - src/utils/messages.py - Templates completos
  
- [x] 5.4 Implementar sistema de logging
  - src/utils/logger.py - Configuración completa
  - src/utils/messages.py
  - Templates de recordatorios
  - Templates de feedback
  - Templates de reportes

### Fase 6: Punto de Entrada y Orquestación
- [ ] 6.1 Implementar utilidades
  - src/utils/logger.py - Configuración de logging
  - src/utils/validators.py - Validadores comunes
  - src/utils/formatters.py - Formateadores de fecha/hora
  
- [ ] 6.2 Crear punto de entrada principal
  - main.py - Inicialización del bot
  - Configuración de handlers
  - Inicialización de scheduler
  - Manejo de señales para shutdown limpio

### Fase 7: Testing
- [ ] 7.1 Configurar entorno de testing
  - tests/conftest.py con fixtures comunes
  - Mock de Telegram Bot API
  - Base de datos de prueba en memoria
  
- [ ] 7.2 Implementar tests unitarios
  - tests/unit/test_services.py - Tests de servicios
  - tests/unit/test_repositories.py - Tests de repositorios
  - tests/unit/test_models.py - Tests de modelos
  
- [ ] 7.3 Implementar tests de integración
  - tests/integration/test_handlers.py - Tests de handlers
  - tests/integration/test_scheduler.py - Tests de scheduler
  - tests/integration/test_workflow.py - Tests de flujo completo

### Fase 8: Documentación
- [x] 8.1 Actualizar README.md
  - Descripción del proyecto
  - Requisitos y dependencias
  - Instrucciones de instalación
  - Guía de uso (comandos del bot)
  - Configuración de variables de entorno
  - Guía completa para desarrollo con IA
  
- [ ] 8.2 Documentar arquitectura
  - docs/architecture.md - Diagrama de arquitectura
  - docs/database-schema.md - Esquema de base de datos
  - docs/deployment.md - Guía de deployment
  
- [ ] 8.3 Documentar API del bot
  - docs/bot-commands.md - Comandos disponibles
  - docs/bot-flows.md - Flujos de conversación

### Fase 9: Docker y Deployment
- [ ] 9.1 Crear Dockerfile
  - Imagen base Python 3.10-slim
  - Multi-stage build para optimizar tamaño
  - Configuración de usuario no-root
  
- [ ] 9.2 Crear docker-compose.yml
  - Servicio del bot
  - Volúmenes para persistencia
  - Variables de entorno
  
- [ ] 9.3 Preparar scripts de deployment
  - scripts/start.sh - Iniciar bot
  - scripts/stop.sh - Detener bot
  - scripts/backup.sh - Backup de base de datos

### Fase 10: Revisión Final y Optimización
- [ ] 10.1 Realizar limpieza de código
  - Ejecutar black para formateo
  - Ejecutar isort para ordenar imports
  - Ejecutar flake8 para linting
  - Ejecutar mypy para verificar tipos
  
- [ ] 10.2 Verificar seguridad
  - Ejecutar bandit para análisis de seguridad
  - Validar que no hay secretos en el código
  - Verificar manejo de errores y excepciones
  
- [ ] 10.3 Optimizar rendimiento
  - Revisar queries a base de datos
  - Optimizar carga de módulos
  - Verificar manejo de memoria

## 🔍 Consideraciones Técnicas Importantes

### 1. Librería de Telegram
**Decisión:** Usar `python-telegram-bot` v20+ 
- Más estable y documentado
- Soporte para async/await
- Comunidad más grande
- Mejor para MVP

### 2. Manejo de Zona Horaria
**Decisión:** Usar hora local del entrenador
- Almacenar timezone en configuración
- Usar `zoneinfo` (built-in Python 3.9+)
- Convertir todos los horarios a timezone configurado

### 3. Persistencia de Tareas Programadas
**Decisión:** Usar SQLite jobstore de APScheduler
- Las tareas sobreviven reinicios del bot
- Evita reprogramar en cada inicio
- Sincronización automática con base de datos

### 4. Autenticación del Entrenador
**Decisión:** Validar por Telegram user_id
- Configurar TRAINER_TELEGRAM_ID en variables de entorno
- Decorator para validar permisos en comandos admin
- Respuesta de error amigable para usuarios no autorizados

### 5. Gestión de Estados de Conversación
**Decisión:** Usar ConversationHandler de python-telegram-bot
- Para flujos multi-paso (ej: configurar semana completa)
- Estados claros y manejables
- Timeout para conversaciones inactivas

## ✅ Revisión Final
(Se completará al finalizar todas las tareas)

### Resumen de cambios realizados:
- Por completar...

### Archivos modificados:
- Por completar...

### Funcionalidades agregadas:
- Por completar...

### Notas importantes:
- Por completar...

