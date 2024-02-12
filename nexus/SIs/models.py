from django.db import models

from shifts.models import (
    RecurringShift,
    ShiftKind,
)

from users.models import (
    Positions,
    PositionChoices
)

from core.models import (
    Classes,
    ClassTimes,
    Semester,
)

class SIRoleInfo(models.Model):
    position = models.ForeignKey(
        to=Positions,
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        help_text="The position that this role is for."
    )
    
    assigned_class = models.ForeignKey(
        to=Classes,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        help_text="The class that this role is for."
    )
    
    class Meta:
        unique_together = [
            "position",
            "assigned_class",
        ]
    
    def save(self, *args, **kwargs):
        if self.position.position != PositionChoices.SI:
            raise ValueError("This role is not for an SI position.")
        if self.id is not None:
            old_role = SIRoleInfo.objects.get(id=self.id)
            SIReccuringShiftInfo.objects.filter(role=old_role).delete()
        super(SIRoleInfo, self).save(*args, **kwargs)
        class_times = ClassTimes.objects.filter(orignal_class=self.assigned_class)
        active_semester = Semester.objects.get_active_semester()
        for class_time in class_times:
            rs = RecurringShift.objects.create(
                position=self.position,
                day=class_time.class_day,
                start_time=class_time.start_time,
                duration=class_time.duration,
                building=class_time.building,
                room=class_time.room,
                kind=ShiftKind.CLASS,
                start_date=active_semester.classes_start,
                end_date=active_semester.classes_end,
            )
            SIReccuringShiftInfo.objects.create(
                role=self,
                class_time=class_time,
                recuring_shift=rs,
            )

class SIReccuringShiftInfo(models.Model):
    role = models.ForeignKey(
        to=SIRoleInfo,
        on_delete=models.RESTRICT,
        null=False,
        blank=False
    )
    
    class_time = models.ForeignKey(
        to=ClassTimes,
        on_delete=models.RESTRICT,
        null=False,
        blank=False
    )
    
    recuring_shift = models.ForeignKey(
        to=RecurringShift,
        on_delete=models.RESTRICT,
        null=False,
        blank=False
    )
    
    class Meta:
        unique_together = [
            "role",
            "class_time",
        ]
    
    def delete(self):
        self.recuring_shift.delete()
        super(SIReccuringShiftInfo, self).delete()