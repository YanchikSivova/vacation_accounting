import os

from django.test import override_settings
import pytest

from db import database
from db.create_db import create_database
from db.database import get_connection


def _client():
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'vacation_project.settings',
    )

    import django
    from django.test import Client

    django.setup()
    return Client()


@pytest.fixture(autouse=True)
def project_database(monkeypatch, tmp_path):
    database_path = tmp_path / 'project.sqlite'
    monkeypatch.setattr(database, 'DB_PATH', database_path)
    create_database(database_path)

    connection = get_connection(database_path)
    try:
        connection.executemany(
            """
            INSERT INTO employees (
                id, name, vacation_days_available, vacation_days_total
            )
            VALUES (?, ?, ?, ?)
            """,
            [
                (1, 'Сивова Яна', 28, 28),
                (2, 'Машуня', 20, 28),
            ],
        )
        connection.executemany(
            """
            INSERT INTO vacation_types (id, name, deducts_vacation_days)
            VALUES (?, ?, ?)
            """,
            [
                (1, 'Ежегодный оплачиваемый', 1),
                (2, 'Неоплачиваемый', 0),
                (3, 'По уходу за ребёнком', 0),
                (4, 'По болезни', 0),
            ],
        )
        connection.executemany(
            """
            INSERT INTO leave_requests (
                id, employee_id, vacation_type_id, start_date, end_date,
                duration, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    1, 1, 1, '2026-09-15', '2026-09-25', 11, 'cancelled',
                ),
                (
                    2, 2, 1, '2026-11-02', '2026-11-05', 4, 'approved',
                ),
                (
                    3, 1, 2, '2026-12-01', '2026-12-02', 2, 'pending',
                ),
            ],
        )
        connection.commit()
    finally:
        connection.close()


def test_homepage_has_navigation_and_bootstrap():
    response = _client().get('/')

    assert response.status_code == 200
    assert b'<!doctype html>' in response.content
    assert b'id="page-home"' in response.content
    assert b'bootstrap@5.3.3' in response.content
    assert b'/static/homepage/css/style.css' in response.content
    assert b'/static/homepage/js/main.js' in response.content
    assert b'/static/homepage/img/logo.svg' in response.content
    assert b'href="/employees/"' in response.content
    assert b'href="/vacations/"' in response.content
    assert b'href="/requests/"' in response.content
    assert b'href="/employees/available/"' in response.content
    assert b'href="/requests/statistics/"' in response.content


def test_employee_pages_display_domain_data():
    client = _client()

    employee_list = client.get('/employees/')
    employee_detail = client.get('/employees/1/')

    assert employee_list.status_code == 200
    assert 'Сивова Яна'.encode() in employee_list.content
    assert employee_detail.status_code == 200
    assert 'Доступно оплачиваемых дней:'.encode() in employee_detail.content
    assert 'из 28'.encode() in employee_detail.content
    assert 'Подробнее'.encode() in employee_list.content


def test_employee_list_uses_database_pagination():
    connection = get_connection()
    try:
        connection.executemany(
            """
            INSERT INTO employees (
                id, name, vacation_days_available, vacation_days_total
            )
            VALUES (?, ?, ?, ?)
            """,
            [
                (employee_id, f'A employee {employee_id}', 28, 28)
                for employee_id in range(3, 12)
            ],
        )
        connection.commit()
    finally:
        connection.close()

    client = _client()
    first_page = client.get('/employees/')
    second_page = client.get('/employees/?page=2')
    missing_page = client.get('/employees/?page=99')

    assert 'Всего сотрудников: 11'.encode() in first_page.content
    assert 'Страница 1 из 2'.encode() in first_page.content
    assert 'Сивова Яна'.encode() not in first_page.content
    assert 'Сивова Яна'.encode() in second_page.content
    assert 'Страница 2 из 2'.encode() in second_page.content
    assert missing_page.status_code == 404


def test_employee_name_is_escaped_in_html():
    connection = get_connection()
    try:
        connection.execute(
            """
            INSERT INTO employees (
                id, name, vacation_days_available, vacation_days_total
            )
            VALUES (?, ?, ?, ?)
            """,
            (7, '<script>alert(1)</script>', 28, 28),
        )
        connection.commit()
    finally:
        connection.close()

    response = _client().get('/employees/')

    assert response.status_code == 200
    assert b'&lt;script&gt;alert(1)&lt;/script&gt;' in response.content
    assert b'<script>alert(1)</script>' not in response.content


def test_vacation_type_page_displays_all_types_and_balance_rule():
    response = _client().get('/vacations/')

    assert response.status_code == 200
    assert 'Ежегодный оплачиваемый'.encode() in response.content
    assert 'Неоплачиваемый'.encode() in response.content
    assert 'По уходу за ребёнком'.encode() in response.content
    assert 'По болезни'.encode() in response.content
    assert 'Не уменьшает лимит дней'.encode() in response.content


def test_empty_lists_have_empty_state():
    connection = get_connection()
    try:
        connection.execute('DELETE FROM leave_requests')
        connection.execute('DELETE FROM employees')
        connection.commit()
    finally:
        connection.close()

    employees_response = _client().get('/employees/')
    requests_response = _client().get('/requests/')

    assert 'Сотрудников пока нет.'.encode() in employees_response.content
    assert 'Заявок пока нет.'.encode() in requests_response.content


def test_request_pages_display_request_and_related_objects():
    client = _client()

    request_list = client.get('/requests/')
    request_detail = client.get('/requests/1/')

    assert request_list.status_code == 200
    assert 'Заявка №1'.encode() in request_list.content
    assert request_detail.status_code == 200
    assert 'Сивова Яна'.encode() in request_detail.content
    assert 'Ежегодный оплачиваемый'.encode() in request_detail.content
    assert 'Отменена'.encode() in request_detail.content


def test_active_request_filter_and_date_search_use_database():
    client = _client()

    active_requests = client.get('/requests/active/')
    approved_requests = client.get('/requests/?status=approved')
    available_on_request_date = client.get(
        '/employees/available/?date=2026-11-03'
    )
    available_on_empty_date = client.get(
        '/employees/available/?date=2026-10-01'
    )

    assert active_requests.status_code == 200
    assert 'Заявка №2'.encode() in active_requests.content
    assert 'Заявка №1'.encode() not in active_requests.content
    assert approved_requests.status_code == 200
    assert 'Заявка №2'.encode() in approved_requests.content
    assert 'Заявка №3'.encode() not in approved_requests.content
    assert available_on_request_date.status_code == 200
    assert 'Сивова Яна'.encode() in available_on_request_date.content
    assert 'Машуня'.encode() not in available_on_request_date.content
    assert available_on_empty_date.status_code == 200
    assert 'Сивова Яна'.encode() in available_on_empty_date.content
    assert 'Машуня'.encode() in available_on_empty_date.content


def test_invalid_search_date_and_statistics_page():
    client = _client()

    invalid_date = client.get('/employees/available/?date=not-a-date')
    statistics = client.get('/requests/statistics/')

    assert invalid_date.status_code == 200
    assert 'Укажите корректную дату'.encode() in invalid_date.content
    assert statistics.status_code == 200
    assert 'Всего заявок: 3'.encode() in statistics.content
    assert 'Активных заявок: 2'.encode() in statistics.content
    assert 'Запрошено оплачиваемых дней:'.encode() in statistics.content


def test_unknown_urls_and_domain_ids_show_custom_404():
    client = _client()
    missing_pages = {
        '/not-found/': b'id="page-not-found"',
        '/employees/999/': 'Сотрудник не найден'.encode(),
        '/requests/999/': 'Заявка не найдена'.encode(),
    }

    with override_settings(DEBUG=False):
        for url, expected_content in missing_pages.items():
            response = client.get(url)

            assert response.status_code == 404
            assert expected_content in response.content
            assert b'href="/"' in response.content
