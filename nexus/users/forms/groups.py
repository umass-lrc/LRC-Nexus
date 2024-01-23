from django import forms
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div

from crispy_bootstrap5.bootstrap5 import FloatingField

from dal import autocomplete

from ..models import (
    PositionGroups,
    Positions,
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
                Div(
                    FloatingField('name'),
                    css_class='col-md-8 justify-content-center',
                ),
                Div(
                    Submit('submit', 'Create Group', css_class='btn btn-primary'),
                    css_class='d-flex text-center col-md-4 justify-content-center',
                    style='margin-bottom:2rem;'
                ),
                css_class='row align-items-center justify-content-center',
            ),
        )

class AddGroupMemeberForm(forms.Form):
    member = forms.ModelChoiceField(
        queryset=Positions.objects.all(),
        widget=autocomplete.ModelSelect2(url='position_autocomplete'),
        required=True,
    )
    
    def __init__(self, group_id, *args, **kwargs):
        super(AddGroupMemeberForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('add_group_member', kwargs={'group_id': group_id}),
            'hx-swap': 'multi:#members-body:beforeend,#add_member_form_message:innerHTML',
        }
        self.helper.layout = Layout(
            Div(
                Div(
                    'member',
                    css_class='col-md-8 justify-content-center',
                ),
                Div(
                    Submit('submit', 'Add Member', css_class='btn btn-primary'),
                    css_class='d-flex text-center col-md-4 justify-content-center',
                ),
                css_class='row align-items-center justify-content-center',
            ),
        )