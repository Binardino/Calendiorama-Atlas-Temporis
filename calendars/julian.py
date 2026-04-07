from convertdate import julian
from calendars.base import CalendarConverter, CalendarDate

class JulianCalendar(CalendarConverter):
    def from_jdn(self, jdn:int) -> CalendarDate:
        #Julian calendar
        #julian lib returns a tuple (year, month, day)
        year, month, day = julian.from_jd(jdn)

        return CalendarDate(
            year=year,
            month=month,
            day=day,
            calendar_name="Julian",
            formatted=f"{year:04d}-{month:02d}-{day:02d}"
        )

    def to_jdn(self, cal_date: CalendarDate) -> int:
        # Implementation of Julian date to JDN conversion
        return int(julian.to_jd(cal_date.year, cal_date.month, cal_date.day) + 0.5)