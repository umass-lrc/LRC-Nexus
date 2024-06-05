from django import forms
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, HTML

from crispy_bootstrap5.bootstrap5 import FloatingField

from dal import autocomplete
from tinymce.widgets import TinyMCE

from ..models import (
    Opportunity,
    Majors,
    CitizenshipStatus,
    StudyLevel,
    MinGPARestriction,
    MajorRestriction,
    CitizenshipRestriction,
    StudyLevelRestriction,
)

class CreateOpportunityForm(forms.ModelForm):
    min_gpa = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        required=False,
        label='Minimum GPA',
        help_text='Minimum GPA required to apply for this opportunity.',
    )
    
    restricted_majors = forms.ModelMultipleChoiceField(
        queryset=Majors.objects.all(),
        required=False,
        label='Restricted to Majors',
        widget=autocomplete.ModelSelect2Multiple(),
        help_text='Select the majors that are allowed to apply for this opportunity.',
    )
    
    require_all_majors = forms.BooleanField(
        required=False,
        initial=False,
        label='Require All Majors',
        help_text='Check this box if the applicant must be part of all the majors listed as part of restricted to majors.',
    )
    
    restricted_to_citizenship_status = forms.ModelMultipleChoiceField(
        queryset=CitizenshipStatus.objects.all(),
        required=False,
        label='Restricted to Citizenship Status',
        widget=autocomplete.ModelSelect2Multiple(),
        help_text='Select the citizenship statuses that are allowed to apply for this opportunity.',
    )
    
    restricted_to_study_level = forms.ModelMultipleChoiceField(
        queryset=StudyLevel.objects.all(),
        required=False,
        label='Restricted to Study Level',
        widget=autocomplete.ModelSelect2Multiple(),
        help_text='Select the study levels that are allowed to apply for this opportunity.',
    )
    
    class Meta:
        model = Opportunity
        fields = ['title', 'short_description', 'description', 'keywords', 'related_to_major', 'related_to_track', 'on_campus', 'location', 'link', 'deadline', 'additional_info', 'is_paid', 'is_for_credit', 'active', 'show_on_website', 'show_on_website_start_date', 'show_on_website_end_date']
        widgets = {
            'related_to_track': autocomplete.ModelSelect2Multiple(),
            'related_to_major': autocomplete.ModelSelect2Multiple(),
            'keywords': autocomplete.ModelSelect2Multiple(url='autocomplete-keyword',attrs={'data-tags': 'true'}),
            'link': forms.URLInput(),
            'short_description': TinyMCE(attrs={'cols': 80, 'rows': 30}),
            'description': TinyMCE(attrs={'cols': 80, 'rows': 30}),
            'additional_info': TinyMCE(attrs={'cols': 80, 'rows': 30}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'show_on_website_start_date': forms.DateInput(attrs={'type': 'date'}),
            'show_on_website_end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, check_opportunity=False, **kwargs):
        super(CreateOpportunityForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper(self)
        if self.instance.id is not None:
            self.helper.attrs = {
                'hx-post': reverse('update_opportunity' if not check_opportunity else 'check_opp_update_opportunity', kwargs={'opp_id': self.instance.id}),
                'hx-swap': f'multi:#ot-{self.instance.id}:outerHTML,#update-opportunity-message',
                'onsubmit': 'tinyMCE.triggerSave()',
            }
            
            min_gpa = MinGPARestriction.objects.filter(opportunity=self.instance).first()
            if min_gpa:
                self.initial['min_gpa'] = min_gpa.gpa
            major_restriction = MajorRestriction.objects.filter(opportunity=self.instance).first()
            if major_restriction:
                self.initial['restricted_majors'] = major_restriction.majors.all()
                self.initial['require_all_majors'] = major_restriction.must_be_all_majors
            citizenship_restriction = CitizenshipRestriction.objects.filter(opportunity=self.instance).first()
            if citizenship_restriction:
                self.initial['restricted_to_citizenship_status'] = citizenship_restriction.citizenship_status.all()
            study_level_restriction = StudyLevelRestriction.objects.filter(opportunity=self.instance).first()
            if study_level_restriction:
                self.initial['restricted_to_study_level'] = study_level_restriction.study_level.all()
            
        else:
            self.helper.attrs = {
                'hx-post': reverse('create_opportunity_form'),
                'hx-swap': f'multi:#create-opportunity-message:outerHTML,#create-opportunity-form:outerHTML',
                'onsubmit': 'tinyMCE.triggerSave()',
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
                Div(
                    HTML('<h4>Restrictions</h4>'),
                    Div(
                        FloatingField('min_gpa'),
                        FloatingField('restricted_majors'),
                        'require_all_majors',
                        FloatingField('restricted_to_citizenship_status'),
                        FloatingField('restricted_to_study_level'),
                        style="margin-left: 2rem;"
                    ),
                ),
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

class SimpleSearchForm(forms.Form):
    search = forms.ModelChoiceField(
        required=False,
        label='',
        queryset=Opportunity.objects.all(),
        widget=autocomplete.ModelSelect2(url='autocomplete-opportunity', attrs={'data-tags': 'true'}),
    )
    
    def __init__(self, *args, **kwargs):
        super(SimpleSearchForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('opportunities_list'),
            'hx-target': f'#roles_body',
        }
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Fieldset(
                'Basic Search',
                Div(
                    Div(
                        FloatingField('search'),
                        css_class='col-md-9 justify-content-center',
                    ),
                    Div(
                        Submit('submit', 'Search', css_class='btn btn-primary'),
                        css_class='col-md-3 text-center justify-content-center',
                    ),
                    css_class='row',
                ),
            ),
        )