from django.contrib import admin

from .models import LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'employee',
        'vacation',
        'start_date',
        'end_date',
        'duration',
        'status',
    )
    list_display_links = ('id',)
    list_editable = ('status',)
    list_filter = ('status', 'start_date', 'vacation')
    search_fields = ('employee__name', 'vacation__name')
    ordering = ('start_date', 'pk')
    date_hierarchy = 'start_date'
    list_select_related = ('employee', 'vacation')
    autocomplete_fields = ('employee', 'vacation')
    list_per_page = 25
    list_max_show_all = 100
