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
    
    class Meta:
        ordering = ['keyword']
    
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
        search_query = search_query.strip()
        search_query_list = []
        i = 0
        while i < len(search_query):
            if search_query[i] == '"':
                start = i
                i += 1
                while i < len(search_query) and search_query[i] != '"':
                    i += 1
                search_query_list.append(search_query[start + 1:i])
                i += 1
            elif search_query[i] == ' ':
                i += 1
            else:
                start = i
                while i < len(search_query) and search_query[i] != ' ':
                    i += 1
                search_query_list.append(search_query[start:i])
        
        search_query_list = [query for query in search_query_list if query != '']
        
        filter_query = [
            (Q(faculty__last_name__icontains=query) |
            Q(faculty__first_name__icontains=query) |
            Q(faculty__email__icontains=query) |
            Q(positions__position__icontains=query) |
            Q(subjects__short_name__icontains=query) |
            Q(subjects__description__icontains=query) |
            Q(keywords__keyword__icontains=query) |
            Q(lab_name__icontains=query) |
            Q(research_outline__icontains=query) |
            Q(miscellaneous__icontains=query)) if search_query_list not in ['AND', 'OR'] else query 
            for query in search_query_list 
        ]
        
        final_query = None
        i = 0    
        while i < len(filter_query):
            if final_query is None:
                if filter_query[i] not in ['AND', 'OR']:
                    final_query = filter_query[i]
            elif filter_query[i] in ['AND', 'OR']:
                j = i + 1
                while j < len(filter_query) and filter_query[j] in ['AND', 'OR']:
                    j += 1
                if j < len(filter_query):
                    final_query = final_query & filter_query[j] if filter_query[i] == 'AND' else final_query | filter_query[j]
                i = j
            else:
                final_query = final_query & filter_query[i]
            i += 1
        return self.all().filter(final_query).distinct()

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
        max_length=500,
        blank=True,
        null=True
    )
    
    lab_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    
    lab_website = models.URLField(
        max_length=500,
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
        search_query = search_query.strip()
        search_query_list = []
        i = 0
        while i < len(search_query):
            if search_query[i] == '"':
                start = i
                i += 1
                while i < len(search_query) and search_query[i] != '"':
                    i += 1
                search_query_list.append(search_query[start + 1:i])
                i += 1
            elif search_query[i] == ' ':
                i += 1
            else:
                start = i
                while i < len(search_query) and search_query[i] != ' ':
                    i += 1
                search_query_list.append(search_query[start:i])
        
        search_query_list = [query for query in search_query_list if query != '']
        
        filter_query = [
            (Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query) |
            Q(keywords__keyword__icontains=query) |
            Q(related_to_major__major__icontains=query) |
            Q(related_to_track__track__icontains=query) |
            Q(location__icontains=query) |
            Q(additional_info__icontains=query)) if query not in ['AND', 'OR'] else query 
            for query in search_query_list 
        ]
        
        final_query = None
        i = 0    
        while i < len(filter_query):
            if final_query is None:
                if filter_query[i] not in ['AND', 'OR']:
                    final_query = filter_query[i]
            elif filter_query[i] in ['AND', 'OR']:
                j = i + 1
                while j < len(filter_query) and filter_query[j] in ['AND', 'OR']:
                    j += 1
                if j < len(filter_query):
                    final_query = final_query & filter_query[j] if filter_query[i] == 'AND' else final_query | filter_query[j]
                i = j
            else:
                final_query = final_query & filter_query[i]
            i += 1
        print(final_query)
        return self.all().filter(final_query).distinct()

# Do not delete this function or else migrations will break
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
        max_length=500,
        blank=False,
        null=False,
        unique=True
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
    
    link_not_working_override = models.BooleanField(
        default=False
    )
    
    website_data = models.TextField(
        default="",
        blank=True,
        null=True
    )
    
    featured = models.BooleanField(
        default=False
    )
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title
    
    def get_link(self):
        if self.link_not_working and not self.link_not_working_override:
            return reverse('opp_page_not_found')
        return self.link
    
    def check_link(self):
        try:
            netloc = urlparse(self.link).netloc
            status = netloc not in ['lrcstaff.umass.edu', 'localhost:8000', '127.0.0.1:8000']
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'upgrade-insecure-requests': '1',
                'dnt': '1',
                'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'priority': 'u=0, i',
                'x-forwarded-proto': 'https',
                'x-https': 'on',
            }
            req = requests.get(self.link, headers=headers, timeout=10) if status else None
            status = status and req.status_code >= 200 and req.status_code < 300
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