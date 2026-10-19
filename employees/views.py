from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.users import User, find_user_by_id
from storage import load_users


def _employees() -> list[User]:
    return load_users(str(settings.BASE_DIR / 'data' / 'users.json'))


def employee_list(request: HttpRequest) -> HttpResponse:
    """Показать сотрудников и остаток оплачиваемых дней."""
    context = {'employees': _employees()}
    return render(request, 'employees/employee_list.html', context)


def employee_detail(
    request: HttpRequest,
    employee_id: int,
) -> HttpResponse:
    """Показать сотрудника; для неизвестного ID вернуть 404."""
    employee = find_user_by_id(_employees(), employee_id)
    context = {'employee': employee}
    return render(
        request,
        'employees/employee_detail.html',
        context,
        status=404 if employee is None else 200,
    )
