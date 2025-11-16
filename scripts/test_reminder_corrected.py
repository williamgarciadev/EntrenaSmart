# -*- coding: utf-8 -*-
"""
Test del sistema de recordatorios CORREGIDO
============================================

Prueba que los recordatorios se ejecuten correctamente con el event loop.
"""
import asyncio
import time
from datetime import datetime, timedelta
import sys
import threading

sys.path.insert(0, '.')

from src.models.base import init_db, get_db
from src.services.scheduler_service import SchedulerService
from src.services.training_service import TrainingService
from src.utils.logger import logger


# Mock de telegram Application para pruebas
class MockBot:
    class InnerBot:
        async def send_message(self, chat_id, text, parse_mode=None):
            logger.info(f"✅ [RECORDATORIO ENVIADO] chat_id={chat_id}")
            logger.info(f"📝 Contenido: {text[:50]}...")
            return True

    def __init__(self):
        self.bot = self.InnerBot()


async def run_test():
    """Función async para ejecutar el test con event loop activo."""
    print('\n' + '='*70)
    print('TEST DE RECORDATORIOS - VERSION CORREGIDA')
    print('='*70)
    print(f'Hora actual: {datetime.now().strftime("%H:%M:%S")}')

    # Inicializar BD
    init_db()
    db = next(get_db())

    # Crear scheduler con MockBot
    mock_bot = MockBot()
    scheduler = SchedulerService(db, bot=mock_bot)

    # Obtener event loop actual
    current_loop = asyncio.get_running_loop()
    print(f"Event loop activo: {current_loop}")

    scheduler.initialize_scheduler()

    # Iniciar scheduler
    print('\n🚀 Iniciando BackgroundScheduler...')
    scheduler.start()
    print(f"✅ Scheduler iniciado")
    print(f"✅ Event loop en scheduler: {scheduler.event_loop}")

    # Obtener Yolanda
    from src.models.student import Student
    yolanda = db.query(Student).filter_by(name='Yolanda').first()

    if not yolanda or not yolanda.chat_id:
        print('❌ ERROR: Yolanda no está disponible o no tiene chat_id')
        db.close()
        return

    # Programar para 3 segundos en el futuro
    now = datetime.now()
    test_time = now + timedelta(seconds=3)
    test_time_str = test_time.strftime("%H:%M")

    print(f'\n📅 Programando entrenamiento:')
    print(f'  ⏰ Hora actual: {now.strftime("%H:%M:%S")}')
    print(f'  🏋️ Entrenamiento: Hoy a las {test_time_str}')
    reminder_time = test_time - timedelta(minutes=5)
    print(f'  🔔 Recordatorio: {reminder_time.strftime("%H:%M:%S")} (5 min antes)')

    # Crear servicio de training
    training_service = TrainingService(db, scheduler)

    # Crear entrenamiento
    training = training_service.add_training(
        student_id=yolanda.id,
        weekday=now.weekday(),
        weekday_name=now.strftime('%A'),
        time_str=test_time_str,
        session_type="Test Correcto"
    )

    print(f'\n✅ Entrenamiento creado: ID={training.id}')

    # Mostrar jobs
    jobs = scheduler.get_scheduled_jobs()
    print(f'\n📋 Jobs programados: {len(jobs)}')
    for job in jobs:
        print(f'  - {job["id"]}: próxima_ejecución={job["next_run_time"]}')

    db.close()

    # Esperar a que se ejecute
    print(f'\n⏳ Esperando ejecución del recordatorio...')
    wait_time = max(1, (test_time - now).total_seconds() + 60)

    for i in range(int(wait_time)):
        remaining = int(wait_time) - i
        print(f'   [{remaining}s restantes]', end='\r')
        await asyncio.sleep(1)

    print(f'\n✅ Test completado. Revisa los logs arriba para "✅ [RECORDATORIO ENVIADO]"')
    print('='*70 + '\n')

    scheduler.stop()


if __name__ == '__main__':
    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        print('\n⚠️ Test interrumpido por el usuario')
    except Exception as e:
        logger.error(f'Error en test: {str(e)}', exc_info=True)
        raise
