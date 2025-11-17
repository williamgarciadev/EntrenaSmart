# -*- coding: utf-8 -*-
"""
Parser para Configuración Semanal de Entrenamientos
===================================================

Parsea respuestas como:
- "Lunes, Miércoles y Viernes 5:00 AM"
- "Martes y Jueves 6:30 PM"
- "Lunes 5am, Miercoles 6pm, Viernes 5am"
"""
import re
from typing import List, Dict, Optional
from datetime import datetime
from backend.src.utils.logger import logger


class WeeklyScheduleParser:
    """
    Parser para interpretar programación semanal de entrenamientos.
    """

    # Mapeo de días en español (con variaciones comunes)
    DAY_MAPPING = {
        "lunes": 0, "lun": 0,
        "martes": 1, "mar": 1,
        "miércoles": 2, "miercoles": 2, "mier": 2, "mie": 2,
        "jueves": 3, "jue": 3,
        "viernes": 4, "vier": 4, "vie": 4,
        "sábado": 5, "sabado": 5, "sab": 5,
        "domingo": 6, "dom": 6
    }

    @classmethod
    def parse(cls, text: str) -> Optional[List[Dict[str, any]]]:
        """
        Parsea texto libre y extrae días y horas.

        Soporta dos formatos:
        1. Un horario para varios días: "Lunes, Miércoles y Viernes 5:00 AM"
        2. Horarios diferentes por día: "Lunes 5am, Miércoles 6pm, Viernes 5am"

        Args:
            text: Texto del usuario

        Returns:
            Lista de dicts con 'day' (int) y 'time' (str) o None si no se pudo parsear

        Examples:
            >>> WeeklyScheduleParser.parse("Lunes, Miércoles y Viernes 5:00 AM")
            [{'day': 0, 'time': '05:00'}, {'day': 2, 'time': '05:00'}, {'day': 4, 'time': '05:00'}]

            >>> WeeklyScheduleParser.parse("Lunes 5am, Miércoles 6pm")
            [{'day': 0, 'time': '05:00'}, {'day': 2, 'time': '18:00'}]
        """
        text = text.lower().strip()
        logger.info(f"🔍 [PARSER] Parseando: '{text}'")

        # Detectar si tiene múltiples horarios (formato: "día hora, día hora")
        # Buscar patrones como "lunes 5am, miércoles 6pm"
        segments = re.split(r',\s*(?=\w+\s+\d)', text)

        if len(segments) > 1:
            # Formato con diferentes horarios por día
            logger.info(f"📋 [PARSER] Detectados {len(segments)} segmentos con horarios individuales")
            return cls._parse_multiple_times(segments)
        else:
            # Formato con un solo horario para todos los días
            logger.info(f"📋 [PARSER] Formato simple: un horario para todos los días")
            return cls._parse_single_time(text)

    @classmethod
    def _parse_single_time(cls, text: str) -> Optional[List[Dict[str, any]]]:
        """Parsea formato simple: un horario para varios días."""
        # Extraer hora
        time_str = cls._extract_time(text)
        if not time_str:
            return None

        # Extraer días
        days = []
        for day_name, day_num in cls.DAY_MAPPING.items():
            if day_name in text:
                if day_num not in days:
                    days.append(day_num)

        if not days:
            logger.warning(f"⚠️ [PARSER] No se encontraron días en: '{text}'")
            return None

        # Crear entrada para cada día con el mismo horario
        result = [{'day': day, 'time': time_str} for day in sorted(days)]
        logger.info(f"✅ [PARSER] Resultado: {result}")
        return result

    @classmethod
    def _parse_multiple_times(cls, segments: List[str]) -> Optional[List[Dict[str, any]]]:
        """Parsea formato complejo: diferentes horarios por día."""
        result = []

        for segment in segments:
            segment = segment.strip()
            logger.info(f"  🔍 [PARSER] Procesando segmento: '{segment}'")

            # Extraer hora del segmento
            time_str = cls._extract_time(segment)
            if not time_str:
                logger.warning(f"  ⚠️ [PARSER] No se encontró hora en segmento: '{segment}'")
                continue

            # Extraer día del segmento
            day_num = None
            for day_name, num in cls.DAY_MAPPING.items():
                if day_name in segment:
                    day_num = num
                    break

            if day_num is None:
                logger.warning(f"  ⚠️ [PARSER] No se encontró día en segmento: '{segment}'")
                continue

            result.append({'day': day_num, 'time': time_str})
            logger.info(f"  ✅ [PARSER] Segmento parseado: día={day_num}, hora={time_str}")

        if not result:
            logger.warning(f"⚠️ [PARSER] No se pudo parsear ningún segmento")
            return None

        logger.info(f"✅ [PARSER] Resultado final: {result}")
        return result

    @classmethod
    def _extract_time(cls, text: str) -> Optional[str]:
        """Extrae y normaliza hora de un texto."""
        time_match = re.search(
            r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?',
            text,
            re.IGNORECASE
        )

        if not time_match:
            return None

        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        meridiem = time_match.group(3).lower() if time_match.group(3) else None

        # Convertir a formato 24h
        if meridiem == 'pm' and hour != 12:
            hour += 12
        elif meridiem == 'am' and hour == 12:
            hour = 0

        # Validar hora
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            logger.warning(f"⚠️ [PARSER] Hora inválida: {hour}:{minute}")
            return None

        return f"{hour:02d}:{minute:02d}"

    @classmethod
    def format_days(cls, days: List[int]) -> str:
        """
        Formatea lista de días a texto legible.

        Args:
            days: Lista de números de día (0-6)

        Returns:
            Texto formateado (ej: "Lunes, Miércoles y Viernes")
        """
        day_names_spanish = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        names = [day_names_spanish[d] for d in days]

        if len(names) == 1:
            return names[0]
        elif len(names) == 2:
            return f"{names[0]} y {names[1]}"
        else:
            return ", ".join(names[:-1]) + f" y {names[-1]}"
