from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, HTML
from crispy_forms.bootstrap import AccordionGroup

from crispy_bootstrap5.bootstrap5 import BS5Accordion, FloatingField
from django.urls import reverse

from core.models import (
    Buildings,
)

from shifts.models import (
    ShiftKind,
)

from users.models import (
    Positions,
    PositionChoices,
)

shift_type_choices = {
    PositionChoices.TUTOR: [
        ShiftKind.TUTOR_DROP_IN,
        ShiftKind.TUTOR_APPOINTMENT,
        ShiftKind.MEETING,
        ShiftKind.TRAINING,
        ShiftKind.OTHER,
    ],
    PositionChoices.TUTOR_PM: [
        ShiftKind.OBSERVATION,
        ShiftKind.MEETING,
        ShiftKind.TRAINING,
        ShiftKind.OTHER,
    ],
    PositionChoices.OURS_MENTOR: [
        ShiftKind.OURS_MENTOR_HOURS,
        ShiftKind.MEETING,
        ShiftKind.TRAINING, 
        ShiftKind.OTHER,
    ],
    PositionChoices.OURS_MENTOR_PM: [
        ShiftKind.OBSERVATION,
        ShiftKind.MEETING,
        ShiftKind.TRAINING,
        ShiftKind.OTHER,
    ],
    PositionChoices.OFFICE_ASSISTANT: [
        ShiftKind.OA_HOURS,
        ShiftKind.MEETING,
        ShiftKind.TRAINING,
        ShiftKind.OTHER,
    ],
    PositionChoices.OFFICE_ASSISTANT_PM: [
        ShiftKind.OBSERVATION,
        ShiftKind.MEETING,
        ShiftKind.TRAINING,
        ShiftKind.OTHER,
    ],
    PositionChoices.TECH: [
        ShiftKind.MEETING,
        ShiftKind.OTHER,
    ],
    PositionChoices.SI: [
        ShiftKind.CLASS,
        ShiftKind.SI_SESSION,
        ShiftKind.PREPARATION,
        ShiftKind.MEETING,
        ShiftKind.TRAINING,
        ShiftKind.OTHER,
    ],
    PositionChoices.SI_PM: [
        ShiftKind.OBSERVATION,
        ShiftKind.MEETING,
        ShiftKind.TRAINING,
        ShiftKind.OTHER,
    ],
}

class PunchInForm(forms.Form):
    building = forms.ModelChoiceField(queryset=Buildings.objects.none(), required=True)
    room = forms.CharField(initial=1020, max_length=10, required=True)
    kind = forms.ChoiceField(choices=ShiftKind.choices, required=True)
    
    def __init__(self, position, is_punched_in, *args, **kwargs):
        super(PunchInForm, self).__init__(*args, **kwargs)
        
        self.fields['building'].queryset = Buildings.objects.all()
        try:
            self.fields['building'].initial = Buildings.objects.get(short_name='LIBR')
        except Buildings.DoesNotExist:
            self.fields['building'].initial = None

        self.fields['kind'].choices = [(sk.value, sk.label) for sk in shift_type_choices[position.position]]
        
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('punch_in_out_position', kwargs={'position_id': position.id}),
            'hx-swap': f'multi:#punch-in-out-{position.id}:outerHTML,#punch-in-out-message:innerHTML',
        }
        self.helper.layout = Layout(
            Fieldset(
                str(position),
                FloatingField('building'),
                FloatingField('room'),
                FloatingField('kind'),
                Div(
                    Submit('punch_in_submit', 'Punch In' if not is_punched_in else 'Punch Out of Other & Punch In', css_class='btn btn-primary',onclick="clickedButton(this)"),
                    css_class='text-center',
                ),
            ),
        )

class PunchOutForm(forms.Form):
    def __init__(self, position, *args, **kwargs):
        super(PunchOutForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('punch_in_out_position', kwargs={'position_id': position.id}),
            'hx-swap': f'multi:#punch-in-out-{position.id}:outerHTML,#punch-in-out-message:innerHTML',
        }
        self.helper.layout = Layout(
            Fieldset(
                str(position),
                Div(
                    Submit('submit', 'Punch Out', css_class='btn btn-primary',onclick="clickedButton(this)"),
                    css_class='text-center',
                ),
            ),
        )

class ShiftPunchInForm(forms.Form):
    position = forms.ModelChoiceField(queryset=Positions.objects.all(), required=True)
    start = forms.DateTimeField(required=True)
    duration = forms.DurationField(required=True)
    building = forms.ModelChoiceField(queryset=Buildings.objects.all(), required=True)
    room = forms.CharField(max_length=10, required=True)
    kind = forms.ChoiceField(choices=ShiftKind.choices, required=True)
    
    def __init__(self, shift, position, is_punched_in, *args, **kwargs):
        super(ShiftPunchInForm, self).__init__(*args, **kwargs)
        
        self.fields['position'].disabled = True
        self.fields['start'].disabled = True
        self.fields['duration'].disabled = True
        self.fields['building'].disabled = True
        self.fields['room'].disabled = True
        self.fields['kind'].disabled = True
        
        self.fields['position'].initial = shift.position
        self.fields['start'].initial = shift.start
        self.fields['duration'].initial = shift.duration
        self.fields['building'].initial = shift.building
        self.fields['room'].initial = shift.room
        self.fields['kind'].initial = shift.kind
        
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('shift_punch_in_out', kwargs={'shift_id': shift.id}),
            'hx-swap': f'multi:#punch-in-out-{position.id}:outerHTML,#punch-in-out-message:innerHTML',
        }
        
        self.helper.layout = Layout(
            Fieldset(
                str(shift),
                FloatingField('position'),
                FloatingField('start'),
                FloatingField('duration'),
                FloatingField('building'),
                FloatingField('room'),
                FloatingField('kind'),
                Div(
                    Submit('submit', 'Punch In' if not is_punched_in else 'Punch Out of Other & Punch In', css_class='btn btn-primary'),
                    css_class='text-center',
                ),
                active=False,
            ),
        )

