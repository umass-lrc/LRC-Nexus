from django.db import models

from shifts.models import (
    Shift,
)

from users.models import (
    Positions,
)

from core.models import (
    Classes,
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

class SIShiftInfo(models.Model):
    shift = models.OneToOneField(
        to=Shift,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text="The shift that this shift info is for."
    )
    
    role = models.ForeignKey(
        to=SIRoleInfo,
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        help_text="The role that this shift info is for."
    )
    
    class Meta:
        unique_together = [
            "shift",
            "role",
        ]

