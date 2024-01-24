from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div
from crispy_forms.bootstrap import AccordionGroup

from crispy_bootstrap5.bootstrap5 import BS5Accordion
from django.urls import reverse

from ..models import (
    Semester,
    Holiday,
    DaySwitch,
)

class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = (
            'term',
            'year',
            'classes_start',
            'classes_end',
        )
        widgets = {
            'classes_start': forms.DateInput(attrs={'type': 'date'}),
            'classes_end': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(SemesterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('create_semester'),
            'hx-swap': 'multi:#semester-body:beforeend,#add-semester-message:innerHTML,#add-semester-form:innerHTML',
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                'term',
                'year',
                'classes_start',
                'classes_end',
            ),
            Div(
                Submit('submit', 'Add Semester', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )

class SemesterReadOnly(forms.ModelForm):
    class Meta:
        model = Semester
        fields = (
            'term',
            'year',
            'classes_start',
            'classes_end',
            'active'
        )
        widgets = {
            'term': forms.Select(choices=Semester.Terms, attrs={'disabled': True}),
            'year': forms.NumberInput(attrs={'disabled': True}),
            'classes_start': forms.DateInput(attrs={'type': 'date', 'disabled': True}),
            'classes_end': forms.DateInput(attrs={'type': 'date', 'disabled': True}),
            'active': forms.CheckboxInput(attrs={'disabled': True}),
        }
    
    def __init__(self, *args, **kwargs):
        super(SemesterReadOnly, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset(
                "You can't edit the basics of a semester once it's created. If you need to change something, you can delete the semester and create a new one.",
                'term',
                'year',
                'active',
                'classes_start',
                'classes_end',
            ),
        )

class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = (
            'date',
        )
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, semester_id, *args, **kwargs):
        super(HolidayForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('add_holiday', kwargs={'semester_id': semester_id}),
            'hx-target': '#holidays',
        }
        self.helper.layout = Layout(
            BS5Accordion(
                AccordionGroup(
                    "Add Holiday", 
                    "date", 
                    Div(
                        Submit('submit', 'Add Holiday', css_class='btn btn-primary'),
                        css_class='text-center',
                    ),
                    active=False,
                ),
            ),
        )

class DaySwitchForm(forms.ModelForm):
    class Meta:
        model = DaySwitch
        fields = (
            'date',
            'day_to_follow',
        )
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, semester_id, *args, **kwargs):
        super(DaySwitchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('add_day_switch', kwargs={'semester_id': semester_id}),
            'hx-target': '#day_switches',
        }
        self.helper.layout = Layout(
            BS5Accordion(
                AccordionGroup(
                    "Add Day Switch", 
                    "date",
                    "day_to_follow", 
                    Div(
                        Submit('submit', 'Add Day Switch', css_class='btn btn-primary'),
                        css_class='text-center',
                    ),
                    active=False,
                ),
            ),
        )