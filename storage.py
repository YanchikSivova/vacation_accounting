import json
import os

from models import User, VacationRequest


def load_users(filename: str) -> list[User]:
    """Загрузить пользователей из JSON в виде объектов User."""
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [User.from_data(item) for item in data]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Ошибка чтения {filename}: {e}")
        return []


def save_users(filename: str, users: list[User]) -> None:
    """Сохранить пользователей в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            [u.to_dict() for u in users],
            f,
            ensure_ascii=False,
            indent=2,
            )


def load_vacation_requests(
    filename: str,
    users: list[User],
) -> list[VacationRequest]:
    """Загрузить заявки из JSON и восстановить связи с User."""
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        result: list[VacationRequest] = []
        for item in data:
            request = VacationRequest.from_data(item, users)
            if request is not None:
                result.append(request)
        return result
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        print(f"Ошибка чтения {filename}: {e}")
        return []


def save_vacation_requests(
    filename: str,
    requests: list[VacationRequest],
) -> None:
    """Сохранить заявки на отпуск в JSON."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            [request.to_dict() for request in requests],
            f,
            ensure_ascii=False,
            indent=2,
        )
