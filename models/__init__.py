# Удобный импорт классов из пакета
from .users import User
from .vacations import VACATION_TYPES, Vacation, VacationRequest

__all__ = ["User", "Vacation", "VacationRequest", "VACATION_TYPES"]
