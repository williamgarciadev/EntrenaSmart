# -*- coding: utf-8 -*-
"""
Script de prueba para el sistema de recordatorios
==================================================

Crea un entrenamiento de prueba y verifica que el recordatorio se programa y ejecuta.
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
            logger.info(f"[MOCK] Mensaje enviado a {chat_id}: {text[:50]}...")
            return True

    def __init__(self):
        self.bot = self.InnerBot()

print('\n' + '='*70)
print('TEST DEL SISTEMA DE RECORDATORIOS')
print('='*70)
print(f'Hora actual: {datetime.now().strftime("%H:%M:%S")}')

# Inicializar BD
init_db()
db = next(get_db())

# Crear scheduler
scheduler = SchedulerService(db, bot=MockBot())
scheduler.initialize_scheduler()

# Iniciar scheduler para que ejecute jobs
print('\nIniciando scheduler...')
scheduler.start()
print('Scheduler iniciado\n')

# Crear un entrenamiento de prueba para Yolanda en 3 minutos
from src.models.student import Student
yolanda = db.query(Student).filter_by(name='Yolanda').first()

if not yolanda:
    print('ERROR: No se encontró a Yolanda en BD')
    sys.exit(1)

if not yolanda.chat_id:
    print('ERROR: Yolanda no tiene chat_id configurado')
    sys.exit(1)

# Calcular hora de prueba (ahora + 2 minutos)
now = datetime.now()
test_time = now + timedelta(minutes=2)
test_time_str = test_time.strftime("%H:%M")

print(f'Creando entrenamiento de prueba para Yolanda...')
print(f'  Horario: Hoy a las {test_time_str}')
print(f'  Chat ID: {yolanda.chat_id}')

# Crear servicio de training
training_service = TrainingService(db, scheduler)

# Crear entrenamiento
training = training_service.add_training(
    student_id=yolanda.id,
    weekday=now.weekday(),  # Hoy
    weekday_name=now.strftime('%A'),  # Nombre del día actual
    time_str=test_time_str,
    session_type="Test Recordatorio"
)

print(f'Entrenamiento creado: ID={training.id}')

# Verificar jobs programados
print('\nJobs programados en APScheduler:')
jobs = scheduler.get_scheduled_jobs()
print(f'  Total jobs: {len(jobs)}')
for job in jobs:
    print(f'    - {job["id"]}: proxima ejecucion={job["next_run_time"]}')

# Esperar a que se ejecute
print(f'\nEsperando recordatorio (aproximadamente {int((test_time - now).total_seconds() / 60)} minutos)...')
db.close()

# Dar tiempo para que ejecute (un poco más del tiempo especificado + margen)
sleep_time = (test_time - now).total_seconds() + 30  # 30 segundos de margen

print(f'Durmiendo {int(sleep_time)} segundos...')
time.sleep(sleep_time)

print(f'\nHora actual: {datetime.now().strftime("%H:%M:%S")}')
print('Si viste [MOCK] Mensaje enviado arriba, el recordatorio funcionó correctamente!')
print('\n' + '='*70 + '\n')

scheduler.stop()
