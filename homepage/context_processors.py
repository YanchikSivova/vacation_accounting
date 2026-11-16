from employees.models import Employee


def site_context(request) -> dict[str, int | str]:
    return {
        'site_name': 'Учёт отпусков',
        'employee_count': Employee.objects.count(),
    }
