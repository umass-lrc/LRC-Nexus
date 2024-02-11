from django import forms
from django.urls import reverse
from django.contrib.admin import widgets 

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, HTML
from crispy_forms.bootstrap import AccordionGroup

from crispy_bootstrap5.bootstrap5 import  BS5Accordion, FloatingField

from dal import autocomplete

from users.models import (
    PositionChoices,
)

from ..models import (
    Payroll,
    PayrollStatus,
)

class WeekSelectForm(forms.Form):
    week = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
            }
        ),
        required=True,
    )
    
    position = forms.MultipleChoiceField(
        choices=PositionChoices.choices,
        widget=autocomplete.ModelSelect2Multiple(),
        initial=[ps[0] for ps in PositionChoices.choices],
        required=True,
    )
    
    def __init__(self, *args, **kwargs):
        super(WeekSelectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('all_weekly_payroll'),
            'hx-target': '#payroll-body',
            'hx-swap': 'outerHTML',
        }
        self.helper.layout = Layout(
            Div(
                Div(
                    FloatingField('week'),
                    css_class="col-md-4 justify-content-center",
                ),
                Div(
                    FloatingField('position'),
                    css_class="col-md-4 justify-content-center",
                ),
                Div(
                    Submit('submit', 'Get Payroll', css_class='btn btn-primary'),
                    css_class="d-flex text-center col-md-4 justify-content-center",
                ),
                css_class="row align-items-center justify-content-center"
            )
        )

class StatusForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        disabled=True,
    )
    position = forms.CharField(
        required=True,
        disabled=True,
    )
    
    class Meta:
        model = Payroll
        fields = [
            "status",
        ]
        widgets = {
            "status": forms.Select(choices=PayrollStatus.choices),
        }
    
    def __init__(self, *args, **kwargs):
        super(StatusForm, self).__init__(*args, **kwargs)
        self.fields['name'].initial = str(self.instance.position.user)
        self.fields['position'].initial = self.instance.position.get_position_display()
        self.fields['status'].help_text = ""
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div(
                FloatingField('name'),
                FloatingField('position'),
                FloatingField('status',
                    hx_post=reverse('single_weekly_payroll', kwargs={'payroll_id': self.instance.id}),
                    hx_target=f"#payroll-{self.instance.id}",
                    hx_swap="outerHTML",
                ),
                css_class="row align-items-center justify-content-center"
            )
        )