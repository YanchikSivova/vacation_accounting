from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.repository import list_vacation_types


def vacation_type_list(request: HttpRequest) -> HttpResponse:
    """Показать типы отпуска и их влияние на лимит оплачиваемых дней."""
    context = {'vacations': list_vacation_types()}
    return render(request, 'vacations/vacation_list.html', context)
