from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div

from crispy_bootstrap5.bootstrap5 import FloatingField

from ..models import (
    NexusUser,
)

class CreateUserForm(forms.ModelForm):
    class Meta:
        model = NexusUser
        fields = ['email', 'first_name', 'last_name']
    
    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('email'),
                FloatingField('first_name'),
                FloatingField('last_name'),
            ),
            Div(
                Submit('submit', 'Create User', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )