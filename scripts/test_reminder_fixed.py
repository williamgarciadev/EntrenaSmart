# -*- coding: utf-8 -*-
"""
Test del sistema de recordatorios CON FUTURO REAL
==================================================

Programa un entrenamiento para 5 minutos en el futuro y verifica
que el recordatorio se ejecute.
"""
import asyncio
import time
from datetime import datetime, timedelta
import sys

sys.path.insert(0, '.')

from src.models.base import init_db, get_db
from src.services.scheduler_service import SchedulerService
from src.services.training_service import TrainingService
from src.utils.logger import logger

# Mock de telegram Application para pruebas
class MockBot:
    class InnerBot:
        async def send_message(self, chat_id, text, parse_mode=None):
            logger.info(f"[SUCCESS] Recordatorio enviado a {chat_id}")
            logger.info(f"[SUCCESS] Contenido: {text[:100]}...")
            return True

    def __init__(self):
        self.bot = self.InnerBot()

print('\n' + '='*70)
print('TEST DE RECORDATORIOS - VERSION CORREGIDA')
print('='*70)
print(f'Hora actual: {datetime.now().strftime("%H:%M:%S")}')

# Inicializar BD
init_db()
db = next(get_db())

# Crear scheduler
scheduler = SchedulerService(db, bot=MockBot())
scheduler.initialize_scheduler()

# Iniciar scheduler
print('\nIniciando BackgroundScheduler...')
scheduler.start()
print('Scheduler iniciado\n')

# Obtener Yolanda
from src.models.student import Student
yolanda = db.query(Student).filter_by(name='Yolanda').first()

if not yolanda or not yolanda.chat_id:
    print('ERROR: Yolanda no está disponible o no tiene chat_id')
    sys.exit(1)

# IMPORTANTE: Programar para 10 minutos en el FUTURO
# (5 min recordatorio + 5 min de margen)
now = datetime.now()
test_time = now + timedelta(minutes=10)
test_time_str = test_time.strftime("%H:%M")

print(f'Programando entrenamiento:')
print(f'  Hora actual: {now.strftime("%H:%M:%S")}')
print(f'  Entrenamiento: Hoy a las {test_time_str}')
print(f'  Recordatorio: {5} minutos antes = {(test_time - timedelta(minutes=5)).strftime("%H:%M:%S")}')

# Crear servicio de training
training_service = TrainingService(db, scheduler)

# Crear entrenamiento
training = training_service.add_training(
    student_id=yolanda.id,
    weekday=now.weekday(),
    weekday_name=now.strftime('%A'),
    time_str=test_time_str,
    session_type="Test Final"
)

print(f'\nEntrenamiento creado: ID={training.id}')

# Mostrar jobs
jobs = scheduler.get_scheduled_jobs()
print(f'\nJobs programados:')
for job in jobs:
    print(f'  - {job["id"]}: proxima_ejecucion={job["next_run_time"]}')

db.close()

# Esperar (con margen extra)
print(f'\nEsperando {int((test_time - now).total_seconds())} segundos para recordatorio...')
wait_time = (test_time - now).total_seconds() + 60  # 60 segundos de margen
time.sleep(wait_time)

print(f'\nTest completado. Revisa los logs arriba para [SUCCESS]')
print('='*70 + '\n')

scheduler.stop()
