from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div
from crispy_forms.bootstrap import AccordionGroup

from crispy_bootstrap5.bootstrap5 import BS5Accordion

from ..models import (
    Course,
    CourseSubject,
)

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = (
            'subject',
            'number',
            'name',
            'is_cross_listed',
            'main_course'
        )
        widgets = {
            'subject': forms.Select(choices=CourseSubject.objects.all()),
            'main_course': forms.Select(choices=Course.objects.all()),
        }