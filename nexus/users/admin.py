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
    list_display = ('semester', 'user', 'position', 'hourly_pay')
    list_filter = ('semester', 'user', 'position', 'hourly_pay')
    search_fields = ('semester', 'user', 'position', 'hourly_pay')
    ordering = ('semester', 'user', 'position')

@admin.register(PositionGroups)
class PositionGroupsAdmin(admin.ModelAdmin):
    list_display = ('semester', 'name')
    list_filter = ('semester', 'name')
    search_fields = ('semester', 'name')
    ordering = ('semester', 'name')