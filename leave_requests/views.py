from datetime import date

from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from employees.models import Employee
from vacations.models import VacationType
from .models import LeaveRequest

ACTIVE_STATUSES = (
    LeaveRequest.Status.PENDING,
    LeaveRequest.Status.APPROVED,
)
REQUESTS_PER_PAGE = 5
SORT_FIELDS = {
    'date': 'start_date',
    'employee': 'employee__name',
    'vacation': 'vacation__name',
    'duration': 'duration',
    'status': 'status',
}


def _request_list_context(
    request: HttpRequest,
    active_only: bool = False,
) -> dict[str, object]:
    requests = LeaveRequest.objects.select_related('employee', 'vacation')
    errors = []
    selected_status = request.GET.get('status', '').strip()
    selected_date = request.GET.get('date', '').strip()
    selected_employee = request.GET.get('employee', '').strip()
    selected_vacation = request.GET.get('vacation', '').strip()
    selected_sort = request.GET.get('sort', 'date').strip()

    if active_only:
        requests = requests.active()
        selected_status = ''
    elif selected_status:
        if selected_status not in LeaveRequest.Status.values:
            errors.append('Выбран неизвестный статус заявки.')
        else:
            requests = requests.filter(status=selected_status)

    if selected_date:
        try:
            parsed_date = date.fromisoformat(selected_date)
            if parsed_date.isoformat() != selected_date:
                raise ValueError
        except ValueError:
            errors.append('Укажите корректную дату в формате ГГГГ-ММ-ДД.')
        else:
            requests = requests.filter(
                start_date__lte=parsed_date,
                end_date__gte=parsed_date,
            )

    if selected_employee:
        if selected_employee.isdecimal():
            requests = requests.filter(employee_id=int(selected_employee))
        else:
            errors.append('Выберите корректного сотрудника.')

    if selected_vacation:
        if selected_vacation.isdecimal():
            requests = requests.filter(vacation_id=int(selected_vacation))
        else:
            errors.append('Выберите корректный тип отпуска.')

    if selected_sort not in SORT_FIELDS:
        selected_sort = 'date'

    if errors:
        requests = requests.none()

    requests = requests.order_by(SORT_FIELDS[selected_sort], 'pk')
    paginator = Paginator(requests, REQUESTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    return {
        'requests': page_obj,
        'page_obj': page_obj,
        'total_requests': paginator.count,
        'selected_status': selected_status,
        'selected_date': selected_date,
        'selected_employee': selected_employee,
        'selected_vacation': selected_vacation,
        'status_choices': LeaveRequest.Status.choices,
        'selected_sort': selected_sort,
        'employees': Employee.objects.order_by('name', 'pk'),
        'vacations': VacationType.objects.order_by('pk'),
        'errors': errors,
        'active_only': active_only,
    }


def request_list(request: HttpRequest) -> HttpResponse:
    """Show leave requests with filtering, sorting, and pagination."""
    return render(
        request,
        'leave_requests/request_list.html',
        _request_list_context(request),
    )


def active_request_list(request: HttpRequest) -> HttpResponse:
    """Show only pending and approved leave requests."""
    return render(
        request,
        'leave_requests/request_list.html',
        _request_list_context(request, active_only=True),
    )


def request_detail(
    request: HttpRequest,
    request_id: int,
) -> HttpResponse:
    """Показать заявку; для неизвестного ID вернуть страницу 404."""
    vacation_request = LeaveRequest.objects.select_related(
        'employee',
        'vacation',
    ).filter(
        pk=request_id,
    ).first()
    return render(
        request,
        'leave_requests/request_detail.html',
        {'vacation_request': vacation_request},
        status=404 if vacation_request is None else 200,
    )


def request_statistics(request: HttpRequest) -> HttpResponse:
    """Display leave-request totals grouped by employee and leave type."""
    summary = LeaveRequest.objects.aggregate(
        total_requests=Count('pk'),
        active_requests=Count('pk', filter=Q(status__in=ACTIVE_STATUSES)),
        cancelled_requests=Count(
            'pk',
            filter=Q(status=LeaveRequest.Status.CANCELLED),
        ),
        completed_requests=Count(
            'pk',
            filter=Q(status=LeaveRequest.Status.COMPLETED),
        ),
    )
    by_employee = Employee.objects.annotate(
        employee_name=F('name'),
        active_request_count=Count(
            'leave_requests',
            filter=Q(leave_requests__status__in=ACTIVE_STATUSES),
        ),
        active_paid_days=Coalesce(
            Sum(
                'leave_requests__duration',
                filter=Q(
                    leave_requests__status__in=ACTIVE_STATUSES,
                    leave_requests__vacation__deducts_vacation_days=True,
                ),
            ),
            0,
        ),
    ).values(
        'id',
        'employee_name',
        'active_request_count',
        'active_paid_days',
    ).order_by('name', 'pk')
    by_vacation_type = VacationType.objects.annotate(
        vacation_name=F('name'),
        active_request_count=Count(
            'leave_requests',
            filter=Q(leave_requests__status__in=ACTIVE_STATUSES),
        ),
    ).values(
        'id',
        'vacation_name',
        'active_request_count',
    ).order_by('pk')
    high_activity = Employee.objects.annotate(
        employee_name=F('name'),
        active_request_count=Count(
            'leave_requests',
            filter=Q(leave_requests__status__in=ACTIVE_STATUSES),
        ),
    ).filter(
        active_request_count__gt=1,
    ).values(
        'id',
        'employee_name',
        'active_request_count',
    ).order_by('-active_request_count', 'name', 'pk')
    context = {
        'summary': summary,
        'by_employee': by_employee,
        'by_vacation_type': by_vacation_type,
        'high_activity': high_activity,
    }
    return render(request, 'leave_requests/statistics.html', context)
