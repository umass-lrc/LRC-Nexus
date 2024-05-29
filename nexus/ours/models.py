from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.db.models import CharField, Value
from django.db.models.functions import Concat

import datetime
import requests
from urllib.parse import urlparse

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

class FacultyDetailsManager(models.Manager):
    def basic_search(self, search_query):
        return self.all().annotate(
            last_name_first_name=Concat('faculty__last_name', Value(' '), 'faculty__first_name', output_field=CharField()),
            first_name_last_name=Concat('faculty__first_name', Value(' '), 'faculty__last_name', output_field=CharField()),
        ).filter(
            Q(last_name_first_name__icontains=search_query) |
            Q(first_name_last_name__icontains=search_query) |
            Q(faculty__email__icontains=search_query) |
            Q(positions__position__icontains=search_query) |
            Q(subjects__short_name__icontains=search_query) |
            Q(subjects__description__icontains=search_query) |
            Q(keywords__keyword__icontains=search_query) |
            Q(lab_name__icontains=search_query) |
            Q(research_outline__icontains=search_query) |
            Q(miscellaneous__icontains=search_query)
        ).distinct()

class FacultyDetails(models.Model):
    faculty = models.OneToOneField(
        to=Faculty, 
        on_delete=models.CASCADE, 
        primary_key=True
    )
    
    positions = models.ManyToManyField(
        to=FacultyPosition,
        blank=True,
    )
    
    subjects = models.ManyToManyField(
        to=CourseSubject,
        blank=True,
    )
    
    keywords = models.ManyToManyField(
        to=Keyword,
        blank=True,
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
    
    objects = FacultyDetailsManager()
    
    def __str__(self):
        return str(self.faculty)
    
    class Meta:
        ordering = ['faculty__last_name', 'faculty__first_name']

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
        return self.citizenship_status
    
    def opportunity_set(self):
        opp_ids = CitizenshipRestriction.objects.filter(citizenship_status__in=[self]).values_list('opportunity__id', flat=True)
        return Opportunity.objects.filter(id__in=opp_ids)

class OpportunityManager(models.Manager):
    def basic_search(self, search_query):
        return self.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(keywords__keyword__icontains=search_query) |
            Q(related_to_major__major__icontains=search_query) |
            Q(related_to_track__track__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(additional_info__icontains=search_query)
        ).distinct()

def url_for_page_not_found():
    return f"https://lrcstaff.umass.edu{reverse('opp_page_not_found')}"

class Opportunity(models.Model):
    title = models.CharField(
        max_length=255,
        null=False,
        blank=False
    )
    
    short_description = models.TextField(
        null=True,
        blank=True
    )
    
    description = models.TextField(
        null=True,
        blank=True
    )
    
    keywords = models.ManyToManyField(
        to=Keyword,
        blank=True,
    )
    
    related_to_major = models.ManyToManyField(
        to=Majors,
        blank=True,
    )
    
    related_to_track = models.ManyToManyField(
        to=Tracks,
        blank=True,
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
        blank=False,
        null=False,
        default=url_for_page_not_found 
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
        default=True
    )
    
    show_on_website_start_date = models.DateField(
        blank=False,
        null=False,
        default=datetime.date.today,
    )
    
    show_on_website_end_date = models.DateField(
        blank=False,
        null=False,
        default=datetime.date(2099, 12, 31),
    )
    
    link_not_working = models.BooleanField(
        default=False
    )
    
    website_data = models.TextField(
        default="",
        blank=True,
        null=True
    )
    
    def __str__(self):
        return self.title
    
    def get_link(self):
        if self.link_not_working:
            return reverse('opp_page_not_found')
        if requests.get(self.link).status_code != 200:
            self.link_not_working = True
            self.save()
            return reverse('opp_page_not_found')
        return self.link
    
    def check_link(self):
        try:
            netloc = urlparse(self.link).netloc
            status = netloc not in ['lrcstaff.umass.edu', 'localhost:8000', '127.0.0.1:8000']
            req = requests.get(self.link, timeout=10) if status else None
            status = status and req.status_code == 200
            if status and (self.link_not_working or self.website_data == ""):
                self.link_not_working = False
                self.website_data = '\n'.join([line for line in req.text.split('\n') if line.strip() != ''])
                self.save()
            if not status:
                self.link_not_working = True
                self.save()
        except:
            self.link_not_working = True
            self.save()
    
    def check_and_get_link(self):
        self.check_link()
        return self.get_link()
    
    objects = OpportunityManager()

class MinGPARestriction(models.Model):
    opportunity = models.OneToOneField(
        to=Opportunity, 
        on_delete=models.CASCADE
    )
    
    gpa = models.DecimalField(
        max_digits=3,
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