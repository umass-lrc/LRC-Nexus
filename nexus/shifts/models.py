from django.db import models

from core.models import (
    Buildings,
    Day,
)

from users.models import (
    Positions,
    NexusUser,
)

class ShiftKind(models.TextChoices):
        SI_SESSION = "SI Session"
        TUTOR_DROP_IN = "Tutor Drop-In"
        TUTOR_APPOINTMENT = "Tutor Appointment"
        GROUP_TUTORING = "Group Tutoring"
        TRAINING = "Training"
        OBSERVATION = "Observation"
        CLASS = "Class"
        PREPARATION = "Preparation"
        MEETING = "Meeting"
        OURS_MENTOR_HOURS = "OURS Mentor Hours"
        OA_HOURS = "OA Hours"
        OTHER = "Other"

class RecurringShift(models.Model):
    position = models.ForeignKey(
        to=Positions,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text="The position that this recurring shift is for."
    )
    
    day = models.PositiveSmallIntegerField(
        choices=Day.choices,
        null=False,
        blank=False,
        help_text="The day of the week that this recurring shift is for."
    )
    
    start_time = models.TimeField(
        null=False,
        blank=False,
        help_text="The start time of the recurring shift."
    )
    
    duration = models.DurationField(
        null=False,
        blank=False,
        help_text="The duration of the recurring shift."
    )
    
    building = models.ForeignKey(
        to=Buildings,
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        help_text="The building the recurring shift is in."
    )
    
    room = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        help_text="The room the recurring shift is in."
    )
    
    kind = models.CharField(
        max_length=30,
        choices=ShiftKind.choices,
        null=False,
        blank=False,
        help_text="The kind of recurring shift."
    )
    
    note = models.TextField(
        null=True,
        blank=True,
        help_text="Any notes for the recurring shift. This will be copied to all shifts."
    )
    
    document = models.FileField(
        null=True,
        blank=True,
        help_text="Any attached document for the recurring shift. This will be copied to all shifts."
    )
    
    require_punch_in_out = models.BooleanField(
        default=False,
        help_text="Whether or not the recurring shift requires punch in/out."
    )
    
    start_date = models.DateField(
        null=False,
        blank=False,
        help_text="The start date of the recurring shift."
    )
    
    end_date = models.DateField(
        null=False,
        blank=False,
        help_text="The end date of the recurring shift. This is inclusive."
    )

class Shift(models.Model):
    position = models.ForeignKey(
        to=Positions,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text="The position that this shift is for."
    )
    
    start = models.DateTimeField(
        null=False,
        blank=False,
        help_text="The start date/time of the shift."
    )
    
    duration = models.DurationField(
        null=False,
        blank=False,
        help_text="The duration of the shift."
    )
    
    building = models.ForeignKey(
        to=Buildings,
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        help_text="The building the shift is in."
    )
    
    room = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        help_text="The room the shift is in."
    )
    
    kind = models.CharField(
        max_length=30,
        choices=ShiftKind.choices,
        null=False,
        blank=False,
        help_text="The kind of shift."
    )
    
    note = models.TextField(
        null=True,
        blank=True,
        help_text="Any notes for the shift."
    )
    
    document = models.FileField(
        null=True,
        blank=True,
        help_text="Any attached document for the shift."
    )
    
    require_punch_in_out = models.BooleanField(
        default=False,
        help_text="Whether or not the shift requires punch in/out."
    )
    
    recurring_shift = models.ForeignKey(
        to=RecurringShift,
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )
    
    dropped = models.BooleanField(
        default=False,
        help_text="Whether or not the shift is dropped."
    )
    
    changed = models.BooleanField(
        default=False,
        help_text="Whether or not the shift has been changed."
    )
    
    def __str__(self):
        return f"{self.position} - {self.kind} - {self.start} - {self.duration}"


class AttendanceInfo(models.Model):
    shift = models.OneToOneField(
        to=Shift,
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        help_text="The shift that this attendance info is for.",
    )
    
    punch_in_time = models.TimeField(
        null=True,
        blank=True,
        help_text="The time you punched in for the shift."
    )
    
    punch_out_time = models.TimeField(
        null=True,
        blank=True,
        help_text="The time you punched out for the shift."
    )
    
    attended = models.BooleanField(
        default=False,
        help_text="Whether or not you attended the shift?"
    )
    
    reason_not_attended = models.TextField(
        null=True,
        blank=True,
        help_text="The reason you did not attend the shift."
    )
    
    signed = models.BooleanField(
        default=False,
        help_text="Whether or not you approved the information provided."
    )
    
    sign_datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date/time the information was signed."
    )
    
    flag_late = models.BooleanField(
        default=False,
        help_text="Whether or not the shift was signed after the payroll period."
    )
    
    def __str__(self):
        return f"{self.shift} - {self.attendance_code} - {self.start} - {self.end}"

class State(models.TextChoices):
    NOT_VIEWED = "Not Viewed"
    IN_PROGRESS = "In Progress"
    DENIED = "Denied"
    APPROVED = "Approved"

class ChangeRequest(models.Model):
    shift = models.ForeignKey(
        to=Shift,
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        help_text="The shift that this change request is for."
    )
    
    start = models.DateTimeField(
        null=False,
        blank=False,
        help_text="The start date/time of the shift."
    )
    
    duration = models.DurationField(
        null=False,
        blank=False,
        help_text="The duration of the shift."
    )
    
    building = models.ForeignKey(
        to=Buildings,
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        help_text="The building the shift is in."
    )
    
    room = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        help_text="The room the shift is in."
    )
    
    kind = models.CharField(
        max_length=30,
        choices=ShiftKind.choices,
        null=False,
        blank=False,
        help_text="The kind of shift."
    )
    
    reason = models.TextField(
        null=False,
        blank=False,
        help_text="The reason for the change request."
    )
    
    state = models.CharField(
        max_length=15,
        choices=State.choices,
        null=False,
        blank=False,
        help_text="The state of the change request."
    )
    
    last_change_by = models.ForeignKey(
        to=NexusUser,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        help_text="The last person to change the state of the change request."
    )
    
    last_changed_on = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date/time the change request was last changed."
    )

class DropRequest(models.Model):
    shift = models.ForeignKey(
        to=Shift,
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        help_text="The shift that this drop request is for."
    )
    
    reason = models.TextField(
        null=False,
        blank=False,
        help_text="The reason for the drop request."
    )
    
    state = models.CharField(
        max_length=15,
        choices=State.choices,
        null=False,
        blank=False,
        help_text="The state of the drop request."
    )
    
    last_change_by = models.ForeignKey(
        to=NexusUser,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        help_text="The last person to change the state of the drop request."
    )
    
    last_changed_on = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date/time the drop request was last changed."
    )