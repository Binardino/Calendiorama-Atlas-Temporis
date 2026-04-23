from calendars.base import CalendarConverter, CalendarDate
from pyluach import dates
from datetime import date

class HebrewCalendar(CalendarConverter):
    # Hebrew lunisolar calendar. 
    # 12 months in ordinary years, 13 in leap years (7/19 Metonic cycle).
    # pyluach numbers months from Nisan (religious year): 
    # Nisan=1 ... Tevet=10 ... Adar II=13.
    # month_name() is used for formatting 
    # to avoid manual dict that could desync from pyluach numbering.
    
    def from_jdn(self, jdn: int) -> CalendarDate:
        # datetime.date.fromordinal() requires ordinal >= 1 (year 1 CE minimum).
        # The Hebrew calendar extends to 3761 BCE (year 1 Anno Mundi) 
        # but that range is inaccessible here 
        # — requires a direct pyluach constructor in a future phase.
        if jdn < 1721426:
            return CalendarDate(year=0, month=0, day=0,
                                calendar_name="Hebrew", formatted="",
                                out_of_range=True)
        # JDN → Python date → HebrewDate (pyluach has no direct from_jd).
        # 1721425 = offset between Python ordinal (epoch: Jan 1 year 1 = ordinal 1)
        #           and Julian Day Number  (epoch: Jan 1 4713 BCE = JDN 1)
        python_date = date.fromordinal(jdn - 1721425)
        h_date      = dates.HebrewDate.from_pydate(python_date)

        return CalendarDate(year=h_date.year,
                            month=h_date.month,
                            day=h_date.day,
                            calendar_name="Hebrew",
                            formatted=f"{h_date.day} {h_date.month_name()} {h_date.year}")

    def to_jdn(self, cal_date:CalendarDate) -> int:
        # HebrewDate → Python date → JDN 
        # (reverse of from_jdn, avoids JulianDay float handling)
        pydate = dates.HebrewDate(cal_date.year, cal_date.month, cal_date.day).to_pydate()
        return pydate.toordinal() + 1721425
        