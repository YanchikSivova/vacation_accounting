import json
import os

from models import User, Vacation


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


def load_vacations(filename: str, users: list[User]) -> list[Vacation]:
    """Загрузить заявки из JSON и восстановить связи с User."""
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        result: list[Vacation] = []
        for item in data:
            v = Vacation.from_data(item, users)
            if v is not None:
                result.append(v)
        return result
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Ошибка чтения {filename}: {e}")
        return []


def save_vacations(filename: str, vacations: list[Vacation]) -> None:
    """Сохранить объекты Vacation в JSON."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            [v.to_dict() for v in vacations],
            f,
            ensure_ascii=False,
            indent=2,
        )
