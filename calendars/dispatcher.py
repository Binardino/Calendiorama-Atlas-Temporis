
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

def get_calendars(region_id: str, jdn: int) -> list[CalendarDate]:
    """Return all CalendarDate objects applicable to a region for a given Julian Day Number."""
    names = _region_map.get(region_id, _region_map['default'])
    return [CONVERTERS[name]().from_jdn(jdn) for name in names]

# Priority score per calendar — higher = more culturally significant for a region.
# Used by get_primary_calendar() to pick one calendar when a region has several.
_CALENDAR_PRIORITY = {
    "persian": 6, "hebrew" : 5,
    "japanese": 4, "coptic": 3,
    "ethiopian": 3, "hijri": 2,
    "gregorian": 1,"julian": 1 }

def get_primary_calendar(region_id: str, jdn: int) -> tuple[str, CalendarDate]:
    """Return (internal_key, CalendarDate) for the most significant calendar of a region.

    The internal key (e.g. 'hijri', 'persian') is the same string used as a key
    in CONVERTERS and in the JS CALENDAR_COLORS dict. It is NOT the display name
    stored on CalendarDate.calendar_name (e.g. 'Islamic', 'Persian').
    Returning the key avoids a name-mapping step on the client side.
    """
    names = _region_map.get(region_id, _region_map['default'])
    primary_name = max(names, key=lambda name: _CALENDAR_PRIORITY.get(name, 0))
    return primary_name, CONVERTERS[primary_name]().from_jdn(jdn)