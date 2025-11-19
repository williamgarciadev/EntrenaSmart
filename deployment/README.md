# EntrenaSmart - Deployment Options

Esta carpeta contiene las configuraciones para desplegar EntrenaSmart en diferentes entornos.

## Opciones de Despliegue

### 🚂 Railway (Producción en la Nube)

**Recomendado para**: Producción, acceso público, alta disponibilidad

**Pros**:
- ✅ Despliegue automático desde GitHub
- ✅ Escalado automático
- ✅ SSL/HTTPS incluido
- ✅ PostgreSQL administrado
- ✅ Dominios públicos gratuitos
- ✅ Monitoreo y logs integrados

**Contras**:
- ❌ Costo mensual ($5-15/mes estimado)
- ❌ Requiere configuración inicial
- ❌ Menos control sobre la infraestructura

**Ver documentación**: [railway/README.md](railway/README.md)

---

### 🐳 Docker Compose (Local/Self-Hosted)

**Recomendado para**: Desarrollo local, staging, self-hosting

**Pros**:
- ✅ Gratis
- ✅ Control total
- ✅ Fácil de debuggear
- ✅ No requiere internet para funcionar
- ✅ Datos locales

**Contras**:
- ❌ Sin SSL (solo HTTP local)
- ❌ Requiere servidor propio para producción
- ❌ Mantenimiento manual
- ❌ No escalable automáticamente

**Ver documentación**: [docker/README.md](docker/README.md)

---

## Comparación Rápida

| Característica | Railway | Docker Compose |
|----------------|---------|----------------|
| **Costo** | $5-15/mes | Gratis (+ servidor) |
| **Setup Time** | 30 minutos | 5 minutos |
| **SSL/HTTPS** | ✅ Incluido | ❌ Manual |
| **Escalado** | ✅ Automático | ❌ Manual |
| **Base de Datos** | ✅ Administrada | ⚠️ Manual |
| **Backups** | ✅ Automáticos | ❌ Manual |
| **Monitoreo** | ✅ Incluido | ❌ Manual |
| **Acceso Público** | ✅ Fácil | ⚠️ Requiere config |
| **Desarrollo Local** | ❌ No recomendado | ✅ Perfecto |

---

## ¿Cuál elegir?

### Elige **Railway** si:
- Quieres desplegar en producción
- Necesitas acceso público desde cualquier lugar
- Prefieres no preocuparte por infraestructura
- El costo mensual es aceptable
- Quieres SSL/HTTPS automático

### Elige **Docker Compose** si:
- Estás desarrollando localmente
- Quieres testear antes de desplegar
- Tienes tu propio servidor
- Prefieres control total
- Quieres evitar costos mensuales

---

## Arquitectura

Ambas opciones despliegan la misma arquitectura:

```
┌─────────────────────────────────────────────────┐
│                   Internet                      │
└────────────┬────────────────────┬────────────────┘
             │                    │
             │                    │
      ┌──────▼──────┐      ┌──────▼──────┐
      │   Telegram  │      │   Browser   │
      │     API     │      │   (Users)   │
      └──────┬──────┘      └──────┬──────┘
             │                    │
             │                    │
      ┌──────▼──────┐      ┌──────▼──────┐
      │     Bot     │      │  Frontend   │
      │  (Python)   │      │  (React)    │
      └──────┬──────┘      └──────┬──────┘
             │                    │
             │              ┌─────▼─────┐
             │              │    API    │
             └──────────────►  (FastAPI)│
                            └─────┬─────┘
                                  │
                            ┌─────▼─────┐
                            │ PostgreSQL│
                            │ (Database)│
                            └───────────┘
```

### Componentes

1. **Bot** - Bot de Telegram (Python, python-telegram-bot)
   - Gestiona conversaciones con usuarios
   - Programa entrenamientos
   - Envía recordatorios
   - Genera reportes semanales

2. **API** - Backend REST (FastAPI)
   - CRUD de estudiantes
   - CRUD de entrenamientos
   - CRUD de mensajes programados
   - Autenticación JWT
   - Documentación Swagger

3. **Frontend** - Aplicación web (React + Vite)
   - Dashboard del entrenador
   - Gestión de estudiantes
   - Gestión de plantillas
   - Configuración de recordatorios

4. **PostgreSQL** - Base de datos relacional
   - Almacena todos los datos
   - Soporte para tipos ARRAY
   - Timestamps con timezone

---

## Migración entre Entornos

### De Docker Local → Railway

1. Exportar datos de PostgreSQL local:
   ```bash
   cd deployment/docker
   docker-compose exec postgres pg_dump -U entrenasmart entrenasmart > backup.sql
   ```

2. Desplegar en Railway (ver railway/README.md)

3. Importar datos a Railway:
   ```bash
   railway run -s Postgres psql < backup.sql
   ```

### De Railway → Docker Local

1. Exportar datos de Railway:
   ```bash
   railway run -s Postgres pg_dump > backup.sql
   ```

2. Iniciar Docker local (ver docker/README.md)

3. Importar datos:
   ```bash
   cd deployment/docker
   cat backup.sql | docker-compose exec -T postgres psql -U entrenasmart entrenasmart
   ```

---

## Soporte

- **Documentación Railway**: [railway/README.md](railway/README.md)
- **Documentación Docker**: [docker/README.md](docker/README.md)
- **Guías completas**: Ver `/RAILWAY_DEPLOY.md` y archivos relacionados en la raíz

---

## Próximos Pasos

1. **Desarrollo Local**: Comienza con Docker Compose
2. **Testing**: Prueba todas las funcionalidades localmente
3. **Producción**: Despliega en Railway cuando estés listo
4. **Monitoreo**: Configura alertas y monitoreo en Railway

¡Buena suerte con tu despliegue! 🚀
