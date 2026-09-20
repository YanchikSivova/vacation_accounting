import json
import os


def load_users(filename: str) -> dict[int, dict]:
    """Загрузить пользователей из JSON-файла."""
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {user["id"]: user for user in data}
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Ошибка чтения {filename}: {e}")
        return {}


def save_users(filename: str, users: dict[int, dict]) -> None:
    """Сохранить пользователей в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(list(users.values()), f, ensure_ascii=False, indent=2)


def load_vacations(filename: str) -> list[dict]:
    """Загрузить заявки из JSON-файла."""
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Ошибка чтения {filename}: {e}")
        return []


def save_vacations(filename: str, vacations: list[dict]) -> None:
    """Сохранить заявки в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(vacations, f, ensure_ascii=False, indent=2)
