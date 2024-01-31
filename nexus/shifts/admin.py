from django.contrib import admin

# Register your models here.
from .models import (
    RecurringShift,
    Shift,
    AttendanceInfo,
    ChangeRequest,
    DropRequest,
)

@admin.register(RecurringShift)
class RecurringShiftAdmin(admin.ModelAdmin):
    list_display = ('position', 'day', 'start_time', 'duration')
    list_filter = ('position', 'day', 'start_time', 'duration')
    search_fields = ('position', 'day', 'start_time', 'duration')
    ordering = ('position', 'day', 'start_time', 'duration')
    
@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('position', 'kind', 'start', 'duration')
    list_filter = ('position', 'kind', 'start', 'duration')
    search_fields = ('position', 'kind', 'start', 'duration')
    ordering = ('position', 'kind', 'start', 'duration')

@admin.register(AttendanceInfo)
class AttendanceInfoAdmin(admin.ModelAdmin):
    list_display = ('shift', 'attended', 'signed', 'flag_late')
    list_filter = ('shift', 'attended', 'signed', 'flag_late')
    search_fields = ('shift', 'attended', 'signed', 'flag_late')
    ordering = ('shift', 'attended', 'signed', 'flag_late')

@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('shift', 'reason', 'kind', 'state', 'last_change_by')
    list_filter = ('shift', 'reason', 'kind', 'state', 'last_change_by')
    search_fields = ('shift', 'reason', 'kind', 'state', 'last_change_by')
    ordering = ('shift', 'reason', 'kind', 'state', 'last_change_by')
    
@admin.register(DropRequest)
class DropRequestAdmin(admin.ModelAdmin):
    list_display = ('shift', 'reason', 'state')
    list_filter = ('shift', 'reason', 'state')
    search_fields = ('shift', 'reason', 'state')
    ordering = ('shift', 'reason', 'state')