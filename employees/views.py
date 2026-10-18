from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from homepage.views import page
from models.users import User, find_user_by_id
from storage import load_users


def _employees() -> list[User]:
    return load_users(str(settings.BASE_DIR / 'data' / 'users.json'))


def employee_list(request: HttpRequest) -> HttpResponse:
    """Показать сотрудников и остаток оплачиваемых дней."""
    employees = _employees()
    if employees:
        items = format_html_join(
            '',
            '<li class="list-group-item d-flex justify-content-between">'
            '<a href="{}">{}</a>'
            '<span>{} из {} дней</span>'
            '</li>',
            (
                (
                    reverse('employees:detail', args=[employee.id]),
                    employee.name,
                    employee.vacation_days_available,
                    employee.vacation_days_total,
                )
                for employee in employees
            ),
        )
    else:
        items = format_html(
            '<li class="list-group-item">Сотрудников пока нет.</li>'
        )

    content = format_html(
        '<h1 class="mb-4">Сотрудники</h1>'
        '<ul class="list-group">{}</ul>',
        items,
    )
    return page('Сотрудники', content)


def employee_detail(
    request: HttpRequest,
    employee_id: int,
) -> HttpResponse:
    """Показать сотрудника; для неизвестного ID вернуть 404."""
    employee = find_user_by_id(_employees(), employee_id)
    if employee is None:
        raise Http404('Сотрудник не найден.')

    content = format_html(
        '<div class="card"><div class="card-body">'
        '<h1 class="card-title">{}</h1>'
        '<p class="card-text">ID: {}</p>'
        '<p class="card-text">Доступно оплачиваемых дней: {} из {}</p>'
        '<a class="btn btn-outline-secondary" href="{}">'
        'К списку сотрудников</a>'
        '</div></div>',
        employee.name,
        employee.id,
        employee.vacation_days_available,
        employee.vacation_days_total,
        reverse('employees:list'),
    )
    return page(employee.name, content)
