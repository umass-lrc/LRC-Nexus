from datetime import timedelta

from django.db import models

from users.models import (
    Positions,
)

class PayrollStatus(models.TextChoices):
    NOT_IN_HR = "Not In HR"
    IN_HR_ON_TIME = "In HR On Time"
    IN_HR_VIA_LATE_PAY = "In HR Via Late Pay"

class Payroll(models.Model):
    position = models.ForeignKey(
        to=Positions,
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        help_text="The position that this payroll is for."
    )
    
    week_end = models.DateField(
        null=False,
        blank=False,
        help_text="The end date of the payroll week."
    )
    
    status = models.CharField(
        max_length=30,
        choices=PayrollStatus.choices,
        null=False,
        blank=False,
        help_text="The status of the payroll."
    )
    
    class Meta:
        unique_together = [
            "position",
            "week_end",
        ]
    
    def save(self, *args, **kwargs):
        print("\n\n###########WTF!!##############\n\n")
        update = self.id is not None
        super(Payroll, self).save(*args, **kwargs)
        if update:
            return
        PayrollInHR.objects.create(payroll=self)
        PayrollInHRViaLatePay.objects.create(payroll=self)
        PayrollNotInHR.objects.create(payroll=self)
        PayrollNotSigned.objects.create(payroll=self)
        return

class PayrollInHR(models.Model):
    payroll = models.OneToOneField(
        to=Payroll,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    
    sunday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Sunday."
    )
    
    monday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Monday."
    )
    
    tuesday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Tuesday."
    )
    
    wednesday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Wednesday."
    )
    
    thursday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Thursday."
    )
    
    friday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Friday."
    )
    
    saturday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Saturday."
    )
    
    total_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked for the week."
    )

class PayrollInHRViaLatePay(models.Model):
    payroll = models.OneToOneField(
        to=Payroll,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    
    sunday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Sunday."
    )
    
    monday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Monday."
    )
    
    tuesday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Tuesday."
    )
    
    wednesday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Wednesday."
    )
    
    thursday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Thursday."
    )
    
    friday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Friday."
    )
    
    saturday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Saturday."
    )
    
    total_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked for the week."
    )

class PayrollNotInHR(models.Model):
    payroll = models.OneToOneField(
        to=Payroll,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    
    sunday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Sunday."
    )
    
    monday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Monday."
    )
    
    tuesday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Tuesday."
    )
    
    wednesday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Wednesday."
    )
    
    thursday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Thursday."
    )
    
    friday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Friday."
    )
    
    saturday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Saturday."
    )
    
    total_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked for the week."
    )

class PayrollNotSigned(models.Model):
    payroll = models.OneToOneField(
        to=Payroll,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    
    sunday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Sunday."
    )
    
    monday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Monday."
    )
    
    tuesday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Tuesday."
    )
    
    wednesday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Wednesday."
    )
    
    thursday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Thursday."
    )
    
    friday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Friday."
    )
    
    saturday_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked on Saturday."
    )
    
    total_hours = models.DurationField(
        null=False,
        blank=False,
        default=timedelta(hours=0),
        help_text="The total number of hours worked for the week."
    )
