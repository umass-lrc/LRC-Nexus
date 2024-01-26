from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, HTML

from crispy_forms.bootstrap import AccordionGroup, PrependedText
from crispy_bootstrap5.bootstrap5 import FloatingField, BS5Accordion
from django.urls import reverse

from ..models import (
    Course,
    Semester,
    Classes,
    ClassTimes,
    Faculty,
)

class semesterSelector(forms.Form):
    semester = forms.ModelChoiceField(queryset=Semester.objects.all(), required=True)
    
    def __init__(self, *args, **kwargs):
        super(semesterSelector, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('all_classes'),
            'hx-swap': 'multi:#classes-body:innerHTML,#semester-form-message:innerHTML,#edit-class-message:innerHTML,#edit-class-form:innerHTML,#add-class-message:innerHTML,#add-class-form:innerHTML',
        }
        self.helper.layout = Layout(
            Div(
                Div(
                    FloatingField('semester'),
                    css_class='col-md-8 justify-content-center',
                ),
                Div(
                    Submit('submit', 'Select Semester', css_class='btn btn-primary'),
                    css_class='col-md-4 justify-content-center text-center',
                    style='margin-bottom:1rem;'
                ),
                css_class='row align-items-center',
            )
        )
        
class createClassForm(forms.ModelForm):
    class Meta:
        model = Classes
        fields = [
            'semester',
            'course',
            'faculty',
        ]
        widgets = {
            'semester': forms.Select(choices=Semester.objects.all(), attrs={'disabled': 'disabled'}),
            'course': forms.Select(choices=Course.objects.all()),
            'faculty': forms.Select(choices=Faculty.objects.all()),
        }
    
    def __init__(self, *args, edit=False, **kwargs):
        super(createClassForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        if not edit:
            self.helper.attrs = {
                'hx-post': reverse('create_class', kwargs={'semester_id': kwargs['initial']['semester'].id}),
                'hx-swap': 'multi:#classes-body:beforeend,#add-class-message:innerHTML,#add-class-form:innerHTML',
            }
        else:
            self.helper.attrs = {
                'hx-post': reverse('edit_class', kwargs={'class_id': kwargs['instance'].id}),
                'hx-swap': f'multi:#ct-{kwargs["instance"].id}:innerHTML,#edit-class-message:innerHTML',
            }
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('semester'),
                FloatingField('course'),
                FloatingField('faculty'),
            ),
            Div(
                Submit('submit', 'Add Class' if not edit else 'Update Class', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )
class addClassTimeForm(forms.ModelForm):
    hours = forms.IntegerField(min_value=0, max_value=24, required=True)
    minutes = forms.IntegerField(min_value=0, max_value=59, required=True)
    class Meta:
        model = ClassTimes
        fields = [
            'class_day',
            'start_time',
            'building',
            'room',
        ]
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, class_id, *args, **kwargs):
        super(addClassTimeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('add_class_time', kwargs={'class_id': class_id}),
            'hx-swap': f"multi:#class-times-body:beforeend,#ct-{class_id}:innerHTML,#add-class-time-message:innerHTML,#add-class-time-form:innerHTML"
        }
        self.helper.layout = Layout(
            BS5Accordion(
                AccordionGroup(
                    "Add Class Time",
                    Fieldset(
                        '',
                        FloatingField('class_day'),
                        FloatingField('start_time'),
                        HTML("""
                            <label class="form-label requiredField">Duration<span class="asteriskField">*</span></label>
                        """),
                        Div(
                            Div(
                                FloatingField('hours'),
                                css_class='col-md-6',
                            ),
                            Div(
                                FloatingField('minutes'),
                                css_class='col-md-6',
                            ),
                            css_class='row',
                        ),
                        FloatingField('building'),
                        FloatingField('room'),
                    ),
                    Div(
                        Submit('submit', 'Add Class Time', css_class='btn btn-primary'),
                        css_class='text-center',
                    ),
                    active=False,
                ),
            ),
            )