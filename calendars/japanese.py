
from calendars.base import CalendarConverter, CalendarDate
from pathlib import Path
import json

class JapaneseCalendar(CalendarConverter):
    def __init__(self):
        era_file = Path('data/calendars/japanese_eras.json')
        with open(era_file, 'r') as f:
            raw = json.load(f)

        # Pre-process: convert ISO date strings to datetime.date objects once at init.
        # era["end"] stays None for the current open-ended era (Reiwa).
        self._eras = [
            {
                **era,
                "start": date.fromisoformat(era["start"]),
                "end":   date.fromisoformat(era["end"]) if era["end"] else None,
            }
            for era in raw['eras']
        ]

    def _find_era(self, greg_date: date) -> dict | None:
        # Check which Japanese era matches Input Gregorian date
         
        # Linear scan over 248 eras — fast enough for this use case.
        # Boundary convention: use <= for end so that the last day of an era
        # (e.g. 2019-04-30 for Heisei) is still matched, not lost in a gap.
        return next(
            (era for era in self._eras
             if greg_date >= era["start"] and (era["end"] is None or greg_date <= era["end"])),
            None,  # date before 645-07-17 or in an inter-era gap
        )

    def from_jdn(self, jdn: int) -> CalendarDate:
        return CalendarDate(year=year,
                            month=month,
                            day=day,
                            calendar_name="Japanese",
                            formatted=f"{day} {self.MONTH_NAMES[month]} {year}"
        )
        
    def to_jdn(self, CalendarDate) -> int:
        return super().to_jdn(date)