import os
import sqlite3
from datetime import date

import django
import pytest

from django.conf import settings
from django.core.management import call_command
from django.db import connections
from django.test import Client, override_settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vacation_project.settings')
django.setup()


def _models():
    from employees.models import Employee
    from leave_requests.models import LeaveRequest
    from vacations.models import VacationType

    return Employee, LeaveRequest, VacationType


@pytest.fixture(scope='session', autouse=True)
def django_database(tmp_path_factory):
    database_path = tmp_path_factory.mktemp('django-db') / 'project.sqlite'
    original_database_name = settings.DATABASES['default']['NAME']
    settings.DATABASES['default']['NAME'] = database_path
    try:
        connections.close_all()
        call_command('migrate', verbosity=0, interactive=False)
        yield
    finally:
        connections.close_all()
        settings.DATABASES['default']['NAME'] = original_database_name


@pytest.fixture(autouse=True)
def project_database(django_database):
    Employee, LeaveRequest, VacationType = _models()
    LeaveRequest.objects.all().delete()
    Employee.objects.all().delete()
    VacationType.objects.all().delete()
    VacationType.objects.bulk_create(
        [
            VacationType(
                id=1,
                name='Ежегодный оплачиваемый',
                deducts_vacation_days=True,
            ),
            VacationType(id=2, name='Неоплачиваемый'),
            VacationType(id=3, name='По уходу за ребёнком'),
            VacationType(id=4, name='По болезни'),
        ],
    )
    Employee.objects.bulk_create(
        [
            Employee(
                id=1,
                name='Сивова Яна',
                vacation_days_available=28,
                vacation_days_total=28,
            ),
            Employee(
                id=2,
                name='Машуня',
                vacation_days_available=20,
                vacation_days_total=28,
            ),
        ],
    )
    LeaveRequest.objects.bulk_create(
        [
            LeaveRequest(
                id=1,
                employee_id=1,
                vacation_id=1,
                start_date=date(2026, 9, 15),
                end_date=date(2026, 9, 25),
                duration=11,
                status=LeaveRequest.Status.CANCELLED,
            ),
            LeaveRequest(
                id=2,
                employee_id=2,
                vacation_id=1,
                start_date=date(2026, 11, 2),
                end_date=date(2026, 11, 5),
                duration=4,
                status=LeaveRequest.Status.APPROVED,
            ),
            LeaveRequest(
                id=3,
                employee_id=1,
                vacation_id=2,
                start_date=date(2026, 12, 1),
                end_date=date(2026, 12, 2),
                duration=2,
                status=LeaveRequest.Status.PENDING,
            ),
        ],
    )


def _client():
    return Client()


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
    Employee, _, _ = _models()
    Employee.objects.bulk_create(
        [
            Employee(
                id=employee_id,
                name=f'A employee {employee_id}',
                vacation_days_available=28,
                vacation_days_total=28,
            )
            for employee_id in range(3, 12)
        ],
    )

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
    Employee, _, _ = _models()
    Employee.objects.create(
        id=7,
        name='<script>alert(1)</script>',
        vacation_days_available=28,
        vacation_days_total=28,
    )

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
    Employee, LeaveRequest, _ = _models()
    LeaveRequest.objects.all().delete()
    Employee.objects.all().delete()

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


