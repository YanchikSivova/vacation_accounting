from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.users import User
from models.vacations import (
    VacationRequest,
    find_request_by_id,
    sort_requests_by_start,
)
from storage import load_users, load_vacation_requests


def _requests() -> list[VacationRequest]:
    users: list[User] = load_users(
        str(settings.BASE_DIR / 'data' / 'users.json')
    )
    return load_vacation_requests(
        str(settings.BASE_DIR / 'data' / 'vacations.json'),
        users,
    )


def request_list(request: HttpRequest) -> HttpResponse:
    """Показать заявки, отсортированные по дате начала."""
    context = {'requests': sort_requests_by_start(_requests())}
    return render(
        request,
        'leave_requests/request_list.html',
        context,
    )


def request_detail(
    request: HttpRequest,
    request_id: int,
) -> HttpResponse:
    """Показать заявку; для неизвестного ID вернуть страницу 404."""
    vacation_request = find_request_by_id(_requests(), request_id)
    context = {'vacation_request': vacation_request}
    return render(
        request,
        'leave_requests/request_detail.html',
        context,
        status=404 if vacation_request is None else 200,
    )
