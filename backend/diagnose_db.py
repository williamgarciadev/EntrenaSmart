#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la conexión a la base de datos.
Ejecutar en Railway para ver qué DATABASE_URL se está recibiendo.
"""
import os
import sys

print("=" * 70)
print("DIAGNÓSTICO DE BASE DE DATOS")
print("=" * 70)
print()

# 1. Ver todas las variables de entorno relacionadas con DATABASE
print("1. Variables de entorno relacionadas con DATABASE:")
print("-" * 70)
for key, value in sorted(os.environ.items()):
    if 'DATABASE' in key.upper() or 'POSTGRES' in key.upper() or 'PG' in key.upper():
        # Ocultar contraseñas
        if 'PASSWORD' in key.upper() or 'PASS' in key.upper():
            display_value = '*' * 8
        elif value.startswith('postgresql://'):
            # Ocultar password en URL
            parts = value.split('@')
            if len(parts) == 2:
                user_pass = parts[0].split('://')
                if len(user_pass) == 2:
                    display_value = f"{user_pass[0]}://***:***@{parts[1]}"
                else:
                    display_value = value
            else:
                display_value = value
        else:
            display_value = value
        print(f"  {key} = {display_value}")
print()

# 2. Ver el valor específico de DATABASE_URL
print("2. DATABASE_URL específicamente:")
print("-" * 70)
database_url = os.getenv('DATABASE_URL')
if database_url:
    print(f"  Existe: Sí")
    print(f"  Valor raw: {database_url[:50]}...")
    print(f"  Longitud: {len(database_url)} caracteres")

    # Detectar si es una referencia Railway sin resolver
    if database_url.startswith('${{'):
        print(f"  ⚠️  PROBLEMA: Parece una referencia Railway sin resolver!")
        print(f"  Valor completo: {database_url}")
        print()
        print("  Esto significa que:")
        print("    - El servicio PostgreSQL no existe, o")
        print("    - El nombre del servicio no coincide con la referencia")
        print()
    elif database_url.startswith('postgresql://'):
        print(f"  ✓ Es una URL PostgreSQL válida")
        # Extraer info
        try:
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            print(f"  Host: {parsed.hostname}")
            print(f"  Puerto: {parsed.port or 5432}")
            print(f"  Base de datos: {parsed.path.lstrip('/')}")
            print(f"  Usuario: {parsed.username}")
        except Exception as e:
            print(f"  Error parseando URL: {e}")
    elif database_url.startswith('sqlite://'):
        print(f"  ⚠️  Es SQLite (no debería ser en Railway)")
        print(f"  Valor: {database_url}")
    else:
        print(f"  ⚠️  Formato desconocido")
        print(f"  Valor: {database_url}")
else:
    print(f"  Existe: No")
    print(f"  ❌ DATABASE_URL no está definida!")
print()

# 3. Intentar conectar
print("3. Intentando cargar configuración de la aplicación:")
print("-" * 70)
try:
    # Agregar path al backend
    sys.path.insert(0, '/app')
    from backend.src.core.config import settings

    db_url = settings.get_database_url
    print(f"  URL obtenida: {db_url[:50]}...")
    print(f"  Es PostgreSQL: {settings.is_postgres}")
    print(f"  Es MySQL: {settings.is_mysql}")
    print(f"  Es SQLite: {settings.is_sqlite}")

    if settings.is_sqlite:
        print()
        print("  ❌ ¡PROBLEMA! La aplicación está usando SQLite")
        print("     Esto confirma que DATABASE_URL no se está resolviendo correctamente")
    elif settings.is_postgres:
        print()
        print("  ✓ La aplicación detectó PostgreSQL correctamente")

        # Intentar conexión
        print()
        print("4. Intentando conectar a la base de datos:")
        print("-" * 70)
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(db_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.scalar()
                print(f"  ✓ ¡Conexión exitosa!")
                print(f"  Versión PostgreSQL: {version}")
        except Exception as e:
            print(f"  ❌ Error conectando: {e}")

except Exception as e:
    print(f"  ❌ Error cargando configuración: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("FIN DEL DIAGNÓSTICO")
print("=" * 70)
