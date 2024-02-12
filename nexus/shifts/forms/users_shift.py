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
)

from ..models import (
    Shift,
    RecurringShift,
)

class UserLookUp(forms.Form):
    user = forms.ModelChoiceField(
        queryset=NexusUser.objects.all(),
        widget=autocomplete.ModelSelect2(url='user-autocomplete'),
        required=True,
    )
    
    def __init__(self, *args, **kwargs):
        super(UserLookUp, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('users_shift'),
            'hx-swap': 'multi:#look-up-message:innerHTML,#calendar:innerHTML,#add-shift:innerHTML,#add-edit-recurring:innerHTML,#record-meeting:innerHTML',
        }
        self.helper.layout = Layout(
            Div(
                Div(
                    'user',
                    css_class='col-md-8 justify-content-center',
                ),
                Div(
                    Submit('submit', 'Look Up', css_class='btn btn-primary'),
                    css_class='d-flex text-center col-md-4 justify-content-center',
                ),
                css_class='row align-items-center justify-content-center',
            ),
        )

class AddShiftForm(forms.ModelForm):
    hours = forms.IntegerField(min_value=0, max_value=24, required=True)
    minutes = forms.IntegerField(min_value=0, max_value=59, required=True)
    class Meta:
        model = Shift
        fields = ['position', 'start', 'building', 'room', 'kind', 'note', 'document', 'require_punch_in_out']
        widgets = {
            'start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, user_id, edit, *args, **kwargs):
        super(AddShiftForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['position'].queryset = Positions.objects.filter(semester=Semester.objects.get_active_semester(),user__id=user_id)
        if edit:
            self.helper.attrs = {
                'hx-post': reverse('edit_shift', kwargs={'shift_id': kwargs['instance'].id}),
                'hx-swap': 'multi:#edit-shift-message:innerHTML,#edit-shift-form:innerHTML'
            }
        else:
            self.helper.attrs = {
                'hx-post': reverse('add_shift', kwargs={'user_id': user_id}),
                'hx-swap': 'multi:#add-shift-message:innerHTML,#add-shift-form:innerHTML'
            }
        self.helper.layout = Layout(
            Fieldset(
                "",
                FloatingField('position'),
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
            ),
            Div(
                Submit('submit', 'Add Shift' if not edit else 'Edit Shift', css_class='btn btn-primary'),
                css_class='text-center',
            ),
        )

class AddRecurringShiftForm(forms.ModelForm):
    hours = forms.IntegerField(min_value=0, max_value=24, required=True)
    minutes = forms.IntegerField(min_value=0, max_value=59, required=True)
    
    class Meta:
        model = RecurringShift
        fields = ['position', 'day', 'start_time', 'building', 'room', 'kind', 'note', 'document', 'require_punch_in_out', 'start_date', 'end_date']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, user_id, edit, *args, blank=False, **kwargs):
        super(AddRecurringShiftForm, self).__init__(*args, **kwargs)
        self.fields['position'].queryset = Positions.objects.filter(semester=Semester.objects.get_active_semester(),user__id=user_id)
        self.helper = FormHelper(self)
        
        if blank:
            self.helper.layout = Layout(
                BS5Accordion(
                    AccordionGroup(
                        "Edit Recurring Shift",
                        HTML("""To edit a Recurring Shift, please go to it's row and click edit."""),
                        active=False,
                    ),    
                ),
            )
            return
        
        if edit:
            self.helper.attrs = {
                'hx-post': reverse('edit_recurring', kwargs={'rshift_id': kwargs['instance'].id}),
                'hx-swap': f'multi:#rt-{kwargs["instance"].id}:innerHTML,#edit-recurring-message:innerHTML',
            }
        else:
            self.helper.attrs = {
                'hx-post': reverse('add_recurring', kwargs={'user_id': user_id}),
                'hx-swap': 'multi:#recurring-body:beforeend,#add-recurring-message:innerHTML,#add-recurring-form:innerHTML'
            }
        
        
        self.helper.layout = Layout(
            BS5Accordion(
                AccordionGroup(
                    "Add Recurring Shift" if not edit else "Edit Recurring Shift",
                    Fieldset(
                        "",
                        FloatingField('position'),
                        FloatingField('day'),
                        FloatingField('start_time'),
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
                        FloatingField('start_date'),
                        FloatingField('end_date'),
                    ),
                    Div(
                        Submit('submit', 'Add Recurring Shift' if not edit else 'Edit Recurring Shift', css_class='btn btn-primary'),
                        css_class='text-center',
                    ),
                    active=False,
                ),
            ),
        )