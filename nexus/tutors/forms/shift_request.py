from django import forms
from django.urls import reverse
from django.contrib.admin import widgets 

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, HTML
from crispy_forms.bootstrap import AccordionGroup

from crispy_bootstrap5.bootstrap5 import  BS5Accordion, FloatingField

from dal import autocomplete

from shifts.models import (
    ChangeRequest,
    DropRequest,
)

class AddRequestForm(forms.ModelForm):
    hours = forms.IntegerField(min_value=0, max_value=24, required=True)
    minutes = forms.IntegerField(min_value=0, max_value=59, required=True)
    
    class Meta:
        model = ChangeRequest
        fields = [
            'position',
            'start',
            'building',
            'room',
            'kind',
            'require_punch_in_out',
        ]
        widgets = {
            'start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(AddRequestForm, self).__init__(*args, **kwargs)
        self.fields['position'].queryset = self.fields['position'].queryset.filter(
            user = kwargs['instance'].position.user,
            semester = kwargs['instance'].position.semester,
        )
        self.fields['hours'].initial = kwargs['instance'].duration.seconds // 3600
        self.fields['minutes'].initial = (kwargs['instance'].duration.seconds // 60) % 60
        self.helper = FormHelper()
        self.helper.attrs = {
            'hx-post': reverse('tutor_add_request_form', kwargs={'req_id': kwargs['instance'].id}),
            'hx-swap': f'multi:#art-{kwargs["instance"].id}:innerHTML,#request-message:innerHTML,#request-form:innerHTML',
        }
        self.helper.layout = Layout(
            HTML('{% include "add_request_details.html" %}'),
            Fieldset(
                'Edit Request',
                'position',
                'start',
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
                'building',
                'room',
                'kind',
                'require_punch_in_out',
            ),
            Div(
                Div(
                    Submit('deney', 'Deny Request',  css_class="btn btn-danger"),
                    css_class="col-4 d-block mx-auto",
                ),
                Div(
                    Submit('update', 'Update Request',  css_class="btn btn-warning"),
                    css_class="col-4 d-block mx-auto",
                ),
                Div(
                    Submit('update_and_approve', 'Update & Approve Request',  css_class="btn btn-primary"),
                    css_class="col-4 d-block mx-auto",
                ),
                css_class="row justify-content-center",
            ),
        )


class ChangeRequestForm(forms.ModelForm):
    hours = forms.IntegerField(min_value=0, max_value=24, required=True)
    minutes = forms.IntegerField(min_value=0, max_value=59, required=True)
    
    class Meta:
        model = ChangeRequest
        fields = [
            'position',
            'start',
            'building',
            'room',
            'kind',
            'require_punch_in_out',
        ]
        widgets = {
            'start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ChangeRequestForm, self).__init__(*args, **kwargs)
        self.fields['position'].queryset = self.fields['position'].queryset.filter(
            user = kwargs['instance'].shift.position.user,
            semester = kwargs['instance'].shift.position.semester,
        )
        if kwargs['instance'].position is None:
            self.initial['position'] = kwargs['instance'].shift.position
        self.fields['hours'].initial = kwargs['instance'].duration.seconds // 3600
        self.fields['minutes'].initial = (kwargs['instance'].duration.seconds // 60) % 60
        self.helper = FormHelper()
        self.helper.attrs = {
            'hx-post': reverse('tutor_change_request_form', kwargs={'req_id': kwargs['instance'].id}),
            'hx-swap': f'multi:#crt-{kwargs["instance"].id}:innerHTML,#request-message:innerHTML,#request-form:innerHTML',
        }
        self.helper.layout = Layout(
            HTML('{% include "change_request_details.html" %}'),
            Fieldset(
                'Edit Request',
                'position',
                'start',
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
                'building',
                'room',
                'kind',
                'require_punch_in_out',
            ),
            Div(
                Div(
                    Submit('deney', 'Deny Request',  css_class="btn btn-danger"),
                    css_class="col-4 d-block mx-auto",
                ),
                Div(
                    Submit('update', 'Update Request',  css_class="btn btn-warning"),
                    css_class="col-4 d-block mx-auto",
                ),
                Div(
                    Submit('update_and_approve', 'Update & Approve Request',  css_class="btn btn-primary"),
                    css_class="col-4 d-block mx-auto",
                ),
                css_class="row justify-content-center",
            ),
        )