from django.urls import path

from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.employee_list, name='list'),
    path('<int:employee_id>/', views.employee_detail, name='detail'),
]
