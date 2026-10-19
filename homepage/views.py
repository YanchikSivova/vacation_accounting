from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница приложения."""
    return render(request, 'homepage/index.html')


def page_not_found(
    request: HttpRequest,
    exception: Exception,
) -> HttpResponse:
    """Показать оформленную страницу для неизвестного URL или объекта."""
    return render(
        request,
        'homepage/404.html',
        status=404,
    )
