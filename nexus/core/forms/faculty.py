from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div
from crispy_forms.bootstrap import AccordionGroup

from crispy_bootstrap5.bootstrap5 import BS5Accordion

from ..models import (
    Faculty,
)

class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = (
            'first_name',
            'last_name',
            'email',
        )
    
    def __init__(self, *args, button=None, **kwargs):
        super(FacultyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Div('first_name', css_class='col-md-6'),
                    Div('last_name', css_class='col-md-6'),
                    css_class='row',
                ),
                'email',
            ),
            Div(
                Submit('submit', 'Add Faculty' if button is None else button, css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )