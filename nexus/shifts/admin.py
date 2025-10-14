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
    list_display = ('position', 'day', 'start_time', 'duration', 'building', 'room', 'kind')
    list_filter = ('day', 'kind', 'building', 'require_punch_in_out')
    search_fields = ('position__user__first_name', 'position__user__last_name', 'position__user__email', 'kind', 'building__short_name', 'room')
    ordering = ('position', 'day', 'start_time')
    list_per_page = 50
    list_select_related = ('position', 'position__user', 'building')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'position', 
            'position__user', 
            'building'
        )
    
@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('position', 'kind', 'start', 'duration', 'building', 'room', 'attended_status')
    list_filter = ('kind', 'start', 'building', 'require_punch_in_out', 'dropped')
    search_fields = ('position__user__first_name', 'position__user__last_name', 'position__user__email', 'kind', 'building__short_name', 'room')
    ordering = ('-start', 'position')
    list_per_page = 50
    date_hierarchy = 'start'
    list_select_related = ('position', 'position__user', 'building')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'position', 
            'position__user', 
            'building'
        ).prefetch_related('attendance_info')
    
    def attended_status(self, obj):
        """Show attendance status in a readable format"""
        try:
            att_info = obj.attendance_info
            if att_info.attended:
                return "✅ Attended"
            elif att_info.punch_in_time and not att_info.punch_out_time:
                return "🕐 In Progress"
            else:
                return "❌ Not Attended"
        except:
            return "❓ Unknown"
    attended_status.short_description = "Status"

@admin.register(AttendanceInfo)
class AttendanceInfoAdmin(admin.ModelAdmin):
    list_display = ('shift_info', 'attended', 'signed', 'flag_late', 'punch_in_time', 'punch_out_time')
    list_filter = ('attended', 'signed', 'flag_late', 'punch_in_time', 'punch_out_time')
    search_fields = ('shift__position__user__first_name', 'shift__position__user__last_name', 'shift__position__user__email', 'shift__kind')
    ordering = ('-shift__start', 'attended', 'signed')
    list_per_page = 50
    list_select_related = ('shift', 'shift__position', 'shift__position__user', 'shift__building')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'shift', 
            'shift__position', 
            'shift__position__user', 
            'shift__building'
        )
    
    def shift_info(self, obj):
        """Show shift information in a readable format"""
        return f"{obj.shift.kind} - {obj.shift.position.user.get_full_name()} ({obj.shift.start.strftime('%m/%d %I:%M %p')})"
    shift_info.short_description = "Shift"

@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('shift_info', 'reason', 'kind', 'state', 'last_change_by')
    list_filter = ('kind', 'state', 'last_change_by')
    search_fields = ('shift__position__user__first_name', 'shift__position__user__last_name', 'shift__position__user__email', 'reason', 'kind')
    ordering = ('-id', 'state')
    list_per_page = 50
    list_select_related = ('shift', 'shift__position', 'shift__position__user', 'last_change_by')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'shift', 
            'shift__position', 
            'shift__position__user', 
            'last_change_by'
        )
    
    def shift_info(self, obj):
        """Show shift information in a readable format"""
        return f"{obj.shift.kind} - {obj.shift.position.user.get_full_name()} ({obj.shift.start.strftime('%m/%d %I:%M %p')})"
    shift_info.short_description = "Shift"
    
@admin.register(DropRequest)
class DropRequestAdmin(admin.ModelAdmin):
    list_display = ('shift_info', 'reason', 'state')
    list_filter = ('state',)
    search_fields = ('shift__position__user__first_name', 'shift__position__user__last_name', 'shift__position__user__email', 'reason')
    ordering = ('-id', 'state')
    list_per_page = 50
    list_select_related = ('shift', 'shift__position', 'shift__position__user')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'shift', 
            'shift__position', 
            'shift__position__user'
        )
    
    def shift_info(self, obj):
        """Show shift information in a readable format"""
        return f"{obj.shift.kind} - {obj.shift.position.user.get_full_name()} ({obj.shift.start.strftime('%m/%d %I:%M %p')})"
    shift_info.short_description = "Shift"