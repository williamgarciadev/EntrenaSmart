# -*- coding: utf-8 -*-
"""
Debug detallado del scheduler
"""
import sys
from datetime import datetime, timedelta
import pytz

sys.path.insert(0, '.')

from src.models.base import init_db, get_db
from src.services.scheduler_service import SchedulerService
from src.utils.logger import logger

# Mock de telegram
class MockBot:
    class InnerBot:
        async def send_message(self, chat_id, text, parse_mode=None):
            logger.info(f"[MOCK] send_message({chat_id}, ...)")
            return True
    def __init__(self):
        self.bot = self.InnerBot()

print('\n' + '='*70)
print('DEBUG: Detalles del Scheduler')
print('='*70)

init_db()
db = next(get_db())

scheduler = SchedulerService(db, bot=MockBot())
scheduler.initialize_scheduler()
scheduler.start()

# Simular schedule_training_reminder
tz = pytz.timezone("America/Bogota")
now = datetime.now(tz)
print(f'Hora actual: {now}')
print(f'Weekday (0=lun, 5=sab): {now.weekday()}')

weekday = now.weekday()  # Hoy
training_time = (now + timedelta(minutes=3)).strftime("%H:%M")
print(f'Entrenamiento programado para HOY a las {training_time}')

# Calcular hora de recordatorio (3 minutos menos que training_time)
parts = training_time.split(':')
hour = int(parts[0])
minute = int(parts[1])
time_obj = datetime(2000, 1, 1, hour, minute)
reminder_time = time_obj - timedelta(minutes=5)
reminder_hour = reminder_time.hour
reminder_minute = reminder_time.minute

print(f'Hora del recordatorio: {reminder_hour:02d}:{reminder_minute:02d}')

weekday_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
trigger_day = weekday_names[weekday]
print(f'Dia (nombre): {trigger_day}')

# Verificar la lógica de trigger
today_weekday = now.weekday()
print(f'\nComparación: today_weekday ({today_weekday}) == weekday ({weekday})? {today_weekday == weekday}')

if today_weekday == weekday:
    reminder_datetime = now.replace(
        hour=reminder_hour,
        minute=reminder_minute,
        second=0,
        microsecond=0
    )
    print(f'Reminder datetime calculado: {reminder_datetime}')
    print(f'Comparación: reminder_datetime > now? {reminder_datetime > now}')

    if reminder_datetime > now:
        print('-> DateTrigger debería agregarse para HOY')
    else:
        print('-> DateTrigger NO se agregará (hora ya pasó)')
else:
    print('-> Hoy no es el día, no se agregará DateTrigger')

db.close()
scheduler.stop()

print('\n' + '='*70 + '\n')
