# -*- coding: utf-8 -*-
"""
Script de debug del sistema de recordatorios
"""
import sys
from datetime import datetime
import pytz

sys.path.insert(0, '.')

from src.core.config import settings

print('\nDEBUG: Comparacion de timezones y weekdays')
print('='*70)

now_local = datetime.now()
print(f'datetime.now() (local): {now_local}')
print(f'  weekday: {now_local.weekday()} (0=lunes, 5=sabado)')

tz_bogota = pytz.timezone('America/Bogota')
now_tz = datetime.now(tz_bogota)
print(f'\ndatetime.now(America/Bogota): {now_tz}')
print(f'  weekday: {now_tz.weekday()} (0=lunes, 5=sabado)')

print(f'\nTimezone en settings: {settings.timezone}')
print(f'Reminder minutes before: {settings.reminder_minutes_before}')

# Verificar si hoy es sábado
today_is_saturday = now_tz.weekday() == 5
print(f'\n¿Hoy es sábado? {today_is_saturday}')

print('\n' + '='*70 + '\n')
