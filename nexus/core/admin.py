from django.contrib import admin

from .models import (
    Semester,
    Holiday,
    DaySwitch,
    CourseSubject,
    Course,
    Faculty,
    Buildings,
    Classes,
    ClassTimes,
)

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('term', 'year', 'classes_start', 'classes_end', 'active')
    list_filter = ('term', 'year', 'active')
    search_fields = ('term', 'year')
    ordering = ('-year', 'term')

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('semester', 'date')
    list_filter = ('semester',)
    search_fields = ('date',)
    ordering = ('date',)

@admin.register(DaySwitch)
class DaySwitchAdmin(admin.ModelAdmin):
    list_display = ('semester', 'date', 'day_to_follow')
    list_filter = ('semester',)
    search_fields = ('date',)
    ordering = ('date',)

@admin.register(CourseSubject)
class CourseSubjectAdmin(admin.ModelAdmin):
    list_display = ('description', 'short_name')
    search_fields = ('description', 'short_name')
    ordering = ('description',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('subject', 'number', 'name', 'is_cross_listed', 'main_course')
    list_filter = ('subject', 'number', 'is_cross_listed', 'main_course')
    search_fields = ('subject', 'number', 'name')
    ordering = ('subject', 'number')

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('last_name', 'first_name')

@admin.register(Buildings)
class BuildingsAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name')
    search_fields = ('short_name', 'name')
    ordering = ('short_name',)

@admin.register(Classes)
class ClassesAdmin(admin.ModelAdmin):
    list_display = ('course', 'faculty', 'semester')
    list_filter = ('course', 'faculty', 'semester')
    search_fields = ('course', 'faculty')
    ordering = ('course', 'faculty')

@admin.register(ClassTimes)
class ClassTimesAdmin(admin.ModelAdmin):
    list_display = ('class_day', 'start_time', 'duration', 'building', 'room')
    list_filter = ('class_day', 'building')
    search_fields = ('class_day', 'building', 'room')
    ordering = ('class_day', 'start_time')