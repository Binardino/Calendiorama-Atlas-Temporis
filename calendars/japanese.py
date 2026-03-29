
from calendars.base import CalendarConverter, CalendarDate
from pathlib import Path
import json
import date

class JapaneseCalendar(CalendarConverter):
    def __init__(self):
        #loading Japanese calendar JSON mapper
        __file = 'data/calendars/japanese_eras.json'
        with open(Path(__file__), 'r') as f:
            jcalendar_json = json.load(f)

    def find_era(self, gregorian_date):
        japanese_date = jcalendar_json[gregorian_date]

        return japanese_date
    
    def from_jdn(self, jdn: int) -> CalendarDate:
        return CalendarDate(year=year,
                            month=month,
                            day=day,
                            calendar_name="Japanese",
                            formatted=f"{day} {self.MONTH_NAMES[month]} {year}"
        )
        
    def to_jdn(self, CalendarDate) -> int:
        return super().to_jdn(date)