
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class CalendarDate:
    year          : int
    month         : int
    day           : int
    calendar_name : str
    formatted     : str
    out_of_range  : bool = False

class CalendarConverter(ABC):
    @abstractmethod
    def from_jdn(self, jdn: int) -> CalendarDate:
        pass

    @abstractmethod
    def to_jdn(self, date: CalendarDate) -> int:
        raise NotImplementedError("to_jdn method not implemented for this calendar")