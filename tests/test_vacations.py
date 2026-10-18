from datetime import date

from models import VACATION_TYPES
from models.users import User
from models.vacations import (
    Vacation,
    VacationRequest,
    cancel_vacation_request,
    create_vacation_request,
    is_user_available,
)


def make_user() -> User:
    return User(1, "Сивова Яна", 28, 28)


def test_vacation_types_define_leave_categories():
    assert [vacation.name for vacation in VACATION_TYPES] == [
        "Ежегодный оплачиваемый",
        "Неоплачиваемый",
        "По уходу за ребёнком",
        "По болезни",
    ]
    assert VACATION_TYPES[0].deducts_vacation_days is True
    assert all(
        not vacation.deducts_vacation_days for vacation in VACATION_TYPES[1:]
    )


def test_vacation_request_creation():
    user = make_user()
    request = VacationRequest(
        1, user, VACATION_TYPES[0], "2026-09-15", "2026-09-20", 6
    )
    assert request.id == 1
    assert request.user is user
    assert isinstance(request.vacation, Vacation)
    assert request.status == "pending"


def test_cancel_paid_vacation_request_returns_days():
    user = make_user()
    requests: list[VacationRequest] = []
    request = create_vacation_request(
        requests, user, VACATION_TYPES[0], date(2026, 9, 15), date(2026, 9, 20)
    )
    assert request is not None
    assert user.vacation_days_available == 22

    request.cancel()
    assert request.status == "cancelled"
    assert user.vacation_days_available == 28


def test_create_paid_vacation_request_success():
    user = make_user()
    requests: list[VacationRequest] = []
    request = create_vacation_request(
        requests, user, VACATION_TYPES[0], date(2026, 9, 15), date(2026, 9, 20)
    )
    assert request is not None
    assert len(requests) == 1
    assert user.vacation_days_available == 22


def test_create_unpaid_vacation_request_does_not_deduct_days():
    user = make_user()
    requests: list[VacationRequest] = []
    request = create_vacation_request(
        requests,
        user,
        VACATION_TYPES[1],
        date(2026, 9, 15),
        date(2026, 10, 20),
    )
    assert request is not None
    assert request.vacation is VACATION_TYPES[1]
    assert user.vacation_days_available == 28


def test_cancel_unpaid_vacation_request_does_not_change_balance():
    user = make_user()
    requests: list[VacationRequest] = []
    request = create_vacation_request(
        requests, user, VACATION_TYPES[1], date(2026, 9, 15), date(2026, 9, 20)
    )
    assert request is not None

    request.cancel()
    assert user.vacation_days_available == 28


def test_non_paid_vacation_types_do_not_change_balance():
    for vacation in VACATION_TYPES[1:]:
        user = make_user()
        requests: list[VacationRequest] = []
        request = create_vacation_request(
            requests,
            user,
            vacation,
            date(2026, 9, 15),
            date(2026, 9, 20),
        )

        assert request is not None
        assert user.vacation_days_available == 28
        request.cancel()
        assert user.vacation_days_available == 28


def test_paid_vacation_request_cannot_exceed_balance():
    user = make_user()
    requests: list[VacationRequest] = []
    request = create_vacation_request(
        requests, user, VACATION_TYPES[0], date(2026, 9, 1), date(2026, 10, 1)
    )
    assert request is None
    assert requests == []
    assert user.vacation_days_available == 28


def test_overlapping_vacation_requests_are_forbidden():
    user = make_user()
    requests: list[VacationRequest] = []
    create_vacation_request(
        requests, user, VACATION_TYPES[0], date(2026, 9, 15), date(2026, 9, 20)
    )
    second_request = create_vacation_request(
        requests, user, VACATION_TYPES[1], date(2026, 9, 18), date(2026, 9, 25)
    )
    assert second_request is None


def test_is_user_available_empty():
    user = make_user()
    assert is_user_available([], user, date(2026, 9, 15), date(2026, 9, 20))


def test_cancel_vacation_request():
    user = make_user()
    requests: list[VacationRequest] = []
    create_vacation_request(
        requests, user, VACATION_TYPES[0], date(2026, 9, 15), date(2026, 9, 20)
    )
    ok = cancel_vacation_request(requests, 1)
    assert ok is True
    assert requests[0].status == "cancelled"
    assert user.vacation_days_available == 28
