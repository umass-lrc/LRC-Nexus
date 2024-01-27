from django import forms
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div

from crispy_bootstrap5.bootstrap5 import FloatingField

class loadUsersForm(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(loadUsersForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('load_users'),
            'hx-swap': 'multi:#load-users-message:innerHTML,#load-users-logs:innerHTML',
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('file'),
            ),
            Div(
                Submit('submit', 'Load Users', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )