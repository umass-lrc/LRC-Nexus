from datetime import datetime, timedelta
from django.utils import timezone

from django.db import models

from core.models import (
    Buildings,
    Day,
    Holiday,
    Semester,
    DaySwitch,
    ClassTimes,
)

from users.models import (
    Positions,
    NexusUser,
)

from payrolls.models import (
    Payroll,
    PayrollStatus,
    PayrollNotSigned,
    PayrollNotInHR,
)

def get_weekend(date):
    while date.weekday() != 5:
        date += timedelta(days=1)
    return date

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

def recurring_shift_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    filename = filename.replace(' ', '_')
    filename = datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + '_' + filename
    return f'rec_shift_{instance.position.id}/{filename}'

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
        upload_to=recurring_shift_directory_path,
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
    
    class_time = models.ForeignKey(
        to=ClassTimes,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        help_text="The class time that this recurring shift is for."
    )
    
    def save(self, *args, **kwargs):
        update = self.id is not None
        recurring_shift = super(RecurringShift, self).save(*args, **kwargs)
        
        todays_date = datetime.now().date()
        start_date = self.start_date if self.start_date > todays_date else todays_date
        
        if update:
            shifts = Shift.objects.filter(recurring_shift=self, start__date__gte=start_date).all()
            
            for shift in shifts:
                shift.delete()
        
        while (start_date.weekday()+1)%7 != self.day:
            start_date += timedelta(days=1)
        
        if start_date > self.end_date:
            return recurring_shift
        
        active_sem = Semester.objects.get_active_semester()
        holidays = Holiday.objects.filter(semester=active_sem, date__gte=start_date, date__lte=self.end_date).values_list('date', flat=True)
        day_switches = DaySwitch.objects.filter(semester=active_sem, date__gte=start_date, date__lte=self.end_date).all()
        day_switches_dates = day_switches.values_list('date', flat=True)
        date_which_follow_day = day_switches.filter(day_to_follow=self.day).values_list('date', flat=True)
        
        for date in date_which_follow_day:
            Shift.objects.create(
                position=self.position,
                start=timezone.make_aware(datetime.combine(date, self.start_time)),
                duration=self.duration,
                building=self.building,
                room=self.room,
                kind=self.kind,
                note=self.note,
                document=self.document,
                require_punch_in_out=self.require_punch_in_out,
                recurring_shift=self,
            )
        
        while start_date <= self.end_date:
            if not (start_date in holidays or start_date in day_switches_dates):
                Shift.objects.create(
                    position=self.position,
                    start=timezone.make_aware(datetime.combine(start_date, self.start_time)),
                    duration=self.duration,
                    building=self.building,
                    room=self.room,
                    kind=self.kind,
                    note=self.note,
                    document=self.document,
                    require_punch_in_out=self.require_punch_in_out,
                    recurring_shift=self,
                )
            start_date += timedelta(days=7)
        
        return recurring_shift
    
    def delete(self):
        todays_date = datetime.now().date()
        for shift in Shift.objects.filter(recurring_shift=self, start__date__gte=todays_date).all():
            shift.delete()
        super(RecurringShift, self).delete()

