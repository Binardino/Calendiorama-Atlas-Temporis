from convertdate import coptic
from calendars.base import CalendarConverter, CalendarDate

class CopticCalendar(CalendarConverter):
    # Coptic (Alexandrian) solar calendar, used by the Coptic Orthodox Church.
    # Year 1 = Era of the Martyrs (Diocletian), starting 284 CE.
    # 12 months of 30 days + 1 intercalary month (Nasie) of 5 or 6 days.
    # Currently ~283 years behind Gregorian.
    # convertdate.coptic uses pure arithmetic — no datetime.date dependency.

    def from_jdn(self, jdn: int) -> CalendarDate:
        # 1825030 ≈ 284 CE (Coptic epoch, Era of the Martyrs).
        # convertdate.coptic won't crash before this date but returns year <= 0.
        if jdn < 1825030:
            return CalendarDate(year=0, month=0, day=0,
                                calendar_name="Coptic", formatted="",
                                out_of_range=True)
        # coptic.from_jd() returns a tuple (year, month, day)
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
        return int(coptic.to_jd(cal_date.year, cal_date.month, cal_date.day) + 0.5)