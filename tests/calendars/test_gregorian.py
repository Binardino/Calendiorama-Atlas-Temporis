from calendars.gregorian import GregorianCalendar, CalendarDate

# testing gregorian based on known date : January 1st 2000
def test_from_jdn():
    #arrange
    converter = GregorianCalendar()

    #act
    result = converter.from_jdn(2451545)

    #assert
    assert result.year == 2000
    assert result.month == 1
    assert result.day == 1

def test_to_jdn():
    #arrange
    converter = GregorianCalendar()

    #act
    date = CalendarDate(year=2000, month=1, day=1, 
                        calendar_name="Gregorian", 
                        formatted="2000-01-01")
    
    result = converter.to_jdn(date)

    #assert
    assert result == 2451545