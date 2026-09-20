from datetime import date
from users import reduce_vacation_days, restore_vacation_days


def _calc_duration(start: date, end: date) -> int:
    """Длительность отпуска в днях (включительно)."""
    return (end - start).days + 1


def is_user_available(
    vacations: list[dict],
    user_id: int,
    start: date,
    end: date,
) -> bool:
    """Проверить, нет ли у пользователя пересекающихся заявок."""
    for v in vacations:
        if v["user_id"] != user_id or v["status"] == "cancelled":
            continue
        v_start = date.fromisoformat(v["start_date"])
        v_end = date.fromisoformat(v["end_date"])
        if start <= v_end and end >= v_start:
            return False
    return True


def create_vacation(
    vacations: list[dict],
    users: dict[int, dict],
    user_id: int,
    start: date,
    end: date,
) -> tuple[bool, str]:
    """Создать заявку на отпуск.

    Возвращает (успех, сообщение).
    """
    user = users.get(user_id)
    if user is None:
        return False, "Ошибка: пользователь не найден."

    duration = _calc_duration(start, end)
    if duration <= 0:
        return False, "Ошибка: дата окончания раньше даты начала."
    if duration > user["vacation_days_available"]:
        return False, (
            f"Ошибка: недостаточно дней. "
            f"Доступно {user['vacation_days_available']}," 
            f" запрошено {duration}."
        )
    if not is_user_available(vacations, user_id, start, end):
        return False, "Ошибка: на эти даты уже есть активная заявка."

    if not reduce_vacation_days(user, duration):
        return False, "Ошибка: не удалось списать дни."

    vacation_id = max((v["id"] for v in vacations), default=0) + 1
    vacation = {
        "id": vacation_id,
        "user_id": user_id,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "duration": duration,
        "status": "pending",
    }
    vacations.append(vacation)
    return True, f"Заявка №{vacation_id} создана (ожидает согласования)."


def cancel_vacation(
    vacations: list[dict],
    users: dict[int, dict],
    vacation_id: int,
) -> tuple[bool, str]:
    """Отменить заявку и вернуть дни пользователю."""
    for v in vacations:
        if v["id"] == vacation_id:
            if v["status"] == "cancelled":
                return False, "Заявка уже отменена."
            user = users.get(v["user_id"])
            if user:
                restore_vacation_days(user, v["duration"])
            v["status"] = "cancelled"
            return True, f"Заявка №{vacation_id} отменена."
    return False, f"Заявка №{vacation_id} не найдена."


def get_vacation_status(vacation: dict) -> str:
    """Текстовый статус заявки (сохранён из ПР1)."""
    statuses = {
        "pending": "Ожидает согласования",
        "approved": "Согласована",
        "cancelled": "Отменена",
    }
    return statuses.get(vacation["status"], "Неизвестный статус")


def filter_vacations_by_user(
        vacations: list[dict], 
        user_id: int
) -> list[dict]:
    """Отобрать заявки пользователя (генератор + list)."""
    return [v for v in vacations if v["user_id"] == user_id]


def sort_vacations_by_start(vacations: list[dict]) -> list[dict]:
    """Отсортировать заявки по дате начала (lambda-функция)."""
    return sorted(vacations, key=lambda v: v["start_date"])