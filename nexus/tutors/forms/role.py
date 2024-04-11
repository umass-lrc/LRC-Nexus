from django import forms
from django.urls import reverse
from django.contrib.admin import widgets 

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, HTML
from crispy_forms.bootstrap import AccordionGroup

from crispy_bootstrap5.bootstrap5 import  BS5Accordion, FloatingField

from dal import autocomplete

from ..models import (
    TutorRoleInfo,
)

class AssignRoleForm(forms.ModelForm):
    class Meta:
        model = TutorRoleInfo
        fields = ['position', 'assigned_courses']
        widgets = {
            'assigned_courses': autocomplete.ModelSelect2Multiple(url='course-autocomplete'),
        }
    
    def __init__(self, role_id, *args, **kwargs):
        super(AssignRoleForm, self).__init__(*args, **kwargs)
        self.fields['position'].initial = TutorRoleInfo.objects.get(id=role_id).position
        self.fields['position'].widget.attrs['disabled'] = 'True'
        self.fields['assigned_courses'].initial = TutorRoleInfo.objects.get(id=role_id).assigned_courses.all()
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('tutor_update_role', kwargs={'role_id': role_id}),
            'hx-swap': f'multi:#rt-{role_id}:innerHTML,#update-role-message:innerHTML,#update-role-form:innerHTML',
        }
        self.helper.layout = Layout(
            Fieldset(
                "",
                FloatingField('position'),
                FloatingField('assigned_courses'),
            ),
            Div(
                Submit('submit', 'Update Role', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )
