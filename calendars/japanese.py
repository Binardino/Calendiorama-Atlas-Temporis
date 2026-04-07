
from calendars.base import CalendarConverter, CalendarDate
from pathlib import Path
from datetime import date
import json

class JapaneseCalendar(CalendarConverter):
    # Japanese calendar uses same months & days structure as Gregorian
    # BUT uses specific era counting
    # No need to have astronomical conversion 
    # BUT need to have mapping table between Gregorian & Japanese era
    def __init__(self):
        # one time loader of all Japanese eras as mapper
        era_file = Path(__file__).parent.parent / 'data' / 'calendars' / 'japanese_eras.json'
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
        # 1721425 days is the fixed offset between Python's date ordinal epoch
        # (year 1, Jan 1) and the Julian Day Number epoch (4713 BCE).
        greg_date = date.fromordinal(jdn - 1721425)

        era = self._find_era(greg_date)

        if era is None:
            # Dates before 645 CE or in historical gaps have no era name.
            # wip how to format pre 645 CE dates
            formatted = greg_date.isoformat()
        else:
            # Era year 1 = the calendar year the era began.
            # e.g. Heisei started 1989 → year 2000 = 2000 - 1989 + 1 = 12
            era_year  = greg_date.year - era["start"].year + 1
            formatted = f"{era['kanji']} {era_year}年{greg_date.month}月{greg_date.day}日"

        return CalendarDate(
            year=greg_date.year,
            month=greg_date.month,
            day=greg_date.day,
            calendar_name="Japanese",
            formatted=formatted,
        )

    def to_jdn(self, cal_date: CalendarDate) -> int:
        # CalendarDate.year stores the Gregorian year (same months/days as Gregorian).
        # Inverse of date.fromordinal(jdn - 1721425).
        d = date(cal_date.year, cal_date.month, cal_date.day)
        return d.toordinal() + 1721425
