
from calendars.base import CalendarConverter, CalendarDate
from convertdate import persian

class PersianCalendar(CalendarConverter):
    MONTH_NAMES = {
    1: "Farvardin", 2: "Ordibehesht", 3: "Khordad",
    4: "Tir",       5: "Mordad",      6: "Shahrivar",
    7: "Mehr",      8: "Aban",        9: "Azar",
    10: "Dey",      11: "Bahman",     12: "Esfand",
                    }
    
    def from_jdn(self, jdn: int) -> CalendarDate:
        #persian lib returns a tuple (year, month, day)
        year, month, day = persian.from_jd(jdn)

        return CalendarDate(year=year,
                            month=month,
                            day=day,
                            calendar_name="persian",
                            formatted=f"{day} {self.MONTH_NAMES[month]} {year}"
        )
    
    def to_jdn(self, cal_date: CalendarDate) -> int:
        # Implementation of Persian date to JDN conversion
        return int(persian.to_jd(cal_date.year, cal_date.month, cal_date.day))