class ShiftPunchOutForm(forms.Form):
    
    def __init__(self, shift, position, *args, **kwargs):
        super(ShiftPunchOutForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('shift_punch_in_out', kwargs={'shift_id': shift.id}),
            'hx-swap': f'multi:#punch-in-out-{position.id}:outerHTML,#punch-in-out-message:innerHTML',
        }
        
        self.helper.layout = Layout(
            Fieldset(
                str(shift),
                Div(
                    Submit('submit', 'Punch Out', css_class='btn btn-primary'),
                    css_class='text-center',
                ),
            ),
        )

class SignShiftForm(forms.Form):
    position = forms.ModelChoiceField(queryset=Positions.objects.all(), required=True)
    start = forms.DateTimeField(required=True)
    duration = forms.DurationField(required=True)
    building = forms.ModelChoiceField(queryset=Buildings.objects.all(), required=True)
    room = forms.CharField(max_length=10, required=True)
    kind = forms.ChoiceField(choices=ShiftKind.choices, required=True)
    reason = forms.CharField(max_length=100, required=False, help_text="<b>Only needed if you didn't attend.</b> Specify why you didn't attend.")
    
    def __init__(self, requires_punch_in_out, *args, **kwargs):
        super(SignShiftForm, self).__init__(*args, **kwargs)
        
        self.fields['position'].disabled = True
        self.fields['start'].disabled = True
        self.fields['duration'].disabled = True
        self.fields['building'].disabled = True
        self.fields['room'].disabled = True
        self.fields['kind'].disabled = True
        
        self.fields['position'].initial = kwargs['initial']['position']
        self.fields['start'].initial = kwargs['initial']['start']
        self.fields['duration'].initial = kwargs['initial']['duration']
        self.fields['building'].initial = kwargs['initial']['building']
        self.fields['room'].initial = kwargs['initial']['room']
        self.fields['kind'].initial = kwargs['initial']['kind']
        
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('attendance_for_shift', kwargs={'shift_id': kwargs['initial']['shift_id']}),
            'hx-swap': f'multi:#attendance-shift-{kwargs["initial"]["shift_id"]}:outerHTML,#attendance-shift-message:innerHTML',
        }
        self.helper.layout = Layout(
            BS5Accordion(
                AccordionGroup(
                    str(kwargs['initial']['shift']),
                    FloatingField('position'),
                    FloatingField('start'),
                    FloatingField('duration'),
                    FloatingField('building'),
                    FloatingField('room'),
                    FloatingField('kind'),
                    FloatingField('reason'),
                    Div(
                        Submit('did_attend', 'Attended', css_class='btn btn-primary') if not requires_punch_in_out else Div(),
                        Submit('did_not_attend', "Didn't Attend", css_class='btn btn-danger'),
                        css_class='text-center',
                    ),
                    active=False,
                ),
            ),
        )
        
class WeekPayrollApproveForm(forms.Form):
    extra_context = {}
    
    def __init__(self, payroll, *args, **kwargs):
        super(WeekPayrollApproveForm, self).__init__(*args, **kwargs)
        
        self.extra_context = {'payroll': payroll}
        self.helper = FormHelper(self)
        self.helper.attrs = {
            'hx-post': reverse('approve_entire_week', kwargs={'payroll_id': payroll.id}),
            'hx-swap': f'multi:#approve-week-{payroll.id}:outerHTML,#approve-weeks-message:innerHTML',
        }
        self.helper.layout = Layout(
            BS5Accordion(
                AccordionGroup(
                    f"{payroll.position.get_position_display()} - {str(payroll.week_end)}",
                    Div(
                        HTML("""
                            {% load hours %}
                            <table class="table table-bordered table-striped">
                            <thead>
                            <tr>
                                <th class="text-center" scope="col">Sunday</th>
                                <th class="text-center" scope="col">Monday</th>
                                <th class="text-center" scope="col">Tuesday</th>
                                <th class="text-center" scope="col">Wednesday</th>
                                <th class="text-center" scope="col">Thursday</th>
                                <th class="text-center" scope="col">Friday</th>
                                <th class="text-center" scope="col">Saturday</th>
                                <th class="text-center" scope="col">Total</th>
                            </tr>
                            </thead>
                            <tbody>
                                <td class="text-end">{{payroll.not_in_hr.sunday_hours|hours}}</td>
                                <td class="text-end">{{payroll.not_in_hr.monday_hours|hours}}</td>
                                <td class="text-end">{{payroll.not_in_hr.tuesday_hours|hours}}</td>
                                <td class="text-end">{{payroll.not_in_hr.wednesday_hours|hours}}</td>
                                <td class="text-end">{{payroll.not_in_hr.thursday_hours|hours}}</td>
                                <td class="text-end">{{payroll.not_in_hr.friday_hours|hours}}</td>
                                <td class="text-end">{{payroll.not_in_hr.saturday_hours|hours}}</td>
                                <th class="text-end" scope="row">{{payroll.not_in_hr.total_hours|hours}}</th>
                            </tbody>
                            </table>
                        """),
                        css_class='table-responsive',
                    ),
                    Div(
                        HTML("<p><b>Please refrain from approving if you find any discrepancies in the hours.</b> Instead, please fill out the Payroll Correction form available at the supervisor desk in the LRC main office.</p>"),
                        css_class='text-center text-danger',
                    ),
                    Div(
                        Submit('submit', 'Approve', css_class='btn btn-primary'),
                        css_class='text-center',
                    ),
                    active=False,
                ),
            ),
        )