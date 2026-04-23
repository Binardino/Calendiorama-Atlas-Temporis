from calendars.base import CalendarConverter, CalendarDate
from hijridate import convert
from convertdate import islamic, gregorian

class HijriCalendar(CalendarConverter):
    # Islamic Hijri lunar calendar.
    # Year 1 AH = July 622 CE (Hijra: migration of the Prophet Muhammad from Mecca to Medina).
    # Pure lunar calendar: 12 months of 29 or 30 days = 354 days/year.
    # Drifts ~11 days/year relative to Gregorian 
    #           → same Hijri date falls on different seasons.
    #
    # Two calculation systems exist, hence the dual-library strategy below:
    #   - Umm al-Qura (astronomical, Saudi Arabia): hijri_converter 
    #                  - covers 1356–1500 AH (1937–2077 CE)
    #   - Tabular Islamic (arithmetic rule): convertdate.islamic 
    #                  - covers all dates, ±1–2 day margin
    MONTH_NAMES = {
    1: "Muharram",  2: "Safar",      3: "Rabi' al-Awwal",
    4: "Rabi' al-Thani", 5: "Jumada al-Ula", 6: "Jumada al-Thani",
    7: "Rajab",     8: "Sha'ban",    9: "Ramadan",
    10: "Shawwal", 11: "Dhu al-Qi'dah", 12: "Dhu al-Hijjah",
    }

    def from_jdn(self, jdn: int) -> CalendarDate:
        # Islamic calendar begins 1 Muharram 1 AH = 622-07-16 CE (JDN ~1948439).
        if jdn < 1948439:
            return CalendarDate(year=0, month=0, day=0,
                                calendar_name="Islamic", formatted="",
                                out_of_range=True)

        # the function uses 2 different method sequentially
        # according to the two aforementioned calculation systems
        year, month, day = gregorian.from_jd(jdn)
        try:
            # Step 1a: attempt Umm al-Qura conversion (more accurate, but limited range).
            # Raises OutOfRangeError if date is outside 1356–1500 AH.

            hijri_date       = convert.Gregorian(year, month, day).to_hijri()
            year, month, day = hijri_date.year, hijri_date.month, hijri_date.day

        except Exception:
            #out of hijri_converter range (i.e. before or after)
            # -> use tabular Islamic calendar

            # Step 1b: fall back to tabular Islamic calendar
            #                   (less accurate but all dates, ±1–2 days).
            # Used for all historical dates before 1937 CE
            year, month, day = islamic.from_jd(jdn)

        return CalendarDate(year=year,
                            month=month,
                            day=day,
                            calendar_name="Islamic",
                            formatted=f"{day} {self.MONTH_NAMES[month]} {year} AH"
                            )

    def to_jdn(self, cal_date: CalendarDate) -> int:
        # Uses tabular Islamic arithmetic for all dates
        #               (consistent, no range restriction).
        # Note: for dates in 1937–2077, this may differ by ±1–2 days from Umm al-Qura.
        return int(islamic.to_jd(cal_date.year, cal_date.month, cal_date.day) + 0.5)
