from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div
from crispy_forms.bootstrap import AccordionGroup

from crispy_bootstrap5.bootstrap5 import BS5Accordion, FloatingField
from django.urls import reverse

from core.models import (
    Buildings,
)

from shifts.models import (
    ShiftKind,
)

class PunchInForm(forms.Form):
    building = forms.ModelChoiceField(queryset=Buildings.objects.all(), required=True)
    room = forms.CharField(max_length=10, required=True)
    kind = forms.ChoiceField(choices=ShiftKind.choices, required=True)
    
    def __init__(self, position, *args, **kwargs):
        super(PunchInForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('punch_in_out_position', kwargs={'position_id': position.id}),
            'hx-swap': f'multi:#punch-in-out-form-{position.id}:innerHTML,#punch-in-out-message:innerHTML',
        }
        self.helper.layout = Layout(
            BS5Accordion(
                AccordionGroup(
                    str(position),
                    FloatingField('building'),
                    FloatingField('room'),
                    FloatingField('kind'),
                    Div(
                        Submit('submit', 'Punch In', css_class='btn btn-primary'),
                        css_class='text-center',
                    ),
                    active=False,
                ),
            ),
        )

class PunchOutForm(forms.Form):
    building = forms.ModelChoiceField(queryset=Buildings.objects.all(), required=True)
    room = forms.CharField(max_length=10, required=True)
    kind = forms.ChoiceField(choices=ShiftKind.choices, required=True)
    
    def __init__(self, position, *args, **kwargs):
        super(PunchOutForm, self).__init__(*args, **kwargs)
        
        self.fields['building'].initial = kwargs['initial']['building']
        self.fields['room'].initial = kwargs['initial']['room']
        self.fields['kind'].initial = kwargs['initial']['kind']
        
        self.fields['building'].disabled = True
        self.fields['room'].disabled = True
        self.fields['kind'].disabled = True
        
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('punch_in_out_position', kwargs={'position_id': position.id}),
            'hx-swap': f'multi:#punch-in-out-form-{position.id}:innerHTML,#punch-in-out-message:innerHTML',
        }
        self.helper.layout = Layout(
            BS5Accordion(
                AccordionGroup(
                    str(position),
                    Div(
                        Submit('submit', 'Punch Out', css_class='btn btn-primary'),
                        css_class='text-center',
                    ),
                    active=True,
                ),
            ),
        )