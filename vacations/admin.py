from django.contrib import admin
from django.db.models import Count

from leave_requests.models import LeaveRequest
from .models import VacationType


class VacationLeaveRequestInline(admin.TabularInline):
    model = LeaveRequest
    fields = ('employee', 'start_date', 'end_date', 'duration', 'status')
    autocomplete_fields = ('employee',)
    extra = 0
    show_change_link = True


@admin.register(VacationType)
class VacationTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'deducts_vacation_days', 'request_count')
    list_display_links = ('name',)
    list_editable = ('deducts_vacation_days',)
    list_filter = ('deducts_vacation_days',)
    search_fields = ('name',)
    ordering = ('pk',)
    list_per_page = 25
    inlines = (VacationLeaveRequestInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _leave_request_count=Count('leave_requests'),
        )

    @admin.display(description='Заявок', ordering='_leave_request_count')
    def request_count(self, vacation):
        return vacation._leave_request_count
