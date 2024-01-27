from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    NexusUser,
    Positions,
    PositionGroups,
)

@admin.register(NexusUser)
class NexusUserAdmin(UserAdmin):
    pass

@admin.register(Positions)
class PositionsAdmin(admin.ModelAdmin):
    list_display = ('semester', 'user', 'faculty', 'hourly_pay')
    list_filter = ('semester', 'user', 'faculty', 'hourly_pay')
    search_fields = ('semester', 'user', 'faculty', 'hourly_pay')
    ordering = ('semester', 'user', 'faculty')

@admin.register(PositionGroups)
class PositionGroupsAdmin(admin.ModelAdmin):
    list_display = ('semester', 'name')
    list_filter = ('semester', 'name')
    search_fields = ('semester', 'name')
    ordering = ('semester', 'name')