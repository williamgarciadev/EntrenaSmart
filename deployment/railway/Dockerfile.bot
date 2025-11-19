# EntrenaSmart - Dockerfile
# Bot de Telegram para Entrenadores Personales

FROM python:3.11-slim

# Metadatos
LABEL maintainer="EntrenaSmart Team"
LABEL description="Bot de Telegram para gestión de entrenamientos"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p storage/backups logs

# Crear usuario no-root
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

# Cambiar a usuario no-root
USER botuser

# Comando por defecto
CMD ["python", "backend/main.py"]

