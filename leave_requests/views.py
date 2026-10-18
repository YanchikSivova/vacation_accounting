from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from homepage.views import page
from models.users import User
from models.vacations import (
    VacationRequest,
    find_request_by_id,
    get_request_status,
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
    requests = sort_requests_by_start(_requests())
    if requests:
        items = format_html_join(
            '',
            '<li class="list-group-item d-flex justify-content-between '
            'align-items-center">'
            '<a href="{}">Заявка №{} · {} · {}</a>'
            '<span class="badge {}">{}</span>'
            '</li>',
            (
                (
                    reverse('leave_requests:detail', args=[item.id]),
                    item.id,
                    item.vacation.name,
                    item.start_date,
                    (
                        'text-bg-secondary'
                        if item.status == 'cancelled'
                        else 'text-bg-primary'
                    ),
                    get_request_status(item),
                )
                for item in requests
            ),
        )
    else:
        items = format_html(
            '<li class="list-group-item">Заявок пока нет.</li>'
        )

    content = format_html(
        '<h1 class="mb-4">Заявки на отпуск</h1>'
        '<ul class="list-group">{}</ul>',
        items,
    )
    return page('Заявки на отпуск', content)


def request_detail(
    request: HttpRequest,
    request_id: int,
) -> HttpResponse:
    """Показать заявку; для неизвестного ID вернуть страницу 404."""
    vacation_request = find_request_by_id(_requests(), request_id)
    if vacation_request is None:
        raise Http404('Заявка не найдена.')

    content = format_html(
        '<div class="card"><div class="card-body">'
        '<h1 class="card-title">Заявка №{}</h1>'
        '<p class="card-text">Сотрудник: <a href="{}">{}</a></p>'
        '<p class="card-text">Тип отпуска: {}</p>'
        '<p class="card-text">Период: {} — {}</p>'
        '<p class="card-text">Продолжительность: {} дней</p>'
        '<p class="card-text">Статус: {}</p>'
        '<a class="btn btn-outline-secondary" href="{}">'
        'К списку заявок</a>'
        '</div></div>',
        vacation_request.id,
        reverse(
            'employees:detail',
            args=[vacation_request.user.id],
        ),
        vacation_request.user.name,
        vacation_request.vacation.name,
        vacation_request.start_date,
        vacation_request.end_date,
        vacation_request.duration,
        get_request_status(vacation_request),
        reverse('leave_requests:list'),
    )
    return page(f'Заявка №{vacation_request.id}', content)
