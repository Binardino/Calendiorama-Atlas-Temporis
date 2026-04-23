
from calendars.base import CalendarConverter, CalendarDate
from convertdate import persian

class PersianCalendar(CalendarConverter):
    MONTH_NAMES = {
    # Persian Solar Hijri (Jalali) calendar, officially used in Iran and Afghanistan.
    # Year 1 = Nowruz of 622 CE (vernal equinox of the Hijra year).
    # Currently ~621 years behind Gregorian.
    # 12 months: first 6 have 31 days, next 5 have 30, 
    # last has 29 (30 in leap year).
    1: "Farvardin", 2: "Ordibehesht", 3: "Khordad",
    4: "Tir",       5: "Mordad",      6: "Shahrivar",
    7: "Mehr",      8: "Aban",        9: "Azar",
    10: "Dey",      11: "Bahman",     12: "Esfand",
                    }
    
    def from_jdn(self, jdn: int) -> CalendarDate:
        # 2122292 ≈ 1079 CE (Jalali calendar reform by Omar Khayyam).
        if jdn < 2122292:
            return CalendarDate(year=0, month=0, day=0,
                                calendar_name="Persian", formatted="",
                                out_of_range=True)

        #persian lib returns a tuple (year, month, day)
        year, month, day = persian.from_jd(jdn)

        return CalendarDate(year=year,
                            month=month,
                            day=day,
                            calendar_name="Persian",
                            formatted=f"{day} {self.MONTH_NAMES[month]} {year}"
        )
    
    def to_jdn(self, cal_date: CalendarDate) -> int:
        # Implementation of Persian date to JDN conversion
        return int(persian.to_jd(cal_date.year, cal_date.month, cal_date.day))