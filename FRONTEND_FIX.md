# 🔧 Frontend Fix - Nginx Configuration

## Problema Identificado

El contenedor frontend (Nginx) no estaba iniciando debido a un problema con la configuración de Nginx en el Dockerfile.

### Error Original
```
2025/11/17 02:04:31 [emerg] 1#1: unknown directive "
" in /etc/nginx/conf.d/default.conf:1
nginx: [emerg] unknown directive "
" in /etc/nginx/conf.d/default.conf:1
```

### Causa Raíz
El Dockerfile original usaba `echo` con caracteres de escape para generar la configuración de Nginx:

```dockerfile
RUN echo 'server {\n\
    listen 80;\n\
    ...
}' > /etc/nginx/conf.d/default.conf
```

Este enfoque es frágil porque:
- Los saltos de línea `\n` no se interpretan correctamente en todos los entornos
- Los caracteres especiales pueden causar problemas de encoding en Windows
- Es difícil de mantener y depurar

## Solución Implementada

### 1. Crear archivo nginx.conf separado
Se creó `/frontend/nginx.conf` con la configuración correcta:

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html index.htm;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/javascript application/javascript application/json;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Deny hidden files
    location ~ /\. {
        deny all;
    }
}
```

### 2. Actualizar Dockerfile
El Dockerfile ahora copia el archivo de configuración en lugar de generarlo dinámicamente:

```dockerfile
# Production stage
FROM nginx:alpine

# Copiar configuración nginx desde archivo
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar build del stage anterior
COPY --from=builder /app/dist /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/index.html || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## Beneficios

✅ **Más mantenible**: Archivo de configuración legible y separado
✅ **Más robusto**: No depende de caracteres de escape
✅ **Multiplataforma**: Funciona correctamente en Windows, Linux y macOS
✅ **Mejorado**: Incluye compresión gzip y headers de proxy correctos
✅ **Health check**: Endpoint `/health` para verificar disponibilidad

## Verificación

```bash
# Build
docker-compose build --no-cache frontend

# Iniciar
docker-compose up -d

# Verificar
docker-compose ps
# Debería mostrar: entrenasmart-frontend ... Up (healthy)

# Probar acceso
curl http://localhost:5173  # Debe retornar HTTP 200
curl http://localhost:8000/health  # Debe retornar JSON de salud
```

## Archivos Modificados

1. **frontend/Dockerfile** - Simplificado y mejorado
2. **frontend/nginx.conf** - Creado (nuevo archivo)

---

**Fecha**: 2025-11-16
**Status**: ✅ Resuelto y Verificado
