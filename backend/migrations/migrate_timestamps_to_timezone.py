#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migración para convertir timestamps a timezone-aware
================================================================

Convierte todas las columnas created_at y updated_at de TIMESTAMP
a TIMESTAMPTZ (timezone-aware) usando America/Bogota como zona horaria.

Los timestamps existentes se interpretan como UTC y se convierten a Bogotá.

Uso:
    python backend/migrations/migrate_timestamps_to_timezone.py
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

# Agregar el directorio raíz al path para imports
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

# Cargar variables de entorno desde .env.docker si existe
env_path = root_dir / '.env.docker'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from sqlalchemy import create_engine, text

# Configurar logger
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def migrate_timestamps_to_timezone():
    """
    Migra todos los timestamps a timezone-aware (TIMESTAMPTZ).

    Proceso:
    1. Convierte created_at y updated_at a TIMESTAMPTZ
    2. Interpreta timestamps existentes como UTC
    3. Los convierte a America/Bogota
    """
    logger.info("=" * 70)
    logger.info("🕐 MIGRACIÓN DE TIMESTAMPS A TIMEZONE-AWARE")
    logger.info("=" * 70)

    # Construir database URL directamente
    postgres_password = os.getenv('POSTGRES_PASSWORD', 'entrenasmart123')
    database_url = f"postgresql://entrenasmart:{postgres_password}@localhost:5432/entrenasmart"

    logger.info(f"📊 Conectando a: postgresql://entrenasmart:***@localhost:5432/entrenasmart")

    # Crear engine de SQLAlchemy
    engine = create_engine(database_url)

    # Lista de tablas a migrar
    tables = [
        'students',
        'trainings',
        'training_day_configs',
        'feedbacks',
        'message_schedules',
        'message_templates',
        'weekly_reminder_configs'
    ]

    try:
        with engine.connect() as conn:
            # Iniciar transacción
            trans = conn.begin()

            try:
                logger.info("📊 Verificando timezone de PostgreSQL...")
                result = conn.execute(text("SHOW timezone"))
                current_tz = result.scalar()
                logger.info(f"   Timezone actual: {current_tz}")

                # Migrar cada tabla
                for table in tables:
                    logger.info(f"\n📋 Procesando tabla: {table}")

                    # Verificar si la tabla existe
                    check_query = text(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE table_name = '{table}'
                        )
                    """)
                    exists = conn.execute(check_query).scalar()

                    if not exists:
                        logger.warning(f"   ⚠️  Tabla {table} no existe - saltando...")
                        continue

                    # Contar registros antes
                    count_query = text(f"SELECT COUNT(*) FROM {table}")
                    count = conn.execute(count_query).scalar()
                    logger.info(f"   Registros encontrados: {count}")

                    if count == 0:
                        logger.info(f"   ✅ Tabla vacía - solo actualizando tipo de columna...")

                    # Migrar created_at
                    logger.info(f"   🔄 Migrando created_at...")
                    migrate_column_query = text(f"""
                        ALTER TABLE {table}
                        ALTER COLUMN created_at TYPE TIMESTAMPTZ
                        USING created_at AT TIME ZONE 'UTC' AT TIME ZONE 'America/Bogota'
                    """)
                    conn.execute(migrate_column_query)
                    logger.info(f"   ✅ created_at migrado")

                    # Migrar updated_at
                    logger.info(f"   🔄 Migrando updated_at...")
                    migrate_column_query = text(f"""
                        ALTER TABLE {table}
                        ALTER COLUMN updated_at TYPE TIMESTAMPTZ
                        USING updated_at AT TIME ZONE 'UTC' AT TIME ZONE 'America/Bogota'
                    """)
                    conn.execute(migrate_column_query)
                    logger.info(f"   ✅ updated_at migrado")

                    # Verificar resultado
                    if count > 0:
                        verify_query = text(f"""
                            SELECT created_at, updated_at
                            FROM {table}
                            LIMIT 1
                        """)
                        result = conn.execute(verify_query).fetchone()
                        if result:
                            logger.info(f"   ✅ Ejemplo de timestamp migrado:")
                            logger.info(f"      created_at: {result[0]}")
                            logger.info(f"      updated_at: {result[1]}")

                # Commit de la transacción
                trans.commit()

                logger.info("\n" + "=" * 70)
                logger.info("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
                logger.info("=" * 70)
                logger.info(f"Tablas procesadas: {len([t for t in tables])}")
                logger.info("Todos los timestamps ahora son timezone-aware (America/Bogota)")
                logger.info("\n💡 Próximos pasos:")
                logger.info("   1. Reinicia los contenedores: docker-compose restart")
                logger.info("   2. Verifica que nuevos registros usen timezone correcto")
                logger.info("   3. Revisa que los recordatorios se programen en hora de Bogotá")

            except Exception as e:
                trans.rollback()
                logger.error(f"❌ Error durante la migración: {e}", exc_info=True)
                raise

    except Exception as e:
        logger.error(f"❌ Error conectando a la base de datos: {e}", exc_info=True)
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    try:
        migrate_timestamps_to_timezone()
        sys.exit(0)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Migración cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Migración fallida: {e}")
        sys.exit(1)
