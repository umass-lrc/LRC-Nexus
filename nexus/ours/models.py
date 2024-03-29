from django.db import models

from core.models import (
    Faculty,
    CourseSubject,
)

class Keyword(models.Model):
    keyword = models.CharField(
        max_length=255,
        unique=True
    )
    
    def __str__(self):
        return self.keyword

class FacultyPosition(models.Model):
    position = models.CharField(
        max_length=255,
        unique=True
    )
    
    def __str__(self):
        return self.position

class FacultyDetails(models.Model):
    faculty = models.OneToOneField(
        to=Faculty, 
        on_delete=models.CASCADE, 
        primary_key=True
    )
    
    positions = models.ManyToManyField(
        to=FacultyPosition,
        blank=True,
        null=True,
    )
    
    subjects = models.ManyToManyField(
        to=CourseSubject,
        blank=True,
        null=True,
    )
    
    keywords = models.ManyToManyField(
        to=Keyword,
        blank=True,
        null=True,
    )
    
    personal_website = models.URLField(
        blank=True,
        null=True
    )
    
    lab_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    
    lab_website = models.URLField(
        blank=True,
        null=True
    )
    
    research_outline = models.TextField(
        blank=True,
        null=True
    )
    
    miscellaneous = models.TextField(
        blank=True,
        null=True
    )
    
    allowed_to_post_oportunities = models.BooleanField(
        default=False
    )

class Majors(models.Model):
    major = models.CharField(
        max_length=255,
        unique=True
    )
    
    def __str__(self):
        return self.major
    
class Tracks(models.Model):
    track = models.CharField(
        max_length=255,
        unique=True
    )
    
    def __str__(self):
        return self.track

class CitizenshipStatus(models.Model):
    citizenship_status = models.CharField(
        max_length=255,
        unique=True
    )
    
    def __str__(self):
        return self.citizenship

class Opportunity(models.Model):
    title = models.CharField(
        max_length=255,
        null=False,
        blank=False
    )
    
    short_description = models.TextField(
        null=False,
        blank=False
    )
    
    description = models.TextField(
        null=False,
        blank=False
    )
    
    keywords = models.ManyToManyField(
        to=Keyword,
        blank=True,
        null=True,
    )
    
    related_to_major = models.ManyToManyField(
        to=Majors,
        blank=True,
        null=True,
    )
    
    related_to_track = models.ManyToManyField(
        to=Tracks,
        blank=True,
        null=True,
    )
    
    on_campus = models.BooleanField(
        default=False
    )
    
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    
    link = models.URLField(
        blank=True,
        null=True
    )
    
    deadline = models.DateField(
        blank=True,
        null=True
    )
    
    additional_info = models.TextField(
        blank=True,
        null=True
    )
    
    is_paid = models.BooleanField(
        default=False
    )
    
    is_for_credit = models.BooleanField(
        default=False
    )
    
    active = models.BooleanField(
        default=True
    )
    
    show_on_website = models.BooleanField(
        default=False
    )
    
    show_on_website_start_date = models.DateField(
        blank=True,
        null=True
    )
    
    show_on_website_end_date = models.DateField(
        blank=True,
        null=True
    )

class MinGPARestriction(models.Model):
    opportunity = models.OneToOneField(
        to=Opportunity, 
        on_delete=models.CASCADE
    )
    
    gpa = models.DecimalField(
        max_digits=1,
        decimal_places=2,
        null=False,
        blank=False
    )

class MajorRestriction(models.Model):
    opportunity = models.OneToOneField(
        to=Opportunity, 
        on_delete=models.CASCADE
    )
    
    majors = models.ManyToManyField(
        to=Majors
    )
    
    must_be_all_majors = models.BooleanField(
        default=False
    )

class CitizenshipRestriction(models.Model):
    opportunity = models.OneToOneField(
        to=Opportunity, 
        on_delete=models.CASCADE
    )
    
    citizenship_status = models.ManyToManyField(
        to=CitizenshipStatus
    )

class StudyLevel(models.Model):
    study_level = models.CharField(
        max_length=255,
        unique=True
    )
    
    def __str__(self):
        return self.study_level

class StudyLevelRestriction(models.Model):
    opportunity = models.OneToOneField(
        to=Opportunity, 
        on_delete=models.CASCADE
    )
    
    study_level = models.ManyToManyField(
        to=StudyLevel
    )

class CustomOpportunityRestrictions(models.Model):
    opportunity = models.ForeignKey(
        to=Opportunity, 
        on_delete=models.CASCADE
    )
    
    name = models.CharField(
        max_length=100,
        null=False,
        blank=False
    )
    
    criteria = models.CharField(
        max_length=255,
        null=False,
        blank=False
    )