from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div

from crispy_bootstrap5.bootstrap5 import FloatingField

from ..models import (
    NexusUser,
)

class LogInForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    password = forms.CharField(label="Password", required=True, widget=forms.PasswordInput())
    
    def __init__(self, *args, **kwargs):
        super(LogInForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('email'),
                FloatingField('password'),
            ),
            Div(
                Submit('submit', 'Log In', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )