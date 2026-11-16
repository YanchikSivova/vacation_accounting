from django.contrib import admin
from django.db.models import Count

from leave_requests.models import LeaveRequest
from .models import Employee


class EmployeeLeaveRequestInline(admin.TabularInline):
    model = LeaveRequest
    fields = ('vacation', 'start_date', 'end_date', 'duration', 'status')
    autocomplete_fields = ('vacation',)
    extra = 0
    show_change_link = True


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'vacation_days_available',
        'vacation_days_total',
        'vacation_days_used',
        'leave_request_count',
    )
    list_display_links = ('name',)
    list_editable = ('vacation_days_available',)
    list_filter = ('vacation_days_available', 'vacation_days_total')
    search_fields = ('name',)
    ordering = ('name', 'pk')
    list_per_page = 25
    readonly_fields = ('slug', 'vacation_days_used')
    fields = (
        'name',
        'slug',
        'vacation_days_available',
        'vacation_days_total',
        'vacation_days_used',
    )
    inlines = (EmployeeLeaveRequestInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _leave_request_count=Count('leave_requests'),
        )

    @admin.display(description='Заявок', ordering='_leave_request_count')
    def leave_request_count(self, employee):
        return employee._leave_request_count
