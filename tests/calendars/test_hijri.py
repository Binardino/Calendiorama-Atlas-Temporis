
from calendars.hijri import HijriCalendar, CalendarDate

#JDN 2451545 = January 1st 2000 = 24 Ramadan 1420 AH.
#from_jdn uses Umm al-Qura (hijridate), to_jdn uses tabular Islamic
#(convertdate): round-trip may differ by +/-1 day outside 1937-2077 range.

def test_from_jdn():
    #arrange
    converter = HijriCalendar()

    #act
    result = converter.from_jdn(2451545)

    #assert
    assert result.year == 1420    
    assert result.month == 9
    assert result.day == 24
    
def test_to_jdn():
    #arrange
    converter = HijriCalendar()

    #act
    result = CalendarDate(year=1420, month = 9, day = 24,
                          calendar_name="Hijri",
                          formatted='24 Ramadan 1420 AH'
                          )
    
    #assert
    assert converter.to_jdn(result) == 2451545