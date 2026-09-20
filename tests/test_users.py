from users import create_user, find_user_by_name, reduce_vacation_days


def test_create_user():
    users = {}
    user = create_user(users, "Сивова Яна", 28)
    assert user["name"] == "Сивова Яна"
    assert user["vacation_days_available"] == 28
    assert len(users) == 1


def test_find_user_by_name():
    users = {}
    create_user(users, "Сивова Яна", 28)
    create_user(users, "Иванов Иван", 14)
    found = find_user_by_name(users, "сивова")
    assert len(found) == 1
    assert found[0]["name"] == "Сивова Яна"


def test_reduce_vacation_days_success():
    users = {}
    user = create_user(users, "Тест", 28)
    assert reduce_vacation_days(user, 10) is True
    assert user["vacation_days_available"] == 18


def test_reduce_vacation_days_fail():
    users = {}
    user = create_user(users, "Тест", 5)
    assert reduce_vacation_days(user, 10) is False
    assert user["vacation_days_available"] == 5