def shift_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    filename = filename.replace(' ', '_')
    filename = datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + '_' + filename
    return f'shift_{instance.position.id}/{filename}'

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
        upload_to=shift_directory_path,
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
    
    
    def save(self, *args, **kwargs):
        update = self.id is not None
        if update:
            old_shift = Shift.objects.get(id=self.id)
            if AttendanceInfo.objects.get(shift=old_shift).signed:
                raise Exception("Cannot edit a signed shift.")
            not_signed_payroll = PayrollNotSigned.objects.get(payroll__position=old_shift.position, payroll__week_end=get_weekend(old_shift.start.date()))
            start_weekday = old_shift.start.weekday()
            if start_weekday == 6:
                not_signed_payroll.sunday_hours -= old_shift.duration
            elif start_weekday == 0:
                not_signed_payroll.monday_hours -= old_shift.duration
            elif start_weekday == 1:
                not_signed_payroll.tuesday_hours -= old_shift.duration
            elif start_weekday == 2:
                not_signed_payroll.wednesday_hours -= old_shift.duration
            elif start_weekday == 3:
                not_signed_payroll.thursday_hours -= old_shift.duration
            elif start_weekday == 4:
                not_signed_payroll.friday_hours -= old_shift.duration
            elif start_weekday == 5:
                not_signed_payroll.saturday_hours -= old_shift.duration
            not_signed_payroll.save()
        shift = super(Shift, self).save(*args, **kwargs)
        
        if not update:
            AttendanceInfo.objects.create(
                shift=self,
            )
            
        if not Payroll.objects.filter(position=self.position, week_end=get_weekend(self.start.date())).exists():
            Payroll.objects.create(
                position=self.position,
                week_end=get_weekend(self.start.date()),
                status=PayrollStatus.NOT_IN_HR,
            )
        
        not_signed_payroll = PayrollNotSigned.objects.get(payroll__position=self.position, payroll__week_end=get_weekend(self.start.date()))
        start_weekday = self.start.weekday()
        if start_weekday == 6:
            not_signed_payroll.sunday_hours += self.duration
        elif start_weekday == 0:
            not_signed_payroll.monday_hours += self.duration
        elif start_weekday == 1:
            not_signed_payroll.tuesday_hours += self.duration
        elif start_weekday == 2:
            not_signed_payroll.wednesday_hours += self.duration
        elif start_weekday == 3:
            not_signed_payroll.thursday_hours += self.duration
        elif start_weekday == 4:
            not_signed_payroll.friday_hours += self.duration
        elif start_weekday == 5:
            not_signed_payroll.saturday_hours += self.duration
        not_signed_payroll.save()
        
        return shift
    
    def delete(self):
        attendance = AttendanceInfo.objects.get(shift=self)
        if attendance.signed:
            raise Exception("Cannot delete a signed shift.")
        attendance.delete()
        not_signed_payroll = PayrollNotSigned.objects.get(payroll__position=self.position, payroll__week_end=get_weekend(self.start.date()))
        start_weekday = self.start.weekday()
        if start_weekday == 6:
            not_signed_payroll.sunday_hours -= self.duration
        elif start_weekday == 0:
            not_signed_payroll.monday_hours -= self.duration
        elif start_weekday == 1:
            not_signed_payroll.tuesday_hours -= self.duration
        elif start_weekday == 2:
            not_signed_payroll.wednesday_hours -= self.duration
        elif start_weekday == 3:
            not_signed_payroll.thursday_hours -= self.duration
        elif start_weekday == 4:
            not_signed_payroll.friday_hours -= self.duration
        elif start_weekday == 5:
            not_signed_payroll.saturday_hours -= self.duration
        not_signed_payroll.save()
        super(Shift, self).delete()
    
    def __str__(self):
        return f"{self.kind} {self.building.short_name}-{self.room} {timezone.localtime(self.start).strftime('%m/%d, %I:%M %p')}"


class AttendanceInfo(models.Model):
    shift = models.OneToOneField(
        to=Shift,
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        help_text="The shift that this attendance info is for.",
        related_name="attendance_info",
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
    
    def did_attend(self):
        pns = PayrollNotSigned.objects.get(payroll__position=self.shift.position, payroll__week_end=get_weekend(self.shift.start.date()))
        nihr = PayrollNotInHR.objects.get(payroll__position=self.shift.position, payroll__week_end=get_weekend(self.shift.start.date()))
        start_weekday = self.shift.start.weekday()
        pns.total_hours -= self.shift.duration
        nihr.total_hours += self.shift.duration
        if start_weekday == 6:
            pns.sunday_hours -= self.shift.duration
            nihr.sunday_hours += self.shift.duration
        elif start_weekday == 0:
            pns.monday_hours -= self.shift.duration
            nihr.monday_hours += self.shift.duration
        elif start_weekday == 1:
            pns.tuesday_hours -= self.shift.duration
            nihr.tuesday_hours += self.shift.duration
        elif start_weekday == 2:
            pns.wednesday_hours -= self.shift.duration
            nihr.wednesday_hours += self.shift.duration
        elif start_weekday == 3:
            pns.thursday_hours -= self.shift.duration
            nihr.thursday_hours += self.shift.duration
        elif start_weekday == 4:
            pns.friday_hours -= self.shift.duration
            nihr.friday_hours += self.shift.duration
        elif start_weekday == 5:
            pns.saturday_hours -= self.shift.duration
            nihr.saturday_hours += self.shift.duration
        pns.save()
        nihr.save()
    
    def did_not_attend(self):
        pns = PayrollNotSigned.objects.get(payroll__position=self.shift.position, payroll__week_end=get_weekend(self.shift.start.date()))
        start_weekday = self.shift.start.weekday()
        pns.total_hours -= self.shift.duration
        if start_weekday == 6:
            pns.sunday_hours -= self.shift.duration
        elif start_weekday == 0:
            pns.monday_hours -= self.shift.duration
        elif start_weekday == 1:
            pns.tuesday_hours -= self.shift.duration
        elif start_weekday == 2:
            pns.wednesday_hours -= self.shift.duration
        elif start_weekday == 3:
            pns.thursday_hours -= self.shift.duration
        elif start_weekday == 4:
            pns.friday_hours -= self.shift.duration
        elif start_weekday == 5:
            pns.saturday_hours -= self.shift.duration
        pns.save()
        
    def __str__(self):
        return f"{self.shift} - Signed:{self.signed}"

class State(models.TextChoices):
    NOT_VIEWED = "Not Viewed"
    IN_PROGRESS = "In Progress"
    DENIED = "Denied"
    APPROVED = "Approved"

class ChangeRequest(models.Model):
    shift = models.ForeignKey(
        to=Shift,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        help_text="The shift that this change request is for."
    )
    
    position = models.ForeignKey(
        to=Positions,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="The position assosiated with this request."
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