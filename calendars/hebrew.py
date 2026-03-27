from calendars.base import CalendarConverter, CalendarDate
from pyluach import dates

class HebrewCalendar(CalendarConverter):
    MONTH_NAMES = {
    1: "Tishri",  2: "Cheshvan", 3: "Kislev",  4: "Tevet",
    5: "Shevat",  6: "Adar I",   7: "Adar II",  8: "Nisan",
    9: "Iyar",   10: "Sivan",   11: "Tammuz", 12: "Av",
    13: "Elul",
                }
    
    from_jdn(self, jdn:int) -> CalendarDate:
    h_date = dates.HebrewDate.from_jd(jdn)

    return CalendarDate(year=h_date.year,
                        month=h_date.month,
                        day=h_date.day,
                        calendar_name="Hebrew",
                        formatted=f"{day} {self.MONTH_NAMES[month]} {year}")

    to_jdn(self, jdn:int) -> CalendarDate: