from convertdate import coptic
from calendars.base import CalendarConverter, CalendarDate

class EthiopianCalendar(CalendarConverter):
    # Ethiopian (Ge'ez) calendar, official calendar of Ethiopia.
    # Shares structure with the Coptic calendar (both derived from ancient Egyptian).
    # Year 1 = 8 CE (Incarnation era, ~7.5 years behind Gregorian).
    # 13 months: 12 × 30 days + Pagumē (5 or 6 epagomenal days in leap year).
    # No dedicated convertdate module — computed via coptic.from_jd() + year offset 276.
    # Relationship: Ethiopian year = Coptic year + 276
    #   Coptic epoch 284 CE → Ethiopian epoch 8 CE (284 - 276 = 8).

    def from_jdn(self, jdn: int) -> CalendarDate:
        # 1724221 ≈ 8 CE (Ethiopian epoch = Coptic epoch − 276 solar years).
        # convertdate.coptic won't crash before this date but year offset would be nonsensical.
        if jdn < 1724221:
            return CalendarDate(year=0, month=0, day=0,
                                calendar_name="Ethiopian", formatted="",
                                out_of_range=True)
        # coptic.from_jd() returns (year, month, day); Ethiopian year = Coptic year + 276.
        year, month, day = coptic.from_jd(jdn)

        return CalendarDate(
            year=year + 276,
            month=month,
            day=day,
            calendar_name="Ethiopian",
            formatted=f"{year + 276:04d}-{month:02d}-{day:02d}"
        )

    def to_jdn(self, cal_date: CalendarDate) -> int:
        # - 276 to convert Ethiopian year back to Coptic year before calling coptic.to_jd().
        # + 0.5 because coptic.to_jd() returns a float JDN at noon; cast to midnight int.
        return int(coptic.to_jd(cal_date.year - 276, cal_date.month, cal_date.day) + 0.5)
