from django.db import models

# Create your models here.
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
    class Terms(models.TextChoices):
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