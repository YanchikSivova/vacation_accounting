from datetime import date
from users import create_user
from vacations import create_vacation, is_user_available, cancel_vacation


def test_is_user_available_empty():
    assert is_user_available([], 1, date(2026, 9, 15), date(2026, 9, 20))


def test_create_vacation_success():
    users = {}
    create_user(users, "Тест", 28)
    vacations = []
    ok, msg = create_vacation(
        vacations, users, 1, date(2026, 9, 15), date(2026, 9, 20)
    )
    assert ok is True
    assert len(vacations) == 1
    assert users[1]["vacation_days_available"] == 22


def test_create_vacation_overlap_forbidden():
    users = {}
    create_user(users, "Тест", 28)
    vacations = []
    create_vacation(vacations, users, 1, date(2026, 9, 15), date(2026, 9, 20))
    ok, msg = create_vacation(
        vacations, users, 1, date(2026, 9, 18), date(2026, 9, 25)
    )
    assert ok is False
    assert "активная заявка" in msg


def test_create_vacation_not_enough_days():
    users = {}
    create_user(users, "Тест", 3)
    vacations = []
    ok, msg = create_vacation(
        vacations, users, 1, date(2026, 9, 1), date(2026, 9, 10)
    )
    assert ok is False
    assert "недостаточно" in msg.lower()


def test_cancel_vacation_restores_days():
    users = {}
    create_user(users, "Тест", 28)
    vacations = []
    create_vacation(vacations, users, 1, date(2026, 9, 1), date(2026, 9, 5))
    ok, msg = cancel_vacation(vacations, users, 1)
    assert ok is True
    assert users[1]["vacation_days_available"] == 28
    assert vacations[0]["status"] == "cancelled"