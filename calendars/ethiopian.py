from convertdate import ethiopian
from calendars.base import CalendarConverter, CalendarDate

class EthiopianCalendar(CalendarConverter):
    def from_jdn(self, jdn: int) -> CalendarDate:
        # Ethiopian calendar has about 7.5 years negative difference from Gregorian calendar
        # based on Coptic calendar, which is itself based on the ancient Egyptian calendar. 
        # Ethiopian calendar has 13 months : 
        # 12 months of 30 days each + 5 or 6 epagomenal days in a leap year.
        
        # ethiopian lib returns a tuple (year, month, day)
        year, month, day = ethiopian.from_jd(jdn)

        return CalendarDate(
            year=year,
            month=month,
            day=day,
            calendar_name="Ethiopian",
            formatted=f"{year:04d}-{month:02d}-{day:02d}"
        )

    def to_jdn(self, cal_date: CalendarDate) -> int:
        # Implementation of Ethiopian date to JDN conversion
        return int(ethiopian.to_jd(cal_date.year, cal_date.month, cal_date.day))
