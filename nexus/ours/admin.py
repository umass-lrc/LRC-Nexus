from django.contrib import admin

from .models import (
    Keyword,
    FacultyPosition,
    FacultyDetails,
    Majors,
    Tracks,
    CitizenshipStatus,
    Opportunity,
    MinGPARestriction,
    MajorRestriction,
    CitizenshipRestriction,
    StudyLevel,
    StudyLevelRestriction,
)

# Register your models here.

@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('keyword',)
    search_fields = ('keyword',)
    ordering = ('keyword',)

@admin.register(FacultyPosition)
class FacultyPositionAdmin(admin.ModelAdmin):
    list_display = ('position',)
    search_fields = ('position',)
    ordering = ('position',)

@admin.register(FacultyDetails)
class FacultyDetailsAdmin(admin.ModelAdmin):
    list_display = ('faculty',)
    search_fields = ('faculty', )
    ordering = ('faculty', )

@admin.register(Majors)
class MajorsAdmin(admin.ModelAdmin):
    list_display = ('major',)
    search_fields = ('major',)
    ordering = ('major',)
    
@admin.register(Tracks)
class TracksAdmin(admin.ModelAdmin):
    list_display = ('track',)
    search_fields = ('track',)
    ordering = ('track',)

@admin.register(CitizenshipStatus)
class CitizenshipStatusAdmin(admin.ModelAdmin):
    list_display = ('citizenship_status',)
    search_fields = ('citizenship_status',)
    ordering = ('citizenship_status',)
    
@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ('title',)

