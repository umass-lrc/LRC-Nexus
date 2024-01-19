from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div

from ..models import (
    Buildings,
)

class BuildingsForm(forms.ModelForm):
    class Meta:
        model = Buildings
        fields = (
            'short_name',
            'name',
        )
    
    def __init__(self, *args, button=None, **kwargs):
        super(BuildingsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Div('short_name', css_class='col-md-6'),
                    Div('name', css_class='col-md-6'),
                    css_class='row',
                ),
            ),
            Div(
                Submit('submit', 'Add Building' if button is None else button, css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )