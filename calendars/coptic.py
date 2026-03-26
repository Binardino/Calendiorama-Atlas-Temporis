from convertdate import coptic
from calendars.base import CalendarConverter, CalendarDate

class CopticCalendar(CalendarConverter):
    def from_jdn(self, jdn: int) -> CalendarDate:
        # Coptic calendar
        # coptic lib returns a tuple (year, month, day)
        year, month, day = coptic.from_jd(jdn)

        return CalendarDate(
            year=year,
            month=month,
            day=day,
            calendar_name="Coptic",
            formatted=f"{year:04d}-{month:02d}-{day:02d}"
        )

    def to_jdn(self, cal_date: CalendarDate) -> int:
        # Implementation of Coptic date to JDN conversion
        return int(coptic.to_jd(cal_date.year, cal_date.month, cal_date.day))