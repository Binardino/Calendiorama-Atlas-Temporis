
from calendars import *
import json
from pathlib import Path
from calendars.base import CalendarDate

CONVERTERS = {
    "gregorian":  GregorianCalendar,
    "julian":     JulianCalendar,
    "coptic":     CopticCalendar,
    "ethiopian":  EthiopianCalendar,
    "hijri":      HijriCalendar,
    "hebrew":     HebrewCalendar,
    "persian":    PersianCalendar,
    "japanese":   JapaneseCalendar,
}

_DATA_DIR   = Path(__file__).parent.parent / 'data' / 'calendars'
_region_map = json.loads((_DATA_DIR / 'region_calendar_map.json').read_text())

def get_calendars(region_id:str, jdn:int) -> list[CalendarDate]:
    names = _region_map.get(region_id, _region_map['default'])

    return [CONVERTERS[name]().from_jdn(jdn) for name in names]