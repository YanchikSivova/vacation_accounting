from datetime import date

from django.core.paginator import Paginator
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from leave_requests.models import LeaveRequest
from .models import Employee

EMPLOYEES_PER_PAGE = 10


def employee_list(request: HttpRequest) -> HttpResponse:
    """Show a database-paginated employee list."""
    page_value = request.GET.get('page', '1')
    try:
        page_number = int(page_value)
    except ValueError:
        page_number = 1
        page_error = 'Номер страницы должен быть положительным целым числом.'
    else:
        page_error = ''
        if page_number < 1:
            page_number = 1
            page_error = (
                'Номер страницы должен быть положительным целым числом.'
            )

    paginator = Paginator(
        Employee.objects.order_by('name', 'pk'),
        EMPLOYEES_PER_PAGE,
    )
    if page_number > paginator.num_pages:
        raise Http404('Страница сотрудников не найдена.')

    page_obj = paginator.page(page_number)
    context = {
        'employees': page_obj.object_list,
        'total_employees': paginator.count,
        'page_number': page_number,
        'page_count': paginator.num_pages,
        'page_error': page_error,
    }
    return render(request, 'employees/employee_list.html', context)


def employee_detail(
    request: HttpRequest,
    employee_id: int,
) -> HttpResponse:
    """Показать сотрудника; для неизвестного ID вернуть 404."""
    employee = Employee.objects.filter(pk=employee_id).first()
    return render(
        request,
        'employees/employee_detail.html',
        {'employee': employee},
        status=404 if employee is None else 200,
    )


def available_employees(request: HttpRequest) -> HttpResponse:
    """Find employees without an active leave request on the selected date."""
    selected_date = request.GET.get('date', '').strip()
    employees = Employee.objects.none()
    error = ''

    if selected_date:
        try:
            parsed_date = date.fromisoformat(selected_date)
            if parsed_date.isoformat() != selected_date:
                raise ValueError
        except ValueError:
            error = 'Укажите корректную дату в формате ГГГГ-ММ-ДД.'
        else:
            booked_employee_ids = LeaveRequest.objects.filter(
                status__in=(
                    LeaveRequest.Status.PENDING,
                    LeaveRequest.Status.APPROVED,
                ),
                start_date__lte=parsed_date,
                end_date__gte=parsed_date,
            ).values_list('employee_id', flat=True)
            employees = Employee.objects.exclude(
                pk__in=booked_employee_ids,
            ).order_by('name', 'pk')

    context = {
        'employees': employees,
        'selected_date': selected_date,
        'error': error,
    }
    return render(request, 'employees/available.html', context)
