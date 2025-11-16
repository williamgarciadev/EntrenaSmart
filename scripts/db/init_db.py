"""
Script de inicialización de la base de datos
=============================================

Crea las tablas necesarias en la base de datos.
"""
from src.models.base import init_db, engine
from src.utils.logger import logger


def initialize_database() -> None:
    """Inicializa la base de datos creando todas las tablas."""
    try:
        logger.info("Inicializando base de datos...")
        init_db()
        logger.info("✅ Base de datos inicializada correctamente")

        # Mostrar tablas creadas
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        logger.info(f"Tablas creadas: {', '.join(tables)}")

    except Exception as e:
        logger.error(f"❌ Error inicializando base de datos: {str(e)}")
        raise


if __name__ == "__main__":
    initialize_database()

