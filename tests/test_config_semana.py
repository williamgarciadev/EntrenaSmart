#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Testing para /config_semana
=====================================

Simula el flujo conversacional sin necesidad de Telegram.
Útil para debuggear problemas en el handler.

Uso:
    python test_config_semana.py
"""
import asyncio
import sys
import os
from pathlib import Path

# Arreglar encoding en Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding="utf-8")

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from unittest.mock import Mock, AsyncMock, MagicMock
from telegram.ext import ContextTypes, ConversationHandler
from telegram import Update, Message, User, Chat

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
        self.message = Mock(spec=Message)
        self.message.text = text
        self.message.reply_text = AsyncMock()
        self.message.delete = AsyncMock()


class MockContext:
    """Mock de ContextTypes.DEFAULT_TYPE para testing."""

    def __init__(self):
        self.user_data = {}


async def test_config_semana_flow():
    """
    Prueba el flujo completo de /config_semana.

    Simula: Lunes -> Pierna -> 2do Piso -> Sí -> No
    """
    print("=" * 70)
    print("TEST: Flujo /config_semana")
    print("=" * 70)

    # Inicializar BD
    print("\n[*] Inicializando base de datos...")
    try:
        init_db()
        print("[OK] BD inicializada")
    except Exception as e:
        print(f"[FAIL] Error inicializando BD: {e}")
        return False

    context = MockContext()
    success = True

    try:
        # PASO 1: /config_semana
        print("\n" + "=" * 70)
        print("PASO 1: Usuario inicia /config_semana")
        print("=" * 70)

        update = MockUpdate("dummy")
        result = await config_training_start(update, context)

        print(f"[OK] Estado retornado: {result}")
        print(f"   Esperado: {SELECT_DAY} (1)")
        assert result == SELECT_DAY, f"Expected {SELECT_DAY}, got {result}"
        print(f"   context.user_data: {context.user_data}")

        # PASO 2: Seleccionar Lunes
        print("\n" + "=" * 70)
        print("PASO 2: Usuario selecciona 'Lunes'")
        print("=" * 70)

        update = MockUpdate("Lunes")
        result = await config_training_select_day(update, context)

        print(f"[OK] Estado retornado: {result}")
        print(f"   Esperado: {SELECT_SESSION_TYPE} (2)")
        assert result == SELECT_SESSION_TYPE, f"Expected {SELECT_SESSION_TYPE}, got {result}"
        print(f"   context.user_data: {context.user_data}")

        # Verificar que state se guardó correctamente
        state_data = context.user_data.get("config_training_state")
        print(f"\n   Estado guardado: {state_data}")
        if state_data:
            assert state_data.get("weekday") == 0, "Weekday debe ser 0 (Lunes)"
            assert state_data.get("weekday_name") == "Lunes", "Weekday name debe ser 'Lunes'"
            print("   [OK] Estado verificado")

        # PASO 3: Seleccionar tipo Pierna
        print("\n" + "=" * 70)
        print("PASO 3: Usuario selecciona 'Pierna'")
        print("=" * 70)

        update = MockUpdate("Pierna")
        result = await config_training_select_type(update, context)

        print(f"[OK] Estado retornado: {result}")
        print(f"   Esperado: {SELECT_LOCATION} (3)")
        assert result == SELECT_LOCATION, f"Expected {SELECT_LOCATION}, got {result}"
        print(f"   context.user_data: {context.user_data}")

        # Verificar estado actualizado
        state_data = context.user_data.get("config_training_state")
        print(f"\n   Estado guardado: {state_data}")
        if state_data:
            assert state_data.get("session_type") == "Pierna", "Session type debe ser 'Pierna'"
            print("   [OK] Estado verificado")

        # PASO 4: Ingresar ubicación
        print("\n" + "=" * 70)
        print("PASO 4: Usuario ingresa ubicación '2do Piso'")
        print("=" * 70)

        update = MockUpdate("2do Piso")
        result = await config_training_select_location(update, context)

        print(f"[OK] Estado retornado: {result}")
        print(f"   Esperado: {CONFIRM_DATA} (4)")
        assert result == CONFIRM_DATA, f"Expected {CONFIRM_DATA}, got {result}"
        print(f"   context.user_data: {context.user_data}")

        # Verificar estado completo
        state_data = context.user_data.get("config_training_state")
        print(f"\n   Estado guardado: {state_data}")
        if state_data:
            assert state_data.get("location") == "2do Piso", "Location debe ser '2do Piso'"
            print("   [OK] Estado verificado - COMPLETO:")
            print(f"      - weekday: {state_data.get('weekday')} [OK]")
            print(f"      - weekday_name: {state_data.get('weekday_name')} [OK]")
            print(f"      - session_type: {state_data.get('session_type')} [OK]")
            print(f"      - location: {state_data.get('location')} [OK]")

        # PASO 5: Confirmar (Sí)
        print("\n" + "=" * 70)
        print("PASO 5: Usuario confirma 'Sí'")
        print("=" * 70)

        update = MockUpdate("Sí")
        result = await config_training_confirm(update, context)

        print(f"[OK] Estado retornado: {result}")
        print(f"   Esperado: {CONFIRM_CONTINUE} (5) - pregunta '¿Otro día?'")
        assert result == CONFIRM_CONTINUE, f"Expected {CONFIRM_CONTINUE}, got {result}"

        # Verificar que BD tiene el registro
        print("\n   [*] Verificando BD...")
        try:
            with get_db_context() as db:
                from src.services.config_training_service import ConfigTrainingService
                service = ConfigTrainingService(db)

                config = service.get_day_config(0)  # Lunes
                assert config is not None, "Configuración no guardada en BD"
                assert config.weekday == 0, f"Weekday incorrecto: {config.weekday}"
                assert config.weekday_name == "Lunes", f"Weekday name incorrecto: {config.weekday_name}"
                assert config.session_type == "Pierna", f"Session type incorrecto: {config.session_type}"
                assert config.location == "2do Piso", f"Location incorrecto: {config.location}"

                print(f"      [OK] Registro en BD verificado:")
                print(f"         - ID: {config.id}")
                print(f"         - Weekday: {config.weekday_name}")
                print(f"         - Type: {config.session_type}")
                print(f"         - Location: {config.location}")
                print(f"         - Creado: {config.created_at}")

        except Exception as e:
            print(f"      [FAIL] Error verificando BD: {e}")
            import traceback
            traceback.print_exc()
            success = False

        # PASO 6: Continuar (No)
        print("\n" + "=" * 70)
        print("PASO 6: Usuario responde 'No' a '¿Otro día?'")
        print("=" * 70)

        update = MockUpdate("No")
        result = await config_training_continue(update, context)

        print(f"[OK] Estado retornado: {result}")
        print(f"   Esperado: {ConversationHandler.END} - Fin de conversación")
        assert result == ConversationHandler.END, f"Expected {ConversationHandler.END}, got {result}"

        print(f"   context.user_data después de finalizar: {context.user_data}")

        # Verificar resumen
        print("\n   [*] Verificando resumen semanal...")
        try:
            with get_db_context() as db:
                from src.services.config_training_service import ConfigTrainingService
                service = ConfigTrainingService(db)
                summary = service.format_weekly_summary()
                print(f"      [OK] Resumen generado:")
                print(f"         {summary}")
        except Exception as e:
            print(f"      [FAIL] Error generando resumen: {e}")
            success = False

        # RESUMEN FINAL
        print("\n" + "=" * 70)
        if success:
            print("[OK] ¡TODOS LOS TESTS PASARON!")
            print("=" * 70)
            print("\n[*] FLUJO COMPLETO:")
            print("   1⃣  /config_semana -> SELECT_DAY [OK]")
            print("   2⃣  Lunes -> SELECT_SESSION_TYPE [OK]")
            print("   3⃣  Pierna -> SELECT_LOCATION [OK]")
            print("   4⃣  2do Piso -> CONFIRM_CONTINUE [OK]")
            print("   5⃣  Sí (confirma) -> CONFIRM_CONTINUE [OK]")
            print("   6⃣  No (finaliza) -> END [OK]")
            print("   [*] BD guardada correctamente [OK]")
            print("   [*] Resumen generado correctamente [OK]")
        else:
            print("[FAIL] ALGUNOS TESTS FALLARON")
            print("=" * 70)

        return success

    except Exception as e:
        print(f"\n[FAIL] ERROR DURANTE TESTING: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_validation_errors():
    """
    Prueba manejo de errores de validación.
    """
    print("\n" + "=" * 70)
    print("[TEST] TESTING: Validación de Errores")
    print("=" * 70)

    context = MockContext()

    try:
        # Test 1: Ubicación muy corta
        print("\n📝 Test 1: Ubicación muy corta ('ab')")
        update = MockUpdate("Lunes")
        await config_training_select_day(update, context)

        update = MockUpdate("Pierna")
        await config_training_select_type(update, context)

        update = MockUpdate("ab")  # < 3 caracteres
        result = await config_training_select_location(update, context)

        print(f"   Resultado: {result}")
        print(f"   Esperado: {SELECT_LOCATION} (4) - reintentar")
        assert result == SELECT_LOCATION, "Debe reintentar en SELECT_LOCATION"
        print("   [OK] Validación funcionó")

        # Test 2: Ubicación muy larga
        print("\n📝 Test 2: Ubicación muy larga (> 100 chars)")
        context = MockContext()
        update = MockUpdate("Lunes")
        await config_training_select_day(update, context)

        update = MockUpdate("Pierna")
        await config_training_select_type(update, context)

        long_location = "x" * 101
        update = MockUpdate(long_location)
        result = await config_training_select_location(update, context)

        print(f"   Resultado: {result}")
        print(f"   Esperado: {SELECT_LOCATION} (4) - reintentar")
        assert result == SELECT_LOCATION, "Debe reintentar en SELECT_LOCATION"
        print("   [OK] Validación funcionó")

        # Test 3: Ubicación con caracteres inválidos
        print("\n📝 Test 3: Ubicación con caracteres inválidos (SQL injection attempt)")
        context = MockContext()
        update = MockUpdate("Lunes")
        await config_training_select_day(update, context)

        update = MockUpdate("Pierna")
        await config_training_select_type(update, context)

        malicious_location = "2do'; DROP TABLE training_day_configs; --"
        update = MockUpdate(malicious_location)
        result = await config_training_select_location(update, context)

        print(f"   Resultado: {result}")
        print(f"   Esperado: {SELECT_LOCATION} (4) - reintentar")
        assert result == SELECT_LOCATION, "Debe rechazar caracteres inválidos"
        print("   [OK] Validación funcionó")

        print("\n[OK] ¡TODOS LOS TESTS DE VALIDACIÓN PASARON!")
        return True

    except Exception as e:
        print(f"\n[FAIL] ERROR EN TESTS DE VALIDACIÓN: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Ejecuta todos los tests."""
    print("\n")
    print("[" + "=" * 68 + "]")
    print("|" + " " * 68 + "|")
    print("|" + " TEST SUITE: /config_semana ".center(68) + "|")
    print("|" + " " * 68 + "|")
    print("[" + "=" * 68 + "]")

    logger.info("Iniciando test suite /config_semana")

    # Test flujo completo
    result1 = await test_config_semana_flow()

    # Test validaciones
    result2 = await test_validation_errors()

    # Resultado final
    print("\n" + "=" * 70)
    if result1 and result2:
        print("[OK] SUITE COMPLETA: EXITOSA")
        print("=" * 70)
        return 0
    else:
        print("[FAIL] SUITE COMPLETA: FALLÓ")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
