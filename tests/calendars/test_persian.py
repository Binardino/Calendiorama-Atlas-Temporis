from calendars.persian import PersianCalendar, CalendarDate

# JDN 2451545 = January 1st 2000 (Gregorian) = 12 Dey 1378 (Persian/Jalali).
# Persian year 1378 started March 21 1999 (Nowruz, vernal equinox).
# Dey is month 10 (winter month, 30 days).

def test_from_jdn():
    #arrange
    converter = PersianCalendar()

    #act
    result = converter.from_jdn(2451545)

    #assert
    assert result.year == 1378
    assert result.month == 10 
    assert result.day == 12

def test_to_jdn():
    #arrange
    converter = PersianCalendar()

    #act
    result = CalendarDate(year=1378, month = 10, day = 12,
                          calendar_name="Persian",
                          formatted='12 Dey 1378'
                          )
    
    #assert
    assert converter.to_jdn(result) == 2451545


def test_from_jdn_before_epoch():
    # arrange
    converter = PersianCalendar()

    # act
    # 2122291 = one day before the Persian epoch (≈ 1079 CE, Jalali calendar reform by Omar Khayyam)
    result = converter.from_jdn(2122291)

    # assert
    assert result.out_of_range == True
