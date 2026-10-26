import json
import sqlite3
from pathlib import Path

import pytest

from db.create_db import create_database
from db.database import get_connection
from db.import_json import import_json_data


def test_create_database_builds_tables_and_enforces_foreign_keys(tmp_path):
    database_path = tmp_path / 'vacations.sqlite'
    create_database(database_path)

    connection = get_connection(database_path)
    try:
        tables = {
            row['name']
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        assert tables == {'employees', 'vacation_types', 'leave_requests'}
        assert connection.execute('PRAGMA foreign_keys').fetchone()[0] == 1
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO leave_requests (
                    id, employee_id, vacation_type_id, start_date, end_date,
                    duration, status
                )
                VALUES (1, 999, 999, '2026-01-01', '2026-01-01', 1, 'pending')
                """
            )
    finally:
        connection.close()


def test_import_json_is_repeatable_and_migrates_legacy_request(tmp_path):
    database_path = tmp_path / 'vacations.sqlite'
    users_file = tmp_path / 'users.json'
    requests_file = tmp_path / 'requests.json'
    users_file.write_text(
        json.dumps(
            [
                {
                    'id': 1,
                    'name': 'Тестовый сотрудник',
                    'vacation_days_available': 28,
                    'vacation_days_total': 28,
                }
            ]
        ),
        encoding='utf-8',
    )
    requests_file.write_text(
        json.dumps(
            [
                {
                    'id': 1,
                    'user_id': 1,
                    'start_date': '2026-09-01',
                    'end_date': '2026-09-03',
                    'duration': 3,
                    'status': 'pending',
                }
            ]
        ),
        encoding='utf-8',
    )

    create_database(database_path)
    import_json_data(database_path, users_file, requests_file)
    import_json_data(database_path, users_file, requests_file)

    connection = get_connection(database_path)
    try:
        employee_count = connection.execute(
            'SELECT COUNT(*) FROM employees'
        ).fetchone()[0]
        type_count = connection.execute(
            'SELECT COUNT(*) FROM vacation_types'
        ).fetchone()[0]
        request = connection.execute(
            'SELECT * FROM leave_requests WHERE id = 1'
        ).fetchone()
    finally:
        connection.close()

    assert employee_count == 1
    assert type_count == 4
    assert request['vacation_type_id'] == 1
    assert request['status'] == 'pending'


def test_documented_sql_queries_execute_with_parameters(tmp_path):
    database_path = tmp_path / 'vacations.sqlite'
    create_database(database_path)
    import_json_data(database_path)

    statements = [
        statement.strip()
        for statement in (
            (Path(__file__).resolve().parents[1] / 'sql' / 'queries.sql')
            .read_text(encoding='utf-8')
            .split(';')
        )
        if statement.strip()
    ]
    query_parameters = {
        1: (10, 0),
        3: (1,),
        4: ('cancelled',),
        7: ('2026-09-20', '2026-09-20'),
        10: (1,),
    }

    connection = get_connection(database_path)
    try:
        results = [
            connection.execute(
                statement,
                query_parameters.get(index, ()),
            ).fetchall()
            for index, statement in enumerate(statements)
        ]
    finally:
        connection.close()

    assert len(statements) == 16
    assert len(results[0]) == 2
    assert len(results[2]) == 4
