from calendars.julian import JulianCalendar, CalendarDate

# No BCE test: convertdate.julian uses pure arithmetic and handles BCE natively
# (returns negative years). No out_of_range guard exists in JulianCalendar.

def test_from_jdn():
    #arrange
    converter = JulianCalendar()

    #act
    result = converter.from_jdn(2451545)

    #assert
    assert result.year == 1999    
    assert result.month == 12
    assert result.day == 19
    
def test_to_jdn():
    #arrange
    converter = JulianCalendar()

    #act
    result = CalendarDate(year=1999, month = 12, day = 19,
                          calendar_name="Julian",
                          formatted='1999-12-19'
                          )
    
    #assert
    assert converter.to_jdn(result) == 2451545