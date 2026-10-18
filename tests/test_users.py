import pytest

from models.users import User, add_user


def test_user_creation():
    user = User(1, "Сивова Яна", 28, 28)
    assert user.id == 1
    assert user.name == "Сивова Яна"
    assert user.vacation_days_available == 28


def test_user_reduce_days():
    user = User(1, "Сивова Яна", 28, 28)
    assert user.reduce_days(10) is True
    assert user.vacation_days_available == 18


def test_user_reduce_days_fail():
    user = User(1, "Сивова Яна", 5, 5)
    assert user.reduce_days(10) is False
    assert user.vacation_days_available == 5


def test_user_rejects_available_days_outside_limit():
    with pytest.raises(ValueError):
        User(1, "Сивова Яна", 29, 28)
    with pytest.raises(ValueError):
        User(1, "Сивова Яна", -1, 28)


def test_user_rejects_total_days_above_limit():
    with pytest.raises(ValueError):
        User(1, "Сивова Яна", 29, 29)


def test_user_restore_days_does_not_exceed_28():
    user = User(1, "Сивова Яна", 27, 28)

    user.restore_days(5)

    assert user.vacation_days_available == 28


def test_user_from_data_caps_legacy_balance_to_limit():
    user = User.from_data(
        {
            "id": 1,
            "name": "Сивова Яна",
            "vacation_days_available": 38,
            "vacation_days_total": 28,
        }
    )

    assert user.vacation_days_available == 28


def test_user_str():
    user = User(1, "Сивова Яна", 28, 28)
    assert "Сивова Яна" in str(user)


def test_user_from_data():
    data = {
        "id": 1,
        "name": "Сивова Яна",
        "vacation_days_available": 28,
        "vacation_days_total": 28,
    }
    user = User.from_data(data)
    assert user.id == 1
    assert user.name == "Сивова Яна"


def test_add_user():
    users = []
    user = add_user(users, "Сивова Яна", 28)
    assert len(users) == 1
    assert user.id == 1
    assert user.name == "Сивова Яна"
