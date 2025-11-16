#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Testing para /config_semana - PERSISTENCE
====================================================

Simula múltiples flujos conversacionales con persistencia en BD.
Verifica que los datos se guardan y persisten correctamente.

Casos de prueba:
  1. Configurar múltiples días de la semana
  2. Actualizar configuración existente
  3. Verificar integridad de datos
  4. Testing concurrencia (múltiples usuarios)
  5. Testing de rollback en caso de error

Uso:
    python test_config_semana_persistence.py
"""
import asyncio
import sys
import os
from pathlib import Path

# Arreglar encoding en Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))

from unittest.mock import Mock, AsyncMock
from telegram.ext import ConversationHandler

from src.models.base import init_db, get_db_context
from src.handlers.config_training_handler import (
    config_training_start,
    config_training_select_day,
    config_training_select_type,
    config_training_select_location,
    config_training_confirm,
    config_training_continue,
    SELECT_DAY,
    SELECT_SESSION_TYPE,
    SELECT_LOCATION,
    CONFIRM_DATA,
    CONFIRM_CONTINUE
)
from src.utils.logger import logger


class MockUpdate:
    """Mock de telegram.Update para testing."""

    def __init__(self, text: str):
        self.message = Mock()
        self.message.text = text
        self.message.reply_text = AsyncMock()


class MockContext:
    """Mock de ContextTypes.DEFAULT_TYPE para testing."""

    def __init__(self):
        self.user_data = {}


# Configuraciones de prueba (día, tipo, ubicación)
TEST_CONFIGS = [
    ("Lunes", "Pierna", "2do Piso"),
    ("Miércoles", "Funcional", "4to Piso"),
    ("Viernes", "Espalda", "2do Piso - Zona Espalda"),
    ("Sábado", "Pecho", "3er Piso"),
]


async def simulate_config_flow(context: MockContext, day: str, session_type: str, location: str) -> bool:
    """
    Simula un flujo completo de configuracion.

    Returns: True si fue exitoso, False si falló
    """
    try:
        # Inicio
        update = MockUpdate("dummy")
        result = await config_training_start(update, context)
        assert result == SELECT_DAY, f"Expected SELECT_DAY, got {result}"

        # Seleccionar día
        update = MockUpdate(day)
        result = await config_training_select_day(update, context)
        assert result == SELECT_SESSION_TYPE, f"Expected SELECT_SESSION_TYPE, got {result}"

        # Seleccionar tipo
        update = MockUpdate(session_type)
        result = await config_training_select_type(update, context)
        assert result == SELECT_LOCATION, f"Expected SELECT_LOCATION, got {result}"

        # Ingresar ubicación
        update = MockUpdate(location)
        result = await config_training_select_location(update, context)
        assert result == CONFIRM_DATA, f"Expected CONFIRM_DATA, got {result}"

        # Confirmar
        update = MockUpdate("Sí")
        result = await config_training_confirm(update, context)
        assert result == CONFIRM_CONTINUE, f"Expected CONFIRM_CONTINUE after confirm, got {result}"

        return True

    except Exception as e:
        logger.error(f"Error en flujo: {e}", exc_info=True)
        return False


async def test_persistence_multiple_configs():
    """
    Prueba 1: Persiste múltiples configuraciones
    """
    print("=" * 70)
    print("PRUEBA 1: Persistencia de Múltiples Configuraciones")
    print("=" * 70)

    # Inicializar BD
    print("\n[*] Inicializando base de datos...")
    try:
        init_db()
        print("[OK] BD inicializada")
    except Exception as e:
        print(f"[FAIL] Error inicializando BD: {e}")
        return False

    try:
        # Configurar todos los días
        for day, session_type, location in TEST_CONFIGS:
            print(f"\n[*] Configurando {day}: {session_type} ({location})")
            context = MockContext()

            success = await simulate_config_flow(context, day, session_type, location)
            if not success:
                print(f"[FAIL] Falló configuración de {day}")
                return False

            print(f"[OK] {day} guardado correctamente")

        # Verificar todos los registros en BD
        print("\n[*] Verificando persistencia en BD...")
        with get_db_context() as db:
            from src.services.config_training_service import ConfigTrainingService
            service = ConfigTrainingService(db)

            for day, session_type, location in TEST_CONFIGS:
                # Obtener por día
                from src.handlers.config_training_handler import DAYS_SPANISH
                weekday = DAYS_SPANISH[day]
                config = service.get_day_config(weekday)

                assert config is not None, f"Config no encontrada para {day}"
                assert config.session_type == session_type, f"Type incorrecto para {day}"
                assert config.location == location, f"Location incorrecto para {day}"

                print(f"   [OK] {day}: {config.session_type} ({config.location})")

        # Verificar resumen completo
        print("\n[*] Resumen final:")
        with get_db_context() as db:
            service = ConfigTrainingService(db)
            summary = service.format_weekly_summary()
            print(f"   {summary.replace(chr(10), chr(10) + '   ')}")

        print("\n[OK] PRUEBA 1 EXITOSA")
        return True

    except Exception as e:
        print(f"\n[FAIL] Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_update_existing_config():
    """
    Prueba 2: Actualizar configuración existente
    """
    print("\n" + "=" * 70)
    print("PRUEBA 2: Actualizar Configuración Existente")
    print("=" * 70)

    try:
        # Primer flujo: Lunes - Pierna - 2do Piso
        print("\n[*] Configuración inicial: Lunes - Pierna - 2do Piso")
        context = MockContext()
        success = await simulate_config_flow(context, "Lunes", "Pierna", "2do Piso")
        assert success, "Primera configuración falló"
        print("[OK] Guardado")

        # Verificar primer registro
        with get_db_context() as db:
            from src.services.config_training_service import ConfigTrainingService
            service = ConfigTrainingService(db)
            config1 = service.get_day_config(0)  # Lunes
            assert config1.session_type == "Pierna"
            print(f"   [OK] BD: {config1.session_type} ({config1.location})")

        # Segundo flujo: Lunes - Funcional - 4to Piso (actualiza)
        print("\n[*] Actualización: Lunes - Funcional - 4to Piso")
        context = MockContext()
        success = await simulate_config_flow(context, "Lunes", "Funcional", "4to Piso")
        assert success, "Actualización falló"
        print("[OK] Guardado")

        # Verificar segundo registro (debe reemplazar el primero)
        with get_db_context() as db:
            from src.services.config_training_service import ConfigTrainingService
            service = ConfigTrainingService(db)
            config2 = service.get_day_config(0)  # Lunes

            assert config2.session_type == "Funcional", "No se actualizó el tipo"
            assert config2.location == "4to Piso", "No se actualizó la ubicación"
            assert config2.id == config1.id, "Se creó nuevo registro en lugar de actualizar"

            print(f"   [OK] BD actualizada: {config2.session_type} ({config2.location})")
            print(f"   [OK] ID permanece igual: {config2.id}")

        print("\n[OK] PRUEBA 2 EXITOSA")
        return True

    except Exception as e:
        print(f"\n[FAIL] Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_data_integrity():
    """
    Prueba 3: Integridad de datos (todos los campos correctos)
    """
    print("\n" + "=" * 70)
    print("PRUEBA 3: Integridad de Datos")
    print("=" * 70)

    try:
        print("\n[*] Configurando: Miércoles - Brazo - Zona Brazo")
        context = MockContext()
        success = await simulate_config_flow(context, "Miércoles", "Brazo", "Zona Brazo")
        assert success, "Configuración falló"

        # Verificar todos los campos
        with get_db_context() as db:
            from src.services.config_training_service import ConfigTrainingService
            service = ConfigTrainingService(db)
            config = service.get_day_config(2)  # Miércoles

            print("\n[*] Verificando integridad de campos:")

            checks = [
                ("ID", config.id is not None, f"ID: {config.id}"),
                ("Weekday", config.weekday == 2, f"Weekday: {config.weekday}"),
                ("Weekday Name", config.weekday_name == "Miércoles", f"Name: {config.weekday_name}"),
                ("Session Type", config.session_type == "Brazo", f"Type: {config.session_type}"),
                ("Location", config.location == "Zona Brazo", f"Location: {config.location}"),
                ("Is Active", config.is_active == True, f"Active: {config.is_active}"),
                ("Created At", config.created_at is not None, f"Created: {config.created_at}"),
                ("Updated At", config.updated_at is not None, f"Updated: {config.updated_at}"),
            ]

            all_pass = True
            for field, check, value in checks:
                status = "[OK]" if check else "[FAIL]"
                print(f"   {status} {field}: {value}")
                if not check:
                    all_pass = False

            assert all_pass, "Algunos campos fallaron la verificación"

        print("\n[OK] PRUEBA 3 EXITOSA")
        return True

    except Exception as e:
        print(f"\n[FAIL] Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_weekly_summary():
    """
    Prueba 4: Resumen semanal completo
    """
    print("\n" + "=" * 70)
    print("PRUEBA 4: Resumen Semanal Completo")
    print("=" * 70)

    try:
        print("\n[*] Obteniendo resumen semanal...")

        with get_db_context() as db:
            from src.services.config_training_service import ConfigTrainingService
            service = ConfigTrainingService(db)

            schedule = service.get_weekly_schedule()
            all_configs = service.get_all_configs()
            summary = service.format_weekly_summary()

            print(f"\n[OK] Configuraciones encontradas: {len(all_configs)}")
            print(f"[OK] Días configurados: {len(schedule)}")

            print("\n[*] Horario semanal:")
            for day, config in schedule.items():
                print(f"   {day}: {config['session_type']} ({config['location']})")

            print("\n[*] Resumen formateado:")
            for line in summary.split('\n'):
                print(f"   {line}")

            assert len(all_configs) > 0, "Sin configuraciones en BD"
            assert len(schedule) > 0, "Sin días configurados"

        print("\n[OK] PRUEBA 4 EXITOSA")
        return True

    except Exception as e:
        print(f"\n[FAIL] Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_concurrent_configs():
    """
    Prueba 5: Simulación de usuarios concurrentes
    """
    print("\n" + "=" * 70)
    print("PRUEBA 5: Concurrencia (Múltiples Usuarios)")
    print("=" * 70)

    try:
        # Simular 3 usuarios configurando diferentes días simultáneamente
        print("\n[*] Configurando múltiples usuarios en paralelo...")

        configs = [
            ("Lunes", "Pierna", "2do Piso"),
            ("Jueves", "Espalda", "3er Piso"),
            ("Domingo", "Hombros", "Zona Hombros"),
        ]

        # Crear tareas concurrentes
        tasks = []
        for day, session_type, location in configs:
            context = MockContext()
            task = simulate_config_flow(context, day, session_type, location)
            tasks.append(task)

        # Ejecutar todas en paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verificar resultados
        for i, (result, (day, _, _)) in enumerate(zip(results, configs)):
            if isinstance(result, Exception):
                print(f"   [FAIL] {day}: {result}")
                return False
            elif result:
                print(f"   [OK] {day} configurado correctamente")
            else:
                print(f"   [FAIL] {day} falló")
                return False

        # Verificar que todos se guardaron
        print("\n[*] Verificando integridad después de concurrencia...")
        with get_db_context() as db:
            from src.services.config_training_service import ConfigTrainingService
            service = ConfigTrainingService(db)

            from src.handlers.config_training_handler import DAYS_SPANISH
            for day, session_type, location in configs:
                weekday = DAYS_SPANISH[day]
                config = service.get_day_config(weekday)

                if config is None:
                    print(f"   [FAIL] {day} no se guardó")
                    return False

                assert config.session_type == session_type
                assert config.location == location
                print(f"   [OK] {day}: {config.session_type} ({config.location})")

        print("\n[OK] PRUEBA 5 EXITOSA")
        return True

    except Exception as e:
        print(f"\n[FAIL] Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_recovery_rollback():
    """
    Prueba 6: Recuperación y Rollback en Caso de Error
    """
    print("\n" + "=" * 70)
    print("PRUEBA 6: Recuperación y Rollback")
    print("=" * 70)

    try:
        print("\n[*] Prueba de rollback automático...")

        # Contar registros iniciales
        with get_db_context() as db:
            from src.services.config_training_service import ConfigTrainingService
            service = ConfigTrainingService(db)
            initial_count = len(service.get_all_configs())
            print(f"   [OK] Registros iniciales: {initial_count}")

        # Simular error durante transacción (mediante excepción manual)
        print("\n[*] Simulando error durante guardado...")
        try:
            with get_db_context() as db:
                from src.services.config_training_service import ConfigTrainingService
                service = ConfigTrainingService(db)

                # Intentar operación que causará error
                service.configure_day(weekday=-1, session_type="Test", location="Test")

                print("[FAIL] Debería haber lanzado error")
                return False
        except Exception as e:
            print(f"   [OK] Error detectado y manejado: {type(e).__name__}")

        # Verificar que no se guardó nada (rollback automático)
        print("\n[*] Verificando rollback automático...")
        with get_db_context() as db:
            from src.services.config_training_service import ConfigTrainingService
            service = ConfigTrainingService(db)
            final_count = len(service.get_all_configs())

            assert final_count == initial_count, "Registro se guardó a pesar del error"
            print(f"   [OK] Registros después del error: {final_count}")
            print(f"   [OK] Rollback automático funcionó correctamente")

        print("\n[OK] PRUEBA 6 EXITOSA")
        return True

    except Exception as e:
        print(f"\n[FAIL] Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Ejecuta todas las pruebas de persistencia."""
    print("\n")
    print("[" + "=" * 68 + "]")
    print("|" + " " * 68 + "|")
    print("|" + " TEST PERSISTENCE: /config_semana ".center(68) + "|")
    print("|" + " " * 68 + "|")
    print("[" + "=" * 68 + "]")

    logger.info("Iniciando test suite persistencia /config_semana")

    results = []

    # Prueba 1: Múltiples configuraciones
    result1 = await test_persistence_multiple_configs()
    results.append(("Persistencia Múltiple", result1))

    # Prueba 2: Actualizar existente
    result2 = await test_update_existing_config()
    results.append(("Actualizar Existente", result2))

    # Prueba 3: Integridad de datos
    result3 = await test_data_integrity()
    results.append(("Integridad de Datos", result3))

    # Prueba 4: Resumen semanal
    result4 = await test_weekly_summary()
    results.append(("Resumen Semanal", result4))

    # Prueba 5: Concurrencia
    result5 = await test_concurrent_configs()
    results.append(("Concurrencia", result5))

    # Prueba 6: Rollback
    result6 = await test_recovery_rollback()
    results.append(("Rollback", result6))

    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {name}")

    print("\n" + "=" * 70)
    if passed == total:
        print(f"[OK] SUITE COMPLETA: EXITOSA ({passed}/{total} pruebas)")
        print("=" * 70)
        return 0
    else:
        print(f"[FAIL] SUITE COMPLETA: FALLÓ ({passed}/{total} pruebas)")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
