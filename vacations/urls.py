from django.urls import path

from . import views

app_name = 'vacations'

urlpatterns = [
    path('', views.vacation_type_list, name='list'),
]
