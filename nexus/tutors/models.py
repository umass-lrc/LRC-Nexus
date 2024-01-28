from django.db import models

from shifts.models import (
    Shift,
)

from users.models import (
    Positions,
)

from core.models import (
    Course,
)

class TutorRoleInfo(models.Model):
    position = models.OneToOneField(
        to=Positions,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text="The position that this role is for."
    )
    
    assigned_courses = models.ManyToManyField(
        to=Course,
        help_text="Courses that this role is for."
    )

class TutorShiftInfo(models.Model):
    shift = models.OneToOneField(
        to=Shift,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text="The shift that this shift info is for."
    )
    
    role = models.ForeignKey(
        to=TutorRoleInfo,
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