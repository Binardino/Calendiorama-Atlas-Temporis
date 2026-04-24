
from calendars.hebrew import HebrewCalendar, CalendarDate
# JDN 2451545 = January 1st 2000 (Gregorian) = 23 Tevet 5760 (Hebrew).
# Hebrew year 5760 started September 11 1999 (Rosh Hashana).
# pyluach month numbering from Nisan: Tevet = month 10.

def test_from_jdn():
    #arrange
    converter = HebrewCalendar()

    #act
    result = converter.from_jdn(2451545)

    #assert
    assert result.year == 5760    
    assert result.month == 10
    assert result.day == 23
    
def test_to_jdn():
    #arrange
    converter = HebrewCalendar()

    #act
    result = CalendarDate(year=5760, month = 10, day = 23,
                          calendar_name="Hebrew",
                          formatted='5760-10-23'
                          )
    
    #assert
    assert converter.to_jdn(result) == 2451545

def test_from_jdn_before_epoch():
    # arrange
    converter = HebrewCalendar()

    # act
    # 1721425 = one day before JDN 1721426 (1 Jan 1 CE, Python datetime.date minimum)
    # The actual Hebrew epoch is 3761 BCE — inaccessible until pyluach direct constructor is used.
    result = converter.from_jdn(1721425)

    # assert
    assert result.out_of_range == True
