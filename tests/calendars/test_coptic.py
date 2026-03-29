from calendars.coptic import CopticCalendar, CalendarDate

#testing same JDN value 2451545 for all calendar.
#in Coptic calendar, starts in 284 CE, the Martyrs era
#so JDN 2451545 (January 1st 2000 in Gregorian) is 1716, 4th, 22nd
def test_from_jdn():
    # arrange
    converter = CopticCalendar()

    # act
    result = converter.from_jdn(2451545)

    # assert
    assert result.year == 1716
    assert result.month == 4
    assert result.day == 22


def test_to_jdn():
    # arrange
    converter = CopticCalendar()

    # act
    date = CalendarDate(year=1716, month=4, day=22,
                        calendar_name="Coptic",
                        formatted="1716-04-22")
    
    # assert
    assert converter.to_jdn(date) == 2451545