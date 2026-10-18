from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import format_html, format_html_join


def page(title: str, content: str, status: int = 200) -> HttpResponse:
    """Вернуть общий HTML-каркас страницы с навигацией и Bootstrap."""
    bootstrap_url = (
        'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3'
        '/dist/css/bootstrap.min.css'
    )
    navigation = format_html_join(
        '',
        '<a class="nav-link" href="{}">{}</a>',
        (
            (reverse('homepage:index'), 'Главная'),
            (reverse('employees:list'), 'Сотрудники'),
            (reverse('vacations:list'), 'Виды отпуска'),
            (reverse('leave_requests:list'), 'Заявки'),
        ),
    )
    document = format_html(
        '<!doctype html>'
        '<html lang="ru">'
        '<head>'
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>{}</title>'
        '<link href="{}" rel="stylesheet">'
        '<style>body {{ padding-bottom: 3rem; }}</style>'
        '</head>'
        '<body>'
        '<nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">'
        '<div class="container">'
        '<a class="navbar-brand" href="{}">Учёт отпусков</a>'
        '<div class="navbar-nav">{}</div>'
        '</div>'
        '</nav>'
        '<main class="container">{}</main>'
        '</body>'
        '</html>',
        title,
        bootstrap_url,
        reverse('homepage:index'),
        navigation,
        content,
    )
    return HttpResponse(document, status=status)


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница приложения."""
    content = format_html(
        '<section class="p-4 p-md-5 mb-4 bg-light rounded-3">'
        '<h1 class="display-5">Учёт отпусков</h1>'
        '<p class="lead">Сотрудники, виды отпусков и заявки в одном месте.</p>'
        '<p>Просматривайте остаток оплачиваемых дней и '
        'сведения по заявкам.</p>'
        '<a class="btn btn-primary me-2" href="{}">Сотрудники</a>'
        '<a class="btn btn-outline-primary" href="{}">Заявки на отпуск</a>'
        '</section>',
        reverse('employees:list'),
        reverse('leave_requests:list'),
    )
    return page('Учёт отпусков', content)


def page_not_found(
    request: HttpRequest,
    exception: Exception,
) -> HttpResponse:
    """Показать оформленную страницу для неизвестного URL или объекта."""
    content = format_html(
        '<h1 class="text-danger">404 — страница не найдена</h1>'
        '<p>Проверьте адрес или вернитесь на главную страницу.</p>'
        '<a class="btn btn-primary" href="{}">На главную</a>',
        reverse('homepage:index'),
    )
    return page('404 — страница не найдена', content, status=404)
