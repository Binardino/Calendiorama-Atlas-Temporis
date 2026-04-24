from calendars.ethiopian import EthiopianCalendar, CalendarDate

#testing same JDN value 2451545 for all calendar.
#in Coptic calendar, starts in 284 CE, the Martyrs era
#so JDN 2451545 (January 1st 2000 in Gregorian) is 1716, 4th, 22nd
def test_from_jdn():
    # arrange
    converter = EthiopianCalendar()

    # act
    result = converter.from_jdn(2451545)

    # assert
    assert result.year == 1992
    assert result.month == 4
    assert result.day == 22


def test_to_jdn():
    # arrange
    converter = EthiopianCalendar()

    # act
    date = CalendarDate(year=1992, month=4, day=22,
                        calendar_name="Ethiopian",
                        formatted="1992-04-22")
    
    # assert
    assert converter.to_jdn(date) == 2451545


def test_from_jdn_before_epoch():
    # arrange
    converter = EthiopianCalendar()

    # act
    # 1724220 = one day before the Ethiopian epoch (≈ 8 CE, Ge'ez Incarnation era)
    result = converter.from_jdn(1724220)

    # assert
    assert result.out_of_range == True