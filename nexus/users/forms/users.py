from django import forms
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div
from crispy_bootstrap5.bootstrap5 import FloatingField
from ..models import NexusUser

class CreateUserForm(forms.ModelForm):
    class Meta:
        model = NexusUser
        fields = ['email', 'first_name', 'last_name']
    
    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('create_user'),
            'hx-target': '#create_user_form_message',
        }
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

class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = NexusUser
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.TextInput(attrs={'readonly': True}),
        }
    
    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('update_user', kwargs={'user_id': self.instance.id}),
            'hx-swap': f'multi:#ut-{self.instance.id}:outerHTML,#update_user_form_message',
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('email'),
                FloatingField('first_name'),
                FloatingField('last_name'),
            ),
            Div(
                Submit('submit', 'Update User', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )

class SearchUserForm(forms.Form):
    query = forms.CharField(
        label="Search ",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter search term...'})
    )

    def __init__(self, *args, **kwargs):
        super(SearchUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            FloatingField('query'),
            Div(
                Submit('search', 'Search', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )
        