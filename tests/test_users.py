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
