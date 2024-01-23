from django import forms
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div

from crispy_bootstrap5.bootstrap5 import FloatingField

from core.models import (
    Semester,
)

from ..models import (
    PositionChoices,
    Positions,
    NexusUser,
)

class PositionSelector(forms.Form):
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all(),
        label='Semester',
        required=True,
        help_text='Select the semester you want to view positions for.'
    )
    
    position = forms.ChoiceField(
        choices=PositionChoices.choices,
        required=True,
        label='Position',
        help_text='Select the position you want to view.'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('positions'),
            'hx-swap': 'multi:#positions-body:outerHTML,#add-position-form:outerHTML'
        }
        self.helper.layout = Layout(
            Div(
                Div(
                    FloatingField('semester'),
                    css_class='col-md-5 justify-content-center'
                ),
                Div(
                    FloatingField('position'),
                    css_class='col-md-5 justify-content-center'
                ),
                Div(
                    Submit('submit', 'Search', css_class='btn btn-primary'),
                    css_class='d-flex col-md-2 justify-content-center',
                    style='margin-bottom:2rem;'
                ),
                css_class='row align-items-center'
            ),
        )

class PositionForm(forms.ModelForm):
    class Meta:
        model = Positions
        fields = ['semester', 'position', 'user', 'hourly_pay']
        widgets = {
            'semester': forms.Select(choices=Semester.objects.all(), attrs={'disabled': 'disabled'}),
            'position': forms.Select(choices=PositionChoices.choices, attrs={'disabled': 'disabled'}),
            'user': forms.Select(choices=NexusUser.objects.all()),
            'hourly_pay': forms.NumberInput(attrs={'min': 0.00, 'max': 999.99, 'step': 0.01}),
        }
    
    def __init__(self, *args, **kwargs):
        super(PositionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('add_position', kwargs={'semester_id': self.initial.get('semester'), 'position_id': self.initial.get('position')}),
            'hx-swap': 'multi:#positions-body:outerHTML,#add-position-message',
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('semester'),
                FloatingField('position'),
                FloatingField('user'),
                FloatingField('hourly_pay'),
            ),
            Div(
                Submit('submit', 'Add Position', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )