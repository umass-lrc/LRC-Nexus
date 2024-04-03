from django import forms
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div

from crispy_bootstrap5.bootstrap5 import FloatingField

from dal import autocomplete
from tinymce.widgets import TinyMCE

from ..models import (
    Opportunity,
)

class CreateOpportunityForm(forms.ModelForm):
    
    class Meta:
        model = Opportunity
        fields = ['title', 'short_description', 'description', 'keywords', 'related_to_major', 'related_to_track', 'on_campus', 'location', 'link', 'deadline', 'additional_info', 'is_paid', 'is_for_credit', 'active', 'show_on_website', 'show_on_website_start_date', 'show_on_website_end_date']
        widgets = {
            'related_to_track': autocomplete.ModelSelect2Multiple(),
            'related_to_major': autocomplete.ModelSelect2Multiple(),
            'keywords': autocomplete.ModelSelect2Multiple(),
            'link': forms.URLInput(),
            'short_description': TinyMCE(attrs={'cols': 80, 'rows': 30}),
            'description': TinyMCE(attrs={'cols': 80, 'rows': 30}),
            'additional_info': TinyMCE(attrs={'cols': 80, 'rows': 30}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'show_on_website_start_date': forms.DateInput(attrs={'type': 'date'}),
            'show_on_website_end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(CreateOpportunityForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper(self)
        if self.instance.id is not None:
            self.helper.attrs = {
                'hx-post': reverse('update_opportunity', kwargs={'opp_id': self.instance.id}),
                'hx-swap': f'multi:#ot-{self.instance.id}:outerHTML,#update-faculty-message',
            }
        else:
            self.helper.attrs = {
                'hx-post': reverse('create_opportunity_form'),
                'hx-swap': f'multi:#create-opportunity-message:outerHTML,#create-opportunity-form:outerHTML',
            }
        self.helper.layout = Layout(
            Fieldset(
                '',
                FloatingField('title'),
                'short_description',
                'description',
                FloatingField('keywords'),
                FloatingField('related_to_major'),
                FloatingField('related_to_track'),
                'on_campus',
                FloatingField('location'),
                FloatingField('link'),
                FloatingField('deadline'),
                'additional_info',
                'is_paid',
                'is_for_credit',
                'active',
                'show_on_website',
                Div(
                    Div(FloatingField('show_on_website_start_date'), css_class='col-6'),
                    Div(FloatingField('show_on_website_end_date'), css_class='col-6'),
                    css_class='row',
                ),
            ),
            Div(
                Submit('submit', 'Update Opportunity' if self.instance.id is not None else 'Create Opportunity', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )