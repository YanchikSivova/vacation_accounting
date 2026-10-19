from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.vacations import VACATION_TYPES


def vacation_type_list(request: HttpRequest) -> HttpResponse:
    """Показать типы отпуска и их влияние на лимит оплачиваемых дней."""
    context = {'vacations': VACATION_TYPES}
    return render(request, 'vacations/vacation_list.html', context)
