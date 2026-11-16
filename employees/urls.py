from django.urls import path

from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.employee_list, name='list'),
    path('available/', views.available_employees, name='available'),
    path('<int:employee_id>/', views.employee_detail, name='detail'),
    path('<slug:slug>/', views.employee_detail_by_slug, name='slug_detail'),
]
