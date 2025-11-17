# -*- coding: utf-8 -*-
"""
Configuracion Base de SQLAlchemy
==================================

Define la clase base para todos los modelos ORM y la configuracion
de la conexion a la base de datos.
"""
from typing import TypeVar, Generic
from datetime import datetime
from contextlib import contextmanager

from sqlalchemy import create_engine, func, DateTime
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.orm import Mapped, mapped_column

from src.core.config import settings
from src.utils.logger import logger


# ============================================================================
# Configuracion de SQLAlchemy
# ============================================================================

class Base(DeclarativeBase):
    """Clase base para todos los modelos SQLAlchemy."""

    # Columnas comunes a todos los modelos
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.current_timestamp(),
        nullable=False,
        comment="Fecha y hora de creacion del registro"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
        comment="Fecha y hora de ultima actualizacion"
    )


# ============================================================================
# Engine y Sesion
# ============================================================================

# Configurar argumentos de conexión según el tipo de base de datos
_connect_args = {}
_engine_kwargs = {
    "echo": settings.debug,  # Log SQL queries en modo debug
    "future": True,
}

# Solo SQLite necesita check_same_thread
if settings.is_sqlite:
    _connect_args["check_same_thread"] = False

# PostgreSQL necesita configuración de pool
if settings.is_postgres:
    _engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True,  # Verificar conexión antes de usar
        "pool_recycle": 3600,  # Reciclar conexiones cada hora
    })

if _connect_args:
    _engine_kwargs["connect_args"] = _connect_args

# Crear engine de SQLAlchemy
engine = create_engine(
    settings.get_database_url,
    **_engine_kwargs
)

# Crear SessionLocal factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False  # Evitar lazy loading despues de commit
)


# ============================================================================
# Funciones de Inicializacion
# ============================================================================

def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas.

    Esta funcion debe ser llamada una sola vez al inicio de la aplicacion
    para crear las tablas necesarias.

    Nota: La lógica de migración específica de SQLite se ejecuta solo en SQLite.
    PostgreSQL usa Alembic u otro sistema de migración para cambios de esquema.

    Ejemplo:
        >>> from src.models.base import init_db
        >>> init_db()  # Crea todas las tablas
    """
    try:
        logger.info(f"Inicializando base de datos ({settings.get_database_url})...")

        # Lógica de migración específica de SQLite
        if settings.is_sqlite:
            import os
            from sqlalchemy import text

            db_path = settings.get_database_url.replace("sqlite:///", "")
            if os.path.exists(db_path):
                # Verificar si la tabla estudiantes tiene el esquema antiguo
                try:
                    with engine.connect() as conn:
                        result = conn.execute(text("PRAGMA table_info(students)")).fetchall()
                        # result es lista de (cid, name, type, notnull, dflt_value, pk)
                        # Buscar columna chat_id
                        chat_id_info = [col for col in result if col[1] == "chat_id"]
                        if chat_id_info:
                            # col[3] es el flag notnull
                            if chat_id_info[0][3] == 1:  # notnull == True en esquema antiguo
                                logger.warning("Detectado esquema antiguo de base de datos, recreando...")
                                # Eliminar tablas antiguas (en orden inverso de dependencias)
                                conn.execute(text("DROP TABLE IF EXISTS feedbacks"))
                                conn.execute(text("DROP TABLE IF EXISTS trainings"))
                                conn.execute(text("DROP TABLE IF EXISTS students"))
                                conn.commit()
                                logger.info("Tablas antiguas eliminadas")
                except Exception as e:
                    logger.debug(f"Error verificando esquema: {e}")

                # Migrar columnas nuevas de trainings si es necesario
                try:
                    with engine.connect() as conn:
                        # Verificar si tabla trainings existe
                        result = conn.execute(text("PRAGMA table_info(trainings)")).fetchall()
                        if result:
                            columns = [col[1] for col in result]

                            # Agregar columna location si no existe
                            if "location" not in columns:
                                logger.info("Agregando columna 'location' a tabla trainings...")
                                conn.execute(text(
                                    "ALTER TABLE trainings ADD COLUMN location VARCHAR(255) NULL"
                                ))
                                logger.info("Columna 'location' agregada")

                            # Agregar columna training_day_config_id si no existe
                            if "training_day_config_id" not in columns:
                                logger.info("Agregando columna 'training_day_config_id' a tabla trainings...")
                                conn.execute(text(
                                    "ALTER TABLE trainings ADD COLUMN training_day_config_id INTEGER NULL"
                                ))
                                logger.info("Columna 'training_day_config_id' agregada")

                            conn.commit()
                except Exception as e:
                    logger.warning(f"Error migrando schema de trainings: {e}")

        # Crear todas las tablas definidas en los modelos
        Base.metadata.create_all(bind=engine)
        logger.info(f"Base de datos inicializada correctamente ({'SQLite' if settings.is_sqlite else 'PostgreSQL' if settings.is_postgres else 'MySQL'})")
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}", exc_info=True)
        raise


def get_db() -> Session:
    """
    Proporciona una sesion de base de datos.

    Esta funcion debe ser usada en un bloque try/finally para asegurar
    que la sesion se cierre correctamente.

    Returns:
        Session: Sesion de SQLAlchemy

    Ejemplo:
        >>> from src.models.base import get_db
        >>> db = get_db()
        >>> try:
        ...     # usar db...
        ... finally:
        ...     db.close()
    """
    return SessionLocal()


@contextmanager
def get_db_context():
    """
    Context manager para sesiones de base de datos.

    Maneja automáticamente commit/rollback y cierre de sesión.

    Yields:
        Session: Sesion de SQLAlchemy

    Ejemplo:
        >>> from src.models.base import get_db_context
        >>> with get_db_context() as db:
        ...     service = ConfigTrainingService(db)
        ...     service.configure_day(0, "Pierna", "2do Piso")
        ...     # Auto-commit al salir del bloque
        ...     # Si hay excepción, auto-rollback

    Comportamiento:
        - Commit automático si no hay excepciones
        - Rollback automático si ocurre una excepción
        - Cierre garantizado de la sesión
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