def test_request_filters_sorting_and_pagination():
    _, LeaveRequest, _ = _models()
    client = _client()
    filtered = client.get(
        '/requests/?status=approved&date=2026-11-03&employee=2'
        '&vacation=1&sort=duration',
    )

    assert filtered.status_code == 200
    assert 'Всего заявок: 1'.encode() in filtered.content
    assert 'Заявка №2'.encode() in filtered.content
    assert b'name="sort"' in filtered.content

    LeaveRequest.objects.bulk_create(
        [
            LeaveRequest(
                id=request_id,
                employee_id=1,
                vacation_id=2,
                start_date=date(2027, 1, request_id - 3),
                end_date=date(2027, 1, request_id - 3),
                duration=1,
                status=LeaveRequest.Status.PENDING,
            )
            for request_id in range(4, 9)
        ],
    )
    first_page = client.get(
        '/requests/?status=pending&employee=1&sort=date',
    )
    second_page = client.get(
        '/requests/?status=pending&employee=1&sort=date&page=2',
    )

    assert 'Всего заявок: 6'.encode() in first_page.content
    assert b'status=pending&amp;employee=1&amp;sort=date&amp;page=2' in (
        first_page.content
    )
    assert 'Всего заявок: 6'.encode() in second_page.content
    assert 'Заявка №8'.encode() in second_page.content


def test_invalid_request_filters_show_errors_without_results():
    response = _client().get(
        '/requests/?date=not-a-date&employee=bad',
    )

    assert response.status_code == 200
    assert 'Укажите корректную дату'.encode() in response.content
    assert 'Выберите корректного сотрудника'.encode() in response.content
    assert 'Заявка №'.encode() not in response.content


def test_orm_crud_and_protected_relations():
    Employee, LeaveRequest, VacationType = _models()
    employee = Employee.objects.create(
        name='Новый сотрудник',
        vacation_days_available=28,
        vacation_days_total=28,
    )
    vacation = VacationType.objects.get(pk=2)
    vacation_request = LeaveRequest.objects.create(
        employee=employee,
        vacation=vacation,
        start_date=date(2027, 3, 1),
        end_date=date(2027, 3, 2),
        duration=2,
    )
    persisted_request = LeaveRequest.objects.get(pk=vacation_request.pk)
    assert persisted_request.employee == employee

    vacation_request.status = LeaveRequest.Status.APPROVED
    vacation_request.save(update_fields=['status'])
    assert LeaveRequest.objects.get(
        pk=vacation_request.pk,
    ).status == LeaveRequest.Status.APPROVED

    from django.db.models.deletion import ProtectedError

    with pytest.raises(ProtectedError):
        employee.delete()

    vacation_request.delete()
    employee.delete()
    assert not Employee.objects.filter(pk=employee.pk).exists()


def test_sqlite_import_is_repeatable_and_keeps_model_relations(tmp_path):
    from db.import_sqlite_to_orm import import_sqlite_data

    Employee, LeaveRequest, VacationType = _models()
    source_path = tmp_path / 'legacy.sqlite'
    with sqlite3.connect(source_path) as connection:
        connection.executescript(
            """
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                vacation_days_available INTEGER,
                vacation_days_total INTEGER
            );
            CREATE TABLE vacation_types (
                id INTEGER PRIMARY KEY,
                name TEXT,
                deducts_vacation_days INTEGER
            );
            CREATE TABLE leave_requests (
                id INTEGER PRIMARY KEY,
                employee_id INTEGER,
                vacation_type_id INTEGER,
                start_date TEXT,
                end_date TEXT,
                duration INTEGER,
                status TEXT
            );
            INSERT INTO employees VALUES (12, 'Импорт', 18, 28);
            INSERT INTO vacation_types VALUES (12, 'Тестовый отпуск', 1);
            INSERT INTO leave_requests VALUES (
                12, 12, 12, '2026-10-01', '2026-10-03', 3, 'approved'
            );
            """
        )

    counts = import_sqlite_data(source_path)
    repeated_counts = import_sqlite_data(source_path)
    imported_request = LeaveRequest.objects.select_related(
        'employee',
        'vacation',
    ).get(pk=12)

    assert counts == {
        'employees': 1,
        'vacation_types': 1,
        'leave_requests': 1,
    }
    assert repeated_counts == counts
    assert Employee.objects.count() == 3
    assert VacationType.objects.count() == 5
    assert LeaveRequest.objects.count() == 4
    assert imported_request.employee.name == 'Импорт'
    assert imported_request.vacation.name == 'Тестовый отпуск'


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
