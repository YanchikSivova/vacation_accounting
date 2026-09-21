from datetime import date

from models.users import User
from models.vacations import (
    Vacation,
    create_vacation,
    cancel_vacation,
    is_user_available,
)


def make_user() -> User:
    return User(1, "Сивова Яна", 28, 28)


def test_vacation_creation():
    user = make_user()
    v = Vacation(1, user, "2026-09-15", "2026-09-20", 6)
    assert v.id == 1
    assert v.user is user
    assert v.status == "pending"


def test_vacation_cancel_returns_days():
    user = make_user()
    v = Vacation(1, user, "2026-09-15", "2026-09-20", 6)
    user.reduce_days(6)
    v.cancel()
    assert v.status == "cancelled"
    assert user.vacation_days_available == 28


def test_create_vacation_success():
    user = make_user()
    vacations: list[Vacation] = []
    v = create_vacation(vacations, user, date(2026, 9, 15), date(2026, 9, 20))
    assert v is not None
    assert len(vacations) == 1
    assert user.vacation_days_available == 22


def test_create_vacation_overlap_forbidden():
    user = make_user()
    vacations: list[Vacation] = []
    create_vacation(vacations, user, date(2026, 9, 15), date(2026, 9, 20))
    v2 = create_vacation(vacations, user, date(2026, 9, 18), date(2026, 9, 25))
    assert v2 is None


def test_is_user_available_empty():
    user = make_user()
    assert is_user_available([], user, date(2026, 9, 15), date(2026, 9, 20))


def test_cancel_vacation():
    user = make_user()
    vacations: list[Vacation] = []
    create_vacation(vacations, user, date(2026, 9, 15), date(2026, 9, 20))
    ok = cancel_vacation(vacations, 1)
    assert ok is True
    assert vacations[0].status == "cancelled"
    assert user.vacation_days_available == 28
