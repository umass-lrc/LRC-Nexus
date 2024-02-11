from django import forms
from django.urls import reverse
from django.contrib.admin import widgets 

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, HTML
from crispy_forms.bootstrap import AccordionGroup

from crispy_bootstrap5.bootstrap5 import  BS5Accordion, FloatingField

from dal import autocomplete

from core.models import (
    Semester,
    Buildings,
)

from users.models import (
    NexusUser,
    Positions,
    PositionGroups,
)

from ..models import (
    Shift,
    RecurringShift,
)


class SelectGroup(forms.Form):
    group = forms.ModelChoiceField(
        queryset=PositionGroups.objects.all(),
        widget=autocomplete.ModelSelect2(url='group-autocomplete'),
        required=True,
    )
    
    def __init__(self, *args, **kwargs):
        super(SelectGroup, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('group_shift'),
            'hx-swap': 'multi:#members-body:innerHTML,#look-up-form-message:innerHTML,#add-shift-message:innerHTML,#add-shift-form:innerHTML',
        }
        self.helper.layout = Layout(
            Div(
                Div(
                    'group',
                    css_class='col-md-8 justify-content-center',
                ),
                Div(
                    Submit('submit', 'Look Up', css_class='btn btn-primary'),
                    css_class='d-flex text-center col-md-4 justify-content-center',
                ),
                css_class='row align-items-center justify-content-center',
            ),
        )

class BulkShiftAddForm(forms.ModelForm):
    hours = forms.IntegerField(min_value=0, max_value=24, required=True)
    minutes = forms.IntegerField(min_value=0, max_value=59, required=True)
    class Meta:
        model = Shift
        fields = ['start', 'building', 'room', 'kind', 'note', 'document', 'require_punch_in_out']
        widgets = {
            'start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, group_id, *args, **kwargs):
        super(BulkShiftAddForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('group_add_shift', kwargs={'group_id': group_id}),
            'hx-swap': 'multi:#add-shift-message:innerHTML,#add-shift-form:innerHTML'
        }
        self.helper.layout = Layout(
            Fieldset(
                "",
                FloatingField('start'),
                HTML("""
                    <label class="form-label requiredField">Duration<span class="asteriskField">*</span></label>
                """),
                Div(
                    Div(
                        FloatingField('hours'),
                        css_class='col-md-6',
                    ),
                    Div(
                        FloatingField('minutes'),
                        css_class='col-md-6',
                    ),
                    css_class='row',
                ),
                FloatingField('building'),
                FloatingField('room'),
                FloatingField('kind'),
                FloatingField('note'),
                FloatingField('document'),
                'require_punch_in_out',
                Div(
                    Submit('submit', 'Add Shift', css_class='btn btn-primary'),
                    css_class='d-flex text-center justify-content-center',
                ),
            )
        )