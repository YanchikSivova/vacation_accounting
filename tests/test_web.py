import os
from unittest.mock import patch

from models.users import User


def _client():
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'vacation_project.settings',
    )

    import django
    from django.test import Client

    django.setup()
    return Client()


def test_homepage_has_navigation_and_bootstrap():
    response = _client().get('/')

    assert response.status_code == 200
    assert b'<!doctype html>' in response.content
    assert b'bootstrap@5.3.3' in response.content
    assert b'href="/employees/"' in response.content
    assert b'href="/vacations/"' in response.content
    assert b'href="/requests/"' in response.content


def test_employee_pages_display_domain_data():
    client = _client()

    employee_list = client.get('/employees/')
    employee_detail = client.get('/employees/1/')

    assert employee_list.status_code == 200
    assert 'Сивова Яна'.encode() in employee_list.content
    assert employee_detail.status_code == 200
    assert 'Доступно оплачиваемых дней: 28 из 28'.encode() in (
        employee_detail.content
    )


def test_employee_name_is_escaped_in_html():
    employee = User(7, '<script>alert(1)</script>', 28, 28)

    with patch('employees.views._employees', return_value=[employee]):
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


def test_unknown_urls_and_domain_ids_show_custom_404():
    client = _client()

    for url in ('/not-found/', '/employees/999/', '/requests/999/'):
        response = client.get(url)

        assert response.status_code == 404
        assert '404 — страница не найдена'.encode() in response.content
        assert b'class="btn btn-primary" href="/"' in response.content
