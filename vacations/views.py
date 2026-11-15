from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .models import VacationType


def vacation_type_list(request: HttpRequest) -> HttpResponse:
    """Показать типы отпуска и их влияние на лимит оплачиваемых дней."""
    context = {'vacations': VacationType.objects.order_by('pk')}
    return render(request, 'vacations/vacation_list.html', context)
