from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div
from crispy_forms.bootstrap import AccordionGroup

from crispy_bootstrap5.bootstrap5 import BS5Accordion
from django.urls import reverse

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
    
    def __init__(self, edit, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        if not edit:
            self.helper.attrs = {
                'hx-post': reverse('create_course'),
                'hx-swap': 'multi:#course-body:beforeend,#add-course-message:innerHTML,#add-course-form:innerHTML',
            }
        else:
            self.helper.attrs = {
                'hx-post': reverse('edit_course', kwargs={'course_id': kwargs['instance'].id}),
                'hx-swap': f'multi:#ct-{kwargs["instance"].id}:innerHTML,#edit-course-message:innerHTML',
            }
        self.helper.layout = Layout(
            Fieldset(
                '',
                'subject',
                'number',
                'name',
                'is_cross_listed',
                'main_course'
            ),
            Div(
                Submit('submit', 'Add Course' if not edit else 'Update Course', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )