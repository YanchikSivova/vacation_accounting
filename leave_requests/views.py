from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.repository import (
    REQUEST_STATUSES,
    find_request,
    list_requests,
    request_statistics as load_request_statistics,
)


def request_list(request: HttpRequest) -> HttpResponse:
    """Show leave requests, optionally filtered by status."""
    selected_status = request.GET.get('status', '').strip()
    error = ''
    if selected_status and selected_status not in REQUEST_STATUSES:
        error = 'Выбран неизвестный статус заявки.'
        requests = []
    else:
        requests = list_requests(selected_status or None)

    context = {
        'requests': requests,
        'selected_status': selected_status,
        'error': error,
        'active_only': False,
    }
    return render(
        request,
        'leave_requests/request_list.html',
        context,
    )


def active_request_list(request: HttpRequest) -> HttpResponse:
    """Show only pending and approved leave requests."""
    context = {
        'requests': list_requests(active_only=True),
        'selected_status': '',
        'error': '',
        'active_only': True,
    }
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
    vacation_request = find_request(request_id)
    context = {'vacation_request': vacation_request}
    return render(
        request,
        'leave_requests/request_detail.html',
        context,
        status=404 if vacation_request is None else 200,
    )


def request_statistics(request: HttpRequest) -> HttpResponse:
    """Display leave-request totals grouped by employee and leave type."""
    context = load_request_statistics()
    return render(request, 'leave_requests/statistics.html', context)
