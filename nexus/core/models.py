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

class CourseSubject(models.Model):
    short_name = models.CharField(
        primary_key=True,
        unique=True,
        max_length=10,
        null=False,
        blank=False,
        help_text='The short name of the course subject. For example, "COMPSCI" for Computer Science.',
    )
    
    description = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text='The description of the course subject. For example, "Computer Science".',
    )
    
    class Meta:
        ordering = ['short_name']
    
    def __str__(self):
        return f'{self.short_name}'
    
    def long_name(self):
        return f'{self.description}'

class CourseManager(models.Manager):
    def get_cross_listed_courses_for(self, course):
        return self.get_queryset().filter(is_cross_listed=True, main_course=course).all()
    
    def get_main_course_for(self, course):
        if course.is_cross_listed:
            return course.main_course
        return course
    
    def create(self, **obj_data):
        if obj_data['is_cross_listed'] and obj_data['main_course'].is_cross_listed:
            raise ValueError('Main course cannot be cross listed.')
        return super().create(**obj_data)

class Course(models.Model):
    subject = models.ForeignKey(
        to=CourseSubject,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text='The department the course belongs to.',
    )
    
    number = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        help_text='The course number.',
    )
    
    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text='The name of the course.',
    )
    
    is_cross_listed = models.BooleanField(
        default=False,
        help_text='Whether or not the course is cross listed. (Not true for the main course in a cross listed course.)',
    )
    
    main_course = models.ForeignKey(
        to='self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The main course for the cross listed course.',
    )
    
    objects = CourseManager()
    
    def __str__(self):
        return f'{self.subject.short_name} {self.number}'
    
    def str_with_name(self):
        return f'{self.subject.short_name} {self.number} - {self.name}'
    
    def long_name(self):
        return f'{self.subject.description} {self.number} - {self.name}'

class Faculty(models.Model):
    first_name = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text='The first name of the faculty.',
    )
    
    last_name = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text='The last name of the faculty.',
    )
    
    email = models.EmailField(
        unique=True,
        max_length=254,
        null=False,
        blank=False,
        help_text='The email of the faculty.',
    )
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'