from calendars.base import CalendarConverter, CalendarDate
from pyluach import dates

class HebrewCalendar(CalendarConverter):
    MONTH_NAMES = {
        # Lunisolar calendar: 12 months in ordinary years, 13 in leap years (7/19 cycle).
        # Months numbered from Tishri (civil new year), 
        # but the religious year starts at Nisan.
        # Adar II (month 7) only exists in leap years; 
        # pyluach handles this automatically.
        1: "Tishri",  2: "Cheshvan", 3: "Kislev",  4: "Tevet",
        5: "Shevat",  6: "Adar I",   7: "Adar II",  8: "Nisan",
        9: "Iyar",   10: "Sivan",   11: "Tammuz", 12: "Av",
        13: "Elul",
                    }
    
    def from_jdn(self, jdn:int) -> CalendarDate:
        h_date = dates.HebrewDate.from_jd(jdn)

        return CalendarDate(year=h_date.year,
                            month=h_date.month,
                            day=h_date.day,
                            calendar_name="Hebrew",
                            formatted=f"{h_date.day} {self.MONTH_NAMES[h_date.month]} {h_date.year}")

    def to_jdn(self, cal_date:CalendarDate) -> int:
        return int(dates.HebrewDate(cal_date.year, cal_date.month, cal_date.day).to_jd())