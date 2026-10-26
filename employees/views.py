from datetime import date

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from db.repository import (
    count_employees,
    find_available_employees,
    find_employee,
    list_employees,
)

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

    total_employees = count_employees()
    page_count = max(
        1,
        (total_employees + EMPLOYEES_PER_PAGE - 1) // EMPLOYEES_PER_PAGE,
    )
    if page_number > page_count:
        raise Http404('Страница сотрудников не найдена.')

    context = {
        'employees': list_employees(
            limit=EMPLOYEES_PER_PAGE,
            offset=(page_number - 1) * EMPLOYEES_PER_PAGE,
        ),
        'total_employees': total_employees,
        'page_number': page_number,
        'page_count': page_count,
        'page_error': page_error,
    }
    return render(request, 'employees/employee_list.html', context)


def employee_detail(
    request: HttpRequest,
    employee_id: int,
) -> HttpResponse:
    """Показать сотрудника; для неизвестного ID вернуть 404."""
    employee = find_employee(employee_id)
    context = {'employee': employee}
    return render(
        request,
        'employees/employee_detail.html',
        context,
        status=404 if employee is None else 200,
    )


def available_employees(request: HttpRequest) -> HttpResponse:
    """Find employees without an active leave request on the selected date."""
    selected_date = request.GET.get('date', '').strip()
    employees = []
    error = ''

    if selected_date:
        try:
            parsed_date = date.fromisoformat(selected_date)
            if parsed_date.isoformat() != selected_date:
                raise ValueError
        except ValueError:
            error = 'Укажите корректную дату в формате ГГГГ-ММ-ДД.'
        else:
            employees = find_available_employees(parsed_date)

    context = {
        'employees': employees,
        'selected_date': selected_date,
        'error': error,
    }
    return render(request, 'employees/available.html', context)
