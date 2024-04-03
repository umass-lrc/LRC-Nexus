from django import forms
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div

from crispy_bootstrap5.bootstrap5 import FloatingField

from dal import autocomplete
from tinymce.widgets import TinyMCE

from ..models import (
    FacultyDetails,
)

class UpdateFacultyDetailsForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        disabled=True,
    )
    
    last_name = forms.CharField(
        required=True,
        disabled=True,
    )
    
    email = forms.EmailField(
        required=True,
        disabled=True,
    )
    
    class Meta:
        model = FacultyDetails
        fields = ['positions', 'subjects', 'keywords', 'personal_website', 'lab_name', 'lab_website', 'research_outline', 'miscellaneous', 'allowed_to_post_oportunities']
        widgets = {
            'positions': autocomplete.ModelSelect2Multiple(),
            'subjects': autocomplete.ModelSelect2Multiple(),
            'keywords': autocomplete.ModelSelect2Multiple(),
            'personal_website': forms.URLInput(),
            'lab_website': forms.URLInput(),
            'research_outline': TinyMCE(attrs={'cols': 80, 'rows': 30}),
            'miscellaneous': TinyMCE(attrs={'cols': 80, 'rows': 30}),
        }
    
    def __init__(self, *args, **kwargs):
        super(UpdateFacultyDetailsForm, self).__init__(*args, **kwargs)
        
        self.fields['first_name'].initial = self.instance.faculty.first_name
        self.fields['last_name'].initial = self.instance.faculty.last_name
        self.fields['email'].initial = self.instance.faculty.email
        
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('update_faculty_details', kwargs={'faculty_id': self.instance.faculty_id}),
            'hx-swap': f'multi:#ft-{self.instance.faculty_id}:outerHTML,#update-faculty-message',
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    FloatingField('first_name'),
                    FloatingField('last_name'),
                    css_class="row align-items-center justify-content-center"
                ),
                FloatingField('email'),
                FloatingField('positions'),
                FloatingField('subjects'),
                FloatingField('keywords'),
                FloatingField('personal_website'),
                FloatingField('lab_name'),
                FloatingField('lab_website'),
                'research_outline',
                'miscellaneous',
                'allowed_to_post_oportunities',
            ),
            Div(
                Submit('submit', 'Update Faculty Details', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )