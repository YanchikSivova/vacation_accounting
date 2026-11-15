import os
import sqlite3
import sys
from contextlib import closing
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DB = BASE_DIR / 'data' / 'vacation_accounting.sqlite'


def import_sqlite_data(
    source_path: str | Path = SOURCE_DB,
) -> dict[str, int]:
    """Copy legacy SQLite records into Django-managed tables."""
    source = Path(source_path)
    if not source.is_file():
        raise FileNotFoundError(f'Исходная база не найдена: {source}')

    with closing(sqlite3.connect(source)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA query_only = ON')
        employees = connection.execute(
            """
            SELECT id, name, vacation_days_available, vacation_days_total
            FROM employees
            ORDER BY id
            """
        ).fetchall()
        vacation_types = connection.execute(
            """
            SELECT id, name, deducts_vacation_days
            FROM vacation_types
            ORDER BY id
            """
        ).fetchall()
        requests = connection.execute(
            """
            SELECT
                id,
                employee_id,
                vacation_type_id,
                start_date,
                end_date,
                duration,
                status
            FROM leave_requests
            ORDER BY id
            """
        ).fetchall()

    from django.db import transaction

    from employees.models import Employee
    from leave_requests.models import LeaveRequest
    from vacations.models import VacationType

    with transaction.atomic():
        for row in employees:
            Employee.objects.update_or_create(
                pk=row['id'],
                defaults={
                    'name': row['name'],
                    'vacation_days_available': row[
                        'vacation_days_available'
                    ],
                    'vacation_days_total': row['vacation_days_total'],
                },
            )

        for row in vacation_types:
            VacationType.objects.update_or_create(
                pk=row['id'],
                defaults={
                    'name': row['name'],
                    'deducts_vacation_days': bool(
                        row['deducts_vacation_days'],
                    ),
                },
            )

        for row in requests:
            LeaveRequest.objects.update_or_create(
                pk=row['id'],
                defaults={
                    'employee_id': row['employee_id'],
                    'vacation_id': row['vacation_type_id'],
                    'start_date': date.fromisoformat(row['start_date']),
                    'end_date': date.fromisoformat(row['end_date']),
                    'duration': row['duration'],
                    'status': row['status'],
                },
            )

    return {
        'employees': len(employees),
        'vacation_types': len(vacation_types),
        'leave_requests': len(requests),
    }


if __name__ == '__main__':
    import django

    sys.path.insert(0, str(BASE_DIR))
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'vacation_project.settings',
    )
    django.setup()

    counts = import_sqlite_data()
    print('Перенос данных завершён.')
    print(f"Сотрудников: {counts['employees']}")
    print(f"Типов отпуска: {counts['vacation_types']}")
    print(f"Заявок: {counts['leave_requests']}")
