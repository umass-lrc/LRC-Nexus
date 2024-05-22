from django.contrib import admin

from .models import (
    SIRoleInfo,
    SIReccuringShiftInfo,
)

@admin.register(SIRoleInfo)
class SIRoleInfoAdmin(admin.ModelAdmin):
    list_display = ('position', 'assigned_class')
    list_filter = ('position', 'assigned_class')
    search_fields = ('position', 'assigned_class')
    ordering = ('position', 'assigned_class')

@admin.register(SIReccuringShiftInfo)
class SIReccuringShiftInfoAdmin(admin.ModelAdmin):
    list_display = ('role', 'class_time')
    list_filter = ('role', 'class_time')
    search_fields = ('role', 'class_time')
    ordering = ('role', 'class_time')
