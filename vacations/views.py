from django.http import HttpRequest, HttpResponse
from django.utils.html import format_html, format_html_join

from homepage.views import page
from models.vacations import VACATION_TYPES


def vacation_type_list(request: HttpRequest) -> HttpResponse:
    """Показать типы отпуска и их влияние на лимит оплачиваемых дней."""
    items = format_html_join(
        '',
        '<li class="list-group-item d-flex justify-content-between">'
        '<span>{}</span>'
        '<span class="badge {}">{}</span>'
        '</li>',
        (
            (
                vacation.name,
                (
                    'text-bg-primary'
                    if vacation.deducts_vacation_days
                    else 'text-bg-secondary'
                ),
                (
                    'Уменьшает лимит дней'
                    if vacation.deducts_vacation_days
                    else 'Не уменьшает лимит дней'
                ),
            )
            for vacation in VACATION_TYPES
        ),
    )
    content = format_html(
        '<h1 class="mb-4">Виды отпуска</h1>'
        '<p>Лимит от 0 до 28 дней расходуется только при ежегодном '
        'оплачиваемом отпуске.</p>'
        '<ul class="list-group">{}</ul>',
        items,
    )
    return page('Виды отпуска', content)
