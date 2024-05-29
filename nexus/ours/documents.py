from django_elasticsearch_dsl import Document, fields
from elasticsearch_dsl import analyzer, tokenizer
from django_elasticsearch_dsl.registries import registry

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

from core.models import (
    CourseSubject,
)

html_strip = analyzer(
    "html_strip",
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"],
)

@registry.register_document
class KeywordDocument(Document):
    class Index:
        name = "keywords"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Keyword
        fields = ["keyword"]

@registry.register_document
class FacultyDetailsDocument(Document):
    faculty = fields.ObjectField(properties={
        "first_name": fields.TextField(),
        "last_name": fields.TextField(),
        "email": fields.TextField(),
    })
    
    position = fields.ObjectField(properties={
        "position": fields.TextField(),
    })
    
    subjects = fields.NestedField(properties={
        "subject": fields.TextField(),
    })
    
    keywords = fields.NestedField(properties={
        "keyword": fields.TextField(),
    })
    
    research_outline = fields.TextField(attr="research_outline", analyzer=html_strip)
    
    miscellaneous = fields.TextField(attr="miscellaneous", analyzer=html_strip)
    
    class Index:
        name = "faculty_details"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = FacultyDetails
        fields = [
            "lab_name",
        ]
        related_models = [FacultyPosition, Keyword, CourseSubject]
        
    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, FacultyPosition):
            return related_instance.facultydetails_set.all()
        elif isinstance(related_instance, Keyword):
            return related_instance.facultydetails_set.all()
        elif isinstance(related_instance, CourseSubject):
            return related_instance.facultydetails_set.all()
        return related_instance

@registry.register_document
class OpportunityDocument(Document):
    
    short_description = fields.TextField(attr="short_description", analyzer=html_strip)
    
    description = fields.TextField(attr="description", analyzer=html_strip)
    
    website_data = fields.TextField(attr="website_data", analyzer=html_strip)
    
    keywords = fields.NestedField(properties={
        "keyword": fields.TextField(),
    })
    
    related_to_major = fields.NestedField(properties={
        "major": fields.TextField(),
    })
    
    related_to_track = fields.NestedField(properties={
        "track": fields.TextField(),
    })
    
    additional_information = fields.TextField(attr="additional_information", analyzer=html_strip)
    
    class Index:
        name = "opportunities"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Opportunity
        fields = [
            "title",
            "location",
            "deadline",
            "active",
            "show_on_website",
            "show_on_website_start_date",
            "show_on_website_end_date",
        ]
        related_models = [Keyword, Majors, Tracks, CitizenshipStatus]
    
    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Keyword):
            return related_instance.opportunity_set.all()
        elif isinstance(related_instance, Majors):
            return related_instance.opportunity_set.all()
        elif isinstance(related_instance, Tracks):
            return related_instance.opportunity_set.all()
        elif isinstance(related_instance, CitizenshipStatus):
            return related_instance.opportunity_set().all()
        return related_instance