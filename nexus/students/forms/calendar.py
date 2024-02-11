from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, HTML
from crispy_forms.bootstrap import AccordionGroup

from crispy_bootstrap5.bootstrap5 import BS5Accordion, FloatingField
from django.urls import reverse

from core.models import (
    Buildings,
    Semester,
)

from shifts.models import (
    ShiftKind,
    ChangeRequest,
    DropRequest,
)

from users.models import (
    Positions,
)

class AddShiftRequestForm(forms.ModelForm):
    hours = forms.IntegerField(min_value=0, max_value=24, required=True)
    minutes = forms.IntegerField(min_value=0, max_value=59, required=True)
    
    class Meta:
        model = ChangeRequest
        fields = ['position', 'start', 'building', 'room', 'kind', 'reason']
        widgets = {
            'start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, user, *args, **kwargs):
        super(AddShiftRequestForm, self).__init__(*args, **kwargs)
        self.fields['position'].queryset = Positions.objects.filter(user=user, semester=Semester.objects.get_active_semester()).all()
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('add_shift_request'),
            'hx-swap': 'multi:#add-shift-message:innerHTML,#add-shift-form:innerHTML',
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('position'),
                FloatingField('start'),
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
                FloatingField('kind'),
                FloatingField('reason'),
                Div(
                    Submit('submit', 'Make Add Request', css_class='btn btn-primary'),
                    css_class='text-center',
                ),
            ),
        )

class ChangeShiftRequestForm(forms.ModelForm):
    hours = forms.IntegerField(min_value=0, max_value=24, required=True)
    minutes = forms.IntegerField(min_value=0, max_value=59, required=True)
    
    class Meta:
        model = ChangeRequest
        fields = ['shift', 'start', 'building', 'room', 'kind', 'reason']
        widgets = {
            'start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, shift, *args, **kwargs):
        super(ChangeShiftRequestForm, self).__init__(*args, **kwargs)
        self.fields['shift'].initial = shift
        self.fields['shift'].widget.attrs['disabled'] = True
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('change_shift_request', kwargs={'shift_id': shift.id}),
            'hx-swap': 'multi:#shift-request-message:innerHTML,#shift-request:innerHTML',
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('shift'),
                FloatingField('start'),
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
                FloatingField('kind'),
                FloatingField('reason'),
                Div(
                    Submit('submit', 'Make Change Request', css_class='btn btn-primary'),
                    css_class='text-center',
                ),
            ),
        )
        
class DropShiftRequestForm(forms.ModelForm):
    class Meta:
        model = DropRequest
        fields = ['shift', 'reason']
    
    def __init__(self, shift, *args, **kwargs):
        super(DropShiftRequestForm, self).__init__(*args, **kwargs)
        self.fields['shift'].initial = shift
        self.fields['shift'].widget.attrs['disabled'] = True
        self.fields['shift'].required = False
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('drop_shift_request', kwargs={'shift_id': shift.id}),
            'hx-swap': 'multi:#shift-request-message:innerHTML,#shift-request:innerHTML',
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('shift'),
                FloatingField('reason'),
                Div(
                    Submit('submit', 'Make Drop Request', css_class='btn btn-primary'),
                    css_class='text-center',
                ),
            ),
        )