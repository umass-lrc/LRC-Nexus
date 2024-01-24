from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div
from django.urls import reverse

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
    
    def __init__(self, edit, *args, **kwargs):
        super(FacultyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        if not edit:
            self.helper.attrs = {
                'hx-post': reverse('create_faculty'),
                'hx-swap': 'multi:#faculty-body:beforeend,#add-faculty-message:innerHTML,#add-faculty-form:innerHTML',
            }
        else:
            self.helper.attrs = {
                'hx-post': reverse('edit_faculty', kwargs={'faculty_id': kwargs['instance'].id}),
                'hx-swap': f'multi:#ft-{kwargs["instance"].id}:innerHTML,#edit-faculty-message:innerHTML',
            }
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
                Submit('submit', 'Add Faculty' if not edit else "Update Faculty", css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )