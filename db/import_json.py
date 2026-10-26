import json
from pathlib import Path

from db.database import DB_PATH, PROJECT_ROOT, get_connection
from models.users import User
from models.vacations import VACATION_TYPES

USERS_FILE = PROJECT_ROOT / 'data' / 'users.json'
REQUESTS_FILE = PROJECT_ROOT / 'data' / 'vacations.json'


def load_json(filename: str | Path) -> list[dict]:
    with Path(filename).open(encoding='utf-8') as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f'Expected a JSON list in {filename}')
    return data


def import_json_data(
    db_path: str | Path | None = None,
    users_file: str | Path = USERS_FILE,
    requests_file: str | Path = REQUESTS_FILE,
) -> None:
    """Import legacy JSON data; employees and leave types precede requests."""
    users = [
        User.from_data(user).to_dict()
        for user in load_json(users_file)
    ]
    requests = load_json(requests_file)
    connection = get_connection(db_path)

    try:
        connection.executemany(
            """
            INSERT INTO employees (
                id,
                name,
                vacation_days_available,
                vacation_days_total
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                vacation_days_available = excluded.vacation_days_available,
                vacation_days_total = excluded.vacation_days_total
            """,
            [
                (
                    user['id'],
                    user['name'],
                    user['vacation_days_available'],
                    user['vacation_days_total'],
                )
                for user in users
            ],
        )
        connection.executemany(
            """
            INSERT INTO vacation_types (
                id,
                name,
                deducts_vacation_days
            )
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                deducts_vacation_days = excluded.deducts_vacation_days
            """,
            [
                (
                    vacation.id,
                    vacation.name,
                    int(vacation.deducts_vacation_days),
                )
                for vacation in VACATION_TYPES
            ],
        )
        connection.executemany(
            """
            INSERT INTO leave_requests (
                id,
                employee_id,
                vacation_type_id,
                start_date,
                end_date,
                duration,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                employee_id = excluded.employee_id,
                vacation_type_id = excluded.vacation_type_id,
                start_date = excluded.start_date,
                end_date = excluded.end_date,
                duration = excluded.duration,
                status = excluded.status
            """,
            [
                (
                    request['id'],
                    request['user_id'],
                    request.get('vacation_id', 1),
                    request['start_date'],
                    request['end_date'],
                    request['duration'],
                    request['status'],
                )
                for request in requests
            ],
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == '__main__':
    import_json_data()
    print(f'Imported JSON data into {DB_PATH}')
