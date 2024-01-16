from typing import Any
from django.db import models

class Day(models.IntegerChoices):
    SUNDAY = 0, 'Sunday'
    MONDAY = 1, 'Monday'
    TUESDAY = 2, 'Tuesday'
    WEDNESDAY = 3, 'Wednesday'
    THURSDAY = 4, 'Thursday'
    FRIDAY = 5, 'Friday'
    SATURDAY = 6, 'Saturday'

class SemesterManager(models.Manager):
    def get_active_semester(self):
        return self.get_queryset().filter(active=True).first()
    
    def change_active_semester_to(self, semester):
        active_semester = self.get_active_semester()
        if active_semester:
            active_semester.active = False
            active_semester.save()
        semester.active = True
        semester.save()

class Semester(models.Model):
    class Terms(models.IntegerChoices):
        SPRING = 0, 'Spring'
        SUMMER = 1, 'Summer - University'
        SUMMER_UWW_1 = 2, 'Summer - UWW Session 1'
        SUMMER_UWW_2 = 3, 'Summer - UWW Session 2'
        FALL = 4, 'Fall'
        Winter = 5, 'Winter'
    
    term = models.PositiveSmallIntegerField(
        choices = Terms.choices,
        null = False,
        blank = False,
        help_text = 'The term of the semester',
    )
    
    year = models.PositiveSmallIntegerField(\
        null = False,
        blank = False,
        help_text = 'The year of the semester',
    )
    
    active = models.BooleanField(
        default = False,
        help_text = 'Whether or not the semester is active? There can only be one active semester at a time.',
    )
    
    classes_start = models.DateField(
        null = False,
        blank = False,
        help_text = 'The date classes start for the semester. This information will be use to create recurring shifts for classes.',
    )
    
    classes_end = models.DateField(
        null = False,
        blank = False,
        help_text = 'The date classes end for the semester. This information will be use to create recurring shifts for classes.',
    )

    objects = SemesterManager()
    
    def __str__(self):
        return f'{self.term_display} {self.year}'

class HolidayManager(models.Manager):
    def get_holidays_for(self, semester):
        return self.get_queryset().filter(semester=semester)
    
    def is_holiday(self, date):
        active_semester = Semester.objects.get_active_semester()
        return self.get_queryset().filter(semester=active_semester, date=date).exists()

class Holiday(models.Model):
    semester = models.ForeignKey(
        to=Semester,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text='The semester the holiday occurs in.',
    )
    
    date = models.DateField(
        null=False,
        blank=False,
        help_text='The date of the holiday. All shifts on this date will be cancelled.',
    )

    def __str__(self):
        return f'{self.date}'

class DaySwitchManager(models.Manager):
    def get_switches_for(self, semester):
        return self.get_queryset().filter(semester=semester)
    
    def date_to_day(self, date):
        active_semester = Semester.objects.get_active_semester()
        if self.get_queryset().filter(semester=active_semester, date=date).exists():
            return self.get_queryset().get(semester=active_semester,date=date).day_to_follow
        return (date.weekday()+1)%7

class DaySwitch(models.Model):
    semester = models.ForeignKey(
        to=Semester,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text='The semester the day switch occurs in.',
    )
    
    date = models.DateField(
        null=False,
        blank=False,
        help_text='The date of the day switch. This date will act as "day to follow" for recurring shifts.',
    )
    
    day_to_follow = models.PositiveSmallIntegerField(
        choices=Day.choices,
        blank=False,
        null=False,
    )
    
    objects = DaySwitchManager()
    
    def __str__(self):
        return f'{self.date} - {self.day_to_follow_display}'