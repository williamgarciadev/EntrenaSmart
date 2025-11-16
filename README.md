# 🏋️ EntrenaSmart - Bot de Telegram para Gestión de Entrenamientos

[![Version](https://img.shields.io/badge/version-1.0.0-brightgreen.svg)](VERSION)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)](#)

**EntrenaSmart** es un bot inteligente de Telegram que te ayuda a gestionar tu programación de entrenamientos personalizados.

## ✨ Características Principales

### 🎯 Configuración de Entrenamientos
- ✅ Configura tu programación semanal
- ✅ Especifica tipo de entrenamiento
- ✅ Indica ubicación
- ✅ Soporte para múltiples entrenamientos

### ⏰ Recordatorios Automáticos
- ✅ Recordatorios 5 minutos antes
- ✅ Información completa en cada recordatorio
- ✅ Múltiples recordatorios simultáneos

### 👥 Gestión de Usuarios
- ✅ Registro automático
- ✅ Almacenamiento seguro
- ✅ Gestión de estado conversacional

## 🚀 Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/williamgarciadev/EntrenaSmart.git
cd EntrenaSmart

# Crear ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu token de Telegram

# Ejecutar el bot
python main.py
```

## 📖 Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `/start` | Inicia el bot |
| `/registrarme` | Registrar nuevo usuario |
| `/config_semana` | Configurar entrenamientos semanales |
| `/set` | Crear entrenamiento manual |
| `/editar_sesion` | Editar entrenamiento |
| `/semana` | Ver programación semanal |
| `/help` | Ver ayuda |

## 🧪 Testing

```bash
# Tests de flujo básico
python test_config_semana.py

# Tests de persistencia
python test_config_semana_persistence.py
```

**Resultado**: ✅ 16/16 tests pasando

## 🏗️ Tecnologías

- **Python 3.8+**
- **python-telegram-bot 20.7**
- **SQLAlchemy 2.0.23**
- **APScheduler 3.10.4**
- **SQLite**

## 📊 Estadísticas

- **Versión**: 1.0.0
- **Código**: ~3,500 líneas
- **Tests**: 16/16 pasando
- **Status**: ✅ Estable y Listo para Producción

## 📝 Documentación Completa

- [RELEASE_NOTES.md](RELEASE_NOTES.md) - Notas de release
- [CHANGELOG.md](CHANGELOG.md) - Historial de cambios
- [FIX_STATE_MACHINE.md](FIX_STATE_MACHINE.md) - Fix de máquina de estados
- [FIX_REMINDER_BOT_ACCESS.md](FIX_REMINDER_BOT_ACCESS.md) - Fix de recordatorios

## 🔐 Seguridad

- ✅ Validación de entrada
- ✅ Prevención de SQL injection
- ✅ Manejo seguro de tokens
- ✅ Error handling robusto

## 📜 Licencia

MIT License - Ver LICENSE para detalles

## 🎯 Roadmap

- **v1.1**: Mejoras en UI y más tipos de entrenamientos
- **v2.0**: Web dashboard, API REST, PostgreSQL

## 💬 Soporte

Para reportar bugs o sugerir mejoras, abre un issue en GitHub.

---

**Versión**: 1.0.0
**Fecha**: 2025-11-15
**Status**: ✅ Estable

Hecho con ❤️ para la comunidad de fitness
