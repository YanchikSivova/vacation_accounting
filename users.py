def create_user(
    users: dict[int, dict],
    name: str,
    days_available: int = 28,
) -> dict:
    """Создать пользователя и добавить его в словарь users."""

    user_id = max(users.keys(), default=0) + 1
    user = {
        "id": user_id,
        "name": name,
        "vacation_days_available": days_available,
        "vacation_days_total": days_available,
    }
    users[user_id] = user
    return user


def find_user_by_name(users: dict[int, dict], query: str) -> list[dict]:
    """Найти пользователей по подстроке имени."""
    query_lower = query.lower()
    return [
        user for user in users.values()
        if query_lower in user["name"].lower()
    ]


def get_user(users: dict[int, dict], user_id: int) -> dict | None:
    """Получить пользователя по id."""
    return users.get(user_id)


def reduce_vacation_days(user: dict, duration: int) -> bool:
    """Уменьшить количество доступных дней отпуска.

    Возвращает False, если дней недостаточно.
    """
    if user["vacation_days_available"] - duration < 0:
        return False
    user["vacation_days_available"] -= duration
    return True


def restore_vacation_days(user: dict, duration: int) -> None:
    """Вернуть дни при отмене заявки."""
    user["vacation_days_available"] += duration
