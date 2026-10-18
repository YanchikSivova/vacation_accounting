from django.urls import path

from . import views

app_name = 'leave_requests'

urlpatterns = [
    path('', views.request_list, name='list'),
    path('<int:request_id>/', views.request_detail, name='detail'),
]
