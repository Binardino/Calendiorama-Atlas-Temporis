from calendars.japanese import JapaneseCalendar, CalendarDate

# JDN 2451545 = 2000-01-01 (Gregorian) = Heisei 12 (Japanese Imperial).
# Heisei era started 1989-01-08. Era year = 2000 - 1989 + 1 = 12.
# Japanese Imperial uses Gregorian months and days; only the year label differs.


def test_from_jdn():
    converter = JapaneseCalendar()
    result = converter.from_jdn(2451545)
    assert result.year == 2000
    assert result.month == 1
    assert result.day == 1


def test_to_jdn():
    converter = JapaneseCalendar()
    result = CalendarDate(year=2000, month=1, day=1,
                          calendar_name="Japanese",
                          formatted="平成 12年 1 January")
    assert converter.to_jdn(result) == 2451545
