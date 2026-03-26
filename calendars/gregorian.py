from calendars.base import CalendarConverter, CalendarDate
from datetime import date

class GregorianCalendar(CalendarConverter):
    def from_jdn(self, jdn: int) -> CalendarDate:
        #Gregorian calendar
        gregorian_date = date.fromordinal(jdn - 1721424)

        return CalendarDate(
            year=gregorian_date.year,
            month=gregorian_date.month,
            day=gregorian_date.day,
            calendar_name="Gregorian",
            formatted=gregorian_date.strftime("%Y-%m-%d")
        )

    def to_jdn(self, cal_date: CalendarDate) -> int:
        d_date = date(cal_date.year, cal_date.month, cal_date.day)
        
        return d_date.toordinal() + 1721424


