from django import forms
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div

from crispy_bootstrap5.bootstrap5 import FloatingField

from ..models import (
    PositionGroups,
)

class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = PositionGroups
        fields = ['name']
    
    def __init__(self, *args, **kwargs):
        super(CreateGroupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('create_group'),
            'hx-swap': 'multi:#groups-body:beforeend,#add-group-message:innerHTML,#add-group-form:outerHTML',
        }
        self.helper.layout = Layout(
            Div(
                FloatingField('name', css_class='col-md-8 justify-content-center'),
                Div(
                    Submit('submit', 'Create Group', css_class='btn btn-primary'),
                    css_class='text-center col-md-4 justify-content-center',
                ),
                css_class='row align-items-center justify-content-center',
            ),
        )