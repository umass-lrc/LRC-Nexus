from django.db import models

from shifts.models import (
    RecurringShift,
)

from users.models import (
    Positions,
)

from core.models import (
    Classes,
    ClassTimes,
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
        if self.position.position != "SI":
            raise ValueError("This role is not for an SI position.")
        if self.id is not None:
            old_role = SIRoleInfo.objects.get(id=self.id)
            
        new_role = super(SIRoleInfo, self).save(*args, **kwargs)

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

