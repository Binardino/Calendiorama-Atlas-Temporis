from convertdate import coptic
from calendars.base import CalendarConverter, CalendarDate

#no specific convertdate Ethiopian converter
#BUT ethiopian & coptic calendar have same structure & same logic

#Ethiopian year = Coptic year - 276, but earlier I calculated it should be Ethiopian year = Coptic year + 276. Let me reconcile:

##Coptic epoch: 284 CE, so Coptic year 1 = 284 CE
#Ethiopian epoch: 8 CE, so Ethiopian year 1 = 8 CE

#For a given year CE:
#Coptic year ≈ CE - 283 (for dates before Sep 11)
#Ethiopian year ≈ CE - 7 (for dates before Sep 11)

class EthiopianCalendar(CalendarConverter):
    def from_jdn(self, jdn: int) -> CalendarDate:
        # Ethiopian calendar has about 7.5 years negative difference from Gregorian calendar
        # based on Coptic calendar, which is itself based on the ancient Egyptian calendar. 
        # Ethiopian calendar has 13 months : 
        # 12 months of 30 days each + 5 or 6 epagomenal days in a leap year.
        
        # ethiopian lib returns a tuple (year, month, day)
        year, month, day = coptic.from_jd(jdn)

        return CalendarDate(
            year=year + 276,
            month=month,
            day=day,
            calendar_name="Ethiopian",
            formatted=f"{year + 276:04d}-{month:02d}-{day:02d}"
        )

    def to_jdn(self, cal_date: CalendarDate) -> int:
        # Implementation of Ethiopian date to JDN conversion
        return int(coptic.to_jd(cal_date.year - 276, cal_date.month, cal_date.day) + 0.5) 
        # - 276 for Coptic conversion
        # + 0.5 due to to JDN returning float .5 for midnight - adding +5 to get int
